# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
###
### This full package extends VisTrails, providing GIS/Earth Observation
### ingestion, pre-processing, transformation, analytic and visualisation
### capabilities . Included is the abilty to run code transparently in
### OpenNebula cloud environments. There are various software
### dependencies, but all are FOSS.
###
### This file may be used under the terms of the GNU General Public
### License version 2.0 as published by the Free Software Foundation
### and appearing in the file LICENSE.GPL included in the packaging of
### this file.  Please review the following to ensure GNU General Public
### Licensing requirements will be met:
### http://www.opensource.org/licenses/gpl-license.php
###
### If you are unsure which license is appropriate for your use (for
### instance, you are interested in developing a commercial derivative
### of VisTrails), please contact us at vistrails@sci.utah.edu.
###
### This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
### WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
###
#############################################################################
"""This module is the core; holding annotations and mixins.
"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

import Shared  # This lib goes accross as part of the setup
import rpyc  # Node must have rpyc installed so not a problem
#used top make a copy of the returned value
import copy
#node has dummy versions of these so not a problem
from core.modules.vistrails_module import Module


def refreshPackage(connection, packageName, checkVersion=False, force=False):
    reFresh = force
    package = __import__(packageName, fromlist=['packages'])

    try:
        rpackage = connection.modules[packageName]
    except ImportError, er:
        print packageName, er
        reFresh = True

    if (not reFresh) and checkVersion and (rpackage.version != package.version):
        print packageName, "Versions Differ"
        reFresh = True

    if reFresh:
        print "Uploading %s..." % packageName
        rpyc.classic.upload_package(connection, package, "./tmp/" +\
                                    packageName.replace(".", "/"))
        print "Refreshing Modules for  %s..." % packageName
        refreshmodules = [(mod if mod.startswith(packageName) else None) \
            for mod in connection.modules.sys.modules.keys()]
        for refreshmodule in refreshmodules:
            if refreshmodule:
                try:
                    rpackage = connection.modules[refreshmodule]
                    connection.modules.__builtin__.reload(rpackage)
                    #print "Refreshed Module %s..."%refreshmodule
                except ImportError:
                    pass
                    #print "Module %s not refreshed..."%refreshmodule
    else:
        print "Skipping %s..." % packageName


class RPyCModule(Module):
    """
    This forms the basis for ensuring that rpyc-based modules have the correct
    input ports.
    """
    _input_ports = [('rpycnode', '(za.co.csir.eo4vistrails:RpyC Node:rpyc)')]


class RPyCSafeModule(object):
    """
    RPyCSafeModule executes the compute method on a RPyC node.

    This annotation mixes in the code needed to ensure both threadsafe execution
    and rpyc safe execution.
    """

    def __init__(self, requiredVisPackages=[]):
        #Always need packages.eo4vistrails in requiredvispackages
        self._requiredVisPackages = requiredVisPackages

    def __call__(self, clazz):
        if not "packages.eo4vistrails" in self._requiredVisPackages:
            self._requiredVisPackages.append("packages.eo4vistrails")
        clazz._requiredVisPackages = self._requiredVisPackages

        try:
            if Shared.isRemoteRPyCNode:
                return clazz
        except AttributeError:
            Shared.isRemoteRPyCNode = False
        except NameError:
            Shared.isRemoteRPyCNode = False

        if RPyCModule not in clazz.__bases__:
            try:
                clazz._input_ports = clazz._input_ports + RPyCModule._input_ports
            except AttributeError:
                clazz._input_ports = RPyCModule._input_ports
                pass

        if RPyCSafeMixin not in clazz.__bases__:
            new__bases__ = (RPyCSafeMixin,) + clazz.__bases__
            new__dict__ = clazz.__dict__.copy()
            new__dict__['_original_compute'] = new__dict__['compute']

            del(new__dict__['compute'])  # = RPyCSafeMixin.compute

        return type(clazz.__name__, new__bases__, new__dict__)


class RPyCSafeMixin(object):
    """
    This module provides a developer with dummy versions
    of each of the methods that a module would normally supply.

    An instance of a RPyC module created in VisTrails will have the proper
    vistrails module mixed in by the annotation. On a RPyC node
    the dummy verion is used to instantiate a shadow of the original
    module. The shadow's methods are linked back to the original module.
    """

    def clear(self):
        print "clear"
        Module.clear(self)
        if self.conn:
            try:
                self.conn.proc.terminate()
            except:
                pass
            try:
                self.conn.proc.wait()
            except:
                pass
            try:
                self.conn.close()
            except:
                pass

    def getConnection(self):
        connection = None
        if self.hasInputFromPort('rpycnode'):
            v = self.getInputFromPort('rpycnode')
            print v

            (isRemote, connection) = self.inputPorts['rpycnode'][0].obj.getSharedConnection()
            
            if isRemote:
                #TODO: remove once finishing dev should just work of version numbers
                #Upload any vistrails packages that may be required
                for packageName in self._requiredVisPackages:
                    refreshPackage(connection, packageName, checkVersion=True, force=True)

                print "Finished uploading module requirements to node...."

        return connection

    def setResultCopy(self, port, value):
        self.outputPorts[port] = rpyc.classic.obtain(value)

    def compute(self):
        #Get RPyC Node in good standing
        #input from rpycmodule

        self.conn = self.getConnection()

        if not self.conn:
            #run as per normal
            print "run as per normal", self
            self.setResultCopy = self.setResult
            self._original_compute()
        else:
            #redirect StdIO back here so we can see what is going on            
            import sys
            self.conn.modules.sys.stdout = sys.stdout

            #Just sum setup stuff to make sure vistrails is safe
            #self.conn.execute('import core.requirements')
            self.conn.execute('import init_for_library')
            #Make sure it knows its a remote node
            self.conn.execute('import packages.eo4vistrails.rpyc.Shared as Shared')
            self.conn.execute('Shared.isRemoteRPyCNode=True')

            #Instantiate Shadow Object
            print 'from %s import %s' % (self.__module__, self.__class__.__name__)
            print '%s' % self.conn.modules.sys.path
            self.conn.execute('from %s import %s' % (self.__module__, self.__class__.__name__))
            shadow = self.conn.eval('%s()' % (self.__class__.__name__))

            #Hook Up Shadow Objects Methods and Attributes
            #attributes
            for attribute in Module.__dict__:
                if not str(attribute) in ('compute', '__dict__', '__module__', '__doc__', '__str__', '__weakref__', '__init__'):
                    shadow.__setattr__(str(attribute), self.__getattribute__(str(attribute)))

            shadow.inputPorts = self.inputPorts
            shadow.outputPorts = self.outputPorts
            shadow.is_method = self.is_method
            shadow.upToDate = self.upToDate
            shadow.logging = self.logging
            shadow._latest_method_order = self._latest_method_order
            shadow.moduleInfo = self.moduleInfo
            shadow.is_breakpoint = self.is_breakpoint
            shadow.is_fold_operator = self.is_fold_operator
            shadow.is_fold_module = self.is_fold_module
            shadow.computed = self.computed
            shadow.signature = self.signature

            self.conn.execute('import core.interpreter.default')
            shadow.interpreter = self.conn.eval('core.interpreter.default.get_default_interpreter()')

            print "Executing in the shadow class"
            #Call the Shadow Objects Compute
            shadow.compute()

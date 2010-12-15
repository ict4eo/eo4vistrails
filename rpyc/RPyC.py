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
"""
Created on Tue Dec 14 09:38:10 2010

@author: tvzyl

Module forms part of the rpyc vistrails capabilties, used to add multicore
parallel and distributed processing to vistrails.

This Module is the core module holding annotaions and mixins

"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

import Shared

class RPyCSafeModule(object):
    """
    RPyCSafeModule is a Module that executes the compute method on a RPyC node.
    This annotaion mixes in the code needed to ensure both threadsafe execution
    and rpyc safe execution
    """
    def __init__(self, requiredVisPackages=[]):
        #Always need packages.eo4vistrails in requiredvispackages
        if not "packages.eo4vistrails" in requiredVisPackages:
            requiredVisPackages.append("packages.eo4vistrails")
        self.requiredVisPackages = requiredVisPackages
    
    def __call__(self, clazz):
        clazz.requiredVisPackages = self.requiredVisPackages
        try:
            if Shared.isRemoteRPyCNode:
                return clazz
        except AttributeError:
            Shared.isRemoteRPyCNode = False
        except NameError:
            Shared.isRemoteRPyCNode = False
        
        from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
        if ThreadSafeMixin not in clazz.__bases__:
            clazz._oldthreadinit = clazz.__init__
            clazz.__init__ = ThreadSafeMixin.__init__
            clazz.__bases__ = (ThreadSafeMixin,) + clazz.__bases__

        if RPyCSafeMixin not in clazz.__bases__:
            clazz._oldrpycinit = clazz.__init__          
            clazz.__init__ = RPyCSafeMixin.__init__
            clazz.__bases__ = (RPyCSafeMixin,) + clazz.__bases__
            clazz.compute = RPyCSafeMixin.compute

        return clazz

class RPyCSafeMixin(object):
    """
    This is a dummy module used to provide the devloper with dummy versions 
    of each of the methods that Module would normally supply. 
    An instance of a RPyC module created in vistrails will have the proper 
    vistrails module mixed in by the annotation. On a RPyC node 
    the dummy verion is used to instantiate a shadow of the origional 
    module. The shadows methods are linked back to the origional module.
    """
    def __init__(self, *args, **kwargs):
        self._oldthreadinit(*args, **kwargs)
        self._oldrpycinit(*args, **kwargs)
    
    def compute(self):
        """TODO: Do Shadow Compute Here"""
        #Get RPyC Node in good standing
        import rpyc

        rpycnodein = self.forceGetInputFromPort('rpycnode')
        if type(rpycnodein) == list:
            rpycnode = rpycnodein[0]
        else:
            rpycnode = rpycnodein
        
        #if we don't get a good node then we need to create a subprocess
        isSubProc = False
        if rpycnode == None:
            isSubProc = True
            conn = rpyc.classic.connect_subproc()
        else:
            conn = rpyc.classic.connect(rpycnode.get_ip(), rpycnode.get_port())

        #redirect StdIO back here so we can see what is going on        
        rpyc.classic.redirected_stdio(conn)
        
        #Make sure all the right stuff is in place espcially dummy core and packages
        import packages.eo4vistrails.rpyc.dummycore
        rpyc.classic.upload_package(conn, packages.eo4vistrails.rpyc.dummycore, "./tmp/core")

        import packages.eo4vistrails.rpyc.dummypackages
        rpyc.classic.upload_package(conn, packages.eo4vistrails.rpyc.dummypackages, "./tmp/packages")

        #Upload any vsitrails packages that may be required
        for packageName in self.requiredVisPackages:
            print packageName
            package = __import__(packageName, fromlist=['packages'])
            print package
            rpyc.classic.upload_package(conn, package, "./tmp/"+packageName.replace(".","/"))

        #make sure all packages are in the path
        if not "./tmp" in conn.modules.sys.path:
            conn.modules.sys.path.append('./tmp')

        #Make sure it know its a remote node
        conn.execute('import packages.eo4vistrails.rpyc.Shared as Shared')
        conn.execute('Shared.isRemoteRPyCNode=True')

        #Realod the current module
        #import inspect
        #rpyc.classic.update_module(conn, inspect.getmodule(self))
        rmodule = conn.modules[self.__module__]
        conn.modules.__builtin__.reload(rmodule)
        
        #Instantiate Shadow Object
        conn.execute('from '+self.__module__+' import '+self.__class__.__name__)
        shadow = conn.eval(self.__class__.__name__+'()')
        
        #Hook Up Shadow Objects Methods and Attributes
        #attributes
        shadow.logging = self.logging
        shadow.inputPorts = self.inputPorts
        shadow.outputPorts = self.outputPorts
        shadow.upToDate = self.upToDate
        shadow.is_method = self.is_method
        shadow._latest_method_order = self._latest_method_order
        shadow.moduleInfo = self.moduleInfo
        shadow.is_breakpoint = self.is_breakpoint
        shadow.is_fold_operator = self.is_fold_operator
        shadow.is_fold_module = self.is_fold_module
        shadow.computed = self.computed
        shadow.signature = self.signature
        #methods
        shadow.clear = self.clear
        shadow.is_cacheable = self.is_cacheable
        shadow.checkInputPort = self.checkInputPort
        shadow.setResult = self.setResult
        shadow.get_output = self.get_output
        shadow.getInputConnector = self.getInputConnector
        shadow.getInputFromPort = self.getInputFromPort
        shadow.hasInputFromPort = self.hasInputFromPort
        shadow.annotate = self.annotate
        shadow.forceGetInputFromPort = self.forceGetInputFromPort
        shadow.set_input_port = self.set_input_port
        shadow.getInputListFromPort = self.getInputListFromPort
        shadow.forceGetInputListFromPort = self.forceGetInputListFromPort
        shadow.enableOutputPort = self.enableOutputPort
        shadow.removeInputConnector = self.removeInputConnector
        shadow.create_instance_of_type = self.create_instance_of_type
        
        #shadow.updateUpstreamPort(self, port): pass
        #shadow.updateUpstream(self): pass
        #shadow.update(self): pass
        #shadow.compute(self): pass
        #shadow.__str__ = self.__str__
        #shadow.provide_input_port_documentation(cls, port_name): pass
        #shadow.provide_output_port_documentation(cls, port_name): pass            
        
        #Call the Shadow Objects Compute
        shadow.compute()

        if isSubProc:
            conn.proc.terminate()
            conn.proc.wait()
        conn.close()


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

#This lib goes accross as part of the setup
import Shared

#Node must have rpyc installed so not a problem        
import rpyc
from rpyc import Connection, Channel, SocketStream, SlaveService

#node has dummy versions of these so not a problem
from core.modules.vistrails_module import Module, NotCacheable

class RPyCModule(NotCacheable, Module):
    '''
    This module is important as it forms the basis for ensuring that
    rpyc based modules have the correct input ports
    '''
    #TODO: Check if this can be made part of the mixin
    pass


class RPyCSafeModule(object):
    """
    RPyCSafeModule is a Module that executes the compute method on a RPyC node.
    This annotaion mixes in the code needed to ensure both threadsafe execution
    and rpyc safe execution
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
        
        if RPyCSafeMixin not in clazz.__bases__:
            new__bases__ = (RPyCSafeMixin,) + clazz.__bases__
            clazz.compute = RPyCSafeMixin.compute
        
        return type(clazz.__name__, new__bases__, clazz.__dict__.copy())


class RPyCSafeMixin(object):
    """
    This is a dummy module used to provide the devloper with dummy versions 
    of each of the methods that Module would normally supply. 
    An instance of a RPyC module created in vistrails will have the proper 
    vistrails module mixed in by the annotation. On a RPyC node 
    the dummy verion is used to instantiate a shadow of the origional 
    module. The shadows methods are linked back to the origional module.
    """
    
    def compute(self):
        #Get RPyC Node in good standing
        #input from rpycmodule
        self.conn = self.forceGetInputFromPort('rpycsession', None)
        
        #if we don't get a good node then we need to create a subprocess
        self.isSubProc = False
        if self.conn == None:
            self.isSubProc = True
            self.conn = rpyc.classic.connect_subproc()

        #redirect StdIO back here so we can see what is going on        
        rpyc.classic.redirected_stdio(self.conn)
        
        #Make sure all the right stuff is in place espcially dummy core and packages
        import packages.eo4vistrails.rpyc.dummycore
        rpyc.classic.upload_package(self.conn, packages.eo4vistrails.rpyc.dummycore, "./tmp/core")

        import packages.eo4vistrails.rpyc.dummypackages
        rpyc.classic.upload_package(self.conn, packages.eo4vistrails.rpyc.dummypackages, "./tmp/packages")

        #Upload any vsitrails packages that may be required
        for packageName in self.__requiredVisPackages:
            print packageName
            package = __import__(packageName, fromlist=['packages'])
            print package
            rpyc.classic.upload_package(self.conn, package, "./tmp/"+packageName.replace(".","/"))

        #make sure all packages are in the path
        if not "./tmp" in self.conn.modules.sys.path:
            self.conn.modules.sys.path.append('./tmp')

        #Make sure it knows its a remote node
        self.conn.execute('import packages.eo4vistrails.rpyc.Shared as Shared')
        self.conn.execute('Shared.isRemoteRPyCNode=True')

        #Reload the current module
        #import inspect
        #rpyc.classic.update_module(conn, inspect.getmodule(self))
        rmodule = self.conn.modules[self.__module__]
        self.conn.modules.__builtin__.reload(rmodule)
        
        #Instantiate Shadow Object
        self.conn.execute('from '+self.__module__+' import '+self.__class__.__name__)
        shadow = self.conn.eval(self.__class__.__name__+'()')
        
        #Hook Up Shadow Objects Methods and Attributes        
        #attributes
        for attribute in Module.__dict__:
            if not str(attribute) in ('compute', '__dict__', '__module__', '__doc__', '__str__', '__weakref__'):
                shadow.__setattr__(str(attribute), self.__getattribute__(str(attribute)))
        
        #Call the Shadow Objects Compute
        shadow.compute()
        
    def __del__(self):
        try:
            if self.isSubProc:
                self.conn.proc.terminate()
                self.conn.proc.wait()
                self.conn.close()
        except:
            pass

#        shadow.logging = self.logging
#        shadow.inputPorts = self.inputPorts
#        shadow.outputPorts = self.outputPorts
#        shadow.upToDate = self.upToDate
#        shadow.is_method = self.is_method
#        shadow._latest_method_order = self._latest_method_order
#        shadow.moduleInfo = self.moduleInfo
#        shadow.is_breakpoint = self.is_breakpoint
#        shadow.is_fold_operator = self.is_fold_operator
#        shadow.is_fold_module = self.is_fold_module
#        shadow.computed = self.computed
#        shadow.signature = self.signature
#methods
#        shadow.clear = self.clear
#        shadow.is_cacheable = self.is_cacheable
#        shadow.checkInputPort = self.checkInputPort
#        shadow.setResult = self.setResult
#        shadow.get_output = self.get_output
#        shadow.getInputConnector = self.getInputConnector
#        shadow.getInputFromPort = self.getInputFromPort
#        shadow.hasInputFromPort = self.hasInputFromPort
#        shadow.annotate = self.annotate
#        shadow.forceGetInputFromPort = self.forceGetInputFromPort
#        shadow.set_input_port = self.set_input_port
#        shadow.getInputListFromPort = self.getInputListFromPort
#        shadow.forceGetInputListFromPort = self.forceGetInputListFromPort
#        shadow.enableOutputPort = self.enableOutputPort
#        shadow.removeInputConnector = self.removeInputConnector
#        shadow.create_instance_of_type = self.create_instance_of_type
#TODO: should I be allowing this or am i missing something?
#        shadow.updateUpstreamPort = self.updateUpstreamPort
#        shadow.updateUpstream = self.updateUpstream
#        shadow.update = self.update
#shadow.compute(self): pass
#shadow.__str__ = self.__str__
#shadow.provide_input_port_documentation(cls, port_name): pass
#shadow.provide_output_port_documentation(cls, port_name): pass            
    
        
class RPyCSession(Connection, NotCacheable, Module):
    '''
    The Session Module is used to ensure that a single connection to a rpyc
    node can be used accross multiple workflow modules
    '''

    def compute(self):
        rpycnode = self.getInputFromPort('rpycnode')
        Connection.__init__(self, SlaveService, 
                            Channel(SocketStream.connect(rpycnode.get_ip, rpycnode.get_port)), {})
        #self.__connection = rpyc.classic.connect(self.__ip, self.__port)
        self.setResult("value", self)
        
    #def __del__(self):
    #    try:
            #self.__connection.close()
    #    except:
    #        pass
        
class RPyCNode(NotCacheable, Module):
    '''
    The rpyc node is a data structure used to pass around the deatils of
    a rpyc node
    '''
    
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        self.__ip = self.forceGetInputFromPort('ip', '127.0.0.1')
        self.__port = self.forceGetInputFromPort('port', 18812)
        self.setResult("value", self)
            
    def get_ip(self):
        return self.__ip
    
    def set_ip(self, ip):
        self.__ip = ip
    
    def get_port(self):
        return self.__port
    
    def set_port(self, port):
        self.__port = port
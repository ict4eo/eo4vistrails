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
        self.conn = None
        rpycsession = self.forceGetInputFromPort('rpycsession', None)
        if rpycsession:
            self.conn = rpycsession._connection
        
        #if we don't get a good node then we need to create a subprocess
        self.isSubProc = False
        if self.conn == None:
            
            self.isSubProc = True
            self.conn = rpyc.classic.connect_subproc()
            #make sure all packages are in the path
            import core.system
            self.conn.modules.sys.path.append(core.system.vistrails_root_directory())
            
        else:
            #Make sure all the right stuff is in place espcially dummy core and packages
            #on the remote node, no need for this if local as the machine is already set up            
            import packages.eo4vistrails.rpyc.dummycore
            rpyc.classic.upload_package(self.conn, packages.eo4vistrails.rpyc.dummycore, "./tmp/core")
    
            import packages.eo4vistrails.rpyc.dummypackages
            rpyc.classic.upload_package(self.conn, packages.eo4vistrails.rpyc.dummypackages, "./tmp/packages")
    
            #Upload any vsitrails packages that may be required
            for packageName in self._requiredVisPackages:
                package = __import__(packageName, fromlist=['packages'])
                rpyc.classic.upload_package(self.conn, package, "./tmp/"+packageName.replace(".","/"))
    
            #make sure all packages are in the path
            if not "./tmp" in self.conn.modules.sys.path:
                self.conn.modules.sys.path.append('./tmp')

            #Reload the current module
            #import inspect
            #rpyc.classic.update_module(conn, inspect.getmodule(self))
            rmodule = self.conn.modules[self.__module__]
            self.conn.modules.__builtin__.reload(rmodule)
            
        #redirect StdIO back here so we can see what is going on        
        rpyc.classic.redirected_stdio(self.conn)
    
        #Make sure it knows its a remote node
        self.conn.execute('import packages.eo4vistrails.rpyc.Shared as Shared')
        self.conn.execute('Shared.isRemoteRPyCNode=True')
        
        #Instantiate Shadow Object
        print self.__module__, self.__class__.__name__
        self.conn.execute('from '+self.__module__+' import '+self.__class__.__name__)
        shadow = self.conn.eval(self.__class__.__name__+'()')
        
        #Hook Up Shadow Objects Methods and Attributes
        #attributes
        for attribute in Module.__dict__:
            if not str(attribute) in ('compute', '__dict__', '__module__', '__doc__', '__str__', '__weakref__', '__init__'):
                shadow.__setattr__(str(attribute), self.__getattribute__(str(attribute)))
        
        #Call the Shadow Objects Compute
        shadow.compute()
        
        if self.isSubProc:
            self.conn.proc.terminate()
            self.conn.proc.wait()
            self.conn.close()
        
class RPyCNode(Connection, NotCacheable, Module):
    '''
    The rpyc node is a data structure used to pass around the deatils of
    a rpyc node
    '''
    def __init__(self):
        Module.__init__(self)

    def __del__(self):
        print 'cleaning up connections'
        self._connection.proc.terminate()
        self._connection.proc.wait()
        self._connection.close()

    def compute(self):
        self._ip = self.forceGetInputFromPort('ip', '127.0.0.1')
        self._port = self.forceGetInputFromPort('port', 18812)
        #Connection.__init__(self, SlaveService, Channel(SocketStream.connect(rpycnode.get_ip(), rpycnode.get_port())), {})
        self._connection = rpyc.classic.connect(self._ip, self._port)
        self.setResult("value", self)
            
    def get_ip(self):
        return self._ip
    
    def set_ip(self, ip):
        self._ip = ip
    
    def get_port(self):
        return self._port
    
    def set_port(self, port):
        self._port = port
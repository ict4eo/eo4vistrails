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

#node has dummy versions of these so not a problem
from core.modules.vistrails_module import Module, NotCacheable

class RPyCModule(Module):
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
            new__dict__ = clazz.__dict__.copy()
            new__dict__['_original_compute']  = new__dict__['compute']
            del(new__dict__['compute']) # = RPyCSafeMixin.compute

        return type(clazz.__name__, new__bases__, new__dict__)


class RPyCSafeMixin(object):
    """
    This is a dummy module used to provide the devloper with dummy versions 
    of each of the methods that Module would normally supply. 
    An instance of a RPyC module created in vistrails will have the proper 
    vistrails module mixed in by the annotation. On a RPyC node 
    the dummy verion is used to instantiate a shadow of the origional 
    module. The shadows methods are linked back to the origional module.
    """

    def getConnection(self):
        if self.hasInputFromPort('rpycnode'):
            v = self.getInputFromPort('rpycnode')
            print v
             
            if str(v[0]) == 'None' or str(v[0]) == '':
                connection = None
                
            elif str(v[0]) == 'main':
                connection = None
                
            elif str(v[0]) == 'own':
                connection = rpyc.classic.connect_subproc()
                #self.isSubProc = True
                #connection = rpyc.classic.connect_subproc()
                #make sure all packages are in the path
                print "Got a subProc"
                import core.system
                import sys       
                connection.modules.sys.path.append(sys.path)
                connection.modules.sys.path.append(core.system.vistrails_root_directory())
                
            else:
                connection = rpyc.classic.connect(v[0], v[1])

                print "Got a Remote Node"
                #Make sure all the right stuff is in place espcially dummy core and packages
                #on the remote node, no need for this if local as the machine is already set up            
                import packages.eo4vistrails.rpyc.dummycore
                rpyc.classic.upload_package(connection, packages.eo4vistrails.rpyc.dummycore, "./tmp/core")
        
                import packages.eo4vistrails.rpyc.dummypackages
                rpyc.classic.upload_package(connection, packages.eo4vistrails.rpyc.dummypackages, "./tmp/packages")
        
                #Upload any vsitrails packages that may be required
                for packageName in self._requiredVisPackages:
                    package = __import__(packageName, fromlist=['packages'])
                    rpyc.classic.upload_package(connection, package, "./tmp/"+packageName.replace(".","/"))
        
                #make sure all packages are in the path
                if not "./tmp" in connection.modules.sys.path:
                    connection.modules.sys.path.append('./tmp')
    
                #Reload the current module
                #import inspect
                #rpyc.classic.update_module(connection, inspect.getmodule(self))
                rmodule = connection.modules[self.__module__]
                connection.modules.__builtin__.reload(rmodule)
                
        else:
            connection = None

        return connection

    
    def compute(self):
        #Get RPyC Node in good standing
        #input from rpycmodule
        
        conn = self.getConnection()
        
        if not conn:
            #run as per normal
            self._original_compute()
        else:
            #redirect StdIO back here so we can see what is going on    
            import sys
            conn.modules.sys.stdout = sys.stdout
        
            #Make sure it knows its a remote node
            conn.execute('import packages.eo4vistrails.rpyc.Shared as Shared')
            conn.execute('Shared.isRemoteRPyCNode=True')
            
            #Instantiate Shadow Object
            print self.__module__, self.__class__.__name__
            conn.execute('from '+self.__module__+' import '+self.__class__.__name__)
            shadow = conn.eval(self.__class__.__name__+'()')
            
            #Hook Up Shadow Objects Methods and Attributes
            #attributes
            for attribute in Module.__dict__:
                if not str(attribute) in ('compute', '__dict__', '__module__', '__doc__', '__str__', '__weakref__', '__init__'):
                    shadow.__setattr__(str(attribute), self.__getattribute__(str(attribute)))
            
            #Call the Shadow Objects Compute
            shadow.compute()
            
            #conn.proc.terminate()
            #conn.proc.wait()
            #conn.close()


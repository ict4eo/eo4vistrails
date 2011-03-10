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

This Module holds some helper classes to make working with rpyc easier
It also has the rpyc remote code that is used 

"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

from core import packagemanager
from core.modules.module_registry import get_module_registry
from core.modules import basic_modules
from core.modules.vistrails_module import Module, NotCacheable, ModuleError

from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeModule
from RPyC import RPyCModule, RPyCNode, RPyCSafeModule

@ThreadSafeModule()
class RPyCDiscover(NotCacheable, Module):
    """
    RPyCDiscover is a Module that allow one to discover RPyC
    servers
    """
    # This constructor is strictly unnecessary. However, some modules
    # might want to initialize per-object data. When implementing your
    # own constructor, remember that it must not take any extra
    # parameters.
    def __init__(self):
        Module.__init__(self)
        
    def getSlaves(self):
        import rpyc
        discoveredSlavesTuple = list(rpyc.discover("slave"))
        discoveredSlaves = []
        for slave in discoveredSlavesTuple:
            rpycnode = RPyCNode()
            rpycnode.set_ip( slave[0] )
            rpycnode.set_port( slave[1] )
            discoveredSlaves.append(rpycnode)
        return discoveredSlaves

    def compute(self):
        """Vistrails Module Compute, Entry Point Refer, to Vistrails Docs"""
        self.setResult("rpycslaves", self.getSlaves())

@ThreadSafeModule()
class RPyCCode(RPyCModule):
    """
    RPyC is a Module that executes an arbitrary piece of Python code remotely.
    """
    #TODO: If you want a PythonSource execution to fail, call fail(error_message).
    #TODO: If you want a PythonSource execution to be cached, call cache_this().
    
      
    '''
    This constructor is strictly unnecessary. However, some modules
    might want to initialize per-object data. When implementing your
    own constructor, remember that it must not take any extra
    parameters.
    '''
    def __init__(self):
        RPyCModule.__init__(self)

    def run_code(self, code_str, use_input=False, use_output=False):
        """
        run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution.
        """
        import rpyc

        def fail(msg):
            raise ModuleError(self, msg)

        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True
        
        #input from rpycmodule
        self.conn = self.forceGetInputFromPort('rpycsession', None)
                
        #if we don't get a good node then we need to create a subprocess
        self.isSubProc = False
        if self.conn == None:
            print 'executing in single mode'
            self.isSubProc = True
            self.conn = rpyc.classic.connect_subproc()

        #TODO: changed to demo that this is in the cloud!!!!
        #rpyc.classic.redirected_stdio(self.conn)
        
        if use_input:
            inputDict = dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])
            self.conn.namespace.update(inputDict)
        
        if use_output:
            outputDict = dict([(k, self.get_output(k)) for k in self.outputPorts])
            self.conn.namespace.update(outputDict)

        _m = packagemanager.get_package_manager()
        reg = get_module_registry()
        self.conn.namespace.update({'fail': fail,
                        'package_manager': _m,
                        'cache_this': cache_this,
                        'registry': reg,
                        'self': self})
        del self.conn.namespace['source']
        
        print code_str
        self.conn.execute(code_str)
        
        if use_output:
            for k in outputDict.iterkeys():
                if self.conn.namespace[k] != None:
                    self.setResult(k, self.conn.namespace[k])

        if self.isSubProc:
            self.conn.proc.terminate()
            self.conn.proc.wait()
            self.conn.close()

    def compute(self):
        """
        Vistrails Module Compute, Entry Point Refer, to Vistrails Docs
        """
        s = basic_modules.urllib.unquote(
            str(self.forceGetInputFromPort('source', ''))
            )
        self.run_code(s, use_input=True, use_output=True)
        

@RPyCSafeModule()
@ThreadSafeModule()
class RPyCTestModule(Module):
    """This Test Module is to check that ThreadSafe is working and also provides
    a template for others to use ThreadSafe"""
    
    def compute(self):
        from time import ctime, sleep
        import os
        print self.__class__.__bases__
        print "Hello ", self.getInputFromPort("input")
        print self.getInputConnector("input")
        print ctime()," ", os.getpid(), " Started RPyCSafe Module, Waiting 2 Seconds"
        sleep(2)
        print ctime()," ", os.getpid(), " Stoped RPyCSafe Module"


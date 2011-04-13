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

from core.modules.vistrails_module import ModuleError, NotCacheable
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from RPyC import RPyCModule, getSubConnection, getRemoteConnection
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget
from core.modules import basic_modules
import rpyc

class RPyCCode(ThreadSafeMixin, RPyCModule):
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
        ThreadSafeMixin.__init__(self)
        RPyCModule.__init__(self)
    
    def clear(self):
        print "clear"
        RPyCModule.clear(self)
        if self.conn:
            try:
                self.conn.proc.terminate()
                self.conn.proc.wait()
            except:
                pass
            self.conn.close()
               
    def getConnection(self):
        if self.hasInputFromPort('rpycnode'):
            v = self.getInputFromPort('rpycnode')
            print v
             
            if str(v[0]) == 'None' or str(v[0]) == '':
                connection = getSubConnection()
            elif str(v[0]) == 'main':
                connection = getSubConnection()
            elif str(v[0]) == 'own':
                connection = getSubConnection()
            else:
                connection = getRemoteConnection(v[0], v[1])
        else:
            connection = getSubConnection()
        
        return connection

    def run_code(self, code_str, conn, use_input=False, use_output=False):
        """
        run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution.
        """
        if code_str == '':
            return
        
        def fail(msg):
            raise ModuleError(self, msg)

        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True    

        #TODO: changed to demo that this is in the cloud!!!!
        import sys
        conn.modules.sys.stdout = sys.stdout        
        
        if use_input:
            inputDict = dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])
            conn.namespace.update(inputDict)
        
        if use_output:
            outputDict = dict([(k, self.get_output(k)) for k in self.outputPorts])
            conn.namespace.update(outputDict)
        
        from core import packagemanager
        _m = packagemanager.get_package_manager()
        from core.modules.module_registry import get_module_registry
        reg = get_module_registry()
        conn.namespace.update({'fail': fail,
                               'package_manager': _m,
                               'cache_this': cache_this,
                               'registry': reg,
                               'self': self})
               
        del conn.namespace['source']
        
        conn.execute(code_str)
        
        if use_output:
            for k in outputDict.iterkeys():
                try:
                    if conn.namespace[k] != None:
                        self.setResult(k, conn.namespace[k])
                except AttributeError:
                    self.setResult(k, conn.namespace[k])
    
    def compute(self):
        """
        Vistrails Module Compute, Entry Point Refer, to Vistrails Docs
        """
        self.conn = self.getConnection()
        
        from core.modules import basic_modules
        s = basic_modules.urllib.unquote(
            str(self.forceGetInputFromPort('source', ''))
            )
        self.run_code(s, self.conn, use_input=True, use_output=True)


class RPyCNodeWidget(ComboBoxWidget):
    discoveredSlaves = None
    default = ('main',0)
    
    def getKeyValues(self):
        if not self.discoveredSlaves:
            self.discoveredSlaves = {'Own Process':('own',0), 'Main Process':('main',0)}
            try:
                discoveredSlavesTuple = list(rpyc.discover("slave"))
                for slaveTuple in discoveredSlavesTuple:
                    self.discoveredSlaves[slaveTuple[0]] = slaveTuple
            except rpyc.utils.factory.DiscoveryError:
                pass
        return self.discoveredSlaves
           
#Add ComboBox
RPyCNode = basic_modules.new_constant('RpyCNode',
                                       staticmethod(eval),
                                       ('main',0),
                                       staticmethod(lambda x: type(x) == tuple),
                                       RPyCNodeWidget)


###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## This full package extends VisTrails, providing GIS/Earth Observation 
## ingestion, pre-processing, transformation, analytic and visualisation 
## capabilities . Included is the abilty to run code transparently in 
## OpenNebula cloud environments. There are various software 
## dependencies, but all are FOSS.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""TODO:
"""

import copy
from threading import Thread, currentThread
from multiprocessing import RLock #need to check if i actually need this
from core.modules.vistrails_module import Module, NotCacheable, \
        InvalidOutput, ModuleError, ModuleErrors, ModuleBreakpoint

global globalThreadLock
globalThreadLock = RLock()

class ThreadSafeness(object):
    def __init__(self, clazz):
        self.clazz = clazz
        if ThreadSafeMixin not in self.clazz.__bases__:
            self.clazz.__base__ = (ThreadSafeMixin,) + self.clazz.__base__
    
    def __call__(self, *args):  
        return self.clazz(*args)

class ThreadSafe(object):
    """TODO. """
    def __init__(self):
        Module.__init__(self)
        self.computeLock = RLock()
    
    def globalThread(self, module):            
        global globalThreadLock
        globalThreadLock.acquire()
        module.update()
        globalThreadLock.release()
            
    def updateUpstream(self):
        """ TODO. """
        threadList = []
        threadSafeList = []        
        normalList= []        
        foundFirstModule = False

        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                if not foundFirstModule:
                    foundFirstModule = True
                    firstModule = connector.obj
                elif isinstance(connector.obj, ThreadSafe):
                    thread = Thread(target=connector.obj.lockedUpdate)
                    thread.start()
                    threadList.append(thread)
                else:
                    thread = Thread(target=self.globalThread, args=(connector.obj,))
                    thread.start()
                    threadList.append(thread)

        if foundFirstModule:
            if isinstance(firstModule, ThreadSafe):
                firstModule.lockedUpdate()
            else:
                self.globalThread(firstModule)

        for thread in threadList:
            thread.join()

        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

    def update(self):
        """ update() -> None        
        Check if the module is up-to-date then update the
        modules. Report to the logger if available
        
        """     
        try:
             global globalThreadLock
             globalThreadLock.release()
             self.lockedUpdate()
             globalThreadLock.acquire()
        except AssertionError, ae:
            self.lockedUpdate()
            pass
    
    def lockedUpdate(self):
        with self.computeLock:
            self.logging.begin_update(self)
            self.updateUpstream()
            if self.upToDate:
                if not self.computed:
                    self.logging.update_cached(self)
                    self.computed = True
                return
            self.logging.begin_compute(self)
            try:
                if self.is_breakpoint:
                    raise ModuleBreakpoint(self)
                self.compute()
                self.computed = True
            except ModuleError, me:
                if hasattr(me.module, 'interpreter'):
                    raise
                else:
                    msg = "A dynamic module raised an exception: '%s'"
                    msg %= str(me)
                    raise ModuleError(self, msg)
            except ModuleErrors:
                raise
            except KeyboardInterrupt, e:
                raise ModuleError(self, 'Interrupted by user')
            except ModuleBreakpoint:
                raise
            except Exception, e: 
                import traceback
                traceback.print_exc()
                raise ModuleError(self, 'Uncaught exception: "%s"' % str(e))
            self.upToDate = True
            self.logging.end_update(self)
            self.logging.signalSuccess(self)
            
class ThreadSafeMixin(object):
    """TODO. """
    def initLocks(self):
        self.computeLock = RLock()
    
    def globalThread(self, module):            
        global globalThreadLock
        globalThreadLock.acquire()
        module.update()
        globalThreadLock.release()
            
    def updateUpstream(self):
        """ TODO. """
        threadList = []
        threadSafeList = []        
        normalList= []        
        foundFirstModule = False

        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                if not foundFirstModule:
                    foundFirstModule = True
                    firstModule = connector.obj
                elif isinstance(connector.obj, ThreadSafe):
                    thread = Thread(target=connector.obj.lockedUpdate)
                    thread.start()
                    threadList.append(thread)
                else:
                    thread = Thread(target=self.globalThread, args=(connector.obj,))
                    thread.start()
                    threadList.append(thread)

        if foundFirstModule:
            if isinstance(firstModule, ThreadSafe):
                firstModule.lockedUpdate()
            else:
                self.globalThread(firstModule)

        for thread in threadList:
            thread.join()

        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

    def update(self):
        """ update() -> None        
        Check if the module is up-to-date then update the
        modules. Report to the logger if available
        
        """     
        try:
             global globalThreadLock
             globalThreadLock.release()
             self.lockedUpdate()
             globalThreadLock.acquire()
        except AssertionError, ae:
            self.lockedUpdate()
            pass
    
    def lockedUpdate(self):
        with self.computeLock:
            self.logging.begin_update(self)
            self.updateUpstream()
            if self.upToDate:
                if not self.computed:
                    self.logging.update_cached(self)
                    self.computed = True
                return
            self.logging.begin_compute(self)
            try:
                if self.is_breakpoint:
                    raise ModuleBreakpoint(self)
                self.compute()
                self.computed = True
            except ModuleError, me:
                if hasattr(me.module, 'interpreter'):
                    raise
                else:
                    msg = "A dynamic module raised an exception: '%s'"
                    msg %= str(me)
                    raise ModuleError(self, msg)
            except ModuleErrors:
                raise
            except KeyboardInterrupt, e:
                raise ModuleError(self, 'Interrupted by user')
            except ModuleBreakpoint:
                raise
            except Exception, e: 
                import traceback
                traceback.print_exc()
                raise ModuleError(self, 'Uncaught exception: "%s"' % str(e))
            self.upToDate = True
            self.logging.end_update(self)
            self.logging.signalSuccess(self)

class Fork(NotCacheable, ThreadSafe, Module):
    """TODO:"""
    pass

from time import *
class ThreadTestModule(NotCacheable, ThreadSafe, Module):
    """This Test Module is to check that ThreadSafe is working and also provides
    a template for others to use ThreadSafe"""
    def compute(self):
         print ctime()," ", currentThread().name, " Started ThreadSafe Module, Waiting 2 Seconds"
         sleep(2)
         print ctime()," ", currentThread().name, " Stoped ThreadSafe Module"


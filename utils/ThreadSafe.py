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
from threading import *
from core.modules.vistrails_module import Module, NotCacheable, \
        InvalidOutput, ModuleError, ModuleErrors, ModuleBreakpoint

global globalThreadLock
globalThreadLock = RLock()

class ThreadSafe(Module, Thread):
    """TODO. """
    def __init__(self):
        Module.__init__(self)
        Thread.__init__(self)
        self.computeLock = RLock()

    def updateUpstream(self):
        """ TODO. """
        print currentThread().name, " updateUpstream", " for ", self.name
        threadList = []
        threadSafeList = []        
        normalList= []        
        
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                if isinstance(connector.obj, ThreadSafe):
                    threadSafeList.append(connector.obj)
                else:
                    normalList.append(connector.obj)

        if len(threadSafeList) > 0:
            for module in threadSafeList[1:]:
                try:
                    module.start()
                    threadList.append(module)
                except RuntimeError, re:
                    module.lockedUpdate()
            
            firstModule = threadSafeList[0]
            if len(normalList) > 0:
                try:
                    firstModule.start()
                    threadList.append(firstModule)
                except RuntimeError, re:
                    firstModule.lockedUpdate()
            else:
                firstModule.lockedUpdate()

        for module in normalList:
            global globalThreadLock      
            print currentThread().name, " blocked on global Lock", " for ", self.name
            globalThreadLock.acquire()
            print currentThread().name, " acquire global Lock", " for ", self.name
            module.update()
            globalThreadLock.release()
            print currentThread().name, " release global Lock", " for ", self.name

        for thread in threadList:
            print currentThread().name, " waiting for ", thread.name, " to join"
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
        print currentThread().name, " update", " for ", self.name
        
        try:
             global globalThreadLock             
             globalThreadLock.release()
             print currentThread().name, " release global Lock", " for ", self.name
             self.lockedUpdate()
             print currentThread().name, " blocked on global Lock", " for ", self.name
             globalThreadLock.acquire()
             print currentThread().name, " acquire global Lock", " for ", self.name
        except RuntimeError, re:
            self.lockedUpdate()
            pass
    
    def lockedUpdate(self):
        print currentThread().name, " lockedUpdate", " for ", self.name
        
        print currentThread().name, " blocked on compute Lock", " for ", self.name
        with self.computeLock:
            print currentThread().name, " acquire compute Lock", " for ", self.name
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
        print currentThread().name, " release compute Lock", " for ", self.name
        
    def run(self):
        print currentThread().name, " run", " for ", self.name
        self.lockedUpdate()
        

class Fork(ThreadSafe, NotCacheable):
    """TODO:"""
    pass

from time import *
class ThreadTestModule(ThreadSafe, NotCacheable):
    """This Test Module is to check that ThreadSafe is working and also provides
    a template for others to use ThreadSafe"""
    def compute(self):
         print ctime()," ", currentThread().name, " Started ThreadSafe Module, Waiting 2 Seconds"
         sleep(2)
         print ctime()," ", currentThread().name, " Stoped ThreadSafe Module"


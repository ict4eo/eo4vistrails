
#################################################################################
## 

import copy
from threading import Lock, RLock
from threading import Thread
from core.modules.vistrails_module import Module, NotCacheable, InvalidOutput

globalThreadLock = Lock()

class ThreadSafe(Module, Thread):
    """TODO. """
    def __init__(self):
        Module.__init__(self)
        Thread.__init__(self)
        self.threadLock = RLock()   
        self.hasRun = False

    def updateUpstream(self):
        """ TODO. """
        threadList = []
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList[]:                
                if isinstance(connector.obj, ThreadSafe):     
                    with connector.obj.threadLock:
                        if connector.obj.hasRun:
                            connector.obj.update()
                        else:
                            connector.obj.hasRun = True
                            threadList.append(connector.obj)
                            connector.obj.start()

        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:                
                if not isinstance(connector.obj, ThreadSafe):
                    global globalThreadLock
                    with globalThreadLock:
                        connector.obj.update()

        for obj in threadList:              
            obj.join()
            obj.reset()

        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

    def update(self):
        """ update() -> None        
        Check if the module is up-to-date then update the
        modules. Report to the logger if available
        
        """
        with self.threadLock:
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

        
    def reset(self):        
        Thread.__init__(self)
        self.hasRun = False
        
    def run(self):        
        self.update()

class Fork(ThreadSafe, NotCacheable):
    pass

from time import *
class ThreadTestModule(ThreadSafe, NotCacheable):
     def compute(self):
         print ctime()," ", self.name, " Started ThreadSafe Module, Waiting 2 Seconds"
         sleep(2)
         print ctime()," ", self.name, " Stoped ThreadSafe Module"



#################################################################################
## 

import copy
from threading import Lock
from threading import Thread
from core.modules.vistrails_module import Module, NotCacheable, InvalidOutput

globalThreadLock = Lock()

class ThreadSafe(Module, Thread):
    """TODO. """
    def __init__(self):
        Module.__init__(self)
        Thread.__init__(self)
        self.threadLock = Lock()

    def updateUpstream(self):
        """ TODO. """
        global globalThreadLock
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                if isinstance(connector.obj, ThreadSafe):
                    with connector.obj.threadLock:
                        connector.obj.update()
                else:
                    with globalThreadLock:
                        connector.obj.update()
                        
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)
    
    def reset(self):
        Thread.__init__(self)
        
    def run(self):
        self.update()        

class Fork(Module, NotCacheable):
    def updateUpstream(self):
        
        """ TODO. """
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:                
                if isinstance(connector.obj, ThreadSafe):
                    with connector.obj.threadLock:
                        connector.obj.start()

        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:                
                if not isinstance(connector.obj, ThreadSafe):
                    global globalThreadLock
                    with globalThreadLock:
                        connector.obj.update()

        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:              
                if isinstance(connector.obj, ThreadSafe):
                    connector.obj.join()
                    connector.obj.reset()

        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

from time import *
class ThreadTestModule(ThreadSafe, NotCacheable):
     def compute(self):
         print ctime()," ", self.name, " Started ThreadSafe Module, Waiting 2 Seconds"
         sleep(2)
         print ctime()," ", self.name, " Stoped ThreadSafe Module"


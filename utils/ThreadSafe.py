from core.modules.vistrails_module import Module, ModuleError, ModuleErrors, \
    ModuleConnector, InvalidOutput

#################################################################################
## 

from time import *
from threading import Lock

class ThreadSafe(Module):
    """TODO. """
    def __init__(self):
        Module.__init__(self)
        self.threadLock = Lock()

    def updateUpstream(self):
        """ TODO. """
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                if type(connector.obj) == ThreadSafe:
                    with connector.obj:
                        connector.obj.update()
                else:
                    with threadLock:
                        connector.obj.update()
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

class Fork(Module):
    def compute(self):
       pass                


class ThreadTestModule(ThreadSafe):
     def compute(self):
         print localtime()," Started ThreadSafe Module, Waiting 2 Seconds"
         wait(2)
         print localtime()," Stoped ThreadSafe Module"


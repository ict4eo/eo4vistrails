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

from ThreadSafe import ThreadSafe
from multiprocessing import Process, Value, Manager
from multiprocessing.managers import BaseManager
from threading import *
from core.modules.vistrails_module import Module, NotCacheable, \
        InvalidOutput, ModuleError, ModuleErrors, ModuleBreakpoint

class MultiProcessSafe(ThreadSafe):
    """TODO:"""
    def __init__(self):
        ThreadSafe.__init__(self)
        self.manager = Manager()
        
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
                
                #Do Compute in a Parrallel Process
                inputPorts = self.manager.dict(self.inputPorts)
                outputPorts = self.manager.dict()           
                p = Process(target=self.shadowCompute, args=(inputPorts, outputPorts))
                p.start()
                p.join()
                self.inputPorts = dict(inputPorts)
                for key, value in outputPorts.items():
                    self.outputPorts[key] = value                    
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

    def shadowCompute(self, inputPorts, outputPorts):
        self.inputPorts = inputPorts
        self.compute()
        for key, value in self.outputPorts.items():
            if not isinstance(value, ThreadSafe):
                outputPorts[key] = value

from time import *
from multiprocessing import current_process
class MultiProcessTestModule(MultiProcessSafe, NotCacheable):
    """This Test Module is to check that MultiProcess is working and also provides
    a template for others to use MultiProcess"""
    def compute(self):
         print ctime()," ", current_process(), " Started Process Module, Waiting 2 Seconds"
         sleep(2)
         print ctime()," ", current_process(), " Stoped Process Module"
         self.setResult("someString", "someString")
         
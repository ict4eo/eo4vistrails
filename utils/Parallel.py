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
from core.modules.vistrails_module import *

class MultiProcessSafe(ThreadSafe):
    """TODO:"""
    def __init__(self):
        ThreadSafe.__init__(self)
        self.manager = Manager()
   
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
                
                #Do Compute in a Parrallel Process
                inputPorts = self.manager.dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])
                #outputPorts = self.manager.dict([(k, self.get_output(k)) for k in self.outputPorts])
                
                outputPorts = self.manager.dict([(k, None) for k in self.outputPorts])                
                
                
                p = Process(target=self.shadowCompute, args=(inputPorts, outputPorts))
                p.start()
                p.join()
                p.terminate()
                
                
                #for key, value in outputPorts.items():
                #    self.outputPorts[key] = value
                
                self.computed = True
                
            except ModuleError, me:
                p.terminate()
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

    def shadowCompute(self, inputPorts, outputPorts):
        #for key, value in outputPorts.items():
        #    self.set_input_port(key,value)
        self.inputPorts = inputPorts
        self.outputPorts = outputPorts
        self.compute()
        #for key, value in self.outputPorts.items():
        #    try:
        #        outputPorts[key] = value
        #    except:
        #        pass

class MultiProcessCompute():
    '''this is the class that holds the compute module for any multi process 
    safe code. Any code that is to run in a multi process should start from 
    the compute module of this class. Note that some additional helper methods 
    have been added so that this class is a shadow to vistrails module but a 
    pickle-able version. '''
    
    def Compute(self):
        pass

from time import *
from multiprocessing import current_process
from math import sqrt
class MultiProcessTestModule(NotCacheable, MultiProcessSafe, Module):
    """This Test Module is to check that MultiProcess is working and also provides
    a template for others to use MultiProcess"""
    def compute(self):
         print ctime()," ", current_process(), " Started Process Module, Waiting 2 Seconds"
         #sleep(2)
         for i in xrange(10000):
             #waste some time
             for j in xrange(10000):
                 sqrt(i*j)
         print ctime()," ", current_process(), " Stoped Process Module"
         print self.getInputFromPort("someStringAboveMe")
         self.setResult("someString", "someString")


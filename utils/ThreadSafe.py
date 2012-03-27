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
"""This module is used to add threading ability to VisTrails.

This is the core module holding annotations and mixins,
"""
debug = True

# global
import copy
import sys
from threading import Thread, currentThread, Lock, ThreadError, RLock, Event
from Queue import Queue, LifoQueue, Empty
from packages.controlflow.fold import *

from core.modules.sub_module import Group
from core.log.group_exec import GroupExec
from core.log.loop_exec import LoopExec
from core.log.module_exec import ModuleExec

# vistrails
from core.modules.vistrails_module import Module, NotCacheable, \
        InvalidOutput, ModuleError, ModuleBreakpoint, ModuleErrors

from core.interpreter.default import get_default_interpreter


global globalThreadLock
globalThreadLock = RLock()

class ThreadSafeMixin(object):
    """TODO Write docstring."""    
    
    moduleLock = None
    interpreter = get_default_interpreter()
    
    def __init__(self):
        self.computeLock = Lock()
        self.exceptionQ = Queue()        

    def globalThread(self, connector_obj, method, parent_execs):
        """Called by this method to ensure a global threadlock over all non
        threadsafe modules is maintained. This ensures only one of thme will
        execute at a time."""
        global globalThreadLock
        try:
            with globalThreadLock:
                if debug: print self.__class__.__name__, id(self), currentThread().name, "globalThread() With globalThreadLock for %s %s %s"%(connector_obj.__class__.__name__, id(connector_obj), method.__name__)
                if parent_execs:
                    ThreadSafeMixin.interpreter.parent_execs = parent_execs[:]
                method()
        except ModuleError:
            self.exceptionQ.put(sys.exc_info())
            if debug: print self.__class__.__name__, id(self), currentThread().name, "globalThread() exception globalThreadLock for %s %s %s"%(connector_obj.__class__.__name__, id(connector_obj), method.__name__)
            raise
    
    def updateUpstream(self, functionPort=False, parent_execs=None):
        """Alternate verions of Module UpdateUpstream that executes each upstream 
        module in its own thread."""
        threadList = []
        for port_name, connectorList in self.inputPorts.iteritems():
            for connector in connectorList:
                if isinstance(connector.obj, ThreadSafeMixin):
                    if functionPort and port_name == 'FunctionPort':
                        target = connector.obj.updateUpstream
                        args = (False, parent_execs)
                    else:
                        target = connector.obj.update
                        args = (parent_execs,)
                else:
                    target = self.globalThread
                    if functionPort and port_name == 'FunctionPort':
                        args = (connector.obj, connector.obj.updateUpstream, parent_execs)
                    else:
                        args = (connector.obj, connector.obj.update, parent_execs)
                
                thread = Thread(target=target, args=args)
                thread.start()
                threadList.append(thread)
        
        stillWaiting = True
        while stillWaiting:
            stillWaiting = False                        
            for thread in threadList:
                thread.join(0.1)
                if thread.isAlive():
                    stillWaiting = True
            if stillWaiting:
                self.logging.begin_update(self)
            
        if self.exceptionQ.qsize() > 0:
            exec_info = self.exceptionQ.get()
            raise exec_info[0], exec_info[1], exec_info[2]
        
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            if functionPort and iport != 'FunctionPort':
                for connector in connectorList:
                    if connector.obj.get_output(connector.port) is InvalidOutput:
                        self.removeInputConnector(iport, connector)

    def update(self, parent_execs=None):
        """ update() -> None        
        Check if the module is up-to-date then update the
        modules. Report to the logger if available        
        """        
        global globalThreadLock
        #TODO: hadle the case of a non threadsafe fold module
        has_global_thread_lock = globalThreadLock._is_owned()
        
        if has_global_thread_lock:
            assert(parent_execs is None)
        
        lock = self.computeLock if self.__class__.moduleLock is None else self.__class__.moduleLock
        try:
            tmp_exec = None
            if has_global_thread_lock:
                tmp_exec = ThreadSafeMixin.interpreter.parent_execs[:]
                globalThreadLock.release()
                if debug: print self.__class__.__name__, id(self), currentThread().name, "update() release globalThreadLock"
            with lock:
                if debug: print self.__class__.__name__, id(self), currentThread().name, "update() with compute/module-Lock"
                with globalThreadLock:
                    if debug: print self.__class__.__name__, id(self), currentThread().name, "update() with globalThreadLock"
                    # All wrapped up for thread safety                    
                    if tmp_exec:
                        ThreadSafeMixin.interpreter.parent_execs = tmp_exec[:]
                    elif parent_execs:                        
                        ThreadSafeMixin.interpreter.parent_execs = parent_execs[:]
                    
                    self.logging.begin_update(self)
                    self.unLockedGlobalUpstream()

                    if self.upToDate:
                        if not self.computed:
                            self.logging.update_cached(self)
                            self.computed = True
                        return
                    
                    self.logging.begin_compute(self)
                    
                    try:
                        if self.is_breakpoint:
                            raise ModuleBreakpoint(self)
                        self.unLockedGlobalCompute()
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

        except ModuleError:
            self.exceptionQ.put(sys.exc_info())
            if debug: print self.__class__.__name__, id(self), currentThread().name, "update() Exception"
            raise
        finally:
            if has_global_thread_lock:
                globalThreadLock.acquire()
                ThreadSafeMixin.interpreter.parent_execs = tmp_exec[:]
                if debug: print self.__class__.__name__, id(self), currentThread().name, "update() Get globalThreadLock"

    def unLockedGlobalUpstream(self):
        """ update() -> None
        Check if the module is up-to-date then update the
        modules. Report to the logger if available.
        """
        global globalThreadLock
        assert(globalThreadLock._is_owned() == True)
        try:
            upstream_parent_execs = ThreadSafeMixin.interpreter.parent_execs[:]
            parent_execs = ThreadSafeMixin.interpreter.parent_execs[:]            
            if debug: print self.__class__.__name__, id(self), currentThread().name, "updateUpstream() Release globalThreadLock"
            globalThreadLock.release()
            self.updateUpstream(parent_execs=upstream_parent_execs)
        except:
            if debug: print self.__class__.__name__, id(self), currentThread().name, "updateUpstream() Exception"
            raise
        finally:
            globalThreadLock.acquire()
            ThreadSafeMixin.interpreter.parent_execs = parent_execs
            if debug: print self.__class__.__name__, id(self), currentThread().name, "updateUpstream() Get globalThreadLock"

    def unLockedGlobalCompute(self):
        """ update() -> None
        Check if the module is up-to-date then update the
        modules. Report to the logger if available.
        """
        global globalThreadLock
        assert(globalThreadLock._is_owned() == True)
        try:
            self.compute_parent_execs = ThreadSafeMixin.interpreter.parent_execs[:]
            if debug: print self.__class__.__name__, id(self), currentThread().name, "unLockedGlobalCompute", self.compute_parent_execs
            parent_execs = ThreadSafeMixin.interpreter.parent_execs[:]
            if debug: print self.__class__.__name__, id(self), currentThread().name, "compute() Release globalThreadLock"
            globalThreadLock.release()
            self.compute()
        except:
            if debug: print self.__class__.__name__, id(self), currentThread().name, "compute() Exception"
            raise
        finally:
            globalThreadLock.acquire()
            ThreadSafeMixin.interpreter.parent_execs = parent_execs
            if debug: print self.__class__.__name__, id(self), currentThread().name, "compute() Get globalThreadLock"

class Fork(ThreadSafeMixin, NotCacheable, Module):
    """TODO Write docstring."""

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def test(self):
        print "this is a test"

class ThreadSafeFold(ThreadSafeMixin, Fold):
    
    def __init__(self):
        Fold.__init__(self)
        ThreadSafeMixin.__init__(self)
        self.compute_parent_execs = None

    def updateUpstream(self, parent_execs=None):        
        ThreadSafeMixin.updateUpstream(self, True, parent_execs=parent_execs)
    
    def updateFunctionPort(self):
        """
        Function to be used inside the updateUsptream method of the Fold module. It
        updates the modules connected to the FunctionPort port.
        """
        nameInput = self.getInputFromPort('InputPort')
        nameOutput = self.getInputFromPort('OutputPort')
        rawInputList = self.getInputFromPort('InputList')

        # create inputList to always have iterable elements
        # to simplify code
        if len(nameInput) == 1:
            element_is_iter = False
        else:
            element_is_iter = True
        inputList = []
        for element in rawInputList:
            if not element_is_iter:
                inputList.append([element])
            else:
                inputList.append(element)

        ## Update everything for each value inside the list
        for i in xrange(len(inputList)): 
            element = inputList[i]
            if element_is_iter:
                self.element = element
            else:
                self.element = element[0]
            for connector in self.inputPorts.get('FunctionPort'):
                if not self.upToDate:
                    ##Type checking
                    if i==0:
                        self.typeChecking(connector.obj, nameInput, inputList)
                    
                    connector.obj.upToDate = False
                    connector.obj.already_computed = False
                    
                    ## Setting information for logging stuff
                    connector.obj.is_fold_operator = True
                    connector.obj.first_iteration = False
                    connector.obj.last_iteration = False
                    connector.obj.fold_iteration = i
                    if i==0:
                        connector.obj.first_iteration = True
                    if i==((len(inputList))-1):
                        connector.obj.last_iteration = True

                    self.setInputValues(connector.obj, nameInput, element)
                if isinstance(connector.obj, ThreadSafeMixin):
                    connector.obj.update(self.compute_parent_execs)
                else:
                    # we block all other fold operations that are not ThreadSafe Modules
                    global globalThreadLock
                    with globalThreadLock:
                        try:
                            if debug: print self.__class__.__name__, id(self), currentThread().name, "updateFunctionPort", self.compute_parent_execs
                            ThreadSafeMixin.interpreter.parent_execs = self.compute_parent_execs[:]
                            connector.obj.update()
                        except:
                            if debug: print self.__class__.__name__, id(self), currentThread().name, "exception!!!!!!!", ThreadSafeMixin.interpreter.parent_execs
                            if isinstance(connector.obj, Group):
                                if debug: print self.__class__.__name__, id(self), currentThread().name, "exception!!!!!!!", id(connector.obj)
                            raise
                
                ## Getting the result from the output port
                if nameOutput not in connector.obj.outputPorts:
                    raise ModuleError(connector.obj,\
                                      'Invalid output port: %s'%nameOutput)
                self.elementResult = connector.obj.get_output(nameOutput)
            self.operation()

class ThreadSafeMap(ThreadSafeFold):
    """A Map module, that just appends the results in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""
        
        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        self.partialResult.append(self.elementResult)
            
class ThreadTestModule(ThreadSafeMixin,  Module): #NotCacheable,
    """This Test Module is to check that ThreadSafe is working and also
    provides a template for others to use ThreadSafe"""
        
    _input_ports = [('value', '(edu.utah.sci.vistrails.basic:Integer)')]
    
    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        value = self.forceGetInputFromPort('value', 0)
        from time import ctime, sleep
        print ctime(), " ", currentThread().name, \
            " Started ThreadSafe Module, Waiting 2 Seconds", value
        sleep(2)
        print ctime(), " ", currentThread().name, \
            " Stopped ThreadSafe Module", value
        

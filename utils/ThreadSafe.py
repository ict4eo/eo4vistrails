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
    threadSafeFoldLock = RLock()
    
    def __init__(self):
        self.computeLock = Lock()
        self.exceptionQ = Queue()
        self.update_called = False
        self.upstream_called_first = False

    def globalThread(self, connector_obj, method):
        """Called by this method to ensure a global threadlock over all non
        threadsafe modules is maintained. This ensures only one of thme will
        execute at a time."""
        global globalThreadLock
        try:
            with globalThreadLock:
                if debug: print self.__class__.__name__, id(self), currentThread().name, "globalThread() With globalThreadLock for %s %s %s"%(connector_obj.__class__.__name__, id(connector_obj), method.__name__)
                method()
        except ModuleError:
            self.exceptionQ.put(sys.exc_info())
            if debug: print self.__class__.__name__, id(self), currentThread().name, "globalThread() exception globalThreadLock for %s %s %s"%(connector_obj.__class__.__name__, id(connector_obj), method.__name__)
            raise
    
    def updateUpstream(self, functionPort=False):
        """Alternate verions of Module UpdateUpstream that executes each upstream 
        module in its own thread."""
        if not self.upstream_called_first and not self.update_called:
            #This will only be true if the previous module never called our update
            #must be a fold operation of sorts or some special control operation need to proceed with caution                
            self.upstream_called_first = True
        global globalThreadLock
        has_global_thread_lock = globalThreadLock._is_owned()
        try:
            if has_global_thread_lock:
                globalThreadLock.release()
                if debug: print self.__class__.__name__, id(self), currentThread().name, "updateUpstream() Release globalThreadLock"
            
            threadList = []            
            for port_name, connectorList in self.inputPorts.iteritems():
                for connector in connectorList:
                    if isinstance(connector.obj, ThreadSafeMixin):
                        if functionPort and port_name == 'FunctionPort':
                            target = connector.obj.updateUpstream
                        else:
                            target = connector.obj.update
                        args = ()                    
                    else:
                        if functionPort and port_name == 'FunctionPort':
                            target = self.globalThread
                            args = (connector.obj, connector.obj.updateUpstream)
                        else:
                            target = self.globalThread
                            args = (connector.obj, connector.obj.update)

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
        finally:
            if has_global_thread_lock:            
                globalThreadLock.acquire()
                if debug: print self.__class__.__name__, id(self), currentThread().name, "updateUpstream() Get globalThreadLock"

    def update(self, parent_exec=None):
        """ update() -> None        
        Check if the module is up-to-date then update the
        modules. Report to the logger if available        
        """        
        global globalThreadLock        
        #TODO: hadle the case of a non threadsafe fold module
        self.update_called = True
        has_global_thread_lock = globalThreadLock._is_owned()
        if self.__class__.moduleLock:
            lock = self.__class__.moduleLock
            #if debug: print self, id(self), currentThread().name, "lock is of type module"
        else:
            lock = self.computeLock
            #if debug: print self, id(self), currentThread().name, "lock is of type compute"
        try:
            if has_global_thread_lock:
                globalThreadLock.release()
                if debug: print self.__class__.__name__, id(self), currentThread().name, "update() release globalThreadLock"
            with lock:
                if debug: print self.__class__.__name__, id(self), currentThread().name, "update() with compute/module-Lock"
                with globalThreadLock:
                    if debug: print self.__class__.__name__, id(self), currentThread().name, "update() with globalThreadLock"                    
                    self.logging.begin_update(self)
                    self.unLockedGlobalMethod(self.updateUpstream)
                    if self.upToDate:
                        if not self.computed:
                            self.logging.update_cached(self)
                            self.computed = True
                        return

                    if parent_exec:
                        ThreadSafeMixin.interpreter.parent_execs.append(parent_exec)
                    # All wrapped up for thread safety
                    with ThreadSafeMixin.threadSafeFoldLock:
                        self.logging.begin_compute(self)

                        if self.is_fold_module:
                            ThreadSafeMixin.interpreter.parent_execs.pop()
                        if self.is_fold_operator:
                            loop_exec = ThreadSafeMixin.interpreter.parent_execs.pop()
                        if parent_exec:
                            ThreadSafeMixin.interpreter.parent_execs.pop()
                        
                    try:
                        if self.is_breakpoint:
                            raise ModuleBreakpoint(self)
                        self.unLockedGlobalMethod(self.compute)
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
                    #These methods have been deffered so that they will execute in order
                    with ThreadSafeMixin.threadSafeFoldLock:
                        if self.is_fold_operator:
                            ThreadSafeMixin.interpreter.parent_execs.append(loop_exec)
                        if self.is_fold_module:
                            ThreadSafeMixin.interpreter.parent_execs.append(self.module_exec)
    
                        self.logging.end_update(self)
                        self.logging.signalSuccess(self)
        except ModuleError:
            self.exceptionQ.put(sys.exc_info())
            raise
        finally:
            if has_global_thread_lock:
                globalThreadLock.acquire()
                if debug: print self.__class__.__name__, id(self), currentThread().name, "update() Get globalThreadLock"

    def unLockedGlobalMethod(self, method):
        """ update() -> None
        Check if the module is up-to-date then update the
        modules. Report to the logger if available.
        """
        global globalThreadLock
        has_global_thread_lock = globalThreadLock._is_owned()
        try:
            if has_global_thread_lock:
                globalThreadLock.release()
                if debug: print self.__class__.__name__, id(self), currentThread().name, "%s() Release globalThreadLock"%method.__name__
            method()
        finally:
            if has_global_thread_lock:
                globalThreadLock.acquire()
                if debug: print self.__class__.__name__, id(self), currentThread().name, "%s() Get globalThreadLock"%method.__name__

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

    def updateUpstream(self):
        #with ThreadSafeMixin.threadSafeFoldLock:
        ThreadSafeMixin.updateUpstream(self, True)
    
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
                    connector.obj.update(self.module_exec)
                else:
                    # we block all other fold operations that are not ThreadSafe 
                    # Modules
                    global globalThreadLock
                    with globalThreadLock:
                        with ThreadSafeMixin.threadSafeFoldLock:
                            if debug: print self.__class__.__name__, id(self), currentThread().name, ThreadSafeMixin.interpreter.parent_execs, "pre append"
                            ThreadSafeMixin.interpreter.parent_execs.append(self.module_exec)
                            if debug: print self.__class__.__name__, id(self), currentThread().name, ThreadSafeMixin.interpreter.parent_execs, "post append"
                            connector.obj.update()
                            if debug: print self.__class__.__name__, id(self), currentThread().name, ThreadSafeMixin.interpreter.parent_execs, "pre pop"
                            ThreadSafeMixin.interpreter.parent_execs.pop()
                            if debug: print self.__class__.__name__, id(self), currentThread().name, ThreadSafeMixin.interpreter.parent_execs, "post pop"
                
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
            
class ThreadTestModule(ThreadSafeMixin, NotCacheable, Module):
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
        

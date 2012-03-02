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
debug = False

# global
import copy
import sys
from threading import Thread, currentThread, RLock
from Queue import Queue

# vistrails
from core.modules.vistrails_module import Module, NotCacheable, \
        InvalidOutput, ModuleError

global globalThreadLock
globalThreadLock = RLock()

class ThreadSafeMixin(object):
    """TODO Write docstring."""
    
    def __init__(self):
        self.computeLock = RLock()

    def globalThread(self, module, exceptionQ=None):
        """TODO Write docstring."""
        global globalThreadLock
        globalThreadLock.acquire()
        try:
            module.update()
            globalThreadLock.release()
        except ModuleError:
            globalThreadLock.release()
            if exceptionQ is not None:
                exceptionQ.put(sys.exc_info())
            raise
    
    def updateUpstream(self):
        if debug: print self, "Called Me"
        """TODO Write docstring."""
        threadList = []
        exceptionQ = Queue()
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                if isinstance(connector.obj, ThreadSafeMixin):
                    thread = Thread(target=connector.obj.lockedUpdate, kwargs={"exceptionQ":exceptionQ})
                    thread.start()
                    threadList.append(thread)
                else:
                    thread = Thread(target=self.globalThread, args=(connector.obj,), kwargs={"exceptionQ":exceptionQ})
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
            
        if exceptionQ.qsize() > 0:
            exec_info = exceptionQ.get()
            raise exec_info[0], exec_info[1], exec_info[2]
        
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

    def update(self):
        """ update() -> None
        Check if the module is up-to-date then update the
        modules. Report to the logger if available.
        """
        global globalThreadLock        
        try:
            globalThreadLock.release()
            self.lockedUpdate()
            globalThreadLock.acquire()
        except RuntimeError:
            self.lockedUpdate()
        except ModuleError:
            globalThreadLock.acquire()
            raise

    def lockedUpdate(self, exceptionQ=None):
        """TODO Write docstring."""
        if debug: print self, "get compute lock"
        with self.computeLock:
            try:
                Module.update(self)
            except ModuleError:
                if exceptionQ is not None:
                    exceptionQ.put(sys.exc_info())
                raise
        if debug: print self, "release compute lock"

class Fork(ThreadSafeMixin, NotCacheable, Module):
    """TODO Write docstring."""

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def test(self):
        print "this is a test"

class ThreadTestModule(ThreadSafeMixin, NotCacheable, Module):
    """This Test Module is to check that ThreadSafe is working and also
    provides a template for others to use ThreadSafe"""

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        from time import ctime, sleep
        print ctime(), " ", currentThread().name, \
            " Started ThreadSafe Module, Waiting 2 Seconds"
        sleep(2)
        print ctime(), " ", currentThread().name, \
            " Stopped ThreadSafe Module"

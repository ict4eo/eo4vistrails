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
# global
import copy
from threading import Thread, currentThread, RLock
from Queue import Queue

# vistrails
from core.modules.vistrails_module import Module, NotCacheable, \
        InvalidOutput, ModuleError, ModuleErrors, ModuleBreakpoint

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
        except ModuleError, me:
            globalThreadLock.release()
            if exceptionQ is not None:
                exceptionQ.put(me)
            raise me
    
    def updateUpstream(self):
        print self, "Called Me"
        """TODO Write docstring."""
        #ae = None
        threadList = []
        exceptionQ = Queue()
        #foundFirstModule = False
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                #if not foundFirstModule:
                #    foundFirstModule = True
                #    firstModule = connector.obj
                #el
                if isinstance(connector.obj, ThreadSafeMixin):
                    thread = Thread(target=connector.obj.lockedUpdate, kwargs={"exceptionQ":exceptionQ})
                    thread.start()
                    threadList.append(thread)
                else:
                    thread = Thread(target=self.globalThread, args=(connector.obj,), kwargs={"exceptionQ":exceptionQ})
                    thread.start()
                    threadList.append(thread)
        
#        try:
#            if foundFirstModule:
#                if isinstance(firstModule, ThreadSafeMixin):
#                    firstModule.lockedUpdate()
#                else:
#                    self.globalThread(firstModule)
#        except ModuleError, me:
#            ae = me
        stillWaiting = True
        while stillWaiting:
            stillWaiting = False                        
            for thread in threadList:
                thread.join(0.1)
                if thread.isAlive():
                    stillWaiting = True
            if stillWaiting:
                self.logging.begin_update(self)
            
        #if ae is not None:
        #    raise ae
        #el
        if exceptionQ.qsize() > 0:
            raise exceptionQ.get()
        
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
        except RuntimeError, re:
            self.lockedUpdate()
        except ModuleError, me:
            globalThreadLock.acquire()
            raise me

    def lockedUpdate(self, exceptionQ=None):
        """TODO Write docstring."""
        print self, "get compute lock"
        with self.computeLock:
            try:
                Module.update(self)
            except ModuleError, me:
                if exceptionQ is not None:
                    exceptionQ.put(me)
                raise me
        print self, "release compute lock"

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

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 14:19:42 2011

@author: tvzyl
"""
from RPyC import RPyCSafeModule
from core.modules.vistrails_module import Module
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin

@RPyCSafeModule()
class RPyCTestModule(ThreadSafeMixin, Module):
    """This Test Module is to check that ThreadSafe is working and also provides
    a template for others to use ThreadSafe"""
    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)
    
    def compute(self):
        from time import ctime, sleep
        import os
        print self.__class__.__bases__
        print "Hello ", self.forceGetInputFromPort("input","None")
        #rint self.getInputConnector("input")
        print ctime()," ", os.getpid(), " Started RPyCSafe Module, Waiting 1 Seconds"
        sleep(1)
        print ctime()," ", os.getpid(), " Stoped RPyCSafe Module"

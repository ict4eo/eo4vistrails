# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 14:42:53 2010

@author: tvzyl
"""

from core.modules.vistrails_module import NotCacheable, Module
from multiprocessing import current_process
from time import ctime, sleep
from RPyC import RPyCSafeModule

@RPyCSafeModule([])
class RPyCTestModule(NotCacheable, Module):
    """This Test Module is to check that ThreadSafe is working and also provides
    a template for others to use ThreadSafe"""
    
    def compute(self):
        print self.__class__.__bases__
        print "Hello ", self.getInputFromPort("input")
        print self.getInputConnector("input")
        print ctime()," ", current_process(), " Started RPyCSafe Module, Waiting 2 Seconds"
        sleep(2)
        print ctime()," ", current_process(), " Stoped RPyCSafe Module"


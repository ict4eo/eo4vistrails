# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 09:38:10 2010

@author: tvzyl
"""

from core.modules.vistrails_module import Module

class RPyCNodeModule(object):
    pass

class RPyCNode(Module, RPyCNodeModule):
    """ Container class for the numpy.ndarray class """
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        self.ip = self.forceGetInputFromPort('ip')
        self.port = self.forceGetInputFromPort('port', 18812)
        self.setResult("value", self)
        
    def get_ip(self):
        return self.ip
    
    def set_ip(self, ip):
        self.ip = ip
    
    def get_port(self):
        return self.port
    
    def set_port(self, port):
        self.port = port
    
class RPyCModule(Module):
    pass
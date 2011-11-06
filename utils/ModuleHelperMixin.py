# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 15:15:50 2011

@author: tvzyl
"""

class ModuleHelperMixin(object):
    
    def getPortType(self, portName, portType="output"):
        for i in self.moduleInfo['pipeline'].module_list:
            if i.id == self.moduleInfo['moduleId']:
                for j in i.port_specs:
                    if i.port_specs[j].type == portType and i.port_specs[j].name == portName:
                        return i.port_specs[j].signature[0][0]

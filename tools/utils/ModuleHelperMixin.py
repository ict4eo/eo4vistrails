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
                        if str(type(i.port_specs[j].signature[0][0])) == "<netref class '__builtin__.type'>":
                            str_type = str(i.port_specs[j].signature[0][0])
                            str_type = str_type.split("'")[1]
                            if str_type != 'core.modules.vistrails_module.Module':
                                str_type = str_type.replace('vistrails_module', 'basic_modules')
                            exec('import %s'%str_type.rsplit('.',1)[0])
                            return eval(str_type)
                        else:
                            return i.port_specs[j].signature[0][0]

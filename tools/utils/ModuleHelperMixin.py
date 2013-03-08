# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
###
### This full package extends VisTrails, providing GIS/Earth Observation
### ingestion, pre-processing, transformation, analytic and visualisation
### capabilities. Included is the abilty to run code transparently in
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
"""This module forms part ofEO4VisTrails capabilities - it is used to provide
a mixin for a VisTrails Module.
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
                            exec('import %s' % str_type.rsplit('.', 1)[0])
                            return eval(str_type)
                        else:
                            return i.port_specs[j].signature[0][0]

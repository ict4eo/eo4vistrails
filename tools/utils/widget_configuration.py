###########################################################################
##
## Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the ability to run code transparently in
## OpenNebula cloud environments. There are various software
## dependencies, but all are FOSS.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""This module provides extensions to the standard VisTrails
ModuleConfigurationWidget.
"""

# vistrails
from gui.modules.module_configure import StandardModuleConfigurationWidget


class ExtendedModuleConfigurationWidget(StandardModuleConfigurationWidget):

    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)

    def getPortValue(self, portName):
        """Return string value assigned to specified port"""
        for function in self.module.functions:
            #print "widget-config 43", "port",portName,"fn",function.name
            if str(portName) == str(function.name):
                #print "widget-config 45", function.params[0].strValue
                return function.params[0].strValue
        return None

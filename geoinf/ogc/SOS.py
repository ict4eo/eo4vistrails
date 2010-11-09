###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation 
## ingestion, pre-processing, transformation, analytic and visualisation 
## capabilities . Included is the abilty to run code transparently in 
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
"""This module provides an OGC Sensor Observation Service Client via owslib.
"""

#from owslib.wfs import WFS
from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError


#need to import the configuration widget we develop
class SOS(FeatureModel):
    """TO DO - add docstring"""
    def __init__(self):
        FeatureModel.__init__(self)

    def compute(self):
        pass


class SosCommonWidget(QtGui.QWidget):
    """TO DO - add docstring"""
    def __init__(self,  module, parent=None):
        '''parses modules attributes to fetch parameters'''
        QtGui.QWidget.__init__(self, parent)
        self.launchtype = str(module).split(" ")[1].split(":")[1][0:3].lower()
        #self.module = module
        self.setObjectName("SosCommonWidget")
        self.create_config_window()

    def create_config_window(self):
        """TO DO - add docstring"""
        self.setWindowTitle("SOS Configuration Widget")
        self.setMinimumSize(800, 300) 
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)


class SOSConfigurationWidget(OgcConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""
    def __init__(self,  module, controller, parent=None):
        OgcConfigurationWidget.__init__(self,  module, controller, parent)
        
        self.sos_common_widget = SosCommonWidget(module)
        
        self.tabs.addTab(self.sos_common_widget, "")
        self.tabs.setTabText(
            self.tabs.indexOf(self.sos_common_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "SOS Specific Metadata",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.sos_common_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "Stuff for SOS",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
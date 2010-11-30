# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FeatureImport.ui'
#
# Created: Tue Nov 30 10:30:09 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!
###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
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
"""This module provides a Feature file Import
"""

#from owslib.wfs import WFS
import core.modules.module_registry
import core.system
from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from packages.eo4vistrails.geoinf.ogc.OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
#from geoinf.datamodels.Raster import RasterModel


#need to import the configuration widget we develop
class FeatureImport(FeatureModel):
    """TO DO - add docstring

    """
    def __init__(self):
        FeatureModel.__init__(self)

    def compute(self):
        pass


class FeatureImportCommonWidget(QtGui.QWidget):
    """TO DO - add docstring

    """
    def __init__(self, ogc_widget, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("FeatureImportCommonWidget")
        self.parent_widget = ogc_widget
        self.contents = None #  only set in self.loadOfferings()
        self.create_config_window()
        # listen for signals emitted by OgcCommonWidget class
        """self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceActivated'),
            self.loadOfferings
        )
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceDeactivated'),
            self.removeOfferings
        )"""

    def create_config_window(self):
        """Create datacontainers and layout for displaying Feature data."""
        self.setWindowTitle("FeatureImport Configuration Widget")
        self.setMinimumSize(900, 675)
        # main layout
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.placesGroupBox = QtGui.QGroupBox("Places")
        self.placesLayout = QtGui.QVBoxLayout()
        self.placesGroupBox.setLayout(self.placesLayout)
        self.mainLayout.addWidget(self.placesGroupBox)
        self.split = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.mainLayout.addWidget(self.split)
        self.detailsGroupBox = QtGui.QGroupBox("Places Details")
        self.mainLayout.addWidget(self.detailsGroupBox)
        self.detailsLayout = QtGui.QGridLayout()
        self.detailsGroupBox.setLayout(self.detailsLayout)
        # places
        self.lbxPlaces = QtGui.QListWidget()
        self.placesLayout.addWidget(self.lbxPlaces)
        self.btnPlaces = QtGui.QPushButton("Add");
        self.placesLayout.addWidget(self.btnPlaces)
        # places details layout
        #   labels
        #   data containers
        self.lbxDetails = QtGui.QListWidget()
        self.detailsLayout.addWidget(self.lbxDetails)
        self.cbxPlaces = QtGui.QComboBox();
        self.detailsLayout.addWidget(self.cbxPlaces)

        self.buttonGroupBox = QtGui.QGroupBox("")
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonGroupBox.setLayout(self.buttonLayout)
        self.detailsLayout.addWidget(self.buttonGroupBox)
        self.btnCancel = QtGui.QPushButton("Cancel");
        self.btnOpen = QtGui.QPushButton("Open");
        self.buttonLayout.addWidget(self.btnCancel)
        self.buttonLayout.addWidget(self.btnOpen)



        # local signals
        '''self.connect(
            self.lbxOfferings,
            QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),
            self.offeringsChanged'''
            #)
            
def initialize(*args, **keywords):
    """sets everything up"""
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(FeatureImport)
    #input ports
    
    #reg.add_input_port(FeatureModel, "service_version", (core.modules.basic_modules.String, 'Web Map Service version - default 1.1.1'))   
    #output ports
    reg.add_output_port(
        FeatureImport,
        "OGRDataset",
        (ogr.Dataset, 'Feature data in OGR Dataset')
    )


class FeatureImportConfigurationWidget(OgcConfigurationWidget):

    """makes use of code style from OgcConfigurationWidget"""
    def __init__(self,  module, controller, parent=None):
        OgcConfigurationWidget.__init__(self,  module, controller, parent)
        # pass in parent widget i.e. OgcCommonWidget class
        self.wfs_config = FeatureImportCommonWidget(self.ogc_common_widget)
        # tabs
        self.tabs.insertTab(1, self.wfs_config, "")
        self.tabs.setTabText(
            self.tabs.indexOf(self.wfs_config),
            QtGui.QApplication.translate(
                "cConfigurationWidget",
                "FeatureImportCommonWidget",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.wfs_config),
            QtGui.QApplication.translate(
               
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setCurrentIndex(0)

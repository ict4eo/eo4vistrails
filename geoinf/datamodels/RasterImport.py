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
"""This module provides a Raster file Import
"""

# library
import os
import sys
# third party
import fnmatch
from numpy import *
from osgeo import ogr, gdal, osr
from PyQt4 import QtCore, QtGui
from scipy import *
# core
import core.modules.module_registry
import core.system
# eo4vistrails
from packages.eo4vistrails.geoinf.datamodels.Raster import RasterModel
from packages.eo4vistrails.geoinf.ogc.OgcConfigurationWidget import \
    OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, \
    ModuleError


#need to import the configuration widget we develop
class RasterImport(RasterModel):
    """TO DO - add docstring

    """

    def __init__(self):
        RasterModel.__init__(self)

    def compute(self):
        pass


class RasterImportCommonWidget(QtGui.QWidget):
    """TO DO - add docstring

    """

    def __init__(self, ogc_widget, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("RasterImportCommonWidget")
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
        """Create datacontainers and layout for displaying Raster data."""
        self.setWindowTitle("RasterImport Configuration Widget")
        self.setMinimumSize(900, 675)
        # main layout
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.placesGroupBoxButton = QtGui.QPushButton("Load Raster File")
        self.placesGroupBox = QtGui.QLineEdit("Select Rasterfile")
        self.placesLayout = QtGui.QHBoxLayout()
        self.placesGroupBox.setLayout(self.placesLayout)
        self.mainLayout.addWidget(self.placesGroupBoxButton)
        self.mainLayout.addWidget(self.placesGroupBox)

        #self.split = QtGui.QSplitter(QtCore.Qt.Vertical)
        #self.mainLayout.addWidget(self.split)
        self.detailsGroupBox = QtGui.QGroupBox("Rasterfile Metadata")
        self.mainLayout.addWidget(self.detailsGroupBox)
        self.detailsLayout = QtGui.QGridLayout()
        self.detailsGroupBox.setLayout(self.detailsLayout)
        # places
        #self.lbxPlaces = QtGui.QListWidget()
        #self.placesLayout.addWidget(self.lbxPlaces)
        #self.btnPlaces = QtGui.QPushButton("Add");
        #self.placesLayout.addWidget(self.btnPlaces)
        # places details layout
        #   labels
        #   data containers
        self.lbxDetails = QtGui.QListWidget()
        self.detailsLayout.addWidget(self.lbxDetails)
        #self.cbxPlaces = QtGui.QComboBox();
        #self.detailsLayout.addWidget(self.cbxPlaces)

        self.buttonGroupBox = QtGui.QGroupBox("")
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonGroupBox.setLayout(self.buttonLayout)
        self.detailsLayout.addWidget(self.buttonGroupBox)
        self.btnCancel = QtGui.QPushButton("Cancel")
        self.btnExecute = QtGui.QPushButton("Execute")
        self.buttonLayout.addWidget(self.btnCancel)
        self.buttonLayout.addWidget(self.btnExecute)

        self.connect(self.placesGroupBoxButton,
                     QtCore.SIGNAL('clicked(bool)'), self.showDialog)

        self.connect(self.btnExecute, QtCore.SIGNAL('clicked(bool)'),
                     self.getRasterFileMetaData)

    def showDialog(self):
        """TO DO - add docstring"""
        filename = QtGui.QFileDialog.getOpenFileName(
            self, 'Open file', '/home')
        self.placesGroupBox.setText(str(filename))
        fname = open(filename)
        data = fname.read()
        self.lbxDetails.addItem(str(data))

    def getRasterFileMetaData(self):
        """TO DO - add docstring"""
        rstfile = self.placesGroupBox.text()
        metadata = os.popen('gdalinfo ' + str(rstfile)).read()
        self.lbxDetails.addItem(str(metadata))


def initialize(*args, **keywords):
    """sets everything up"""
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(RasterModel)
    """
    #input ports
    #reg.add_input_port(
        RasterModel,
        "service_version",
        (core.modules.basic_modules.String,
        'Web Map Service version - default 1.1.1'))
    """
    #output ports
    reg.add_output_port(
        RasterModel,
        "OGRDataset",
        (ogr.Dataset, 'Raster data in OGR Dataset'))


class RasterImportConfigurationWidget(OgcConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""

    def __init__(self, module, controller, parent=None):
        OgcConfigurationWidget.__init__(self, module, controller, parent)
        # pass in parent widget i.e. OgcCommonWidget class
        self.wfs_config = RasterImportCommonWidget(self.ogc_common_widget)
        # tabs
        self.tabs.insertTab(1, self.wfs_config, "")
        self.tabs.setTabText(
            self.tabs.indexOf(self.wfs_config),
            QtGui.QApplication.translate(
                "cConfigurationWidget",
                "RasterImportCommonWidget",
                None,
                QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.wfs_config),
            QtGui.QApplication.translate('mmmmm', 'nnnn',
                None,
                QtGui.QApplication.UnicodeUTF8))
        self.tabs.setCurrentIndex(0)

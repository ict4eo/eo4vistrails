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
"""This module provides an OGC Web Feature Service Client via owslib.
"""

#from owslib.wfs import WFS
from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError

#from owslib.wfs import WebFeatureService


#need to import the configuration widget we develop

class WFS(NotCacheable,  FeatureModel):
    """TO DO - add docstring

    """
    def __init__(self):
        FeatureModel.__init__(self)

    def compute(self):
        pass

class WFSCommonWidget(QtGui.QWidget):
    """TO DO - add docstring

    """
    def __init__(self, ogc_widget, parent=None):
        """sets parameters for wfs request"""
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("WFSConfigurationWidget")
        self.parent_widget = ogc_widget
        self.service = self.parent_widget.service

        self.create_wfs_config_window()
        # listener for signal emitted by OgcCommonWidget class
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceActivated'),
            self.loadRequest
        )

    def create_wfs_config_window(self):
        """TO DO - add docstring"""
        gridLayout = QtGui.QGridLayout()
        self.setLayout(gridLayout)
        #gridLayout.addWidget(QtGui.QLabel('wfs Url'), 0, 0)
        gridLayout.addWidget(QtGui.QLabel('Available Operations'), 1, 0)
        gridLayout.addWidget(QtGui.QLabel('TypeNames'), 2, 0)
        gridLayout.addWidget(QtGui.QLabel('bbox:'), 3, 0)
        gridLayout.addWidget(QtGui.QLabel('                             min  x'), 3, 1)
        gridLayout.addWidget(QtGui.QLabel('                     min  y'), 3, 3)
        gridLayout.addWidget(QtGui.QLabel('                             max  x'), 4, 1)
        gridLayout.addWidget(QtGui.QLabel('                     max y'), 4, 3)
        gridLayout.addWidget(QtGui.QLabel('ESPG/SRS Code'), 5, 0)
        gridLayout.addWidget(QtGui.QLabel('maxFeatures'), 6, 0)
        #gridLayout.addWidget(QtGui.QLabel('GetFeature'), 7, 0)
        #self.wfsUrlEdit = QtGui.QLineEdit('http://localhost:8080/geoserver/wfs')

        self.minXEdit = QtGui.QLineEdit('0.0')
        self.ESPGEdit = QtGui.QLineEdit('Null')
        self.maxFeaturesEdit = QtGui.QLineEdit('0')

        self.minYEdit = QtGui.QLineEdit('0.0')
        self.maxXEdit = QtGui.QLineEdit('0.0')
        self.maxYEdit = QtGui.QLineEdit('0.0')
        #self.DescribeFeatureTypeEdit = QtGui.QLineEdit('http://')
        #self.GetFeatureEdit = QtGui.QLineEdit('http://')

        #gridLayout.addWidget(self.wfsUrlEdit, 0, 1)
        gridLayout.addWidget(self.minXEdit, 3,2)
        gridLayout.addWidget(self.ESPGEdit, 5,1)
        gridLayout.addWidget(self.maxFeaturesEdit, 6,1)
        gridLayout.addWidget(self.minYEdit, 3, 4)
        gridLayout.addWidget(self.maxXEdit, 4, 2)
        gridLayout.addWidget(self.maxYEdit, 4, 4)
        #gridLayout.addWidget(self.DescribeFeatureTypeEdit, 6, 1)
        #gridLayout.addWidget(self.GetFeatureEdit, 7, 1)
        self.opComboAvailableOperations = QtGui.QComboBox()
        #self.opComboAvailableOperations.addItems(['Null'])
        gridLayout.addWidget(self.opComboAvailableOperations, 1, 1)
        self.opComboLayerNames = QtGui.QComboBox()
        #self.opComboLayerNames.addItems(['Null'])
        gridLayout.addWidget(self.opComboLayerNames, 2, 1)

        #self.opComboSRS = QtGui.QComboBox()
        #self.opComboSRS.addItems(['4326', '', ''])
        #gridLayout.addWidget(self.opComboSRS, 5, 1)

        self.loadRequestButton = QtGui.QPushButton('load')

        gridLayout.addWidget(self.loadRequestButton, 7, 1)
        self.connect(self.loadRequestButton, QtCore.SIGNAL('clicked()'), self.loadRequest)

        self.resetRequestButton = QtGui.QPushButton('reset')
        gridLayout.addWidget(self.resetRequestButton, 7, 2)
        self.connect(self.resetRequestButton, QtCore.SIGNAL('clicked()'), self.clearRequest)

        self.saveRequestButton = QtGui.QPushButton('save')
        gridLayout.addWidget(self.saveRequestButton, 7, 3)
        self.connect(self.saveRequestButton, QtCore.SIGNAL('clicked()'), self.saveRequest)

    def clearRequest(self):
        """TO DO Implement clear fields """
        pass

    def saveRequest(self):
        """TO DO Implement read set parameters, assign to wfs input ports """
        pass

    def loadRequest(self):
        """ loadRequest() -> None
        uses service data to populate the config widget populate fields

        SEE SOS.py for similar code (under loadOfferings method)
        """
        #result = str(self.wfsUrlEdit.text()

        defaultUrl = str(self.wfsUrlEdit.text())
        #defaultUrl = str(self.parent_widget.service.service_valid())

        #if self.parent_widget.service and self.parent_widget.service.service_valid:

             #for content in self.parent_widget.service:
                #print content.id
                #item = QtGui.QListWidgetItem(content.id)
                #self.lbxOfferings.addItem(item)


        wfs = WebFeatureService(defaultUrl)
        layers = list(wfs.contents)

        self.opComboAvailableOperations.addItems([op.name for op in wfs.operations])

        for elem in layers:
            self.opComboLayerNames.addItems([elem])
            crsCode = wfs[str(self.opComboLayerNames.currentText())].crsOptions

        for elemen in crsCode:
            self.ESPGEdit.setText(elemen)
            coordinates = wfs[str(self.opComboLayerNames.currentText())].boundingBoxWGS84
            self.minXEdit.setText(str(coordinates[0]))
            self.minYEdit.setText(str(coordinates[1]))
            self.maxXEdit.setText(str(coordinates[2]))
            self.maxYEdit.setText(str(coordinates[3]))


class WFSConfigurationWidget(OgcConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""
    def __init__(self,  module, controller, parent=None):
        OgcConfigurationWidget.__init__(self,  module, controller, parent)
        # pass in parent widget i.e. OgcCommonWidget class
        self.wfs_config = WFSCommonWidget(self.ogc_common_widget)
        # tabs
        self.tabs.insertTab(1, self.wfs_config, "")
        self.tabs.setTabText(
            self.tabs.indexOf(self.wfs_config),
            QtGui.QApplication.translate(
                "WFSConfigurationWidget",
                "WFS",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.wfs_config),
            QtGui.QApplication.translate(
                "WFSConfigurationWidget",
                "WFS Configuration",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setCurrentIndex(0)


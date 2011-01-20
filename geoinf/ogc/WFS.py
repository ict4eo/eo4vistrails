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

import init
from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from OgcConfigurationWidget import OgcConfigurationWidget, OgcCommonWidget
from OgcService import OGC
from packages.eo4vistrails.geoinf.SpatialTemporalConfigurationWidget import SpatialTemporalConfigurationWidget, SpatialWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError


class WFS(OGC, FeatureModel):
    """
    Override for base OGC service class

    """
    def __init__(self):
        OGC.__init__(self)
        FeatureModel.__init__(self)


class WFSCommonWidget(QtGui.QWidget):
    """Enable WCS-specific parameters to be obtained, displayed and selected."""

    def __init__(self, ogc_widget, spatial_widget,  parent=None):
        """sets parameters for wfs request"""
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("WFSConfigurationWidget")
        self.parent_widget = ogc_widget
        self.service = self.parent_widget.service
        self.coords = spatial_widget
        self.create_wfs_config_window()

        # listener for signal emitted by OgcCommonWidget class
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceActivated'),
            self.loadRequest
            )
           # local signals
        self.connect(
            self.lstFeatures,
            QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),
            self.featureNameChanged
            )

    def create_wfs_config_window(self):
        """TO DO - add docstring"""
        gridLayout = QtGui.QGridLayout()
        self.setLayout(gridLayout)
        gridLayout.addWidget(QtGui.QLabel('TypeNames List:'), 0, 1)
        gridLayout.addWidget(QtGui.QLabel('TypeName Metadata:'), 0, 3)
        gridLayout.addWidget(QtGui.QLabel('bbox:'), 3, 0)
        gridLayout.addWidget(QtGui.QLabel('top_left  X'), 3, 1)
        gridLayout.addWidget(QtGui.QLabel('top_left  Y'), 3, 3)
        gridLayout.addWidget(QtGui.QLabel('bottom_right  X'), 4, 1)
        gridLayout.addWidget(QtGui.QLabel('bottom_right  Y'), 4, 3)
        gridLayout.addWidget(QtGui.QLabel('Default SRS Code'), 5, 0)
        self.cbGetFeature = QtGui.QCheckBox("GetFeature bbox-url", self)
        gridLayout.addWidget(self.cbGetFeature,  7, 0)

        self.minXEdit = QtGui.QLineEdit('0.0')
        self.minXEdit.setEnabled(False)
        self.ESPGEdit = QtGui.QLineEdit('Null')
        self.ESPGEdit.setEnabled(False)
        self.minYEdit = QtGui.QLineEdit('0.0')
        self.minYEdit.setEnabled(False)
        self.maxXEdit = QtGui.QLineEdit('0.0')
        self.maxXEdit.setEnabled(False)
        self.maxYEdit = QtGui.QLineEdit('0.0')
        self.maxYEdit.setEnabled(False)
        self.GetFeatureEdit = QtGui.QLineEdit('http://')

        gridLayout.addWidget(self.minXEdit, 3,2)
        gridLayout.addWidget(self.ESPGEdit, 5,1)
        gridLayout.addWidget(self.minYEdit, 3, 4)
        gridLayout.addWidget(self.maxXEdit, 4, 2)
        gridLayout.addWidget(self.maxYEdit, 4, 4)
        gridLayout.addWidget(self.GetFeatureEdit, 7, 1)

        self.lstFeatures = QtGui.QListWidget()
        gridLayout.addWidget(self.lstFeatures, 1, 1)
        # view selected typename / FeatureName ContentMetadata
        self.htmlView = QtGui.QTextEdit()
        gridLayout.addWidget(self.htmlView, 1, 2,  1,  3)

    def loadRequest(self):
        """ loadRequest() -> None
        uses service data to populate the config widget fields
        """
        if self.parent_widget.service and self.parent_widget.service.service_valid:
            self.contents = self.parent_widget.service.service.__dict__['contents']
            for content in self.contents:
                self.lstFeatures.addItems([content])

    def featureNameChanged(self):
        """Update offering details containers when new offering selected."""
        selected_featureName = self.lstFeatures.selectedItems()[0].text()
        print "Accessing....: " + selected_featureName

        # update wfs bbox values with SpatialTemporalConfigurationWidget bbox values
        self.minXEdit.setText(self.coords.bbox_tlx.text())
        self.minYEdit.setText(self.coords.bbox_tly.text())
        self.maxXEdit.setText(self.coords.bbox_brx.text())
        self.maxYEdit.setText(self.coords.bbox_bry.text())

        if self.parent_widget.service and self.parent_widget.service.service_valid and self.contents:
            for content in self.contents:
                if selected_featureName == content:
                    meta = self.contents[str(selected_featureName)]
                    crsCode = self.contents[str(selected_featureName)].crsOptions
                    name = self.contents[str(selected_featureName)].id
                    title = self.contents[str(selected_featureName)].title
                    coordinates = self.contents[str(selected_featureName)].boundingBoxWGS84
                    operations = self.contents[str(selected_featureName)].verbOptions

            for elem in crsCode:
                self.ESPGEdit.setText(elem)
                if name:
                    self.htmlView.setText("Name: " + name)
                    self.htmlView.append('')
                if title:
                    self.htmlView.append("Title: " + title)
                    self.htmlView.append('')
                if elem:
                    self.htmlView.append("SRS: " + str(elem))
                    self.htmlView.append('')
                if operations:
                    self.htmlView.append("Operations: " + str(operations))
                    self.htmlView.append('')
                if coordinates:
                    self.htmlView.append("LatLongBoundingBox:" + \
                        '   minx= '+ str(coordinates[0]) + \
                        '   miny= '+ str(coordinates[1]) + \
                        '   maxx= '+ str(coordinates[2])  + \
                        '   maxy= '+ str(coordinates[3])
                    )

        if self.cbGetFeature.isChecked():
            selected_featureName = self.lstFeatures.selectedItems()[0].text()
            top_letf_X = self.minXEdit.text()
            top_left_Y = self.minYEdit.text()
            btm_right_X = self.maxXEdit.text()
            btm_right_Y = self.maxYEdit.text()
            wfs_url = self.parent_widget.line_edit_OGC_url.text()
            vers = str(self.parent_widget.launchversion.currentText())
            espg_number =  self.ESPGEdit.text()

            if '?' in wfs_url:
                parts = wfs_url.split('?')
                self.url = parts[0]
            else:
                self.url = wfs_url
                getFeatureBBoxUrl = wfs_url+ \
                "?request=GetFeature&version="+vers+ \
                "&typeName="+str(selected_featureName)+ \
                "&BBOX="+str(top_letf_X) + ','+ str(top_left_Y) +',' + str(btm_right_X)+','+ str(btm_right_Y)+','+ str(espg_number)
                self.GetFeatureEdit.setText(str(getFeatureBBoxUrl))
        else:
            self.GetFeatureEdit.setText("http://no getfeature request constructed")


class WFSConfigurationWidget(OgcConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""
    def __init__(self,  module, controller, parent=None):
        OgcConfigurationWidget.__init__(self,  module, controller, parent)
        # pass in parent widget i.e. OgcCommonWidget class and SpatialWidget Class (read changed coords)
        self.wfs_config_widget = WFSCommonWidget(self.ogc_common_widget,  self.spatial_widget)
        # tabs
        self.tabs.insertTab(1, self.wfs_config_widget, "")
        self.tabs.setTabText(
            self.tabs.indexOf(self.wfs_config_widget),
            QtGui.QApplication.translate(
                "WFSConfigurationWidget",
                "WFS",
                None,
                QtGui.QApplication.UnicodeUTF8
                )
            )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.wfs_config_widget),
            QtGui.QApplication.translate(
                "WFSConfigurationWidget",
                "WFS Configuration",
                None,
                QtGui.QApplication.UnicodeUTF8
                )
            )
        self.tabs.setCurrentIndex(0)

    def getBoundingBox(self):
        """Return a comma-delimited string containing box co-ordinates."""
        top_left_X = self.wfs_config_widget.minXEdit.text()
        top_left_Y = self.wfs_config_widget.minYEdit.text()
        btm_right_X = self.wfs_config_widget.maxXEdit.text()
        btm_right_Y = self.wfs_config_widget.maxYEdit.text()
        return str(top_left_X)+','+str(top_left_Y)+','+str(btm_right_X)+','+str(btm_right_Y)

    def constructRequest(self):
        """Return a URL request from configuration parameters
        Overwrites method defined in OgcConfigurationWidget.
        """
        selected_typeName = self.wfs_config_widget.lstFeatures.selectedItems()[0].text()
        espg_number =  self.wfs_config_widget.ESPGEdit.text()
        wfs_url = self.ogc_common_widget.line_edit_OGC_url.text()
        vers = str(self.ogc_common_widget.launchversion.currentText())

        if '?' in wfs_url:
            parts = wfs_url.split('?')
            self.url = parts[0]
        else:
            self.url = wfs_url

        return self.url + \
            "?request=GetFeature&version="+vers+ \
            "&typeName="+str(selected_typeName)+ \
            "&BBOX="+self.getBoundingBox()+','+str(espg_number)

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


from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError


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
        #gridLayout.addWidget(QtGui.QLabel('wfs Url'), 0, 0)
        gridLayout.addWidget(QtGui.QLabel('Feature Names:'), 1, 0)
        #gridLayout.addWidget(QtGui.QLabel('TypeNames'), 2, 0)
        gridLayout.addWidget(QtGui.QLabel('bbox:'), 3, 0)
        gridLayout.addWidget(QtGui.QLabel('top_left  X'), 3, 1)
        gridLayout.addWidget(QtGui.QLabel('top_left  Y'), 3, 3)
        gridLayout.addWidget(QtGui.QLabel('bottom_right  X'), 4, 1)
        gridLayout.addWidget(QtGui.QLabel('bottom_right  Y'), 4, 3)
        gridLayout.addWidget(QtGui.QLabel('ESPG/SRS Code'), 5, 0)
        gridLayout.addWidget(QtGui.QLabel('maxFeatures'), 6, 0)


        #gridLayout.addWidget(QtGui.QCheckBox('GetCapabilities Request'), 7, 0)
        gridLayout.addWidget(QtGui.QCheckBox('GetFeature Request'), 7, 0)
        gridLayout.addWidget(QtGui.QCheckBox('DescribeFeatureType Request'), 8, 0)

        #self.wfsUrlEdit = QtGui.QLineEdit('http://localhost:8080/geoserver/wfs')

        self.minXEdit = QtGui.QLineEdit('0.0')
        self.ESPGEdit = QtGui.QLineEdit('Null')
        self.maxFeaturesEdit = QtGui.QLineEdit('0')

        self.minYEdit = QtGui.QLineEdit('0.0')
        self.maxXEdit = QtGui.QLineEdit('0.0')
        self.maxYEdit = QtGui.QLineEdit('0.0')

        self.GetCapabilitiesEdit = QtGui.QLineEdit('http://')
        self.GetFeatureEdit = QtGui.QLineEdit('http://')
        self.DescribeFeatureTypeEdit = QtGui.QLineEdit('http://')

        #gridLayout.addWidget(self.wfsUrlEdit, 0, 1)
        gridLayout.addWidget(self.minXEdit, 3,2)
        gridLayout.addWidget(self.ESPGEdit, 5,1)
        gridLayout.addWidget(self.maxFeaturesEdit, 6,1)
        gridLayout.addWidget(self.minYEdit, 3, 4)
        gridLayout.addWidget(self.maxXEdit, 4, 2)
        gridLayout.addWidget(self.maxYEdit, 4, 4)

        #gridLayout.addWidget(self.GetCapabilitiesEdit, 7, 1)
        gridLayout.addWidget(self.GetFeatureEdit, 7, 1)
        gridLayout.addWidget(self.DescribeFeatureTypeEdit, 8, 1)

        self.lstFeatures = QtGui.QListWidget()

        gridLayout.addWidget(self.lstFeatures, 1, 1)


        self.htmlView = QtGui.QTextEdit()   # want to view featureColletion for each selected typename / FeatureName.

        gridLayout.addWidget(self.htmlView, 1, 3)


    '''
    def clearRequest(self):
        """TO DO Implement clear fields """
        self.minXEdit.setText('0.0')
        self.ESPGEdit.setText('Null')
        self.maxFeaturesEdit.setText('0')

        self.minYEdit.setText('0.0')
        self.maxXEdit.setText('0.0')
        self.maxYEdit.setText('0.0')
    '''

    def loadRequest(self):
        """ loadRequest() -> None
        uses service data to populate the config widget populate fields

        SEE SOS.py for similar code (under loadOfferings method)
        """

        if self.parent_widget.service and self.parent_widget.service.service_valid:
            self.contents = self.parent_widget.service.service.__dict__['contents']

            for content in self.contents:
                self.lstFeatures.addItems([content])


    def featureNameChanged(self):
        """Update offering details containers when new offering selected."""

        selected_featureName = self.lstFeatures.selectedItems()[0].text()

        print "Accessing....: " + selected_featureName

        getfeature_request = self.parent_widget.service.service


        if self.parent_widget.service and self.parent_widget.service.service_valid and self.contents:

            featureDetails = getfeature_request.getfeature(typename=[str(selected_featureName)], maxfeatures=1)

            for content in self.contents:

                if selected_featureName == content:

                    crsCode = self.contents[str(selected_featureName)].crsOptions

                    meta = self.contents[str(selected_featureName)]

                    bheki = self.contents[str(selected_featureName)].title



            for elem in crsCode:

                self.ESPGEdit.setText(elem)

                coordinates = self.contents[str(selected_featureName)].boundingBoxWGS84
                self.minXEdit.setText(str(coordinates[0]))
                self.minYEdit.setText(str(coordinates[1]))
                self.maxXEdit.setText(str(coordinates[2]))
                self.maxYEdit.setText(str(coordinates[3]))

                # set metadata for selected layername
                self.htmlView.setText("Name: " )
                self.htmlView.append("Title: " + bheki  )
                self.htmlView.append("Abstract: "  )
                self.htmlView.append("Keywords: "   )
                self.htmlView.append("SRS: " + str(elem))
                self.htmlView.append("Operations: "  )
                self.htmlView.append("LatLongBoundingBox: " + 'minx= '+ str(coordinates[0]) + ' miny= '+ str(coordinates[1]) + ' maxx= '+ str(coordinates[2])  + ' maxy= '+ str(coordinates[3])  )
                self.htmlView.append("MetadataURL: "  )

        #self.htmlView.setText(str(featureDetails.read()))
        #self.htmlView.setText(str([meta])) # what's this funny stuff being shown here.


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


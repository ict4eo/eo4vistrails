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
from OgcConfigurationWidget import OgcConfigurationWidget,  OgcCommonWidget
from packages.eo4vistrails.geoinf.SpatialTemporalConfigurationWidget import SpatialTemporalConfigurationWidget, SpatialWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
from packages.eo4vistrails.geoinf.SpatialTemporalConfigurationWidget import SpatialTemporalConfigurationWidget, SpatialWidget

#need to import the configuration widget we develop


class WFS(NotCacheable,  FeatureModel):
    """TO DO - add docstring

    """
      # testing: create, set port defaults parameters / values
   # _input_ports = [("MinX", "(edu.utah.sci.vistrails.basic:Float)",
    #                  {"defaults": str([23.0]), "labels": str(["XVal"])})]


    def __init__(self):
        FeatureModel.__init__(self)

    def compute(self):
        #pass
        print '..............Printing url from OGC_URL_PORT...........'

        if self.hasInputFromPort(init.OGC_URL_PORT):
            ogc_wfs_url = self.getInputFromPort(init.OGC_URL_PORT)
            print ogc_wfs_url  # print url value


        print '..............Accessing configuration parameters from dict............'

        print wfs_config_dict  #print items from dictionary: this won't work when accessing saved wfs_test.vt, re-configure WFS. dict holds values temporarly


class WFSCommonWidget(QtGui.QWidget):
    """TO DO - add docstring

    """

    def __init__(self, ogc_widget, parent=None):
        """sets parameters for wfs request"""

        QtGui.QWidget.__init__(self, parent)

        self.setObjectName("WFSConfigurationWidget")

        self.parent_widget = ogc_widget

        self.service = self.parent_widget.service

        self.coords = SpatialWidget()

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

        global wfs_config_dict   # global dictionary to hold configuration  parameters

        wfs_config_dict = dict()


    def create_wfs_config_window(self):
        """TO DO - add docstring"""
        gridLayout = QtGui.QGridLayout()
        self.setLayout(gridLayout)
        gridLayout.addWidget(QtGui.QLabel('TypeNames List:'), 0, 1)
        gridLayout.addWidget(QtGui.QLabel('TypeName Metadata:'), 0, 3)
        #gridLayout.addWidget(QtGui.QLabel('Feature Names:'), 1, 0)
        #gridLayout.addWidget(QtGui.QLabel('TypeNames'), 2, 0)
        gridLayout.addWidget(QtGui.QLabel('bbox:'), 3, 0)
        gridLayout.addWidget(QtGui.QLabel('top_left  X'), 3, 1)
        gridLayout.addWidget(QtGui.QLabel('top_left  Y'), 3, 3)
        gridLayout.addWidget(QtGui.QLabel('bottom_right  X'), 4, 1)
        gridLayout.addWidget(QtGui.QLabel('bottom_right  Y'), 4, 3)
        gridLayout.addWidget(QtGui.QLabel('ESPG/SRS Code'), 5, 0)
        gridLayout.addWidget(QtGui.QLabel('maxFeatures'), 6, 0)

        gridLayout.addWidget(QtGui.QCheckBox('GetFeature Request'), 7, 0)
        gridLayout.addWidget(QtGui.QCheckBox('DescrbFeatureType Request'), 8, 0)

        #self.wfsUrlEdit = QtGui.QLineEdit('http://localhost:8080/geoserver/wfs')

        self.minXEdit = QtGui.QLineEdit('0.0')
        self.minXEdit.setEnabled(False)
        self.ESPGEdit = QtGui.QLineEdit('Null')
        self.ESPGEdit.setEnabled(False)
        self.maxFeaturesEdit = QtGui.QLineEdit('0')

        self.minYEdit = QtGui.QLineEdit('0.0')
        self.minYEdit.setEnabled(False)
        self.maxXEdit = QtGui.QLineEdit('0.0')
        self.maxXEdit.setEnabled(False)
        self.maxYEdit = QtGui.QLineEdit('0.0')
        self.maxYEdit.setEnabled(False)

        #self.GetCapabilitiesEdit = QtGui.QLineEdit('http://')
        self.GetFeatureEdit = QtGui.QLineEdit('http://')
        self.DescribeFeatureTypeEdit = QtGui.QLineEdit('http://')

        #gridLayout.addWidget(self.wfsUrlEdit, 0, 1)
        gridLayout.addWidget(self.minXEdit, 3,2)
        gridLayout.addWidget(self.ESPGEdit, 5,1)
        gridLayout.addWidget(self.maxFeaturesEdit, 6,1)
        gridLayout.addWidget(self.minYEdit, 3, 4)
        gridLayout.addWidget(self.maxXEdit, 4, 2)
        gridLayout.addWidget(self.maxYEdit, 4, 4)

        gridLayout.addWidget(self.GetFeatureEdit, 7, 1)
        gridLayout.addWidget(self.DescribeFeatureTypeEdit, 8, 1)

        self.lstFeatures = QtGui.QListWidget()

        gridLayout.addWidget(self.lstFeatures, 1, 1)

        self.htmlView = QtGui.QTextEdit()   # view selected typename / FeatureName ContentMetadata
        #self.htmlView.setEnabled(False)
        gridLayout.addWidget(self.htmlView, 1, 2,  1,  3)


    def loadRequest(self):
        """ loadRequest() -> None
        uses service data to populate the config widget populate fields
        """

        if self.parent_widget.service and self.parent_widget.service.service_valid:
            self.contents = self.parent_widget.service.service.__dict__['contents']


            for content in self.contents:
                self.lstFeatures.addItems([content])


    def featureNameChanged(self):

        """Update offering details containers when new offering selected."""

        selected_featureName = self.lstFeatures.selectedItems()[0].text()

        print "Accessing....: " + selected_featureName

        #getfeature_request = self.parent_widget.service.service

        # read set coordinates
        self.minXEdit.setText(self.coords.bbox_tlx.text())
        self.minYEdit.setText(self.coords.bbox_tly.text())
        self.maxXEdit.setText(self.coords.bbox_brx.text())
        self.maxYEdit.setText(self.coords.bbox_bry.text())


        # testing global dic

        #wfs_config_dict = {'TypeName': str(selected_featureName) ,'minX': str(self.minXEdit.text()), 'minY': str(self.minYEdit.text()),  'maxX': str(self.maxXEdit.text()),  'maxY': str(self.maxYEdit.text()) }

        wfs_config_dict['TypeName'] = str(selected_featureName)
        wfs_config_dict['minX'] = str(self.minXEdit.text())
        wfs_config_dict['minY'] = str(self.minYEdit.text())
        wfs_config_dict['maxX'] = str(self.maxXEdit.text())
        wfs_config_dict['maxY'] = str(self.maxYEdit.text())

        #print "After update.......................:"

        #print wfs_config_dict


        if self.parent_widget.service and self.parent_widget.service.service_valid and self.contents:

            #featureDetails = getfeature_request.getfeature(typename=[str(selected_featureName)], maxfeatures=1)

            for content in self.contents:

                if selected_featureName == content:

                    #print self.contents[str(selected_featureName)].__dict__
                    """
                    'styles': None,
                    'timepositions': None,
                    'crsOptions': ['EPSG:900913'],
                    'title': None,
                    'boundingBoxWGS84': (32.43423534250477, -27.025131724476203, 40.851497819156378, -10.54235793928602),
                    'boundingBox': None,
                    'verbOptions': ['{http://www.opengis.net/wfs}Query', '{http://www.opengis.net/wfs}Insert', '{http://www.opengis.net/wfs}Update', '{http://www.opengis.net/wfs}Delete', '{http://www.opengis.net/wfs}Lock'],
                    'id': 'ict4eo:moz_coast_vulnerability_tide'
                    """

                    meta = self.contents[str(selected_featureName)]
                    crsCode = self.contents[str(selected_featureName)].crsOptions
                    name = self.contents[str(selected_featureName)].id
                    title = self.contents[str(selected_featureName)].title
                    coordinates = self.contents[str(selected_featureName)].boundingBoxWGS84
                    operations = self.contents[str(selected_featureName)].verbOptions

            for elem in crsCode:
                self.ESPGEdit.setText(elem)
                wfs_config_dict['SRS'] = str(self.ESPGEdit.text())

                #self.minXEdit.setText(str(coordinates[0]))
                #self.minYEdit.setText(str(coordinates[1]))
                #self.maxXEdit.setText(str(coordinates[2]))
                #self.maxYEdit.setText(str(coordinates[3]))

                #set metadata for selected layername :
                # how about if we were to read these directly from the GetCapabilities file??
                if name:
                    self.htmlView.setText("Name: " + name)
                    self.htmlView.append('')
                if title:
                    self.htmlView.append("Title: " + title)
                    self.htmlView.append('')
                """ not in wfs ?
                self.htmlView.append("Abstract: " + abstr)
                self.htmlView.append('')
                self.htmlView.append("Keywords: "  + keyw)
                self.htmlView.append('')
                """
                if elem:
                    self.htmlView.append("SRS: " + str(elem))
                    self.htmlView.append('')
                if operations:
                    self.htmlView.append("Operations: " + str(operations))
                    self.htmlView.append('')
                if coordinates:
                    self.htmlView.append("LatLongBoundingBox:" + \
                        ' minx= '+ str(coordinates[0]) + \
                        ' miny= '+ str(coordinates[1]) + \
                        ' maxx= '+ str(coordinates[2])  + \
                        ' maxy= '+ str(coordinates[3])
                    )

        #print "Before update.......................:"
        #print wfs_config_dict

        globals().update(wfs_config_dict)

        #print "After update.......................:"
        #print wfs_config_dict


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

    def okTriggered(self): # , checked=False in parent?
        """Extend method which is extended in OgcTemporalConfigurationWidget."""

        self.wfs_url = self.wfs_config.parent_widget.line_edit_OGC_url.text() # wfs ogc tab url value

        functions = []
        functions.append(('OGC_URL', [str(self.wfs_url)]),)
        self.controller.update_ports_and_functions(self.module.id,
                                                   [],
                                                   [],
                                                   functions)

        OgcConfigurationWidget.okTriggered(self)

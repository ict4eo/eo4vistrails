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
"""This module provides an OGC (Open Geospatial Consortium) Web Coverage Service
(WCS) Client via owslib.
"""

from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Raster import RasterModel
from OgcConfigurationWidget import OgcConfigurationWidget
from OgcService import OGC
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
import init


class WCS(OGC, RasterModel):
    """
    Override for base OGC service class

    """
    def __init__(self):
        OGC.__init__(self)
        RasterModel.__init__(self)


class WCSCommonWidget(QtGui.QWidget):
    """
    WCS module allows connection to a web-based OGC (Open Geospatial Consortium)
    web coverage service.
    Configuration allows the base URL for the service to be set and called.
    Choosing the appropriate combination of specific service type and other
    parameters, will cause the input port to be set with a specific POST call,
    once the configuration interface is closed.
    Running the WCS will cause the specific, parameterised WCS to be called
    and output from the request to be available via the output port(s).

    """
    def __init__(self, ogc_widget, parent=None):
        """sets parameters for wcs request"""
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("WCSCommonWidget")
        self.parent_widget = ogc_widget
        #self.service = self.parent_widget.service
        self.contents = None #  only set in self.loadRequests()
        self.create_wcs_config_window()

        # listen for signals emitted by OgcCommonWidget class
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceActivated'),
            self.loadRequests
            )
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceDeactivated'),
            self.removeRequests
            )

    def create_wcs_config_window(self):
        """TO DO - add docstring"""
        # add widgets here!
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.requestsGroupBox = QtGui.QGroupBox("WCS Request Offerings")
        self.requestsLayout = QtGui.QVBoxLayout()
        self.requestsGroupBox.setLayout(self.requestsLayout)
        self.mainLayout.addWidget(self.requestsGroupBox)
        # add a horizontal split to split the window equally
        self.split = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.mainLayout.addWidget(self.split)
        self.detailsGroupBox = QtGui.QGroupBox("WCS Request Details")
        self.mainLayout.addWidget(self.detailsGroupBox)
        self.detailsLayout = QtGui.QGridLayout()
        self.detailsGroupBox.setLayout(self.detailsLayout)
        # WCS Request offerings layout
        self.requestLbx = QtGui.QListWidget()
        self.requestsLayout.addWidget(self.requestLbx)

        # WCS Request details layout
        # Labels
        self.detailsLayout.addWidget(QtGui.QLabel('Layer ID:'), 0, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Layer Description:'), 1, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('BBox - data bounds:'), 2, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('ULX:'), 3, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('LRX:'), 3, 2)
        self.detailsLayout.addWidget(QtGui.QLabel('ULY:'), 4, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('LRY:'), 4, 2)
        self.detailsLayout.addWidget(QtGui.QLabel('SRS:'), 5, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Output SRS:'), 6, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Output Format:'), 7, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Request Type:'), 8, 0)

        # Data containers
        self.dcLayerId = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcLayerId, 0, 1)
        self.dcLayerDescription = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcLayerDescription, 1,1)
        self.dcULX = QtGui.QLineEdit(' ')
        self.dcULX.setEnabled(False) #sets it not to be editable
        self.detailsLayout.addWidget(self.dcULX, 3,1)
        self.dcLRX = QtGui.QLineEdit(' ')
        self.dcLRX.setEnabled(False)
        self.detailsLayout.addWidget(self.dcLRX, 3,3)
        self.dcULY = QtGui.QLineEdit(' ')
        self.dcULY.setEnabled(False)
        self.detailsLayout.addWidget(self.dcULY, 4,1)
        self.dcLRY = QtGui.QLineEdit(' ')
        self.dcLRY.setEnabled(False)
        self.detailsLayout.addWidget(self.dcLRY, 4,3)
        self.dcSRS = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcSRS, 5, 1)
        self.dcSRSreq = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcSRSreq, 6, 1)
        self.dcReqFormat = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcReqFormat, 7, 1)
        self.dcRequestType = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcRequestType, 8, 1)
        self.dcRequestType.addItem('GetCapabilities')
        self.dcRequestType.addItem('DescribeCoverage')
        self.dcRequestType.addItem('GetCoverage')

        # local signals
        self.connect(
            self.requestLbx,
            QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),
            self.coverageNameChanged
            )

    def loadRequests(self):
        """ loadRequest() -> None
        uses service data to populate the config widget populate fields
        """
        if self.parent_widget.service and self.parent_widget.service.service_valid:
            self.contents = self.parent_widget.service.service.__dict__['contents']
            for content in self.contents:
                self.requestLbx.addItems([content])

    def clearRequests(self):
        """To reset the values in the fields"""
        self.dcLayerId.setText('-')
        self.dcLayerDescription.setText('-')
        self.dcULX.setText('-')
        self.dcLRX.setText('-')
        self.dcULY.setText('-')
        self.dcLRY.setText('-')
        self.dcSRS.setText('-')
        self.dcSRSreq.clear()
        self.dcReqFormat.clear()
        #self.dcRequestType.clear()

    def coverageNameChanged(self):
        """Update offering details containers when new offering selected."""
        self.clearRequests()
        selected_coverageName = self.requestLbx.selectedItems()[0].text()
        if self.parent_widget.service and self.parent_widget.service.service_valid and self.contents:
            for content in self.contents:
                if selected_coverageName == content:
                     self.dcLayerId.setText(self.contents[str(selected_coverageName)].id)
                     self.dcLayerDescription.setText(self.contents[str(selected_coverageName)].title)
                     self.dcULX.setText(str(self.contents[str(selected_coverageName)].boundingBoxWGS84[0])) # 1st item in bbox tuple
                     self.dcLRX.setText(str(self.contents[str(selected_coverageName)].boundingBoxWGS84[1]))
                     self.dcULY.setText(str(self.contents[str(selected_coverageName)].boundingBoxWGS84[2]))
                     self.dcLRY.setText(str(self.contents[str(selected_coverageName)].boundingBoxWGS84[3]))
                     #self.dcSRS.setText(self.contents[str(selected_coverageName)].crsOptions)
                     self.dcSRSreq.addItems(self.contents[str(selected_coverageName)].supportedCRS) #don't know how to access this yet on WCS
                     self.dcReqFormat.addItems(self.contents[str(selected_coverageName)].supportedFormats)# returns a list of values that are unpacked into a combobox

    def removeRequests(self):
        """Remove all details when no WCS is selected."""
        self.clearRequests()
        self.requestLbx.clear()


class WCSConfigurationWidget(OgcConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""
    def __init__(self, module, controller, parent=None):
        OgcConfigurationWidget.__init__(self, module, controller, parent)
        # pass in parent widget i.e. OgcCommonWidget class
        self.wcs_config_widget = WCSCommonWidget(self.ogc_common_widget)
        # tabs
        self.tabs.insertTab(1, self.wcs_config_widget, "")
        self.tabs.setTabText(
            self.tabs.indexOf(self.wcs_config_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "WCS Specific Metadata",
                None,
                QtGui.QApplication.UnicodeUTF8
                )
            )

        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.wcs_config_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "Select WCS-specific parameters",
                None,
                QtGui.QApplication.UnicodeUTF8
                    )
                )
        self.tabs.setCurrentIndex(0)

    def constructRequest(self):
        """Return a URL request from configuration parameters

        Overwrites method defined in OgcConfigurationWidget.
        """
        wcs_url = self.ogc_common_widget.line_edit_OGC_url.text()
        WCSversion = str(self.ogc_common_widget.launchversion.currentText())
        selectedCoverageId = str(self.wcs_config_widget.dcLayerId.text())
        return wcs_url+ \
            "?version="+WCSversion+\
            "&service=WCS"+\
            "&REQUEST=DescribeCoverage"+\
            "&COVERAGE="+selectedCoverageId
        #data = ''
        #type = self.config.dcRequestType.currentText()
        #try:
            #procedure = self.config.

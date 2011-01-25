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
from packages.eo4vistrails.geoinf.SpatialTemporalConfigurationWidget import SpatialTemporalConfigurationWidget, SpatialWidget
from OgcConfigurationWidget import OgcConfigurationWidget
from OgcService import OGC
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
import init

#def ns(tag):
    #return '{http://www.opengis.net/wcs}'+tag

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
    def __init__(self, ogc_widget, spatial_widget, parent=None):
        """sets parameters for wcs request"""
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("WCSCommonWidget")
        self.parent_widget = ogc_widget
        #self.service = self.parent_widget.service
        self.contents = None #  only set in self.loadRequests()
        self.spatialSubset= spatial_widget
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
        
        
        self.detailsLayout.addWidget(QtGui.QLabel('BBox - Spatial Subset:'), 5, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('ULX:'), 6, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('LRX:'), 6, 2)
        self.detailsLayout.addWidget(QtGui.QLabel('ULY:'), 7, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('LRY:'), 7, 2)
        
        self.detailsLayout.addWidget(QtGui.QLabel('SRS:'), 8, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Bands:'), 9, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Output SRS:'), 10, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Output Format:'), 11, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Request Type:'), 12, 0)

        # Data containers
        self.dcLayerId = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcLayerId, 0, 1)
        self.dcLayerDescription = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcLayerDescription, 1,1)
        
        #Bounding box - Grid Envelope
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
        
        #Bounding Box Spatial subset
        self.ssULX = QtGui.QLabel(' ')
        #self.ssULX.setEnabled(False) #sets it not to be editable
        self.detailsLayout.addWidget(self.ssULX, 6,1)
        self.ssLRX = QtGui.QLabel(' ')
        #self.ssLRX.setEnabled(False)
        self.detailsLayout.addWidget(self.ssLRX, 6,3)
        self.ssULY = QtGui.QLabel(' ')
        #self.ssULY.setEnabled(False)
        self.detailsLayout.addWidget(self.ssULY, 7,1)
        self.ssLRY = QtGui.QLabel(' ')
        #self.ssLRY.setEnabled(False)
        self.detailsLayout.addWidget(self.ssLRY, 7,3)
        
        self.dcSRS = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcSRS, 8, 1)
        self.dcBandsreq = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcBandsreq, 9, 1)
        self.dcSRSreq = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcSRSreq, 10, 1)
        self.dcReqFormat = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcReqFormat, 11, 1)
        self.dcRequestType = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcRequestType, 12, 1)
        self.dcRequestType.addItem('GetCapabilities')
        self.dcRequestType.addItem('DescribeCoverage')
        self.dcRequestType.addItem('GetCoverage')

        # local signals
        self.connect(
            self.requestLbx,
            QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),
            self.coverageNameChanged
            )

        #for message box
        self.arrowCursor = QtGui.QCursor(QtCore.Qt.ArrowCursor)

    def removeRequests(self):
        """Remove all details when no WCS is selected."""
        self.clearRequests()
        self.requestLbx.clear()
        #pass

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
        
        #populate other coverage dependent parameters
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
                     #self.dcSRSreq.addItems(self.contents[str(selected_coverageName)].supportedCRS) 
                     self.dcReqFormat.addItems(self.contents[str(selected_coverageName)].supportedFormats) # returns a list of values that are unpacked into a combobo
        #self._getSupportedCRSProperty()
            #print self.contents[str(selected_coverageName)].supportedFormats
        
        """def _getSupportedCRSProperty(self):
        selected_coverageName = self.requestLbx.selectedItems()[0].text()
        if self.parent_widget.service and self.parent_widget.service.service_valid and self.contents:
            for content in self.contents:
                if selected_coverageName == content:
                    id = self.contents[str(selected_coverageName)].id
                    crss=[]
                    for elem in self.parent_widget.service.service.getDescribeCoverage(id).findall(ns('supportedCRSs')):
                        print 'test'
                        for crs in elem.text.split(' '):
                            crss.append(crs)
                            #print len (crss)
                            """
            
        #display spatial subset in WCS window and set warning if data out of bounds
        self.ssULX.setText(str(self.spatialSubset.bbox_tlx.text()))
        self.ssULY.setText(str(self.spatialSubset.bbox_tly.text()))
        self.ssLRX.setText(str(self.spatialSubset.bbox_brx.text()))
        self.ssLRY.setText(str(self.spatialSubset.bbox_bry.text()))
        
        #call to check spatial subset coordinates
        self.checkCoords()

    def checkCoords(self):
        self.setCursor(self.arrowCursor)
        # checks that user entered subset data is not out of bounds. Using Point in Polygon method
        minX = str(self.dcULX.text())
        maxX= str(self.dcLRX.text())
        minY= str(self.dcULY.text())
        maxY= str(self.dcLRY.text())
        x1 = str(self.spatialSubset.bbox_tlx.text())
        y1 = str(self.spatialSubset.bbox_tly.text())
        x2 = str(self.spatialSubset.bbox_brx.text())
        y2 = str(self.spatialSubset.bbox_bry.text())
        
        if minX < x1< maxX and minY < y1 < maxY:
            pass
        else :
         self.showWarning("Warinig: POINT (X1,Y1) OUT OF BOUNDS....Selected area may be empty!!")
        if minX < x2< maxX and minY < y2 < maxY:
            pass
        else :
         self.showWarning("Warinig: POINT (X2,Y2) OUT OF BOUNDS....Selected area may be empty!!")
         
    def showWarning(self, message):
        """Show user a warning dialog."""
        self.setCursor(self.arrowCursor)
        QtGui.QMessageBox.warning(self,"Error",message,QtGui.QMessageBox.Ok)


    def loadRequests(self):
        """ loadRequest() -> None
        uses service data to populate the config widget populate fields
        """
        if self.parent_widget.service and self.parent_widget.service.service_valid:
            self.contents = self.parent_widget.service.service.__dict__['contents']
            for content in self.contents:
                self.requestLbx.addItems([content])


class WCSConfigurationWidget(OgcConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""
    def __init__(self, module, controller, parent=None):
        OgcConfigurationWidget.__init__(self, module, controller, parent)
        # pass in parent widget i.e. OgcCommonWidget class and SpatialWidget Class to read changed coords
        self.wcs_config_widget = WCSCommonWidget(self.ogc_common_widget,  self.spatial_widget)
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
        ULX=str(self.wcs_config_widget.dcULX.text())
        ULY=str(self.wcs_config_widget.dcULY.text())
        BRX=str(self.wcs_config_widget.dcLRX.text())
        BRY=str(self.wcs_config_widget.dcLRY.text())
        
        data = ''
        # request type in request comboBox
        rType = self.wcs_config_widget.dcRequestType.currentText()
        # check for data in comboBoxes
        try:
            bands = self.wcs_config_widget.dcBandsreq.currentText()
        except:
            bands = None
        try:
            coord_system = self.wcs_config_widget.SRSreq.currentText()
        except:
            coord_system = None
        try:
            formats =  str(self.wcs_config_widget.dcReqFormat.currentText())
        except:
            formats = None
        # details per request type:
        if rType == 'DescribeCoverage':
            return wcs_url+ \
            "?version="+WCSversion+\
            "&service=WCS"+\
            "&REQUEST=DescribeCoverage"+\
            "&COVERAGE="+selectedCoverageId
        elif rType == 'GetCoverage':
            return wcs_url+\
            "?service=WCS"+\
            "&version="+WCSversion+\
            "&request=GetCoverage"+\
            "&coverage="+selectedCoverageId+\
            "&bbox="+ULX+","+ULY+","+BRX+","+BRY
            """+\
            "&crs="+coord_system+\
            "&format="+formats+\
            "&res=10&resy=10"
            """
            

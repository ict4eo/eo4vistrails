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
from packages.eo4vistrails.geoinf.SpatialTemporalConfigurationWidget import \
    SpatialTemporalConfigurationWidget, SpatialWidget
from packages.eo4vistrails.utils.WebRequest import WebRequest
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
        self.spatial_widget = spatial_widget
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
        # text for combo boxes
        self.SPATIAL_OFFERING = 'Use Coverage Bounding Box'
        self.SPATIAL_OWN = 'Use Own Bounding Box'
        # add widgets here!
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.requestsGroupBox = QtGui.QGroupBox("WCS Request Coverages")
        self.requestsLayout = QtGui.QVBoxLayout()
        self.requestsGroupBox.setLayout(self.requestsLayout)
        self.mainLayout.addWidget(self.requestsGroupBox)
        # add a horizontal split to split the window equally
        self.split = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.mainLayout.addWidget(self.split)
        self.detailsGroupBox = QtGui.QGroupBox("WCS Coverage Details")
        self.mainLayout.addWidget(self.detailsGroupBox)
        self.detailsLayout = QtGui.QGridLayout()
        self.detailsGroupBox.setLayout(self.detailsLayout)
        # WCS Request offerings layout
        self.requestLbx = QtGui.QListWidget()
        self.requestsLayout.addWidget(self.requestLbx)

        # WCS Request details layout
        # Labels
        self.detailsLayout.addWidget(QtGui.QLabel('Coverage ID:'), 0, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Coverage Description:'), 1, 0)

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

        self.detailsLayout.addWidget(QtGui.QLabel('Width:'), 8, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Height:'), 8, 2)

        self.detailsLayout.addWidget(QtGui.QLabel('SRS:'), 9, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Bands:'), 10, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Output SRS:'), 11, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Output Format:'), 12, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Spatial Delimiter?'), 13, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Request Type:'), 14, 0)

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

        self.dcWidth = QtGui.QLabel(' ')
        #self.dcWidth.setEnabled(False)
        self.detailsLayout.addWidget(self.dcWidth, 8,1)
        self.dcHeight = QtGui.QLabel(' ')
        #self.dcHeight.setEnabled(False)
        self.detailsLayout.addWidget(self.dcHeight, 8,3)

        self.dcSRS = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcSRS, 9, 1)
        self.dcBandsreq = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcBandsreq, 10, 1)
        self.dcSRSreq = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcSRSreq, 11, 1)
        self.dcReqFormat = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcReqFormat, 12, 1)
        self.dcRequestType = QtGui.QComboBox()

        self.cbSpatial = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbSpatial, 13, 1)
        self.cbSpatial.addItem(self.SPATIAL_OFFERING)
        self.cbSpatial.addItem(self.SPATIAL_OWN)
        self.cbSpatial.addItem('')

        self.detailsLayout.addWidget(self.dcRequestType, 14, 1)
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

    def getBoundingBoxStringCoverage(self):
        """Return a comma-delimited string containing box co-ordinates.

        Format: top-left X,Y  bottom-right X,Y
        """
        bbox = self.spatial_widget.getBoundingBox()
        return str(self.dcULX.text()) + ',' + str(self.dcLRX.text()) + ','\
            +  str(self.dcULY.text()) + ',' + str(self.dcLRY.text())

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

                    if self.contents[str(selected_coverageName)].grid:
                        grid = self.contents[str(selected_coverageName)].grid
                        self.dcWidth.setText(str(grid.highlimits[0]))
                        self.dcHeight.setText(str(grid.highlimits[1]))

                    """ NOTE (by Derek Hohls, 2011/2/22):

                    Accessing and interpreting axis information to extract
                    meaning about bands is NOT a trivial operation.  See pages
                    37 and 38 (and preceding) in the OGC WCS spec. (ref:
                    07-067r5_Web_Coverage_Service_WCS_version_1.1_Corrigendum_2.pdf)

                    For the purpose of extracting images, this module assumes
                    that the two values encoded in <gml:high></gml:high> element
                    represent the expected width/height of the image.

                    It is not known at present how to extract reasonable values
                    for the spatial resolution (resX and resY).

                    Time limits are also quite "fiddly" and still need to be
                    addressed.

                    """

                    """
                    print "wcs.py:233 coverage\n",selected_coverageName
                    print "wcs.py:236 grid info:", grid.dimension, \
                            type(grid.dimension), grid.axislabels, \
                            grid.highlimits, grid.lowlimits
                    print "wcs.py:239 timelimits:", \
                        self.contents[str(selected_coverageName)].timelimits
                    print "wcs.py:240 timepositions:", \
                        self.contents[str(selected_coverageName)].timepositions
                    """

                    self.dcLayerId.setText(self.contents[str(selected_coverageName)].id)
                    self.dcLayerDescription.setText(self.contents[str(selected_coverageName)].title)
                    self.dcULX.setText(str(self.contents[str(selected_coverageName)].boundingBoxWGS84[0])) # 1st item in bbox tuple
                    self.dcLRX.setText(str(self.contents[str(selected_coverageName)].boundingBoxWGS84[1]))
                    self.dcULY.setText(str(self.contents[str(selected_coverageName)].boundingBoxWGS84[2]))
                    self.dcLRY.setText(str(self.contents[str(selected_coverageName)].boundingBoxWGS84[3]))
                    self.dcSRS.setText(self.contents[str(selected_coverageName)].supportedCRS[0])
                    #self.dcSRSreq.addItems(self.contents[str(selected_coverageName)].supportedCRS)  # spectral bands
                    self.dcSRSreq.addItems(self.contents[str(selected_coverageName)].supportedCRS)
                    self.dcReqFormat.addItems(self.contents[str(selected_coverageName)].supportedFormats) # returns a list of values that are unpacked into a combobo
                    #print self.contents [str(selected_coverageName)].supportedFormats# .__dict__['_service'].__dict__['contents']['sf:sfdem'].__dict__['_elem']#.supportedFormats

        #display spatial subset in WCS window and set warning if data out of bounds
        self.ssULX.setText(str(self.spatial_widget.bbox_tlx.text()))
        self.ssULY.setText(str(self.spatial_widget.bbox_tly.text()))
        self.ssLRX.setText(str(self.spatial_widget.bbox_brx.text()))
        self.ssLRY.setText(str(self.spatial_widget.bbox_bry.text()))

        #call to check spatial subset coordinates:
        #   see SpatialTemporalConfigurationWidget for checkCoords()
        message = self.spatial_widget.checkCoords(self.getBoundingBoxLayer())
        if message:
            self.showWarning(message)

    def getBoundingBoxLayer(self):
        """Return a tuple containing box co-ordinates for selected layer.
        Format: top-left X, top-left Y, bottom-left X, bottom-left Y

        """
        return (
            self.dcULX.text(),
            self.dcULY.text(),
            self.dcLRX.text(),
            self.dcLRY.text()
            )

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
        width = str(self.wcs_config_widget.dcWidth.text())
        height = str(self.wcs_config_widget.dcHeight.text())
        data = ''

        # check for data in comboBoxes
        try:
            bands = self.wcs_config_widget.dcBandsreq.currentText()
        except:
            bands = None
        try:
            coord_system = self.wcs_config_widget.dcSRSreq.currentText()
        except:
            coord_system = None
        try:
            formats =  self.wcs_config_widget.dcReqFormat.currentText()
        except:
            formats = None
        try:
            spatial_limit = self.wcs_config_widget.cbSpatial.currentText()
        except:
            spatial_limit = None

        # spatial
        if spatial_limit:  # spatial parameters
            if spatial_limit == self.wcs_config_widget.SPATIAL_OWN:
                # see SpatialTemporalConfigurationWidget
                self.bbox = self.spatial_widget.getBoundingBoxString()
            elif spatial_limit == self.wcs_config_widget.SPATIAL_OFFERING:
                # see WcsCommonWidget (this module)
                self.bbox = self.wcs_config_widget.getBoundingBoxStringCoverage()
            else:
                traceback.print_exc()
                raise ModuleError(
                    self,
                    'Unknown WCS bounding box type' + ': %s' % str(error)
                    )
        else:
            self.bbox = None

        # details per request type:
        rType = self.wcs_config_widget.dcRequestType.currentText()
        if rType == 'DescribeCoverage':
            """was trying to get the contents of getDescribeCoverage to display
            in xml format on the terminal, but that does not working becasue
            getDescribeCoverage only returns an element tree object not the
            actual xml - see the printed result on the terminal -
            therefore we can only get a url out of this request see code below -
            I stand to be corrected if my research findings are wrong?

            NOTE BY DEREK:
            A URL is actually all we want to get - this is the configuration
            part of the workflow - once it is executed then the XML data will be
            created and it is then up to "downstream" components connected to
            this one to handle the XML.
            """
            myWCS = self.wcs_config_widget.parent_widget.service.service
            description = myWCS.getDescribeCoverage(selectedCoverageId)
            #describe_doc= description.read()
            #print "wcs.py:361", description

            wcs_url += \
            "?SERVICE=WCS" + \
            "&version=" + WCSversion + \
            "&request=DescribeCoverage" + \
            "&COVERAGE=" + selectedCoverageId
            return 'GET', wcs_url

        elif rType == 'GetCoverage':
            myWCS = self.wcs_config_widget.parent_widget.service.service
            response = myWCS.getCoverage(
                identifier=selectedCoverageId,
                bbox=self.bbox,
                crs= coord_system,
                format=formats)
            # TO DO - update this to handle files as per VisTrails "filePool"
            # http://www.vistrails.org/index.php/UsersGuideVisTrailsPackages#Dealing_with_command_line_tools_and_side_effects
            # derek->bolelang -- so why do we want to do this???
            f=open('myfile.'+ formats,  'wb')
            f.write(response.read())
            f.close()

            wcs_url += \
                "?SERVICE=WCS" + \
                "&version=" + WCSversion + \
                "&request=GetCoverage" + \
                "&COVERAGE=" + selectedCoverageId
            if self.bbox:
                # OLD CODE: "&bbox=" + ULX + "," + ULY + "," + BRX + "," + BRY + \
                #print "wcs.py:450 bbox=", self.bbox
                wcs_url += "&bbox=" + self.bbox + \
                    "&crs=" + coord_system
            wcs_url += \
                "&format=" + formats + \
                "&width=" + width + \
                "&height=" + height
                #"&resx=10&resy=10"
                #TO DO -- allow user to specify resX and resY or height/width
            return 'GET', wcs_url

        else:
            raise ModuleError(
                self,
                'Unknown WCS request type' + ': %s' % str(rType)
                )
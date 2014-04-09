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
"""This module provides an OGC (Open Geospatial Consortium) Web Feature Service
(WFS) Client via owslib.
"""

# library
# third party
from PyQt4 import QtCore, QtGui
# vistrails
from gui.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.vistrails_module import Module, ModuleError, \
                                          new_module, NotCacheable
# eo4vistrails
from vistrails.packages.eo4vistrails.geoinf.SpatialTemporalConfigurationWidget import \
    SpatialTemporalConfigurationWidget, SpatialWidget
# local
from OgcConfigurationWidget import OgcConfigurationWidget
from OgcService import OGC
import init


class WFS(OGC, Module):
    """Override for base OGC service class.
    """

    def __init__(self):
        Module.__init__(self)
        OGC.__init__(self)
        self.webRequest._driver = 'WFS'


class WFSCommonWidget(QtGui.QWidget):
    """The WFS module allows connection to a web-based OGC 
    (Open Geospatial Consortium) web feature service.
    
    Configuration allows the base URL for the service to be set and called.
    Choosing the appropriate combination of specific service type and other
    parameters, will cause the input port to be set with a specific POST call,
    once the configuration interface is closed.
    
    Running the WFS will cause the specific, parameterised WFS to be called
    and output from the request to be available via the output port(s).
    """

    def __init__(self, ogc_widget, spatial_widget, parent=None):
        """Sets parameters for wcs request"""
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("WFSCommonWidget")
        self.parent_widget = ogc_widget
        #self.service = self.parent_widget.service
        self.contents = None #  only set in self.loadRequests()
        self.spatial_widget = spatial_widget
        self.create_wfs_config_window()

        # listen for signals emitted by OgcCommonWidget class
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceActivated'),
            self.loadRequests)
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceDeactivated'),
            self.removeRequests)

    def create_wfs_config_window(self):
        """Create datacontainers and layout for displaying WFS-related data."""
        # text for combo boxes
        self.SPATIAL_OFFERING = 'Use Feature Bounding Box'
        self.SPATIAL_OWN = 'Use Own Bounding Box'
        # add widgets here!
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.requestsGroupBox = QtGui.QGroupBox("WFS Request Features")
        self.requestsLayout = QtGui.QVBoxLayout()
        self.requestsGroupBox.setLayout(self.requestsLayout)
        self.mainLayout.addWidget(self.requestsGroupBox)
        # add a horizontal split to split the window equally
        self.split = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.mainLayout.addWidget(self.split)
        self.detailsGroupBox = QtGui.QGroupBox("WFS Feature Details")
        self.mainLayout.addWidget(self.detailsGroupBox)
        self.detailsLayout = QtGui.QGridLayout()
        self.detailsGroupBox.setLayout(self.detailsLayout)
        # WFS Request offerings layout
        self.requestLbx = QtGui.QListWidget()
        self.requestsLayout.addWidget(self.requestLbx)

        # WFS Request details layout
        # Labels
        self.detailsLayout.addWidget(QtGui.QLabel('Feature ID'), 0, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Feature Description'), 1, 0)

        self.detailsLayout.addWidget(QtGui.QLabel('BBox - Data Bounds:'), 2, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('ULX:'), 3, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('LRX:'), 3, 2)
        self.detailsLayout.addWidget(QtGui.QLabel('ULY:'), 4, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('LRY:'), 4, 2)

        self.detailsLayout.addWidget(QtGui.QLabel('BBox - Spatial Subset:'), 5, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('ULX:'), 6, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('LRX:'), 6, 2)
        self.detailsLayout.addWidget(QtGui.QLabel('ULY:'), 7, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('LRY:'), 7, 2)

        self.detailsLayout.addWidget(QtGui.QLabel('Spatial Reference System'), 8, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Maximum Features'), 9, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Output SRS'), 10, 0)

        self.dcRequestFormatLabel = QtGui.QLabel('Required Request Format')
        self.detailsLayout.addWidget(self.dcRequestFormatLabel, 11, 0)
        self.dcRequestFormatLabel.setVisible(False)  # not in use for WFS
        self.detailsLayout.addWidget(QtGui.QLabel('Spatial Delimiter?'), 12, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Required Request'), 13, 0)

        # Data containers
        self.dcLayerId = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcLayerId, 0, 1)
        self.dcLayerDescription = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcLayerDescription, 1, 1)

        #Bounding box - Grid Envelope
        self.dcULX = QtGui.QLineEdit(' ')
        self.dcULX.setEnabled(False) #sets it not to be editable
        self.detailsLayout.addWidget(self.dcULX, 3, 1)
        self.dcLRX = QtGui.QLineEdit(' ')
        self.dcLRX.setEnabled(False)
        self.detailsLayout.addWidget(self.dcLRX, 3, 3)
        self.dcULY = QtGui.QLineEdit(' ')
        self.dcULY.setEnabled(False)
        self.detailsLayout.addWidget(self.dcULY, 4, 1)
        self.dcLRY = QtGui.QLineEdit(' ')
        self.dcLRY.setEnabled(False)
        self.detailsLayout.addWidget(self.dcLRY, 4, 3)

        #Bounding Box Spatial subset
        self.ssULX = QtGui.QLabel(' ')
        #self.ssULX.setEnabled(False) #sets it not to be editable
        self.detailsLayout.addWidget(self.ssULX, 6, 1)
        self.ssLRX = QtGui.QLabel(' ')
        #self.ssLRX.setEnabled(False)
        self.detailsLayout.addWidget(self.ssLRX, 6, 3)
        self.ssULY = QtGui.QLabel(' ')
        #self.ssULY.setEnabled(False)
        self.detailsLayout.addWidget(self.ssULY, 7, 1)
        self.ssLRY = QtGui.QLabel(' ')
        #self.ssLRY.setEnabled(False)
        self.detailsLayout.addWidget(self.ssLRY, 7, 3)

        self.dcSRS = QtGui.QLabel('__')
        self.detailsLayout.addWidget(self.dcSRS, 8, 1)
        self.dcMaxFeatures = QtGui.QSpinBox()
        self.detailsLayout.addWidget(self.dcMaxFeatures, 9, 1)
        self.dcSRSreq = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcSRSreq, 10, 1)
        self.dcReqFormat = QtGui.QComboBox()
        self.dcReqFormat.setVisible(False)  # not in use for WFS
        self.detailsLayout.addWidget(self.dcReqFormat, 11, 1)

        self.cbSpatial = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbSpatial, 12, 1)
        self.cbSpatial.addItem(self.SPATIAL_OFFERING)
        self.cbSpatial.addItem(self.SPATIAL_OWN)
        self.cbSpatial.addItem('')

        self.dcRequestType = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.dcRequestType, 13, 1)
        self.dcRequestType.addItem('GetFeature')
        self.dcRequestType.addItem('DescribeFeatureType')

        # local signals
        self.connect(
            self.requestLbx,
            QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),
            self.featureNameChanged)

        #for message box
        self.arrowCursor = QtGui.QCursor(QtCore.Qt.ArrowCursor)

    def getBoundingBoxStringFeature(self):
        """Return a comma-delimited string containing box co-ordinates.

        :rtype:
            top-left X, top-left Y  bottom-right X, bottom-right Y
        """
        bbox = self.spatial_widget.getBoundingBox()
        return str(self.dcULX.text()) + ',' + str(self.dcLRX.text()) + ','\
            + str(self.dcULY.text()) + ',' + str(self.dcLRY.text())

    def getBoundingBoxFeature(self):
        """Return a tuple containing box co-ordinates for selected feature.

        :rtype:
            (top-left X, top-left Y, bottom-right X, bottom-right Y)
        """
        return (
            self.dcULX.text(),
            self.dcULY.text(),
            self.dcLRX.text(),
            self.dcLRY.text())

    def removeRequests(self):
        """Remove all details when no WFS is selected."""
        self.clearRequests()
        self.requestLbx.clear()

    def clearRequests(self):
        """To reset the values in the fields"""
        self.dcLayerId.setText('-')
        self.dcLayerDescription.setText('-')
        self.dcULX.setText('')
        self.dcLRX.setText('')
        self.dcULY.setText('')
        self.dcLRY.setText('')
        self.dcSRS.setText('')
        self.dcSRSreq.clear()
        self.dcReqFormat.clear()
        self.dcMaxFeatures.clear()
        self.dcMaxFeatures.setValue(10)
        #self.dcRequestType.clear()

    def featureNameChanged(self):
        """Update offering details containers when new offering selected."""
        self.clearRequests()
        #populate other feature dependent parameters
        selected_featureName = self.requestLbx.selectedItems()[0].text()
        if self.parent_widget.service and self.parent_widget.service.service_valid and self.contents:
            for content in self.contents:
                if selected_featureName == content:
                    _feat = self.contents[str(selected_featureName)]
                    self.dcLayerId.setText(_feat.id)
                    if _feat.title:
                        self.dcLayerDescription.setText(_feat.title)
                    if _feat.boundingBoxWGS84:
                        self.dcULX.setText(str(_feat.boundingBoxWGS84[0])) # 1st item in bbox tuple
                        self.dcLRX.setText(str(_feat.boundingBoxWGS84[1]))
                        self.dcULY.setText(str(_feat.boundingBoxWGS84[2]))
                        self.dcLRY.setText(str(_feat.boundingBoxWGS84[3]))
                    if _feat.crsOptions:
                        self.dcSRS.setText(_feat.crsOptions[0])
                        self.dcSRSreq.addItems(_feat.crsOptions)
                    #self.dcReqFormat.addItems(self.contents[str(selected_featureName)].supportedFormats) # returns a list of values that are unpacked into a combobo
                    #print self.contents [str(selected_featureName)].supportedFormats# .__dict__['_service'].__dict__['contents']['sf:sfdem'].__dict__['_elem']#.supportedFormats

        #display spatial subset in WFS window and set warning if data out of bounds
        self.ssULX.setText(str(self.spatial_widget.bbox_tlx.text()))
        self.ssULY.setText(str(self.spatial_widget.bbox_tly.text()))
        self.ssLRX.setText(str(self.spatial_widget.bbox_brx.text()))
        self.ssLRY.setText(str(self.spatial_widget.bbox_bry.text()))

        #call to check spatial subset coordinates:
        #   see SpatialTemporalConfigurationWidget for checkCoords()
        message = self.spatial_widget.checkCoords(self.getBoundingBoxFeature())
        if message:
            self.showWarning(message)

    def showWarning(self, message):
        """Show user a warning dialog."""
        self.setCursor(self.arrowCursor)
        QtGui.QMessageBox.warning(self, "Error", message, QtGui.QMessageBox.Ok)

    def loadRequests(self):
        """ loadRequest() -> None
        uses service data to populate the config widget populate fields
        """
        if self.parent_widget.service and self.parent_widget.service.service_valid:
            self.contents = self.parent_widget.service.service.__dict__['contents']
            for content in self.contents:
                self.requestLbx.addItems([content])
            self.requestLbx.sortItems()  # for better display of long lists...


class WFSConfigurationWidget(OgcConfigurationWidget,
                             StandardModuleConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""

    def __init__(self, module, controller, parent=None):
        # inherit parent module > access Module methods in core/vistrail/module.py
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)
        OgcConfigurationWidget.__init__(self, module, controller, parent)
        # pass in parent widget i.e. OgcCommonWidget & SpatialWidget to read changed coords
        self.config = WFSCommonWidget(self.ogc_common_widget, self.spatial_widget)

        # map widgets to ports to enable storing of their settings
        port_widget = {
            init.OGC_URL_PORT: self.config.parent_widget.line_edit_OGC_url
        }
        # get and set corresponding port value for a configuration widget
        #  "functions" are VisTrails internal representation of ports at design time
        for function in self.module.functions:
            if function.name in port_widget:
                #print "WFS:308", function.name, function.params[0].strValue
                port_widget[function.name].setText(function.params[0].strValue)

        # move parent tab to first place
        self.tabs.insertTab(1, self.config, "")
        # set WFS-specific tabs
        self.tabs.setTabText(
            self.tabs.indexOf(self.config),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "WFS Specific Metadata",
                None,
                QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.config),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "Select WFS-specific parameters",
                None,
                QtGui.QApplication.UnicodeUTF8))
        self.tabs.setCurrentIndex(0)

    def constructRequest(self, URL):
        """Returns request details from configuration parameters.
        
        .. note::
            Overwrites method defined in OgcConfigurationWidget.
        """
        result = {}
        wfs_url = URL
        WFSversion = str(self.ogc_common_widget.launchversion.currentText())
        selectedFeatureId = str(self.config.dcLayerId.text())
        data = ''
        # check for data in comboBoxes
        try:
            coord_system = self.config.dcSRSreq.currentText()
        except:
            coord_system = None
        try:
            formats = self.config.dcReqFormat.currentText()
        except:
            formats = None
        try:
            spatial_limit = self.config.cbSpatial.currentText()
        except:
            spatial_limit = None
        try:
            feature_limit = self.config.dcMaxFeatures.value()
        except:
            feature_limit = 0

        # details per request type:
        rType = self.config.dcRequestType.currentText()
        if rType == 'DescribeFeatureType':
            wfs_url += \
            "?service=WFS" + \
            "&version=" + WFSversion + \
            "&request=DescribeFeatureType" + \
            "&typename=" + selectedFeatureId
            #print "WFS:343 -return URL for DescribeFeatureType", wfs_url
            result['request_type'] = 'GET'
            result['full_url'] = wfs_url

        elif rType == 'GetFeature':
            wfs_url += \
            "?service=WFS" + \
            "&version=" + WFSversion + \
            "&request=GetFeature" + \
            "&typename=" + selectedFeatureId
            if feature_limit:
                wfs_url += '&maxFeatures=%s' % feature_limit
            if spatial_limit:  # spatial parameters
                if spatial_limit == self.config.SPATIAL_OWN:
                    # see SpatialTemporalConfigurationWidget
                    bbox = self.getBoundingBoxString()
                elif spatial_limit == self.config.SPATIAL_OFFERING:
                    # see WfsCommonWidget (this module)
                    bbox = self.config.getBoundingBoxStringFeature()
                else:
                    # FIXME no exception here...
                    traceback.print_exc()
                    raise ModuleError(
                        self,
                        'Unknown WFS bounding box type' + ': %s' % str(error))
                #print "WFS:392 -return URL for GetFeature", wfs_url
                if bbox:
                    # coord should yield EPSG:nnnn
                    wfs_url += "&bbox=" + bbox + "," + coord_system
            result['request_type'] = 'GET'
            result['full_url'] = wfs_url

        else:
            raise ModuleError(
                self,
                'Unknown WFS request type' + ': %s' % str(rType))

        result['layername'] = selectedFeatureId
        return result

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
"""This module provides an OGC (Open Geospatial Consortium) Sensor Observation
Service (SOS) client, making use of a local version of the owslib library.
"""

# library
import pickle
import traceback
# third party
from PyQt4 import QtCore, QtGui
#from qgis.core import *
#from qgis.gui import *
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from packages.eo4vistrails.utils.ModuleHelperMixin import ModuleHelperMixin
from packages.eo4vistrails.utils.widget_configuration import \
    ExtendedModuleConfigurationWidget
# local
from OgcConfigurationWidget import OgcConfigurationWidget
from OgcService import OGC
#names of ports as constants
import init


class SOS(OGC, FeatureModel):
    """Override for base OGC service class

    """

    def __init__(self):
        OGC.__init__(self)
        FeatureModel.__init__(self)
        self.webRequest._driver = 'ogr'


class SosCommonWidget(QtGui.QWidget):
    """SOS-specific parameters can be obtained, displayed and selected."""

    def __init__(self, module, ogc_widget, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("SosCommonWidget")
        self.module = module
        self.parent_widget = ogc_widget
        self.contents = None  # only set in self.loadOfferings()
        self.create_config_window()

        # listen for signals emitted by OgcCommonWidget class
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceActivated'),
            self.loadOfferings)
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceDeactivated'),
            self.removeOfferings)

    def create_config_window(self):
        """Create datacontainers and layout for displaying SOS-related data."""
        self.setWindowTitle("SOS Configuration Widget")
        self.setMinimumSize(900, 700)
        # text for combo boxes
        self.SPATIAL_OFFERING = 'Use Offering Bounding Box'
        self.SPATIAL_OWN = 'Use Own Bounding Box'
        self.TIME_OFFERING = 'Use Offering Time Period'
        self.TIME_OWN = 'Use Own Time Period'
        # main layout
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.offeringsGroupBox = QtGui.QGroupBox("Offerings")
        self.offeringsLayout = QtGui.QVBoxLayout()
        self.offeringsGroupBox.setLayout(self.offeringsLayout)
        self.mainLayout.addWidget(self.offeringsGroupBox)
        self.split = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.mainLayout.addWidget(self.split)
        self.detailsGroupBox = QtGui.QGroupBox("Offering Details")
        self.mainLayout.addWidget(self.detailsGroupBox)
        self.detailsLayout = QtGui.QGridLayout()
        self.detailsGroupBox.setLayout(self.detailsLayout)
        # offerings
        self.lbxOfferings = QtGui.QListWidget()
        self.offeringsLayout.addWidget(self.lbxOfferings)

        # Offering details layout
        #   labels
        self.detailsLayout.addWidget(QtGui.QLabel('Description'), 0, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Bounding Box'), 1, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Time'), 2, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Procedure'), 3, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Response Format'), 4, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Response Mode'), 5, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Result Model'), 6, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Observed Property'), 7, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Feature of Interest'), 8, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Time Limit?'), 9, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Spatial Delimiter?'), 10, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Request Type'), 11, 0)

        #   data containers
        self.lblDescription = QtGui.QLabel('-')
        self.detailsLayout.addWidget(self.lblDescription, 0, 1)

        self.boundingGroupBox = QtGui.QGroupBox("")
        self.boundingLayout = QtGui.QVBoxLayout()
        self.boundingGroupBox.setLayout(self.boundingLayout)
        self.detailsLayout.addWidget(self.boundingGroupBox, 1, 1)

        self.minGroupBox = QtGui.QGroupBox("")
        self.minLayout = QtGui.QHBoxLayout()
        self.minGroupBox.setLayout(self.minLayout)
        self.boundingLayout.addWidget(self.minGroupBox)
        self.minLayout.addWidget(QtGui.QLabel('Top Left X:'))
        self.lblTL_X = QtGui.QLabel('-')
        self.minLayout.addWidget(self.lblTL_X)
        self.minLayout.addWidget(QtGui.QLabel('Top Left Y:'))
        self.lblTL_Y = QtGui.QLabel('-')
        self.minLayout.addWidget(self.lblTL_Y)

        self.maxGroupBox = QtGui.QGroupBox("")
        self.maxGroupBox.setFlat(True)
        self.maxLayout = QtGui.QHBoxLayout()
        self.maxGroupBox.setLayout(self.maxLayout)
        self.boundingLayout.addWidget(self.maxGroupBox)
        self.maxLayout.addWidget(QtGui.QLabel('Bottom Right X:'))
        self.lblBR_X = QtGui.QLabel('-')
        self.maxLayout.addWidget(self.lblBR_X)
        self.maxLayout.addWidget(QtGui.QLabel('Bottom Right Y:'))
        self.lblBR_Y = QtGui.QLabel('-')
        self.maxLayout.addWidget(self.lblBR_Y)

        self.srsGroupBox = QtGui.QGroupBox("")
        self.srsGroupBox.setFlat(True)
        self.srsLayout = QtGui.QHBoxLayout()
        self.srsGroupBox.setLayout(self.srsLayout)
        self.boundingLayout.addWidget(self.srsGroupBox)
        self.srsLayout.addWidget(QtGui.QLabel('SRS:'))
        self.lblSRS = QtGui.QLabel('-')
        self.srsLayout.addWidget(self.lblSRS)

        self.boundingLayout.addStretch()  # force items upwards -doesnt work??

        self.timeGroupBox = QtGui.QGroupBox("")
        self.timeGroupBox.setFlat(True)
        self.timeLayout = QtGui.QVBoxLayout()
        self.timeGroupBox.setLayout(self.timeLayout)
        self.detailsLayout.addWidget(self.timeGroupBox, 2, 1)
        self.lblStartTime = QtGui.QLabel('-')
        self.timeLayout.addWidget(self.lblStartTime)
        self.timeLayout.addWidget(QtGui.QLabel('to:'))
        self.lblEndTime = QtGui.QLabel('-')
        self.timeLayout.addWidget(self.lblEndTime)

        self.cbProcedure = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbProcedure, 3, 1)
        self.cbResponseFormat = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbResponseFormat, 4, 1)
        self.cbResponseMode = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbResponseMode, 5, 1)
        self.cbResultModel = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbResultModel, 6, 1)
        self.lbObservedProperty = QtGui.QListWidget()
        self.lbObservedProperty.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.detailsLayout.addWidget(self.lbObservedProperty, 7, 1)
        self.cbFOI = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbFOI, 8, 1)

        self.cbTime = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbTime, 9, 1)
        self.cbTime.addItem('')
        self.cbTime.addItem(self.TIME_OFFERING)
        self.cbTime.addItem(self.TIME_OWN)

        self.cbSpatial = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbSpatial, 10, 1)
        self.cbSpatial.addItem('')
        self.cbSpatial.addItem(self.SPATIAL_OFFERING)
        self.cbSpatial.addItem(self.SPATIAL_OWN)

        self.cbRequest = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbRequest, 11, 1)

        # local signals
        self.connect(
            self.lbxOfferings,
            QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),
            self.offeringsChanged)

    def getBoundingBoxOffering(self):
        """Return a tuple containing box co-ordinates.

        Format: top-left X, top-left Y, bottom-left X, bottom-left Y
        """
        return (
            self.lblTL_X.text(),
            self.lblTL_Y.text(),
            self.lblBR_X.text(),
            self.lblBR_Y.text())

    def getTimeIntervalOffering(self):
        """Return a tuple containing start / end in universal time."""
        return (
            self.lblStartTime.text(),
            self.lblEndTime.text(),)

    def restoreConfiguration(self, configuration):
        """Restore all configuration choices previously made.

        NB: These are saved as a dictionary (but in string format) on an
            input port of the module.
        """

        def set_cbox(box, text):
            """Set index for PyQT4 combo box, based on text."""
            try:
                i = box.findText(text)
                if i >= 0:
                    box.setCurrentIndex(i)
                return True
            except:
                return False  # sorry, no.

        def set_lbox(box, text):
            """FIXME!"""
            """Set index for PyQT4 list box, based on text."""
            items = box.findItems(text) #TypeError: QListWidget.findItems(QString, Qt.MatchFlags): not enough arguments

            item = items[0]
            box.setCurrentItem(item)
            return True
            try:
                items = box.findItems(text)
                item = items[0]
                box.setCurrentItem(item)
                return True
            except:
                return False  # sorry, no.

        try:
            config = eval(configuration)
        except:
            config = None

        if config and isinstance(config, dict):
            pass
            """
            # not done yet
            #self.lblTL_X.setText('-')
            #self.lblTL_Y.setText('-')
            #self.lblBR_X.setText('-')
            #self.lblBR_Y.setText('-')
            # self.lblSRS.setText('-') ???

            # must call this first
            if set_lbox(self.lbxOfferings, 'offering'):
                self.offeringsChanged()

            tr = config.get('time_range') or (None, None)
            if tr[0]:
                self.lblStartTime.setText(tr[0])
            if tr[1]:
                self.lblEndTime.setText(tr[1])

            set_cbox(self.cbProcedure, 'pocedure')

            # other cboxs - need to do still
            self.cbRequest.clear()
            self.cbResponseFormat.clear()
            self.cbResponseMode.clear()
            self.cbResultModel.clear()
            self.lbObservedProperty.clear()
            self.cbFOI.clear()
            self.cbTime
            """

    def removeOfferings(self):
        """Remove all offering details when no SOS is selected."""
        self.clearOfferings()
        self.lbxOfferings.clear()

    def clearOfferings(self):
        """Reset all displayed offering and request values."""
        self.lblDescription.setText('-')
        self.lblTL_X.setText('-')
        self.lblTL_Y.setText('-')
        self.lblBR_X.setText('-')
        self.lblBR_Y.setText('-')
        self.lblSRS.setText('-')
        self.lblStartTime.setText('-')
        self.lblEndTime.setText('-')
        self.cbProcedure.clear()
        self.cbRequest.clear()
        self.cbResponseFormat.clear()
        self.cbResponseMode.clear()
        self.cbResultModel.clear()
        self.lbObservedProperty.clear()
        self.cbFOI.clear()
        #self.cbTime.clear()
        #self.cbSpatial.clear()

    def offeringsChanged(self):
        """Update offering details containers when new offering selected."""
        self.clearOfferings()
        selected_offering = self.lbxOfferings.selectedItems()[0].text()
        if self.parent_widget.service and \
            self.parent_widget.service.service_valid and self.contents:
            for content in self.contents:
                if selected_offering == content.id:
                    # description
                    if content.description:
                        self.lblDescription.setText(content.description)
                    elif content.name:
                        self.lblDescription.setText(content.name)
                    else:
                        self.lblDescription.setText(content.id)
                    # service operations
                    for service in self.parent_widget.service.service_operations:
                        self.cbRequest.addItem(service)
                    # update other offering details...
                    if content.time:
                        self.lblStartTime.setText(str(content.time[0]))
                        self.lblEndTime.setText(str(content.time[1]))
                    if content.bounding_box:
                        self.lblTL_X.setText(str(content.bounding_box[0]))
                        self.lblTL_Y.setText(str(content.bounding_box[1]))
                        self.lblBR_X.setText(str(content.bounding_box[2]))
                        self.lblBR_Y.setText(str(content.bounding_box[3]))
                        self.lblSRS.setText(str(content.bounding_box[4]))
                    self.cbProcedure.addItem('')
                    if content.procedure:
                        for pr in content.procedure:
                            self.cbProcedure.addItem(pr)
                    self.cbResponseFormat.addItem('')
                    if content.response_format:
                        for rf in content.response_format:
                            self.cbResponseFormat.addItem(rf)
                    self.cbResponseMode.addItem('')
                    if content.response_mode:
                        for rm in content.response_mode:
                            self.cbResponseMode.addItem(rm)
                    self.cbResultModel.addItem('')
                    if content.result_model:
                        for rd in content.result_model:
                            self.cbResultModel.addItem(rd)
                    if content.observed_property:
                        for op in content.observed_property:
                            self.lbObservedProperty.addItem(op)
                    self.cbFOI.addItem('')
                    if content.feature_of_interest:
                        for foi in content.feature_of_interest:
                            self.cbFOI.addItem(foi)

    def loadOfferings(self):
        """Load the offerings from the service metadata."""
        if self.parent_widget.service and self.parent_widget.service.service_valid:
            self.removeOfferings()  # clear current data
            self.contents = self.parent_widget.service.service.__dict__['contents']
            #print "SOS self.contents", self.contents
            for content in self.contents:
                item = QtGui.QListWidgetItem(content.id)
                self.lbxOfferings.addItem(item)


class SOSConfigurationWidget(OgcConfigurationWidget,
                             ExtendedModuleConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""

    def __init__(self, module, controller, parent=None):
        # inherit parent module > access Module methods in core/vistrail/module.py
        ExtendedModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)
        OgcConfigurationWidget.__init__(self, module, controller, parent)
        # pass in parent widget i.e. OgcCommonWidget class
        self.config = SosCommonWidget(self.module, self.ogc_common_widget)

        # retrieve values from input ports (created in OgcConfigurationWidget)
        self.config.parent_widget.capabilities = self.getPortValue(init.OGC_CAPABILITIES_PORT)
        self.configuration = self.getPortValue(init.CONFIGURATION_PORT)
        self.config.parent_widget.line_edit_OGC_url.setText(
            self.getPortValue(init.OGC_URL_PORT))

        #restore existing capabilities & configuration
        if self.config.parent_widget.capabilities:
            self.config.parent_widget.load_capabilities()
            self.config.restoreConfiguration(self.configuration)

        # move parent tab to first place
        self.tabs.insertTab(1, self.config, "")
        # set SOS-specific tabs
        self.tabs.setTabText(
            self.tabs.indexOf(self.config),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "SOS Specific Metadata",
                None,
                QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.config),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "Select SOS-specific parameters",
                None,
                QtGui.QApplication.UnicodeUTF8))
        self.tabs.setCurrentIndex(0)

    def get_valid_srs(self, srsURN):
        """Return a valid EPSG srsName according to OGC 09-048r3

        Accepts:
          * valid srs string in URN form (delimited by :)

        Returns:
          * valid EPSG srsName string, or default of EPSG 4326 if not found

        Notes:
          * Replace with http://owslib.sourceforge.net/#crs-handling  ???
        """
        srs = None
        try:
            srs_items = srsURN.split(':')
            code = srs_items[len(srs_items) - 1]
            #print "SOS:427", srs_items, code
            if code and int(code) > 0:
                return 'urn:ogc:def:crs:EPSG::' + code  # omit any version no.
            else:
                return 'urn:ogc:def:crs:EPSG::4326'
        except:
            self.raiseError(self, 'Unable to construct valid srsName from %s'\
                            % srsURN)
        return srs

    def constructRequest(self, URL):
        """Return an XML-encoded request from configuration parameters

        Overwrites method defined in OgcConfigurationWidget.
        """
        result = {}
        sos_url = URL
        data = ''
        rType = self.config.cbRequest.currentText()
        try:
            procedure = self.config.cbProcedure.currentText()
        except:
            procedure = None
        try:
            format = self.config.cbResponseFormat.currentText()
        except:
            format = None
        try:
            mode = self.config.cbResponseMode.currentText()
        except:
            mode = None
        try:
            model = self.config.cbResultModel.currentText()
        except:
            model = None

        obs_prop = []
        for item in self.config.lbObservedProperty.selectedItems():
            obs_prop.append(item.text())
        #print "sos:456", obs_prop

        try:
            foi = self.config.cbFOI.currentText()
        except:
            foi = None
        try:
            offering = self.config.lbxOfferings.currentItem().text()
        except:
            offering = None
        try:
            time_limit = self.config.cbTime.currentText()
        except:
            time_limit = None
        try:
            spatial_limit = self.config.cbSpatial.currentText()
        except:
            spatial_limit = None

        # primary parameters
        WARNING_MUST = '%s must be chosen for a "%s" request.'
        WARNING_NOT = '%s must NOT be chosen for a "%s" request.'
        WARNING_CHOICE = 'Either %s or %s must be chosen for a "%s" request.'
        WARNING_ONLY_ONE = 'Cannot select both %s and %s for a "%s" request.'
        # default (null) values for configuration storage
        time_range = (None, None)
        # process by request type
        if rType == 'DescribeSensor':
            if procedure:
                data += '<procedure>' + procedure + '</procedure>\n'
            else:
                self.showWarning(WARNING_MUST % ('Procedure', rType))
                return result

        elif rType == 'GetFeatureOfInterest':
            if not(foi) and not(spatial_limit):
                self.showWarning(WARNING_CHOICE %
                    ('Spatial Limit', 'Feature of Interest', rType))
                return None, None
            if spatial_limit and foi:
                self.showWarning(WARNING_ONLY_ONE %
                    ('Spatial Limit', 'Feature of Interest', rType))
                return None, None
            if foi:
                data += '<FeatureOfInterestId>' + \
                       foi + \
                       '</FeatureOfInterestId>\n'
            if spatial_limit:  # spatial parameters
                if spatial_limit == self.config.SPATIAL_OWN:
                    # see SpatialTemporalConfigurationWidget
                    bbox = self.getBoundingBox()
                elif spatial_limit == self.config.SPATIAL_OFFERING:
                    # see SosCommonWidget (this module)
                    bbox = self.config.getBoundingBoxOffering()
                data += '<location>\n <ogc:BBOX>\n' + \
                    '  <ogc:PropertyName>urn:ogc:data:location</ogc:PropertyName>\n'
                srsName = self.get_valid_srs(self.config.lblSRS.text())
                if srsName:
                    data += '    <gml:Envelope srsName="' + srsName + '">\n'
                else:
                    data += '    <gml:Envelope>\n'
                data += \
                    '   <gml:lowerCorner>' + bbox[2] + ' ' + bbox[3] + \
                    '</gml:lowerCorner>\n' + \
                    '   <gml:upperCorner>' + bbox[0] + ' ' + bbox[1] + \
                    '</gml:upperCorner>\n' + \
                    '  </gml:Envelope>\n' + ' </ogc:BBOX>\n</location>\n'

        elif rType == 'GetObservation':
            if offering:
                data += '<offering>' + offering + '</offering>\n'
            else:
                self.showWarning(WARNING_MUST % ('Offering', rType))
                return None, None
            if time_limit:  # time params
                if time_limit == self.config.TIME_OWN:
                    # see SpatialTemporalConfigurationWidget
                    time_range = self.getTimeInterval()
                elif time_limit == self.config.TIME_OFFERING:
                    # see SpatialTemporalConfigurationWidget
                    time_range = self.config.getTimeIntervalOffering()
                # FIXME this code causes errors with ARC SOS ???
                data += '<eventTime>\n <ogc:TM_During>\n' + \
                    '  <ogc:PropertyName>om:samplingTime</ogc:PropertyName>' + \
                    '  <gml:TimePeriod>\n' + \
                    '   <gml:beginPosition>' + time_range[0] + \
                    '</gml:beginPosition>\n' + \
                    '   <gml:endPosition>' + time_range[1] + \
                    '</gml:endPosition>\n' + \
                    '  </gml:TimePeriod>\n </ogc:TM_During>\n</eventTime>\n'
                """
                #this code does still not work with ARC SOS
                data += '<eventTime>\n' + \
                    '  <gml:TimePeriod>\n' + \
                    '   <gml:beginPosition>' + time_range[0] + \
                    '</gml:beginPosition>\n' + \
                    '   <gml:endPosition>' + time_range[1] + \
                    '</gml:endPosition>\n' + \
                    '  </gml:TimePeriod></eventTime>\n'
                """
            if procedure:
                if not mode:
                    self.showWarning(WARNING_MUST %
                                    ('If a procedure is chosen, Response Mode',
                                     rType))
                    return None, None
                else:
                    data += '<procedure>' + procedure + '</procedure>\n'
            if obs_prop:
                for obs in obs_prop:
                    data += '<observedProperty>' + obs + '</observedProperty>\n'
            else:
                self.showWarning(WARNING_MUST % ('Observed Property', rType))
                return None, None
            if spatial_limit and foi:
                self.showWarning(WARNING_ONLY_ONE %
                    ('Spatial Limit', 'Feature of Interest', rType))
                return None, None
            if foi:
                data += '<featureOfInterest><ObjectID>' + \
                        foi + \
                        '</ObjectID></featureOfInterest>\n'
            if spatial_limit:  # spatial parameters
                if spatial_limit == self.config.SPATIAL_OWN:
                    # see SpatialTemporalConfigurationWidget
                    bbox = self.getBoundingBox()
                elif spatial_limit == self.config.SPATIAL_OFFERING:
                    # see SosCommonWidget (this module)
                    bbox = self.config.getBoundingBoxOffering()
                else:
                    traceback.print_exc()
                    raise ModuleError(
                        self,
                        'Unknown WFS bounding box type' + ': %s' % str(error))
                data += '<featureOfInterest>\n <ogc:BBOX>\n' + \
                    '  <ogc:PropertyName>urn:ogc:data:location</ogc:PropertyName>\n'
                srsName = self.get_valid_srs(self.config.lblSRS.text())
                if srsName:
                    data += '<gml:Envelope srsName="' + srsName + '">\n'
                else:
                    data += '  <gml:Envelope>\n'
                data += \
                    '   <gml:lowerCorner>' + bbox[2] + ' ' + bbox[3] + \
                    '</gml:lowerCorner>\n' + \
                    '   <gml:upperCorner>' + bbox[0] + ' ' + bbox[1] + \
                    '</gml:upperCorner>\n' + \
                    '  </gml:Envelope>\n' + ' </ogc:BBOX>\n</featureOfInterest>\n'
            if format:
                data += '<responseFormat>' + format + '</responseFormat>\n'
            else:
                self.showWarning(WARNING_MUST % ('Response Format', rType))
                return None, None
            if model:
                data += '<resultModel>' + model + '</resultModel>\n'
            if mode:
                data += '<responseMode>' + mode + '</responseMode>\n'

        # add wrappers
        if rType == 'DescribeSensor':
            header = \
            """<DescribeSensor service="SOS" version="1.0.0"
            xmlns="http://www.opengis.net/sos/1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/sos/1.0
            http://schemas.opengis.net/sos/1.0.0/sosDescribeSensor.xsd"
            outputFormat="text/xml;subtype=&quot;sensorML/1.0.1&quot;">\n"""
            data = header + data + '</DescribeSensor>'
        elif rType == 'GetFeatureOfInterest':
            header = \
            """<GetFeatureOfInterest service="SOS" version="1.0.0"
            xmlns="http://www.opengis.net/sos/1.0"
            xmlns:ows="http://www.opengeospatial.net/ows"
            xmlns:gml="http://www.opengis.net/gml"
            xmlns:ogc="http://www.opengis.net/ogc"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/sos/1.0
            http://schemas.opengis.net/sos/1.0.0/sosGetFeatureOfInterest.xsd">\n"""
            data = header + data + '</GetFeatureOfInterest>\n'
        elif rType == 'GetObservation':
            header = \
            """<GetObservation service="SOS" version="1.0.0"
            xmlns="http://www.opengis.net/sos/1.0"
            xmlns:ows="http://www.opengis.net/ows/1.1"
            xmlns:gml="http://www.opengis.net/gml"
            xmlns:ogc="http://www.opengis.net/ogc"
            xmlns:om="http://www.opengis.net/om/1.0"
            xmlns:ns="http://www.opengis.net/om/1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/sos/1.0
            http://schemas.opengis.net/sos/1.0.0/sosGetObservation.xsd">\n"""
            data = header + data + '</GetObservation>\n'
        else:
            raise ModuleError(
                self,
                'Unknown SOS request type' + ': %s' % str(rType))
        # xml header
        data = '<?xml version="1.0" encoding="UTF-8"?>\n' + data
        #print "SOS:656 - data:\n", data  # show line breaks for testing !!!
        data = data.replace('\n', '')  # remove line breaks
        result['request_type'] = 'POST'
        result['data'] = data
        result['capabilities'] = self.config.parent_widget.capabilities
        # ensure that any variables stored here always have default values
        # and that they are converted from PyQt4.QtCore.QString types
        result['configuration'] = {
            'procedure': str(procedure),
            'format': str(format),
            'mode': str(mode),
            'model': str(model),
            'obs_prop': [str(prop) for prop in obs_prop],
            'foi': str(foi),
            'offering': str(offering),
            'time_limit': str(time_limit),
            'spatial_limit': str(spatial_limit),
            'time_range': time_range,  # tuple of start/end times
        }
        return result

    '''
    # HTTP POST _ worth considering for incremental display of capabilities ??
    <?xml version="1.0" encoding="UTF-8"?>
<GetCapabilities xmlns="http://www.opengis.net/sos/1.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sos/1.0
http://schemas.opengis.net/sos/1.0.0/sosGetCapabilities.xsd" service="SOS" updateSequence="">
<ows:AcceptVersions>
   <ows:Version>1.0.0</ows:Version>
</ows:AcceptVersions>
<ows:Sections>
   <ows:Section>OperationsMetadata</ows:Section>
   <ows:Section>ServiceIdentification</ows:Section>
   <ows:Section>Filter_Capabilities</ows:Section>
   <ows:Section>Contents</ows:Section>
</ows:Sections>
</GetCapabilities>
    '''

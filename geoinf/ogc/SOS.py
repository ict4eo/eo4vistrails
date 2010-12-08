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
Service client, making use of the owslib library.
"""

from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
import init

def raiseError(self, msg, error=''):
    """Raise a VisTrails error."""
    import traceback
    traceback.print_exc()
    raise ModuleError(self, msg + ': %s' % str(error))


class SOS(NotCacheable, FeatureModel):
    """
    SOS module allows connection to a web-based OGC (Open Geospatial Consortium)
    sensor observation service.
    Configuration allows the base URL for the service to be set and called.
    Choosing the appropriate combination of specific service type and other
    parameters, will cause the input port to be set with a specific POST call,
    once the configuration interface is closed.
    Running the SOS will cause the specific, parameterised SOS to be called
    and output from the request to be available via the output ports.

    """
    def __init__(self):
        FeatureModel.__init__(self)

    def compute(self):
        """Execute the module to create the output"""
        try:
            request = self.getInputFromPort(init.OGC_POST_REQUEST_PORT)
            print "Request from port :::", init.OGC_POST_REQUEST_PORT, type(request), request, len(request)
        except:
            request = None

        try:
            url = self.getInputFromPort(init.OGC_URL_PORT)
            print "URL from port :::", init.OGC_URL_PORT, type(url), url, len(url)
        except:
            url = None

        try:
            out = self.runRequest(url, request)
            self.setResult(init.OGC_RESULT_PORT, out)
        except Exception, e:
            import traceback
            traceback.print_exc()
            raise ModuleError(self, 'Cannot set output port: %s' % str(e))

    def runRequest(self, url, request):
        """Execute an HTTP POST request for a given URL"""
        import urllib
        import urllib2
        import os
        from  urllib2 import URLError
        result = None
        if url and request:
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = {'User-Agent': user_agent}
            #request = urllib.urlencode(xml)
            req = urllib2.Request(url, request, headers)
            #proxy ?
            #os.environ["http_proxy"] = "http://myproxy.com:3128"
            try:
                urllib2.urlopen(req)
                response = urllib2.urlopen(req)
                result = response.read()
            except URLError, e:
                if hasattr(e, 'reason'):
                    raiseError(self, 'Failed to reach the server. Reason', e.reason)
                elif hasattr(e, 'code'):
                    raiseError(self, 'The server couldn\'t fulfill the request. Error code', e.code)
            except Exception, e:
                raiseError(self, 'Exception', e)
        return result


class SosCommonWidget(QtGui.QWidget):
    """Enable SOS-specific parameters to be obtained, displayed and selected."""
    def __init__(self, ogc_widget, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("SosCommonWidget")
        self.parent_widget = ogc_widget
        self.contents = None #  only set in self.loadOfferings()
        self.create_config_window()
        # listen for signals emitted by OgcCommonWidget class
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceActivated'),
            self.loadOfferings
        )
        self.connect(
            self.parent_widget,
            QtCore.SIGNAL('serviceDeactivated'),
            self.removeOfferings
        )

    def create_config_window(self):
        """Create datacontainers and layout for displaying SOS-specific data."""
        self.setWindowTitle("SOS Configuration Widget")
        self.setMinimumSize(900, 675)
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
        self.detailsLayout.addWidget(QtGui.QLabel('data'), 9, 0)
        #   data containers
        self.lblDescription =  QtGui.QLabel('-')
        self.detailsLayout.addWidget(self.lblDescription , 0, 1)

        self.boundingGroupBox = QtGui.QGroupBox("")
        self.boundingLayout = QtGui.QVBoxLayout()
        self.boundingGroupBox.setLayout(self.boundingLayout)
        self.detailsLayout.addWidget(self.boundingGroupBox, 1, 1)

        self.minGroupBox = QtGui.QGroupBox("")
        self.minLayout = QtGui.QHBoxLayout()
        self.minGroupBox.setLayout(self.minLayout)
        self.boundingLayout.addWidget(self.minGroupBox)
        self.minLayout.addWidget(QtGui.QLabel('Min X:'))
        self.lblMinX =  QtGui.QLabel('-')
        self.minLayout.addWidget(self.lblMinX)
        self.minLayout.addWidget(QtGui.QLabel('Min Y:'))
        self.lblMinY =  QtGui.QLabel('-')
        self.minLayout.addWidget(self.lblMinY)

        self.maxGroupBox = QtGui.QGroupBox("")
        self.maxGroupBox.setFlat(True)
        self.maxLayout = QtGui.QHBoxLayout()
        self.maxGroupBox.setLayout(self.maxLayout)
        self.boundingLayout.addWidget(self.maxGroupBox)
        self.maxLayout.addWidget(QtGui.QLabel('Max X:'))
        self.lblMaxX =  QtGui.QLabel('-')
        self.maxLayout.addWidget(self.lblMaxX)
        self.maxLayout.addWidget(QtGui.QLabel('Max Y:'))
        self.lblMaxY =  QtGui.QLabel('-')
        self.maxLayout.addWidget(self.lblMaxY)

        self.srsGroupBox = QtGui.QGroupBox("")
        self.srsGroupBox.setFlat(True)
        self.srsLayout = QtGui.QHBoxLayout()
        self.srsGroupBox.setLayout(self.srsLayout)
        self.boundingLayout.addWidget(self.srsGroupBox)
        self.srsLayout.addWidget(QtGui.QLabel('SRS:'))
        self.lblSRS =  QtGui.QLabel('-')
        self.srsLayout.addWidget(self.lblSRS)

        self.boundingLayout.addStretch()  # force all items upwards -does not work?

        self.timeGroupBox = QtGui.QGroupBox("")
        self.timeGroupBox.setFlat(True)
        self.timeLayout = QtGui.QVBoxLayout()
        self.timeGroupBox.setLayout(self.timeLayout)
        self.detailsLayout.addWidget(self.timeGroupBox, 2, 1)
        self.lblStartTime =  QtGui.QLabel('-')
        self.timeLayout.addWidget(self.lblStartTime)
        self.timeLayout.addWidget(QtGui.QLabel('to:'))
        self.lblEndTime =  QtGui.QLabel('-')
        self.timeLayout.addWidget(self.lblEndTime)

        self.cbProcedure = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbProcedure, 3, 1)
        self.cbResponseFormat = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbResponseFormat, 4, 1)
        self.cbResponseMode = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbResponseMode, 5, 1)
        self.cbResultModel = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbResultModel, 6, 1)
        self.cbObservedProperty = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbObservedProperty, 7, 1)
        self.cbFOI = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbFOI, 8, 1)

        self.cbRequest = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbRequest, 9, 1)
        self.cbRequest.addItem('GetFeatureOfInterest')
        self.cbRequest.addItem('GetObservation')
        self.cbRequest.addItem('DescribeSensor')

        # local signals
        self.connect(
            self.lbxOfferings,
            QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),
            self.offeringsChanged
        )

    def removeOfferings(self):
        """Remove all offering details when no SOS is selected."""
        self.clearOfferings()
        self.lbxOfferings.clear()

    def clearOfferings(self):
        """Reset all displayed offering values."""
        self.lblDescription.setText('-')
        self.lblMinX.setText('-')
        self.lblMinY.setText('-')
        self.lblMaxX.setText('-')
        self.lblMaxY.setText('-')
        self.lblSRS.setText('-')
        self.lblStartTime.setText('-')
        self.lblEndTime.setText('-')
        self.cbProcedure.clear()
        self.cbResponseFormat.clear()
        self.cbResponseMode.clear()
        self.cbResultModel.clear()
        self.cbObservedProperty.clear()
        self.cbFOI.clear()

    def offeringsChanged(self):
        """Update offering details containers when new offering selected."""
        self.clearOfferings()
        selected_offering = self.lbxOfferings.selectedItems()[0].text()
        if self.parent_widget.service and self.parent_widget.service.service_valid and self.contents:
            for content in self.contents:
                if selected_offering == content.id:
                    if content.description:
                        self.lblDescription.setText(content.description)
                    elif content.name:
                        self.lblDescription.setText(content.name)
                    else:
                        self.lblDescription.setText(content.id)
                    # update other offering details...
                    if content.time:
                        self.lblStartTime.setText(str(content.time[0]))
                        self.lblEndTime.setText(str(content.time[1]))
                    if content.bounding_box:
                        self.lblMinX.setText(str(content.bounding_box[0]))
                        self.lblMinY.setText(str(content.bounding_box[1]))
                        self.lblMaxX.setText(str(content.bounding_box[2]))
                        self.lblMaxY.setText(str(content.bounding_box[3]))
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
                    self.cbObservedProperty.addItem('')
                    if content.observed_property:
                        for op in content.observed_property:
                            self.cbObservedProperty.addItem(op)
                    self.cbFOI.addItem('')
                    if content.feature_of_interest:
                        for foi in content.feature_of_interest:
                            self.cbFOI.addItem(foi)

    def loadOfferings(self):
        """Load the offerings from the service metadata."""
        if self.parent_widget.service and self.parent_widget.service.service_valid:
            self.contents = self.parent_widget.service.service.__dict__['contents']
            for content in self.contents:
                item = QtGui.QListWidgetItem(content.id)
                self.lbxOfferings.addItem(item)


class SOSConfigurationWidget(OgcConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""
    def __init__(self, module, controller, parent=None):
        OgcConfigurationWidget.__init__(self, module, controller, parent)
        #self.parent_module = module
        # pass in parent widget i.e. OgcCommonWidget class
        self.config = SosCommonWidget(self.ogc_common_widget)
        # move parent tab to first place
        self.tabs.insertTab(1, self.config, "")
        # set SOS-specific tabs
        self.tabs.setTabText(
            self.tabs.indexOf(self.config),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "SOS Specific Metadata",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.config),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "Select SOS-specific parameters",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setCurrentIndex(0)

    def constructRequest(self):
        """Return an XML-encoded request from configuration parameters

        Extends method defined in OgcConfigurationWidget.
        """
        data = ''
        type = self.config.cbRequest.currentText()
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
        try:
            obs_prop = self.config.cbObservedProperty.currentText()
        except:
            obs_prop = None
        try:
            foi = self.config.cbFOI.currentText()
        except:
            foi = None
        try:
            offering = self.config.lbxOfferings.currentItem().text()
        except:
            offering = None
        # details
        if type == 'DescribeSensor':
            if procedure:
                data = data + '<procedure>' + procedure + '</procedure>'
        elif type == 'GetFeatureOfInterest':
            if foi:
                data = '<FeatureOfInterestId>' + foi + '</FeatureOfInterestId>'
        elif type == 'GetObservation':
            if offering:
                data = data + '<offering>' + offering + '</offering>'
            # TO DO: time params
            if procedure:
                data = data + '<procedure>' + procedure + '</procedure>'
            if obs_prop:
                data = data + '<observedProperty>' + obs_prop + '</observedProperty>'
            if format:
                data = data + '<responseFormat>' + format + '</responseFormat>'
            if model:
                data = data + '<resultModel>' + model + '</resultModel>'
            if mode:
                data = data + '<responseMode>' + mode + '</responseMode>'
            if foi:
                data = data + '<featureOfInterest><ObjectID>' + foi + '</ObjectID></featureOfInterest>'
            # TO DO: spatial params
        # wrapper
        if type == 'DescribeSensor':
            data = \
            """<DescribeSensor service="SOS" version="1.0.0"
            xmlns="http://www.opengis.net/sos/1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/sos/1.0
            http://schemas.opengis.net/sos/1.0.0/sosDescribeSensor.xsd"
            outputFormat="text/xml;subtype=&quot;sensorML/1.0.1&quot;">""" + \
            data + '</DescribeSensor>'
        elif type == 'GetFeatureOfInterest':
            data = \
            """<GetFeatureOfInterest service="SOS" version="1.0.0"
            xmlns="http://www.opengis.net/sos/1.0"
            xmlns:ows="http://www.opengeospatial.net/ows"
            xmlns:gml="http://www.opengis.net/gml"
            xmlns:ogc="http://www.opengis.net/ogc"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/sos/1.0
            http://schemas.opengis.net/sos/1.0.0/sosGetFeatureOfInterest.xsd">""" + \
            data + '</GetFeatureOfInterest>'
        elif type == 'GetObservation':
            data = \
            """<GetObservation service="SOS" version="1.0.0"
            xmlns="http://www.opengis.net/sos/1.0"
            xmlns:ows="http://www.opengis.net/ows/1.1"
            xmlns:gml="http://www.opengis.net/gml"
            xmlns:ogc="http://www.opengis.net/ogc"
            xmlns:om="http://www.opengis.net/om/1.0"
            xmlns:ns="http://www.opengis.net/om/1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.opengis.net/sos/1.0
            http://schemas.opengis.net/sos/1.0.0/sosGetObservation.xsd"
            srsName="urn:ogc:def:crs:EPSG:4326">""" + \
            data + '</GetObservation>'
        else:
            raiseError(self, 'Unknown request type: check SOS Request combobox')
        # header
        data = '<?xml version="1.0" encoding="UTF-8"?>' + data
        return data

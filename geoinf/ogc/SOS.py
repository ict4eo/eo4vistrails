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
"""This module provides an OGC Sensor Observation Service Client via owslib.
"""

from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError


class SOS(FeatureModel):
    """
    SOS module allows connection to a web-based OGC sensor observation service.
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
        pass
        """        """
        print "input ports (before setting):\n", self.inputPorts
        print "output ports (before setting):\n", self.outputPorts

        try:
            o = 'foo'
            self.setResult('ServiceOutput', o)
        except:
            print "CANNOT setResult for ServiceOutput"

        try:
            i = "http://foo.bar"
            self.set_input_port(self, 'ConfiguredRequest', i)
        except:
            print "CANNOT set_input_port for ConfiguredRequest"

        print "input ports (after setting):\n", self.inputPorts
        print "output ports (after setting):\n", self.outputPorts

        """
        # ----------------------------------------------------------------------

        i = "http://foo.bar"

        try:
            self.setResult('ConfiguredRequest', i)
        except:
            print "NOT set result for ConfiguredRequest"

        try:
            self.setInputPort('ConfiguredRequest', i)
        except:
            print "NOT setInputPort"

        try:
            self.setInput('ConfiguredRequest', i)
        except:
            print "NOT setInput"

        try:
            self.set_input_port('ConfiguredRequest', i)
        except:
            print "NOT set_input_port"

        try:
            self.checkInputPort('ConfiguredRequest')
        except:
            print "NOT checkInputPort('ConfiguredRequest')"

        try:
            foo = self.hasInputFromPort('ConfiguredRequest')
            print "CAN hasInputFromPort('ConfiguredRequest')", foo
        except:
            print "NOT hasInputFromPort('ConfiguredRequest')"

        try:
            self.service_url = self.getInputFromPort('ConfiguredRequest')
            print "CAN getInputFromPort('ConfiguredRequest')", self.service_url
        except:
            print "NOT getInputFromPort('ConfiguredRequest')"

        print "input ports (after setting):\n", self.inputPorts

        outputPort = self.outputPorts.get('ServiceOutput')
        print "type(outputPort)",type(outputPort)

        outputPort = self.outputPorts['self']
        print "type(outputPort)",type(outputPort)

        inputPort = self.inputPorts.get('ConfiguredRequest')
        print "type(inputPort)",type(inputPort)

        # attempted to "lift' code from fold.py... does not work here
        if inputPort:
            module = inputPort.obj
            del module.inputPorts[inputPort]
            element = "FOOBAR"
            new_connector = ModuleConnector(create_constant(element), 'value')
            module.set_input_port(inputPort, new_connector)
        """


class SosCommonWidget(QtGui.QWidget):
    """TO DO - add docstring

    """
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
        # listen for signals emitted by SpatialTemporalConfigurationWidget class
        # ... i.e. grandparent class
        # OK clicked
        self.connect(
            self.parent_widget, # should be  self.parent_widget.parent_widget, ???
            QtCore.SIGNAL('doneConfigure'),
            self.doConfigure
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

        self.testButton = QtGui.QPushButton('&Test', self)
        self.offeringsLayout.addWidget(self.testButton)

        # offering details layout
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

        self.boundingLayout.addStretch()  # force all items upwards -does not work

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

        # local signals
        self.connect(
            self.lbxOfferings,
            QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),
            self.offeringsChanged
        )
        self.connect(
            self.testButton,
            QtCore.SIGNAL("clicked(bool)"),
            self.doConfigure
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
                    if content.procedure:
                        for pr in content.procedure:
                            self.cbProcedure.addItem(pr)
                    if content.response_format:
                        for rf in content.response_format:
                            self.cbResponseFormat.addItem(rf)
                    if content.response_mode:
                        for rm in content.response_mode:
                            self.cbResponseMode.addItem(rm)
                    if content.result_model:
                        for rd in content.result_model:
                            self.cbResultModel.addItem(rd)
                    if content.observed_property:
                        for op in content.observed_property:
                            self.cbObservedProperty.addItem(op)
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

    def doConfigure(self):
        """Set the output request (aka ConfiguredRequest) on the input port."""
        print "OK!!!"


class SOSConfigurationWidget(OgcConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""
    def __init__(self,  module, controller, parent=None):
        OgcConfigurationWidget.__init__(self, module, controller, parent)
        # pass in parent widget i.e. OgcCommonWidget class
        self.sos_config_widget = SosCommonWidget(self.ogc_common_widget)
        # tabs
        self.tabs.insertTab(1, self.sos_config_widget, "")
        self.tabs.setTabText(
            self.tabs.indexOf(self.sos_config_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "SOS Specific Metadata",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.sos_config_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "Select SOS-specific parameters",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setCurrentIndex(0)

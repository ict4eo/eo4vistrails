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

#from owslib.wfs import WFS
from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError


#need to import the configuration widget we develop
class SOS(FeatureModel):
    """TO DO - add docstring

    """
    def __init__(self):
        FeatureModel.__init__(self)

    def compute(self):
        pass


class SosCommonWidget(QtGui.QWidget):
    """TO DO - add docstring

    """
    def __init__(self, ogc_widget, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("SosCommonWidget")
        self.parent_widget = ogc_widget
        self.service = self.parent_widget.service
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
        self.setMinimumSize(800, 300)
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
        # offering details layout
        #   labels
        self.detailsLayout.addWidget(QtGui.QLabel('Description'), 0, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Bounding Box'), 1, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Time'), 2, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Procedure'), 3, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Response Format'), 4, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Response Mode'), 5, 0)
        self.detailsLayout.addWidget(QtGui.QLabel('Result Model'), 6, 0)
        #   data containers
        self.lblDescription =  QtGui.QLabel('-')
        self.detailsLayout.addWidget(self.lblDescription , 0, 1)

        self.boundingGroupBox = QtGui.QGroupBox("")
        self.boundingLayout = QtGui.QHBoxLayout()
        self.boundingGroupBox.setLayout(self.boundingLayout)
        self.detailsLayout.addWidget(self.boundingGroupBox, 1, 1)
        self.boundingLayout.addWidget(QtGui.QLabel('Min X:'))
        self.lblMinX =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblMinX)
        self.boundingLayout.addWidget(QtGui.QLabel('Min Y:'))
        self.lblMinY =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblMinY)
        self.boundingLayout.addWidget(QtGui.QLabel('Max X:'))
        self.lblMaxX =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblMaxX)
        self.boundingLayout.addWidget(QtGui.QLabel('Max Y:'))
        self.lblMaxY =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblMaxY)

        self.timeGroupBox = QtGui.QGroupBox("")
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
        self.lblStartTime.setText('-')
        self.lblEndTime.setText('-')
        self.cbProcedure.clear()
        self.cbResponseFormat.clear()
        self.cbResponseMode.clear()
        self.cbResultModel.clear()

    def offeringsChanged(self):
        """Update offering details containers when new offering selected."""
        self.clearOfferings()
        selected_offering = self.lbxOfferings.selectedItems()[0].text()
        if self.parent_widget.service and self.parent_widget.service.service_valid:
            for content in self.parent_widget.service.service_contents:
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
                        #self.SRS = content.bounding_box[4] #TO DO
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

    def loadOfferings(self):
        """Load the offerings from the service metadata."""
        #fubar = service.__dict__['provider'].__dict__ # only works in OgcService
        if self.parent_widget.service and self.parent_widget.service.service_valid:
            for content in self.parent_widget.service.service_contents:
                #print content.id
                item = QtGui.QListWidgetItem(content.id)
                self.lbxOfferings.addItem(item)


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

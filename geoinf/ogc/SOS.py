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
"""This module provides an OGC Sensor Observation Service Client via owslib.
"""

#from owslib.wfs import WFS
from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError


#need to import the configuration widget we develop
class SOS(FeatureModel):
    """TO DO - add docstring"""
    def __init__(self):
        FeatureModel.__init__(self)

    def compute(self):
        pass


class SosCommonWidget(QtGui.QWidget):
    """TO DO - add docstring"""
    def __init__(self,  module, parent=None):
        '''parses modules attributes to fetch parameters'''
        QtGui.QWidget.__init__(self, parent)
        self.launchtype = str(module).split(" ")[1].split(":")[1][0:3].lower()
        #self.module = module
        self.setObjectName("SosCommonWidget")
        self.create_config_window()

    def create_config_window(self):
        """TO DO - add docstring"""
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
        self.lbxOfferings = QtGui.QListView()
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

        self.boundingGroupBox = QtGui.QGroupBox("BB")
        self.boundingLayout = QtGui.QHBoxLayout()
        self.boundingGroupBox.setLayout(self.boundingLayout)
        self.detailsLayout.addWidget(self.boundingGroupBox, 1, 1)
        self.boundingLayout.addWidget(QtGui.QLabel('Min X'))
        self.lblMinX =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblMinX)
        self.boundingLayout.addWidget(QtGui.QLabel('Min Y'))
        self.lblMinY =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblMinY)
        self.boundingLayout.addWidget(QtGui.QLabel('Max X'))
        self.lblMaxX =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblMaxX)
        self.boundingLayout.addWidget(QtGui.QLabel('Max Y'))
        self.lblMaxY =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblMaxY)

        self.timeGroupBox = QtGui.QGroupBox("Time")
        self.timeLayout = QtGui.QHBoxLayout()
        self.timeGroupBox.setLayout(self.timeLayout)
        self.detailsLayout.addWidget(self.timeGroupBox, 2, 1)
        self.timeLayout.addWidget(QtGui.QLabel('Start'))
        self.lblStartTime =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblStartTime)
        self.timeLayout.addWidget(QtGui.QLabel('End'))
        self.lblEndTime =  QtGui.QLabel('-')
        self.boundingLayout.addWidget(self.lblEndTime)

        self.cbProcedure = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbProcedure, 3, 1)
        self.cbResponseFormat = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbResponseFormat, 4, 1)
        self.cbResponseMode = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbResponseMode, 5, 1)
        self.cbResultModel = QtGui.QComboBox()
        self.detailsLayout.addWidget(self.cbResultModel, 6, 1)

        # initial data - offerings list
        self.loadOfferings()

        # signals
        self.connect(
            self.lbxOfferings,
            QtCore.SIGNAL("itemSelectionChanged()"),
            self.offeringsChanged
        )

    def offeringsChanged(self):
        """Update offering details containers when new offering selected."""
        selected_offering =  self.lbxOfferings.selectedItems()[0].text()
        #TODO...
        pass

    def loadOfferings(self):
        """Load the offerings from the service metadata."""
        model = QtGui.QStandardItemModel()
        model.clear()
        bar = ['one','two','three']
        #get data
        if bar:
            for foo in bar:
                item = QtGui.QStandardItem(foo)
                #item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                #item.setData(QVariant(Qt.Unchecked), Qt.CheckStateRole) #was QVariant(check)
                model.appendRow(item)
            # load list into container
            self.lbxOfferings.setModel(model)


class SOSConfigurationWidget(OgcConfigurationWidget):
    """makes use of code style from OgcConfigurationWidget"""
    def __init__(self,  module, controller, parent=None):
        OgcConfigurationWidget.__init__(self,  module, controller, parent)

        self.sos_common_widget = SosCommonWidget(module)

        self.tabs.addTab(self.sos_common_widget, "")
        self.tabs.setTabText(
            self.tabs.indexOf(self.sos_common_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "SOS Specific Metadata",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.sos_common_widget),
            QtGui.QApplication.translate(
                "OgcConfigurationWidget",
                "Stuff for SOS",
                None,
                QtGui.QApplication.UnicodeUTF8
            )
        )
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

#from owslib.wfs import WFS
from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError

from owslib.wfs import WebFeatureService


#need to import the configuration widget we develop

class WFS(NotCacheable,  FeatureModel):

    def __init__(self):
        FeatureModel.__init__(self)

    def compute(self):
        pass

class WFSCommonWidget(QtGui.QWidget):

    def __init__(self, module, parent=None):

        '''sets parameters for wfs request '''

        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("WFSConfigurationWidget")
        self.create_wfs_config_window()

    def create_wfs_config_window(self):

        gridLayout = QtGui.QGridLayout()
        self.setLayout(gridLayout)
        gridLayout.addWidget(QtGui.QLabel('wfs Url'), 0, 0)
        gridLayout.addWidget(QtGui.QLabel('Available Operations'), 1, 0)
        gridLayout.addWidget(QtGui.QLabel('TypeNames'), 2, 0)
        gridLayout.addWidget(QtGui.QLabel('bbox:'), 3, 0)
        gridLayout.addWidget(QtGui.QLabel('                             min  x'), 3, 1)
        gridLayout.addWidget(QtGui.QLabel('                     min  y'), 3, 3)
        gridLayout.addWidget(QtGui.QLabel('                             max  x'), 4, 1)
        gridLayout.addWidget(QtGui.QLabel('                     max y'), 4, 3)
        gridLayout.addWidget(QtGui.QLabel('ESPG/SRS Code'), 5, 0)
        gridLayout.addWidget(QtGui.QLabel('maxFeatures'), 6, 0)
        #gridLayout.addWidget(QtGui.QLabel('GetFeature'), 7, 0)
        self.wfsUrlEdit = QtGui.QLineEdit('http://localhost:8080/geoserver/wfs')

        self.minXEdit = QtGui.QLineEdit('0.0')
        self.ESPGEdit = QtGui.QLineEdit('Null')
        self.maxFeaturesEdit = QtGui.QLineEdit('0')

        self.minYEdit = QtGui.QLineEdit('0.0')
        self.maxXEdit = QtGui.QLineEdit('0.0')
        self.maxYEdit = QtGui.QLineEdit('0.0')
        #self.DescribeFeatureTypeEdit = QtGui.QLineEdit('http://')
        #self.GetFeatureEdit = QtGui.QLineEdit('http://')

        gridLayout.addWidget(self.wfsUrlEdit, 0, 1)
        gridLayout.addWidget(self.minXEdit, 3,2)
        gridLayout.addWidget(self.ESPGEdit, 5,1)
        gridLayout.addWidget(self.maxFeaturesEdit, 6,1)
        gridLayout.addWidget(self.minYEdit, 3, 4)
        gridLayout.addWidget(self.maxXEdit, 4, 2)
        gridLayout.addWidget(self.maxYEdit, 4, 4)
        #gridLayout.addWidget(self.DescribeFeatureTypeEdit, 6, 1)
        #gridLayout.addWidget(self.GetFeatureEdit, 7, 1)
        self.opComboAvailableOperations = QtGui.QComboBox()
        #self.opComboAvailableOperations.addItems(['Null'])
        gridLayout.addWidget(self.opComboAvailableOperations, 1, 1)
        self.opComboLayerNames = QtGui.QComboBox()
        #self.opComboLayerNames.addItems(['Null'])
        gridLayout.addWidget(self.opComboLayerNames, 2, 1)

        #self.opComboSRS = QtGui.QComboBox()
        #self.opComboSRS.addItems(['4326', '', ''])
        #gridLayout.addWidget(self.opComboSRS, 5, 1)

        self.loadRequestButton = QtGui.QPushButton('load')

        gridLayout.addWidget(self.loadRequestButton, 7, 1)
        self.connect(self.loadRequestButton, QtCore.SIGNAL('clicked()'), self.loadRequest)

        self.resetRequestButton = QtGui.QPushButton('reset')
        gridLayout.addWidget(self.resetRequestButton, 7, 2)
        self.connect(self.resetRequestButton, QtCore.SIGNAL('clicked()'), self.clearRequest)

        self.saveRequestButton = QtGui.QPushButton('save')
        gridLayout.addWidget(self.saveRequestButton, 7, 3)
        self.connect(self.saveRequestButton, QtCore.SIGNAL('clicked()'), self.saveRequest)

    def clearRequest(self):
        """TO-DO Implement clear fields """
        pass



    def saveRequest(self):
        #"""TO-DO implement read set parameters, assign to wfs input ports """
        pass


    def loadRequest(self):

        """ loadRequest() -> None
        use given url to read wfs file, populates the config widget populate fields

        """
        #result = str(self.wfsUrlEdit.text()

        defaultUrl = str(self.wfsUrlEdit.text())

        wfs = WebFeatureService(defaultUrl)

        layers = list(wfs.contents)


        self.opComboAvailableOperations.addItems([op.name for op in wfs.operations])

        for elem in layers:

            self.opComboLayerNames.addItems([elem])

            crsCode = wfs[str(self.opComboLayerNames.currentText())].crsOptions


        for elemen in crsCode:

            self.ESPGEdit.setText(elemen)
            coordinates = wfs[str(self.opComboLayerNames.currentText())].boundingBoxWGS84

            self.minXEdit.setText(str(coordinates[0]))
            self.minYEdit.setText(str(coordinates[1]))
            self.maxXEdit.setText(str(coordinates[2]))
            self.maxYEdit.setText(str(coordinates[3]))

        ''''
        label_wfs_url = QtGui.QLabel('OGC WebFeatureService url:', self)  # should make use of the one from OgcConfigrationWidget instead.
        label_wfs_url.setGeometry(QtCore.QRect(5, 20, 192, 27))
        line_edit_wfs_url = QtGui.QLineEdit("", self)
        line_edit_wfs_url.setGeometry(QtCore.QRect(202, 20, 530, 27))

        lineEdit_MinY = QtGui.QLineEdit("", self)
        lineEdit_MinY.setGeometry(QtCore.QRect(270, 290, 80, 21))
        lineEdit_MinY.setObjectName("lineEdit_MinY")

        lbl_MaxY = QtGui.QLabel("Max Y:", self)
        lbl_MaxY.setGeometry(QtCore.QRect(220, 350, 50, 21))
        lbl_MaxY.setObjectName("lbl_MaxY")

        lineEdit_MaxY = QtGui.QLineEdit("", self)
        lineEdit_MaxY.setGeometry(QtCore.QRect(270, 350, 80, 21))
        lineEdit_MaxY.setObjectName("lineEdit_MaxY")

        lblMinY = QtGui.QLabel("Min Y:", self)
        lblMinY.setGeometry(QtCore.QRect(220, 290, 40, 20))
        lblMinY.setObjectName("lblMinY")

        lbl_bbox = QtGui.QLabel("bbox:", self)
        lbl_bbox.setGeometry(QtCore.QRect(10, 320, 40, 21))
        lbl_bbox.setObjectName("lbl_bbox")

        lbl_TypeNames = QtGui.QLabel( "TypeNames:", self)
        lbl_TypeNames.setGeometry(QtCore.QRect(0, 130, 80, 21))
        lbl_TypeNames.setObjectName("lbl_TypeNames")

        lbl_ESPG = QtGui.QLabel("ESPG Code:", self)
        lbl_ESPG.setGeometry(QtCore.QRect(0, 180, 81, 21))
        lbl_ESPG.setObjectName("lbl_ESPG")

        lbl_MaxFeatures = QtGui.QLabel("MaxFeatures:", self)
        lbl_MaxFeatures.setGeometry(QtCore.QRect(0, 230, 90, 21))
        lbl_MaxFeatures.setObjectName("lbl_MaxFeatures")

        lbl_Operations = QtGui.QLabel("Avail Operations:", self)
        lbl_Operations.setGeometry(QtCore.QRect(0, 80, 124, 21))
        lbl_Operations.setObjectName("lbl_Operations")

        cmb_Operations = QtGui.QComboBox(self)
        cmb_Operations.setGeometry(QtCore.QRect(130, 80, 160, 21))
        cmb_Operations.setObjectName("cmb_Operations")

        cmb_TypeNames = QtGui.QComboBox(self)
        cmb_TypeNames.setGeometry(QtCore.QRect(130, 130, 160, 21))
        cmb_TypeNames.setObjectName("cmb_TypeNames")

        lineEdit_ESPG = QtGui.QLineEdit("", self)
        lineEdit_ESPG.setGeometry(QtCore.QRect(130, 180, 160, 21))
        lineEdit_ESPG.setObjectName("lineEdit_ESPG")

        lineEdit_MaxFeatures = QtGui.QLineEdit("", self)
        lineEdit_MaxFeatures.setGeometry(QtCore.QRect(130, 230, 160, 21))
        lineEdit_MaxFeatures.setObjectName("lineEdit_MaxFeatures")

        lineEdit_MinX = QtGui.QLineEdit("", self)
        lineEdit_MinX.setGeometry(QtCore.QRect(130, 290, 80, 21))
        lineEdit_MinX.setObjectName("lineEdit_MinX")

        lbl_MinX = QtGui.QLabel("Min X:", self)
        lbl_MinX.setGeometry(QtCore.QRect(80, 290, 40, 21))
        lbl_MinX.setObjectName("lbl_MinX")

        lineEdit_MaxX = QtGui.QLineEdit("", self)
        lineEdit_MaxX.setGeometry(QtCore.QRect(130, 350, 80, 21))
        lineEdit_MaxX.setObjectName("lineEdit_MaxX")

        lbl_MaxX = QtGui.QLabel("Max X:", self)
        lbl_MaxX.setGeometry(QtCore.QRect(80, 350, 44, 21))
        lbl_MaxX.setObjectName("lbl_MaxX")

        wfs_treeView = QtGui.QTreeView(self)
        wfs_treeView.setGeometry(QtCore.QRect(355, 81, 460, 390))
        wfs_treeView.setWordWrap(True)
        wfs_treeView.setObjectName("wfs_treeView")

        label_Inspect_browser = QtGui.QLabel("Inspect TypeName Metadata", self)
        label_Inspect_browser.setGeometry(QtCore.QRect(531, 60, 201, 20))
        label_Inspect_browser.setObjectName("label_Inspect_browser")

        loadButton = QtGui.QPushButton(self)
        loadButton.setGeometry(QtCore.QRect(80, 470, 71, 27))
        loadButton.setObjectName("loadButton")

        resetButton = QtGui.QPushButton(self)
        resetButton.setGeometry(QtCore.QRect(180, 470, 71, 27))
        resetButton.setObjectName("resetButton")

        saveButton = QtGui.QPushButton(self)
        saveButton.setGeometry(QtCore.QRect(280, 470, 71, 27))
        saveButton.setObjectName("saveButton")

        loadButton.setText(QtGui.QApplication.translate("QTConfigurationWidget", "Load", None, QtGui.QApplication.UnicodeUTF8))
        saveButton.setText(QtGui.QApplication.translate("QTConfigurationWidget", "Save", None, QtGui.QApplication.UnicodeUTF8))
        resetButton.setText(QtGui.QApplication.translate("QTConfigurationWidget", "Reset", None, QtGui.QApplication.UnicodeUTF8))

        '''

class WFSConfigurationWidget(OgcConfigurationWidget):

    def __init__(self,  module, controller, parent=None):

        OgcConfigurationWidget.__init__(self,  module, controller, parent)

        self.wfs_config = WFSCommonWidget(module)
        self.tabs.addTab(self.wfs_config,  "")

        self.tabs.setTabText(self.tabs.indexOf(self.wfs_config), QtGui.QApplication.translate("WFSConfigurationWidget", "WFS", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabToolTip(self.tabs.indexOf(self.wfs_config), QtGui.QApplication.translate("WFSConfigurationWidget", "WFS Configuration", None, QtGui.QApplication.UnicodeUTF8))




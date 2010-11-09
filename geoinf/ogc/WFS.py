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


#need to import the configuration widget we develop

class WFS(NotCacheable,  FeatureModel):  
   
    def __init__(self):
	FeatureModel.__init__(self)
		
    def compute(self):
	pass

class WFS2(QtGui.QWidget):
    
    def __init__(self,  module, parent=None):

	'''sets parameters for wfs request '''

	QtGui.QWidget.__init__(self, parent)
	
	self.setObjectName("WFSConfigurationWidget")
	self.create_wfs_config_window()
		
    def create_wfs_config_window(self):

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
		lbl_MinX.setWordWrap(False)
		lbl_MinX.setObjectName("lbl_MinX")
		lineEdit_MaxX = QtGui.QLineEdit("", self)
		lineEdit_MaxX.setGeometry(QtCore.QRect(130, 350, 80, 21))
		lineEdit_MaxX.setObjectName("lineEdit_MaxX")
		lbl_MaxX = QtGui.QLabel("Max X:", self)
		lbl_MaxX.setGeometry(QtCore.QRect(80, 350, 44, 21))
		lbl_MaxX.setWordWrap(False)
		lbl_MaxX.setObjectName("lbl_MaxX")
		wfs_treeView = QtGui.QTreeView(self)
		wfs_treeView.setGeometry(QtCore.QRect(355, 81, 460, 390))
		wfs_treeView.setWordWrap(True)
		wfs_treeView.setObjectName("wfs_treeView")
		
		


class WFSConfigurationWidget(OgcConfigurationWidget):
    
    def __init__(self,  module, controller, parent=None):

		OgcConfigurationWidget.__init__(self,  module, controller, parent)

		self.wfs_config = WFS2(module)
		self.tabs.addTab(self.wfs_config,  "")
		
		self.tabs.setTabText(self.tabs.indexOf(self.wfs_config), QtGui.QApplication.translate("WFSConfigurationWidget", "WFS", None, QtGui.QApplication.UnicodeUTF8))
		self.tabs.setTabToolTip(self.tabs.indexOf(self.wfs_config), QtGui.QApplication.translate("WFSConfigurationWidget", "WFS Configuration", None, QtGui.QApplication.UnicodeUTF8))




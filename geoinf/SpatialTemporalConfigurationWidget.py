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
"""This module provides spatial and temporal selection widgetry for configuring geoinf modules.
"""
from PyQt4 import QtCore, QtGui
from core.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.module_registry import get_module_registry
from core.utils import PortAlreadyExists




class SpatioTemporalConfigurationWidgetTabs(QtGui.QTabWidget):
    '''Geoinf Configuration Tab Widgets are added vis the addTab method of the QTabWidget '''
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self,  parent)
        self.setGeometry(QtCore.QRect(20, 20, 990, 740))
        self.setTabShape(QtGui.QTabWidget.Rounded)
        self.setElideMode(QtCore.Qt.ElideNone)
        self.setObjectName("SpatioTemporalConfigurationWidgetTabsInstance")
        
class SpatialWidget(QtGui.QtWidget):
    '''designed to gather coordinates of a bounding box, 
    or in the case of GRASS, a location'''
    def __init__(self,  parent=None):
        QtGui.QtWidget.__init__(self, parent)
        
        self.setObjectName("SpatialParams")
        self.gridLayout = QtGui.QGridLayout()
        self.setLayout(self.gridLayout)
        self.gridLayout.addWidget(QtGui.QLabel('BBox Top Left X'), 0, 0)
        self.bbox_tlx = QtGui.QLineEdit('15.0') 
        self.gridLayout.addWidget(self.bbox_tlx, 0, 1)
        self.gridLayout.addWidget(QtGui.QLabel('BBox Top Left Y'), 0, 2)
        self.bbox_tly = QtGui.QLineEdit('-22.0') 
        self.gridLayout.addWidget(self.bbox_tly, 0, 3)
        self.gridLayout.addWidget(QtGui.QLabel('BBox Bottom Right X'), 1, 0)
        self.bbox_brx = QtGui.QLineEdit('33.0') 
        self.gridLayout.addWidget(self.bbox_brx, 1, 1)
        self.gridLayout.addWidget(QtGui.QLabel('BBox Bottom Right Y'), 1, 2)
        self.bbox_bry = QtGui.QLineEdit('-35.0') 
        self.gridLayout.addWidget(self.bbox_bry, 1, 3)
        
class TemporalWidget(QtGui.QtWidget):
    
    def __init__(self,  parent=None):
        QtGui.QtWidget.__init__(self, parent)
        
        

class SpatialTemporalConfigurationWidget(StandardModuleConfigurationWidget):
    '''makes use of code style from TupleConfigurationWidget'''
    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        
        #initialise the setup necessary for all geoinf widgets that follow
        self.setWindowTitle('Spatial and Temporal parameter setup ')
        self.setToolTip("Setup spatial and temporal paramaters for working with a geoinf module")
        self.createButtons()
        self.createTabs()
        
    def updateVistrail(self):
        msg = "Must implement updateVistrail in subclass"
        raise VistrailsInternalError(msg)
        
    def createTabs(self):
        ''' createTabs() -> None
        create and polulate with widgets the necessary 
        tabs for spatial and temporal paramaterisation
        '''
        self.tabs = SpatioTemporalConfigurationWidgetTabs()
        self.spatial_widget = SpatialWidget()
        self.temporal_widget = TemporalWidget()
        self.tabs.addTab(self.spatial_widget, "")
        self.tabs.addTab(self.temporal_widget, "")
        
    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Ok & Cancel button
        
        """
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setAutoDefault(False)
        self.okButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setShortcut('Esc')
        self.cancelButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.cancelButton)
        self.layout().addLayout(self.buttonLayout)
        self.connect(self.okButton, QtCore.SIGNAL('clicked(bool)'),
                     self.okTriggered)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked(bool)'),
                     self.close)        

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommended size of the configuration window
        
        """
        return QtCore.QSize(512, 256)

    def okTriggered(self, checked = False):
        """ okTriggered(checked: bool) -> None
        Update vistrail controller and module when the user click Ok
        
        """
        if self.updateVistrail():
            self.emit(QtCore.SIGNAL('doneConfigure()'))
            self.close()    

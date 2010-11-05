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
"""This module provides general ogc selection widgetry for configuring geoinf.ogc modules.
This refers primarily to GetCapabilities requests
"""

from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.SpatialTemporalConfigurationWidget import SpatialTemporalConfigurationWidget
#from owslib import wfs,  sos,  wcs
from Common import OgcService

class OgcCommonWidget(QtGui.QWidget):
    
    def __init__(self,  module, parent=None):
        '''parses modules attributes to fetch parameters'''
        QtGui.QWidget.__init__(self, parent)
        
        self.setObjectName("OgcCommonWidget")
        self.create_config_window()
        
    def create_config_window(self):
        self.setGeometry(0,0, 200,300) 
        self.setWindowTitle("General OGC Configuration Widget")         
        self.resize(800,300) 
        self.setMinimumSize(800,300) 
        self.center()         
        
        self.mainLayout = QtGui.QVBoxLayout()
        #self.mainLayout.setGeometry(QtCore.QRect(1, 15, 799, 298))
        self.setLayout(self.mainLayout)

        
        self.urlGroupBox = QtGui.QGroupBox("Service URL:")
        self.urlGroupBox.setGeometry(QtCore.QRect(4, 19, 530, 45))
        
        self.fetchUrlLayout = QtGui.QHBoxLayout()

        self.label_OGC_url = QtGui.QLabel('OGC WebService url:')  
        #self.label_OGC_url.setGeometry(QtCore.QRect(5, 20, 142, 27))
        self.label_OGC_url.setFixedSize(140,  25)
        
        self.line_edit_OGC_url = QtGui.QLineEdit("")
        #self.line_edit_OGC_url.setGeometry(QtCore.QRect(146, 20, 530, 27))
        self.line_edit_OGC_url.setFixedSize(500, 25 )
        
        self.fetchButton = QtGui.QPushButton('&Fetch')
        self.fetchButton.setAutoDefault(False)
        self.fetchButton.setFixedSize(100, 25)
        #self.fetchButton.setGeometry(QtCore.QRect(680, 20, 690, 27))

        self.fetchUrlLayout.addWidget(self.label_OGC_url)
        self.fetchUrlLayout.addWidget(self.line_edit_OGC_url)
        self.fetchUrlLayout.addWidget(self.fetchButton)

        self.urlGroupBox.setLayout(self.fetchUrlLayout)
        
        self.mainLayout.addWidget(self.urlGroupBox)
        
        self.connect(self.fetchButton, QtCore.SIGNAL('clicked(bool)'),
                     self.fetchTriggered)
        print "done first layout"
        #self.fetchUrlLayout.setGeometry(QtCore.QRect(4, 19, 530, 28))

        self.metaLayout = QtGui.QHBoxLayout()
        self.metaGroupBox = QtGui.QGroupBox("Service Metadata")
        self.metaGroupBox.setGeometry(QtCore.QRect(4, 50, 530, 290))
        
        self.metaGroupBox.setLayout(self.metaLayout)
        self.mainLayout.addWidget(self.metaGroupBox)
        
        
        self.serviceIDLayout = QtGui.QVBoxLayout()
        self.serviceIDGroupBox = QtGui.QGroupBox("Service Identification")
        self.serviceIDGroupBox.setGeometry(QtCore.QRect(16,60, 250, 285))
        
        self.serviceIDGroupBox.setLayout(self.serviceIDLayout)
        
        self.metaLayout.addWidget(self.serviceIDGroupBox)
        
               
        self.servicePublisherLayout = QtGui.QVBoxLayout()
        self.servicePublisherGroupBox = QtGui.QGroupBox("Publisher Details")
        self.servicePublisherGroupBox.setGeometry(QtCore.QRect(260,60, 494, 285))
        
        self.servicePublisherGroupBox.setLayout(self.servicePublisherLayout)
        
        self.metaLayout.addWidget(self.servicePublisherGroupBox)        
        
        
        #self.metaLayout.setGeometry(QtCore.QRect(4, 25, 530, 600))     
        
  

        #tab_widget = QtGui.QTabWidget() 
    	
        #ogc_get_capabilities_general_tab = QtGui.QWidget() 
                     

                     
        
        
    
#        self.label_service_meta = QtGui.QLabel('Service Identification:')
#        self.label_service_meta.setGeometry(QtCore.QRect(5, 20, 142, 27))
#        
#        self.label_provider_meta = QtGui.QLabel('Provider Identification:')
#        self.label_provider_meta.setGeometry(QtCore.QRect(146, 20, 530, 27))
    

        
        #self.metaLayout.addWidget(self.label_service_meta)
        #self.metaLayout.addWidget(self.label_provider_meta)


        #self.tabs.addTab(ogc_get_capabilities_general_tab, "OGC GetCapabilities") 
    		
        #vbox = QtGui.QVBoxLayout()   
        #vbox.addWidget(tab_widget)     
        #self.setLayout(vbox)     
       
    def center(self): 
        screen = QtGui.QDesktopWidget().screenGeometry() 
        size = self.geometry() 
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def fetchTriggered(self):
        if  self.line_edit_OGC_url.text()  != "":
            self.service = OgcService(self.line_edit_OGC_url.text(), 'sos','1.0.0')
        
        
class OgcConfigurationWidget(SpatialTemporalConfigurationWidget):
    def __init__(self, module, controller,  parent=None):
        SpatialTemporalConfigurationWidget.__init__(self, module, controller, parent)

        self.ogc_common_widget = OgcCommonWidget(module)

        self.tabs.addTab(self.ogc_common_widget, "")
        self.tabs.setTabText(self.tabs.indexOf(self.ogc_common_widget), QtGui.QApplication.translate("OgcConfigurationWidget", "Service Metadata", None, QtGui.QApplication.UnicodeUTF8))
        self.tabs.setTabToolTip(self.tabs.indexOf(self.ogc_common_widget), QtGui.QApplication.translate("OgcConfigurationWidget", "Inspect basic service metadata for your chosen OGC service", None, QtGui.QApplication.UnicodeUTF8))

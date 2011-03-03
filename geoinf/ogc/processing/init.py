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

# vistrails imports
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

# to use for config window
from core.modules.module_configure import StandardModuleConfigurationWidget


# Qt import statements
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# not sure what these do yet but sure we need them
from httplib import *
from urlparse import urlparse
import os, sys, string, tempfile, urllib2, urllib,  mimetypes


class WPSModule(Module):
    
    def __init__(self):
        Module.__init__(self)
    
    def compute(self):
        pass
        
class WpsWidget(QWidget): #,  QtCore.QObject):
    def __init__(self,  parent=None):
        QWidget.__init__(self,  parent)
        self.setObjectName("WpsWidget")
        self.create_config_window()
    
    
        
        # connect object to slots. Dont need it yet
        #QMetaObject.connectSlotsByName()

#app = QApplication(sys.argv)
#qb = WpsWidget()
#qb.show()
#sys.exit(app.exec_())

class WpsConfigurationWidget(StandardModuleConfigurationWidget):
    "for configuration widget on vistrails module"
    def __init__(self, module,  controller,  parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        self.create_config_window()
        self.setObjectName("WpsConfigWidget")
        
    def create_config_window(self):
        self.setWindowTitle("OGC WPS Configuration Widget")
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumSize(593, 442)
        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)
        self.GroupBox1 = QGroupBox("Server Connections")
        self.mainLayout.addWidget(self.GroupBox1, 0, 0, 1, 1)
        self.mainLayout.setMargin(9)
        self.mainLayout.setSpacing(6)
        self.btnNew = QPushButton(self.GroupBox1)
        self.btnNew.setObjectName("btnNew")
        self.btnNew.setText("New")
        self.mainLayout.addWidget(self.btnNew, 1, 1, 1, 1)
        self.btnEdit = QPushButton(self.GroupBox1)
        #self.btnEdit.setEnabled(False)
        self.btnEdit.setObjectName("btnEdit")
        self.btnEdit.setText("Edit")
        self.mainLayout.addWidget(self.btnEdit, 1, 2, 1, 1)
        #spacer - to provide blank space in the layout
        spacerItem = QSpacerItem(171, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.mainLayout.addItem(spacerItem, 1, 4, 1, 1)
        self.btnConnect = QPushButton(self.GroupBox1)
        self.btnConnect.setEnabled(True)
        self.btnConnect.setObjectName("btnConnect")
        self.btnConnect.setText("Connect")
        self.mainLayout.addWidget(self.btnConnect, 1, 0, 1, 1)
        self.btnDelete = QPushButton(self.GroupBox1)
        #self.btnDelete.setEnabled(False)
        self.btnDelete.setObjectName("btnDelete")
        self.btnDelete.setText("Delete")
        self.mainLayout.addWidget(self.btnDelete, 1, 3, 1, 1)
        self.cmbConnections = QComboBox(self.GroupBox1)
        self.cmbConnections.setObjectName("cmbConnections")
        self.mainLayout.addWidget(self.cmbConnections, 0, 0, 1, 5)
        
        self.hboxlayout = QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName("hboxlayout")
        self.mainLayout.addLayout(self.hboxlayout, 3, 0, 1, 1)
        self.btnAbout = QPushButton()
        self.btnAbout.setObjectName("btnAbout")
        self.btnAbout.setText("About")
        self.hboxlayout.addWidget(self.btnAbout)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setEnabled(True)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.hboxlayout.addWidget(self.buttonBox)
        
        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setObjectName("treeWidget")
        self.mainLayout.addWidget(self.treeWidget, 2, 0, 1, 1)
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.headerItem().setText(0,"Identifier")
        self.treeWidget.headerItem().setText(1, "Title")
        self.treeWidget.headerItem().setText(2, "Abstract")


###############################################################################
## the function initialize is called for each package, after all
## packages have been loaded. It is used to register the module with
## the VisTrails runtime.
## to register module

def initialize(*args, **keywords):

    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()

    # VisTrails cannot currently automatically detect your derived
    # classes, and the ports that they support as input and
    # output. Because of this, you as a module developer need to let
    # VisTrails know that you created a new module. This is done by calling
    # function addModule:
    reg.add_module(WPSModule, configureWidgetType=WpsConfigurationWidget)

    # In a similar way, you need to report the ports the module wants
    # to make available. This is done by calling addInputPort and
    # addOutputPort appropriately. These calls only show how to set up
    # one-parameter ports. We'll see in later tutorials how to set up
    # multiple-parameter plots.
    ##reg.add_input_port(PythonWmsWidget, "WMS url",
                     ##(core.modules.basic_modules.String, 'the wms url'))
    
    ##reg.add_output_port(PythonWmsWidget, "result",
                      ##(core.modules.basic_modules.String, 'the result'))

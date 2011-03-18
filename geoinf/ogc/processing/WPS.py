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
"""This module provides an OGC (Open Geospatial Consortium) Web Processing Service
(WPS) Client via pyWPS.
"""

# vistrails imports
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

# to use for config window
from core.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
import init

# Qt import statements
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Qt imports for wpstools
from PyQt4.QtNetwork import *
from PyQt4 import QtXml

# not sure what these do yet but sure we need them

# TO DO - PLEASE DONT USE "from xxx import *"  - rather "from xxx import A,B.C"

from httplib import *
from urlparse import urlparse
import os, sys, string, tempfile, urllib2, urllib,  mimetypes


class WPS(Module):

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        pass

class WpsWidget(QWidget): #,  QtCore.QObject):
    def __init__(self,  parent=None):
        QWidget.__init__(self,  parent)
        self.setObjectName("WpsWidget")


class WPSConfigurationWidget(StandardModuleConfigurationWidget):
    "for configuration widget on vistrails module"
    def __init__(self, module,  controller,  parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        self.setObjectName("WpsConfigWidget")
        self.create_config_window()
        #self.doc = QtXml.QDomDocument()

    #####################################################
    ## Config widget
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
        """Do not need the NEW, EDIT, DELETE buttons for now"""
        ##self.btnNew = QPushButton(self.GroupBox1)
        ##self.btnNew.setObjectName("btnNew")
        ##self.btnNew.setText("New")
        ##self.mainLayout.addWidget(self.btnNew, 2, 1, 1, 1)
        ##self.btnEdit = QPushButton(self.GroupBox1)
        #self.btnEdit.setEnabled(False)
        ##self.btnEdit.setObjectName("btnEdit")
        ##self.btnEdit.setText("Edit")
        ##self.mainLayout.addWidget(self.btnEdit, 2, 2, 1, 1)
        #spacer - to provide blank space in the layout
        spacerItem = QSpacerItem(171, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.mainLayout.addItem(spacerItem, 3, 4, 1, 1)
        self.btnConnect = QPushButton(self.GroupBox1)
        self.btnConnect.setEnabled(True)
        self.btnConnect.setObjectName("btnConnect")
        self.btnConnect.setText("Connect")
        self.mainLayout.addWidget(self.btnConnect, 3, 0, 1, 1)
        ##self.btnDelete = QPushButton(self.GroupBox1)
        #self.btnDelete.setEnabled(False)
        ##self.btnDelete.setObjectName("btnDelete")
        ##self.btnDelete.setText("Delete")
        ##self.mainLayout.addWidget(self.btnDelete, 2, 3, 1, 1)

        """decided to change the comboBox to a  line edit because at runtime will not be
        chosing from a list bt rather parsing a url"""
        ##self.cmbConnections = QComboBox(self.GroupBox1)
        ##self.cmbConnections.setObjectName("cmbConnections")
        ##self.mainLayout.addWidget(self.cmbConnections, 1, 0, 1, 5)
        self.mainLayout.addWidget(QLabel('WPS URL:'), 1, 0, 1, 1)
        self.URLConnect= QLineEdit(' ')
        self.URLConnect.setEnabled(True) #sets it not to be editable
        self.mainLayout.addWidget(self.URLConnect, 1,1, 1, -1)

        #self.mainLayout.addWidget(QLabel('Connection Name:'), 2, 0, 1, 1)
        #self.URLName= QLineEdit(' ')
        #self.URLName.setEnabled(True) #sets it not to be editable
        #self.mainLayout.addWidget(self.URLName, 2,1, 1, -1)

        self.mainLayout.addWidget(QLabel('WPS Version:'), 2, 0, 1, 1)
        self.launchversion = QComboBox()
        self.launchversion.addItems(['1.0.0',])
        self.mainLayout.addWidget(self.launchversion, 2,1, 1, 1)

        #self.hboxlayout = QHBoxLayout()
        #self.hboxlayout.setSpacing(6)
        #self.hboxlayout.setMargin(0)
        #self.hboxlayout.setObjectName("hboxlayout")
        #self.mainLayout.addLayout(self.hboxlayout, 3, 0, 1, 1)
        self.btnAbout = QPushButton()
        self.btnAbout.setObjectName("btnAbout")
        self.btnAbout.setText("About")
        self.mainLayout.addWidget(self.btnAbout, 5, 0, 1, 1)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.mainLayout.addItem(spacerItem1, 5, 2, 1, 1)
        """self.buttonBox = QDialogButtonBox()
        self.buttonBox.setEnabled(True)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.mainLayout.addWidget(self.buttonBox, 4, 4, 1, 1)
        """
        self.btnCancel = QPushButton('&Cancel', self)
        #self.btnCancel.setText("Cancel")
        self.btnCancel.setAutoDefault(False)
        self.btnCancel.setShortcut('Esc')
        self.btnCancel.setMinimumWidth(100)
        self.btnCancel.setMaximumWidth(100)
        self.mainLayout.addWidget(self.btnCancel, 5, 4, 1, 1)

        self.btnOk = QPushButton('&OK', self)
        #self.btnOk.setText("OK")
        self.btnOk.setMinimumWidth(100)
        self.btnOk.setMaximumWidth(100)
        self.btnOk.setAutoDefault(False)
        self.mainLayout.addWidget(self.btnOk, 5, 5, 1, 1)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setObjectName("treeWidget")
        self.mainLayout.addWidget(self.treeWidget, 4, 0, 1, -1)
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.headerItem().setText(0,"Identifier")
        self.treeWidget.headerItem().setText(1, "Title")
        self.treeWidget.headerItem().setText(2, "Abstract")


        # Signals
        ##Connect button
        self.connect(
            self.btnConnect,
            SIGNAL('clicked(bool)'),
            self.connectServer
            )

        ## OK button
        self.connect(
            self.btnOk,
            SIGNAL('clicked(bool)'),
            self.buttonBox_accepted
            )
        ## Cancel Button
        self.connect(
            self.btnCancel,
            SIGNAL('clicked(bool)'),
            self.close
            )

    #######################################
    #### Connecting to the WPS Server and accessing capabilities

    #def btnConnect_clicked(self):
        #self.connectServer()

    def connectServer(self, connection):
        """this is where to use code for adding items to treeWidget
        see qgswps.py:: createCapabilities Gui"""

        print "show me the URL"

        connection = self.URLConnect.text()
        # pass version here
        version = self.launchversion.currentText()

        print connection

        if not self.webConnectionExists(connection):
            return 0

        print connection

        itemListAll = self.getCapabilities(connection)

        #    QMessageBox.information(None, '', itemListAll)
        self.initTreeWPSServices(itemListAll)

    def webConnectionExists(self, connection):
        try:
            xmlString = self.getServiceXML(connection,"GetCapabilities")
            print 'connection exists'
            return True
        except:
            QMessageBox.critical(None,'','Web Connection Failed')
            return False

    def  getServiceXML(self, name, request, identifier=None):
        """ Gets Server and Connection Info from Stored Server Connections
        Param: String ConnectionName
        Return: Array Server Information (http,www....,/cgi-bin/...,Post||Get,Service Version)
        """
        print 'getServiceXML - name\n', name
        print 'getServiceXML - request\n', request

        result = self.getServer(name)
        print 'getServiceXML - result\n', result

        path = result["path"]
        server = result["server"]
        method = result["method"]
        version = result["version"]
        if identifier:
            myRequest = "?Request="+request+"&identifier="+identifier+"&Service=WPS&Version="+version
        else:
            myRequest = "?Request="+request+"&Service=WPS&Version="+version

        myPath = path+myRequest
        print 'getServiceXML - myPath\n', myPath

        self.verbindung = HTTPConnection(str(server))
        print "self.verbindung\n", self.verbindung

        print "about to call request\n",str(method),str(myPath)
        foo = self.verbindung.request(str(method),str(myPath))

        print "foo\n",foo

        results = self.verbindung.getresponse()
        print "results\n", results

        #print result
        print 'endXML'
        return results.read()

    def getServer(self, name):
        """get server name"""

        settings = QSettings()
        # name = self.URLName.text() # this needs to be passed down from connection
        print 'getserver -name\n',name

        myURL = urlparse(str(name))
        print myURL

        mySettings = "/WPS/"+name
        #    settings.setValue("WPS/connections/selected", QVariant(name) )
        ##settings.setValue(mySettings+"/scheme",  QVariant(myURL.scheme))
        ##settings.setValue(mySettings+"/server",  QVariant(myURL.netloc))
        ##settings.setValue(mySettings+"/path", QVariant(myURL.path))
        settings.setValue(mySettings+"/method",QVariant("GET"))

        ##mySettings =  name # "/WPS/" +name
        print 'getserver - mysettings\n',mySettings

        result = {}
        result["scheme"] = myURL.scheme #str(settings.value(mySettings+"/scheme").toString()) # str(mySettings+"/scheme")
        result["server"] = myURL.netloc # str(mySettings+"/server") # str(settings.value(mySettings+"/server").toString()) #
        result["path"] = myURL.path #str(settings.value(mySettings+"/path").toString()) # str(mySettings+"/path") #
        result["method"] = str(settings.value(mySettings+"/method").toString()) #str(mySettings+"/method")
        result["version"] = str(self.launchversion.currentText()) # str(mySettings+"/version") #settings.value(mySettings+"/version").toString()

        print 'getserver - result\n',result

        return result


    def getCapabilities(self,  connection):
        xmlString = self.getServiceXML(connection, "GetCapabilities")
        #print xmlString
        self.doc = QtXml.QDomDocument()
        test = self.doc.setContent(xmlString,  True)
        #test parsing of xml doc
        if test == True:
            print 'XML document parsed'
        else:
            print 'document not parsed'

        if self.getServiceVersion() != "1.0.0":
            QMessageBox.information(None, 'Error', 'Only WPS Version 1.0.0 is supprted')
            return 0

        version    = self.doc.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","Process")
        title      = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title")
        identifier = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier")
        abstract   = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Abstract")

        itemListAll = []

        print itemListAll

        for i in range(version.size()):
            print 'test loop'
            v_element = version.at(i).toElement()
            print v_element.text()
            i_element = identifier.at(i).toElement()
            print i_element.text()
            t_element = title.at(i+1).toElement()
            print t_element.text()
            a_element = abstract.at(i+1).toElement()
            print a_element.text()
            itemList = []
            itemList.append(i_element.text())
            itemList.append(t_element.text())
            itemList.append(a_element.text())
            # print i_element.text()
            itemListAll.append(itemList)

        return itemListAll

    def getServiceVersion(self):
        #self.doc = QtXml.QDomDocument()
        #root = self.doc.documentElement()
        version = self.launchversion.currentText() #root.attribute("version")
        return version

    def initTreeWPSServices(self, taglist):
        self.treeWidget.setColumnCount(self.treeWidget.columnCount())
        itemList = []
        for items in taglist:
            item = QTreeWidgetItem()
            ident = unicode(items[0],'latin1')
            title = unicode(items[1],'latin1')
            abstract = unicode(items[2],'latin1')
            item.setText(0,ident.strip())
            item.setText(1,title.strip())
            item.setText(2,abstract.strip())
            itemList.append(item)
        self.treeWidget.addTopLevelItems(itemList)


    """def initWpsConnections(self):
        ##    self.btnOk.setEnabled(False)
        #self.btnConnect.setEnabled(False)
        settings = QSettings()
        #settings.beginGroup("WPS")
        connections = settings.childGroups()
        #self.cmbConnections.clear()
        self.URLConnect.addItems(connections)


        if self.cmbConnections.size() > 0:
            self.btnConnect.setEnabled(True)
            self.btnEdit.setEnabled(True)
            self.btnDelete.setEnabled(True)
        return 1
        """

    #######################################################################
    ## Open the Process GUI
    def buttonBox_accepted(self):
        #pass
        print 'Open process GUI'
        #call processGUI function
        self.process = WPSProcessing()
        self.process.processGUI()

    #######################################################################

    def getDescription(self):
        pass

    #########################################################################
    ## Processing Class

class WPSProcessing():

    def processGUI(self):
        print 'process dummy'
        #pass

    def processTools(self):
        pass

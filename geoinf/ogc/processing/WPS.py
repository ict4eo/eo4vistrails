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
            self.okButton_clicked
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

    #######################################################################
    ## Open the Process GUI
    def okButton_clicked(self, bool):
        """ Use code to create process gui - Create the GUI for a selected WPS process based on the DescribeProcess
       response document. Mandatory inputs are marked as red, default is black"""
        #pass
        print 'OPEN PROCESS GUI'
        #call processGUI function
        
        name= self.URLConnect.text()
        item= self.treeWidget.currentItem()

        #self.process = WPSProcessing()
        #self.process.create_process_GUI(self, pName, item)
        ####Will need to move this to class WPSProcessing later when refactoring
        #self.create_process_GUI(self, name, item)
        
        #def create_process_GUI(self,name, item):

        #pass
       
        try:
            self.processIdentifier = item.text(0)
            print self.processIdentifier
        except:
            QMessageBox.warning(None,'',QCoreApplication.translate("QgsWps",'Please select a Process'))
        #return 0
        
        print 'test inputs and outputs'
        
        # Lists which store the inputs and meta information (format, occurs, ...)
        # This list is initialized every time the GUI is created
        self.complexInputComboBoxList = [] # complex input for single raster and vector maps
        self.complexInputListWidgetList = [] # complex input for multiple raster and vector maps
        self.complexInputTextBoxList = [] # complex inpt of type text/plain
        self.literalInputComboBoxList = [] # literal value list with selectable answers
        self.literalInputLineEditList = [] # literal value list with single text line input
        self.complexOutputComboBoxList = [] # list combo box
        self.inputDataTypeList = {}
        self.inputsMetaInfo = {} # dictionary for input metainfo, key is the input identifier
        self.outputsMetaInfo = {} # dictionary for output metainfo, key is the output identifier
        self.outputDataTypeList = {}

        self.processName = name
        
        
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        # Recive the XML process description
        self.pDoc = QtXml.QDomDocument()
        self.pDoc.setContent(self.getServiceXML(self.processName,"DescribeProcess",self.processIdentifier), True)     
        DataInputs = self.pDoc.elementsByTagName("Input")
        DataOutputs = self.pDoc.elementsByTagName("Output")
        

        # Create the layouts and the scroll area
        ##self.dlgProcess = QgsWpsDescribeProcessGui(self.dlg, flags) ## don't need this now, maybe later
        self.dlgProcess = QDialog()
        self.dlgProcessLayout = QGridLayout()
        # Two tabs, one for the process inputs and one for the documentation
        # TODO: add a tab for literal outputs
        self.dlgProcessTab = QTabWidget()
        self.dlgProcessTabFrame = QFrame()
        self.dlgProcessTabFrameLayout = QGridLayout()
        # The process description can be very long, so we make it scrollable
        self.dlgProcessScrollArea = QScrollArea(self.dlgProcessTab)

        self.dlgProcessScrollAreaWidget = QFrame()
        self.dlgProcessScrollAreaWidgetLayout = QGridLayout()

        # First part of the gui is a short overview about the process
        identifier, title, abstract = self.getIdentifierTitleAbstractFromElement(self.pDoc)
        self.addIntroduction(identifier, title)
        
        # If no Input Data  are requested
        if DataInputs.size()==0:
            self.startProcess()
        #return 0
        
        print 'add intro test'
  
        # Generate the input GUI buttons and widgets
        self.generateProcessInputsGUI(DataInputs)
        # Generate the editable outpt widgets, you can set the output to none if it is not requested
        self.generateProcessOutputsGUI(DataOutputs)
    
        self.dlgProcessScrollAreaWidgetLayout.setSpacing(10)
        self.dlgProcessScrollAreaWidget.setLayout(self.dlgProcessScrollAreaWidgetLayout)
        self.dlgProcessScrollArea.setWidget(self.dlgProcessScrollAreaWidget)
        self.dlgProcessScrollArea.setWidgetResizable(True)

        self.dlgProcessTabFrameLayout.addWidget(self.dlgProcessScrollArea)

        self.addOkCancelButtons()

        self.dlgProcessTabFrame.setLayout(self.dlgProcessTabFrameLayout)
        self.dlgProcessTab.addTab(self.dlgProcessTabFrame, "Process")

        self.addDocumentationTab(abstract)

        self.dlgProcessLayout.addWidget(self.dlgProcessTab)
        self.dlgProcess.setLayout(self.dlgProcessLayout)
        self.dlgProcess.setGeometry(QRect(190,100,800,600))
        self.dlgProcess.show()
        
        
    def generateProcessInputsGUI(self, DataInputs):
        """Generate the GUI for all Inputs defined in the process description XML file"""
        # Create the complex inputs at first
        for i in range(DataInputs.size()):
            f_element = DataInputs.at(i).toElement()

            inputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)

            complexData = f_element.elementsByTagName("ComplexData")
            minOccurs = int(f_element.attribute("minOccurs"))
            maxOccurs = int(f_element.attribute("maxOccurs"))

            # Iterate over all complex inputs and add combo boxes, text boxes or list widgets 
            if complexData.size() > 0:
                # Das i-te ComplexData Objekt auswerten
                complexDataTypeElement = complexData.at(0).toElement()
                complexDataFormat = self.getDefaultMimeType(complexDataTypeElement)
                supportedComplexDataFormat = self.getSupportedMimeTypes(complexDataTypeElement)

                # Store the input formats
                self.inputsMetaInfo[inputIdentifier] = supportedComplexDataFormat
                self.inputDataTypeList[inputIdentifier] = complexDataFormat

                # Attach the selected vector or raster maps
                #if self.isMimeTypeVector(complexDataFormat["MimeType"]) != None:
                # Vector inputs
                    #layerNamesList = self.getLayerNameList(0)
                    #if maxOccurs == 1:
                        #self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
                    #else:
                        #self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
                #elif self.isMimeTypeText(complexDataFormat["MimeType"]) != None:
                    # Text inputs
                    #self.complexInputTextBoxList.append(self.addComplexInputTextBox(title, inputIdentifier, minOccurs))
                #elif self.isMimeTypeRaster(complexDataFormat["MimeType"]) != None:
                    # Raster inputs
                    #layerNamesList = self.getLayerNameList(1)
                    #if maxOccurs == 1:
                        #self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
                    #else:
                        #self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
                #else:
                    # We assume text inputs in case of an unknown mime type
                    #self.complexInputTextBoxList.append(self.addComplexInputTextBox(title, inputIdentifier, minOccurs))            

        # Create the literal inputs as second
        for i in range(DataInputs.size()):
            f_element = DataInputs.at(i).toElement()

            inputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)

            literalData = f_element.elementsByTagName("LiteralData")
            minOccurs = int(f_element.attribute("minOccurs"))
            maxOccurs = int(f_element.attribute("maxOccurs"))

            if literalData.size() > 0:
                allowedValuesElement = literalData.at(0).toElement()
                aValues = allowedValuesElement.elementsByTagNameNS("http://www.opengis.net/ows/1.1","AllowedValues")
                dValue = str(allowedValuesElement.elementsByTagName("DefaultValue").at(0).toElement().text())
                print "Checking allowed values " + str(aValues.size())
                if aValues.size() > 0:
                    valList = self.allowedValues(aValues)
                    if len(valList) > 0:
                        if len(valList[0]) > 0:
                            self.literalInputComboBoxList.append(self.addLiteralComboBox(title, inputIdentifier, valList, minOccurs))
                        else:
                            self.literalInputLineEditList.append(self.addLiteralLineEdit(title, inputIdentifier, minOccurs, str(valList)))
                else:
                    self.literalInputLineEditList.append(self.addLiteralLineEdit(title, inputIdentifier, minOccurs, dValue))

    # At last, create the bounding box inputs
        for i in range(DataInputs.size()):
            f_element = DataInputs.at(i).toElement()

            inputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)
      
            bBoxData = f_element.elementsByTagName("BoundingBoxData")
            minOccurs = int(f_element.attribute("minOccurs"))
            maxOccurs = int(f_element.attribute("maxOccurs"))

            if bBoxData.size() > 0:
                crsListe = []
                bBoxElement = bBoxData.at(0).toElement()
                defaultCrsElement = bBoxElement.elementsByTagName("Default").at(0).toElement()
                defaultCrs = defaultCrsElement.elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href")
                crsListe.append(defaultCrs)
                self.addLiteralLineEdit(title+"(minx,miny,maxx,maxy)", inputIdentifier, minOccurs)

                supportedCrsElements = bBoxElement.elementsByTagName("Supported")

                for i in range(supportedCrsElements.size()):
                    crsListe.append(supportedCrsElements.at(i).toElement().elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href"))

                    self.literalInputComboBoxList.append(self.addLiteralComboBox("Supported CRS", inputIdentifier,crsListe, minOccurs))


        self.addCheckBox(QCoreApplication.translate("QgsWps","Process selected objects only"), QCoreApplication.translate("QgsWps","Selected"))
        
    def generateProcessOutputsGUI(self, DataOutputs):
        print 'get outputs'
        
    def addOkCancelButtons(self):
        #print 'ok'
        groupbox = QFrame()
        layout = QHBoxLayout()

        btnOk = QPushButton(groupbox)
        btnOk.setText(QString("Run"))
        btnOk.setMinimumWidth(100)
        btnOk.setMaximumWidth(100)

        btnCancel = QPushButton(groupbox)
        btnCancel.setText("Back")
        btnCancel.setMinimumWidth(100)
        btnCancel.setMaximumWidth(100)

        layout.addWidget(btnOk)
        layout.addStretch(1)
        layout.addWidget(btnCancel)

        groupbox.setLayout(layout)
        self.dlgProcessTabFrameLayout.addWidget(groupbox)

        QObject.connect(btnOk,SIGNAL("clicked()"),self.startProcess)
        QObject.connect(btnCancel,SIGNAL("clicked()"),self.dlgProcess.close)
        
    def startProcess(self):
        print 'start'
        
    def addDocumentationTab(self, abstract):
        # Check for URL
        if str(abstract).find("http://") == 0:
            textBox = QtWebKit.QWebView(self.dlgProcessTab)
            textBox.load(QUrl(abstract))
            textBox.show()
        else:
            textBox = QTextBrowser(self.dlgProcessTab)
            textBox.setText(QString(abstract))

        self.dlgProcessTab.addTab(textBox, "Documentation")
        
    def addComplexInputComboBox(self, title, name, mimeType, namesList, minOccurs):
        """Adds a combobox to select a raster or vector map as input to the process tab"""
        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        #groupbox.setTitle(name)
        groupbox.setMinimumHeight(25)
        layout = QHBoxLayout()
      
        # This input is optional
        if minOccurs == 0:
            namesList.append("<None>")

        comboBox = QComboBox(groupbox)
        comboBox.addItems(namesList)
        comboBox.setObjectName(name)
        comboBox.setMinimumWidth(179)
        comboBox.setMaximumWidth(179)
        comboBox.setMinimumHeight(25)
      
        myLabel = QLabel(self.dlgProcessScrollAreaWidget)
        myLabel.setObjectName("qLabel"+name)

        if minOccurs > 0:
            string = "[" + name + "] <br>" + title
            myLabel.setText("<font color='Red'>" + string + "</font>" + " <br>(" + mimeType + ")")
        else:
            string = "[" + name + "]\n" + title + " <br>(" + mimeType + ")"
            myLabel.setText(string)

        myLabel.setWordWrap(True)
        myLabel.setMinimumWidth(400)
        myLabel.setMinimumHeight(25)

        layout.addWidget(myLabel)
        layout.addStretch(1)
        layout.addWidget(comboBox)
      
        groupbox.setLayout(layout)

        self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

        return comboBox
        
    def addComplexInputListWidget(self, title, name, mimeType, namesList, minOccurs):
        """Adds a widget for multiple raster or vector selections as inputs to the process tab"""
        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        #groupbox.setTitle(name)
        groupbox.setMinimumHeight(25)
        layout = QHBoxLayout()

        # This input is optional
        if minOccurs == 0:
            namesList.append("<None>")

        listWidget = QListWidget(groupbox)
        listWidget.addItems(namesList)
        listWidget.setObjectName(name)
        listWidget.setMinimumWidth(179)
        listWidget.setMaximumWidth(179)
        listWidget.setMinimumHeight(120)
        listWidget.setMaximumHeight(120)
        listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        myLabel = QLabel(self.dlgProcessScrollAreaWidget)
        myLabel.setObjectName("qLabel"+name)

        if minOccurs > 0:
            string = "[" + name + "] <br>" + title
            myLabel.setText("<font color='Red'>" + string + "</font>" + " <br>(" + mimeType + ")")
        else:
            string = "[" + name + "]\n" + title + " <br>(" + mimeType + ")"
            myLabel.setText(string)

        myLabel.setWordWrap(True)
        myLabel.setMinimumWidth(400)
        myLabel.setMinimumHeight(25)

        layout.addWidget(myLabel)
        layout.addStretch(1)
        layout.addWidget(listWidget)

        groupbox.setLayout(layout)

        self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

        return listWidget
        
    def addComplexInputTextBox(self, title, name, minOccurs):
        """Adds a widget to insert text as complex inputs to the process tab"""
        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        #groupbox.setTitle(name)
        groupbox.setMinimumHeight(50)
        layout = QHBoxLayout()

        textBox = QTextEdit(groupbox)
        textBox.setObjectName(name)
        textBox.setMinimumWidth(200)
        textBox.setMaximumWidth(200)
        textBox.setMinimumHeight(50)

        myLabel = QLabel(self.dlgProcessScrollAreaWidget)
        myLabel.setObjectName("qLabel"+name)

        if minOccurs > 0:
            string = "[" + name + "] <br>" + title
            myLabel.setText("<font color='Red'>" + string + "</font>")
        else:
            string = "[" + name + "]\n" + title
            myLabel.setText(string)

        myLabel.setWordWrap(True)
        myLabel.setMinimumWidth(400)
        myLabel.setMinimumHeight(25)

        layout.addWidget(myLabel)
        layout.addStretch(1)
        layout.addWidget(textBox)

        groupbox.setLayout(layout)

        self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

        return textBox
        
    def addLiteralComboBox(self, title, name, namesList, minOccurs):
        
        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        #groupbox.setTitle(name)
        groupbox.setMinimumHeight(25)
        layout = QHBoxLayout()

        comboBox = QComboBox(self.dlgProcessScrollAreaWidget)
        comboBox.addItems(namesList)
        comboBox.setObjectName(name)
        comboBox.setMinimumWidth(179)
        comboBox.setMaximumWidth(179)
        comboBox.setMinimumHeight(25)

        myLabel = QLabel(self.dlgProcessScrollAreaWidget)
        myLabel.setObjectName("qLabel"+name)

        if minOccurs > 0:
            string = "[" + name + "] <br>" + title
            myLabel.setText("<font color='Red'>" + string + "</font>")
        else:
            string = "[" + name + "]\n" + title
            myLabel.setText(string)
        
        myLabel.setWordWrap(True)
        myLabel.setMinimumWidth(400)
        myLabel.setMinimumHeight(25)

        layout.addWidget(myLabel)
        layout.addStretch(1)
        layout.addWidget(comboBox)

        groupbox.setLayout(layout)

        self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

        return comboBox
        
    def addLiteralLineEdit(self, title, name, minOccurs, defaultValue=""):
        
        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        #groupbox.setTitle(name)
        groupbox.setMinimumHeight(25)
        layout = QHBoxLayout()
        
        myLineEdit = QLineEdit(groupbox)
        myLineEdit.setObjectName(name)
        myLineEdit.setMinimumWidth(179)
        myLineEdit.setMaximumWidth(179)
        myLineEdit.setMinimumHeight(25)
        myLineEdit.setText(defaultValue)
        
        myLabel = QLabel(groupbox)
        myLabel.setObjectName("qLabel"+name)
        
        if minOccurs > 0:
            string = "[" + name + "] <br>" + title
            myLabel.setText("<font color='Red'>" + string + "</font>")
        else:
            string = "[" + name + "]\n" + title
            myLabel.setText(string)
        
        myLabel.setWordWrap(True)
        myLabel.setMinimumWidth(400)
        myLabel.setMinimumHeight(25)
        
        layout.addWidget(myLabel)
        layout.addStretch(1)
        layout.addWidget(myLineEdit)
        
        groupbox.setLayout(layout)
        
        self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)
        
        return myLineEdit
        
    def addCheckBox(self,  title,  name):
        
        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        #groupbox.setTitle(name)
        groupbox.setMinimumHeight(25)
        layout = QHBoxLayout()
      
        myCheckBox = QCheckBox(groupbox)
        myCheckBox.setObjectName("chkBox"+name)
        myCheckBox.setChecked(False)
        
        myLabel = QLabel(groupbox)
        myLabel.setObjectName("qLabel"+name)  
        myLabel.setText("(" + name + ")" + "\n" + title)
        myLabel.setMinimumWidth(400)
        myLabel.setMinimumHeight(25)
        myLabel.setWordWrap(True)
        
        layout.addWidget(myLabel)
        layout.addStretch(1)
        layout.addWidget(myCheckBox)
        
        groupbox.setLayout(layout)
        
        self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)
        
    def getIdentifierTitleAbstractFromElement(self, element):
        inputIdentifier = element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier").at(0).toElement().text().simplified()
        title      = element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title").at(0).toElement().text().simplified()
        abstract   = element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Abstract").at(0).toElement().text().simplified()
        
        return inputIdentifier, title, abstract
        
    def addIntroduction(self,  name, title):
        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        groupbox.setTitle(name)
        layout = QVBoxLayout()

        myLabel = QLabel(groupbox)
        myLabel.setObjectName("qLabel"+name)
        myLabel.setText(QString(title))
        myLabel.setMinimumWidth(600)
        myLabel.setMinimumHeight(25)
        myLabel.setWordWrap(True)

        layout.addWidget(myLabel)

        groupbox.setLayout(layout)

        self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)
        
    def getDefaultMimeType(self,  inElement):
        myElement = inElement.elementsByTagName("Default").at(0).toElement()
        return self._getMimeTypeSchemaEncoding(myElement)
        
    def getSupportedMimeTypes(self,  inElement):
        mimeTypes = []
        myElements = inElement.elementsByTagName("Supported").at(0).toElement()
        myFormats = myElements.elementsByTagName('Format')
        for i in range(myFormats.size()):
            myElement = myFormats.at(i).toElement()
            mimeTypes.append(self._getMimeTypeSchemaEncoding(myElement))
        return mimeTypes
        
    def _getMimeTypeSchemaEncoding(self,  Element):
        mimeType = ""
        schema = ""
        encoding = ""
        try:
            mimeType = str(Element.elementsByTagName("MimeType").at(0).toElement().text().simplified().toLower())
            schema = str(Element.elementsByTagName("Schema").at(0).toElement().text().simplified().toLower())
            encoding = str(Element.elementsByTagName("Encoding").at(0).toElement().text().simplified().toLower())
        except:
            pass
    
        return {"MimeType":mimeType,"Schema":schema,"Encoding":encoding}
        
    def isMimeTypeVector(self, mimeType):
        """Check for vector input. Zipped shapefiles must be extracted"""
        for vectorType in VECTOR_MIMETYPES:
            if mimeType.upper() == vectorType["MIMETYPE"]:
                return vectorType["GDALID"]
        return None
        
    def getLayerNameList(self, dataType=0, all=False):
        myLayerList = []    
        
        if all:
            mapLayers = QgsMapLayerRegistry.instance().mapLayers()      
            for (k, layer) in mapLayers.iteritems():
                myLayerList.append(layer.name())
        else:
            mc=self.iface.mapCanvas()
            nLayers=mc.layerCount()
      
            for l in range(nLayers):
                # Nur die Layer des gewnschten Datentypes auswhlen 0=Vectorlayer 1=Rasterlayer
                if mc.layer(l).type() == dataType:
                    myLayerList.append(mc.layer(l).name())
    
        return myLayerList
        
    def allowedValues(self, aValues):
        valList = []

        # Manage a value list defined by a range
        value_element = aValues.at(0).toElement()
        v_range_element = value_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Range")
     
        if v_range_element.size() > 0:
            min_val = value_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","MinimumValue").at(0).toElement().text()
            max_val = value_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","MaximumValue").at(0).toElement().text()
        #       QMessageBox.information(None, '', min_val+' - '+max_val)
            for n in range(int(min_val),int(max_val)+1):
                myVal = QString()
                myVal.append(str(n))
                valList.append(myVal)

        # Manage a value list defined by single values
        v_element = value_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Value")
        if v_element.size() > 0:
            for n in range(v_element.size()):
                mv_element = v_element.at(n).toElement() 
                valList.append(unicode(mv_element.text(),'latin1').strip())
         
        print str(valList)
        return valList 
        
    def isMimeTypeText(self, mimeType):
        """Check for text file input"""
        if mimeType.upper() == "TEXT/PLAIN":
            return "TXT"
        else:
            return None
            
    def isMimeTypeRaster(self, mimeType):
        """Check for raster input"""
        for rasterType in RASTER_MIMETYPES:
            if mimeType.upper() == rasterType["MIMETYPE"]:
                return rasterType["GDALID"]
        return None
        

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

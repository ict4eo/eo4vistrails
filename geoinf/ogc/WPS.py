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

Much of this code comes directly from the QGIS WPS Plugin (dated 09 November 2009)

"""
# library
import mimetypes
import os
import sys
import string
import tempfile
import urllib2
import urllib
from httplib import * #??? are we using this
from urlparse import urlparse
# third party
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyQt4 import QtXml
from qgis.core import *
from qgis.gui import *
# vistrails
import core.modules.module_registry
from core.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
# eo4vistrails
# local
import init


# All supported import raster formats
RASTER_MIMETYPES =        [{"MIMETYPE":"IMAGE/TIFF", "GDALID":"GTiff"},
                           {"MIMETYPE":"IMAGE/PNG", "GDALID":"PNG"}, \
                           {"MIMETYPE":"IMAGE/GIF", "GDALID":"GIF"}, \
                           {"MIMETYPE":"IMAGE/JPEG", "GDALID":"JPEG"}, \
                           {"MIMETYPE":"IMAGE/GEOTIFF", "GDALID":"GTiff"}, \
                           {"MIMETYPE":"APPLICATION/X-ERDAS-HFA", "GDALID":"HFA"}, \
                           {"MIMETYPE":"APPLICATION/NETCDF", "GDALID":"netCDF"}, \
                           {"MIMETYPE":"APPLICATION/X-NETCDF", "GDALID":"netCDF"}, \
                           {"MIMETYPE":"APPLICATION/GEOTIFF", "GDALID":"GTiff"}, \
                           {"MIMETYPE":"APPLICATION/X-GEOTIFF", "GDALID":"GTiff"}]
# All supported input vector formats [mime type, schema]
VECTOR_MIMETYPES =        [{"MIMETYPE":"TEXT/XML", "SCHEMA":"GML", "GDALID":"GML"}, \
                           {"MIMETYPE":"TEXT/XML", "SCHEMA":"KML", "GDALID":"KML"}, \
                           {"MIMETYPE":"APPLICATION/DGN", "SCHEMA":"", "GDALID":"DGN"}, \
                           #{"MIMETYPE":"APPLICATION/X-ZIPPED-SHP", "SCHEMA":"", "GDALID":"ESRI_Shapefile"}, \
                           {"MIMETYPE":"APPLICATION/SHP", "SCHEMA":"", "GDALID":"ESRI_Shapefile"}]
DEBUG = False
DEFAULT_URL = 'http://ict4eo.meraka.csir.co.za/cgi-bin/wps.py'


class WPS(Module):

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        pass


class WpsWidget(QWidget):
    def __init__(self,  parent=None):
        QWidget.__init__(self,  parent)
        self.setObjectName("WpsWidget")


class WPSConfigurationWidget(StandardModuleConfigurationWidget):
    """Configuration widget on vistrails module"""
    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        self.setObjectName("WpsConfigWidget")
        self.create_config_window()
        #self.doc = QtXml.QDomDocument()

    def create_config_window(self):
        """TODO: add doc string"""
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

        """decided to change the comboBox to a line edit because at runtime
        will not be choosing from a list, but rather parsing a url"""
        ##self.cmbConnections = QComboBox(self.GroupBox1)
        ##self.cmbConnections.setObjectName("cmbConnections")
        ##self.mainLayout.addWidget(self.cmbConnections, 1, 0, 1, 5)
        self.mainLayout.addWidget(QLabel('WPS URL:'), 1, 0, 1, 1)
        self.URLConnect = QLineEdit(DEFAULT_URL)
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
        #self.btnAbout = QPushButton()
        #self.btnAbout.setObjectName("btnAbout")
        #self.btnAbout.setText("About")
        #self.mainLayout.addWidget(self.btnAbout, 5, 0, 1, 1)
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
        self.btnCancel.setMinimumWidth(40)
        self.btnCancel.setMaximumWidth(100)
        self.mainLayout.addWidget(self.btnCancel, 5, 4, 1, 1)

        self.btnOk = QPushButton('&OK', self)
        #self.btnOk.setText("OK")
        self.btnOk.setMinimumWidth(40)
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
        #   Connect button
        self.connect(
            self.btnConnect,
            SIGNAL('clicked(bool)'),
            self.connectServer
            )

        #    OK button
        self.connect(
            self.btnOk,
            SIGNAL('clicked(bool)'),
            self.okButton_clicked
            )
        #    Cancel Button
        self.connect(
            self.btnCancel,
            SIGNAL('clicked(bool)'),
            self.close
            )

    def connectServer(self, connection):
        """Add items to treeWidget
        see qgswps.py:: createCapabilities Gui"""
        connection = self.URLConnect.text()
        #print 'WPS:connection', connection
        # pass version here
        version = self.launchversion.currentText()
        if not self.webConnectionExists(connection):
            return 0
        itemListAll = self.getCapabilities(connection)
        #QMessageBox.information(None, '', itemListAll)
        self.initTreeWPSServices(itemListAll)

    def webConnectionExists(self, connection):
        """TODO: add doc string"""
        try:
            xmlString = self.getServiceXML(connection,"GetCapabilities")
            #print 'WPS: connection exists'
            return True
        except:
            QMessageBox.critical(None,'','Web Connection Failed')
            return False

    def getServiceXML(self, name, request, identifier=None):
        """ Gets Server and Connection Info from Stored Server Connections
        Param: String ConnectionName
        Return: Array Server Information (http,www....,/cgi-bin/...,Post||Get,Service Version)
        """
        #print 'WPS: getServiceXML - name/request\n', name, request
        result = self.getServer(name)
        #print 'WPS: getServiceXML - result\n', result
        path = result["path"]
        server = result["server"]
        method = result["method"]
        version = result["version"]
        if identifier:
            myRequest = "?Request="+request+"&identifier="+identifier+"&Service=WPS&Version="+version
        else:
            myRequest = "?Request="+request+"&Service=WPS&Version="+version

        myPath = path+myRequest
        #print 'WPS: getServiceXML - myPath\n', myPath
        self.verbindung = HTTPConnection(str(server))
        #print "WPS: self.verbindung\n", self.verbindung
        #print "WPS: about to call request\n",str(method),str(myPath)
        foo = self.verbindung.request(str(method),str(myPath))
        #print "WPS: foo\n",foo
        results = self.verbindung.getresponse()
        #print "WPS: results\n", results
        return results.read()

    def getServer(self, name):
        """get server name"""

        settings = QSettings()
        # name = self.URLName.text() # this needs to be passed down from connection
        #print 'WPS: getserver -name\n',name

        myURL = urlparse(str(name))
        #print myURL

        mySettings = "/WPS/"+name
        #    settings.setValue("WPS/connections/selected", QVariant(name) )
        ##settings.setValue(mySettings+"/scheme",  QVariant(myURL.scheme))
        ##settings.setValue(mySettings+"/server",  QVariant(myURL.netloc))
        ##settings.setValue(mySettings+"/path", QVariant(myURL.path))
        settings.setValue(mySettings+"/method",QVariant("GET"))
        #print 'WPS: getserver - mysettings\n',mySettings

        result = {}
        result["scheme"] = myURL.scheme #str(settings.value(mySettings+"/scheme").toString()) # str(mySettings+"/scheme")
        result["server"] = myURL.netloc # str(mySettings+"/server") # str(settings.value(mySettings+"/server").toString()) #
        result["path"] = myURL.path #str(settings.value(mySettings+"/path").toString()) # str(mySettings+"/path") #
        result["method"] = str(settings.value(mySettings+"/method").toString()) #str(mySettings+"/method")
        result["version"] = str(self.launchversion.currentText()) # str(mySettings+"/version") #settings.value(mySettings+"/version").toString()

        #print 'WPS: getserver - result\n',result
        return result

    def getCapabilities(self, connection):
        """TODO: add doc string"""
        xmlString = self.getServiceXML(connection, "GetCapabilities")
        #print xmlString
        self.doc = QtXml.QDomDocument()
        test = self.doc.setContent(xmlString, True)
        #test parsing of xml doc
        if test == True:
            print 'WPS: XML document parsed'

        if self.getServiceVersion() != "1.0.0":
            QMessageBox.information(None, 'Error', 'Only WPS Version 1.0.0 is supported')
            return 0

        version    = self.doc.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0","Process")
        title      = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title")
        identifier = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier")
        abstract   = self.doc.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Abstract")

        itemListAll = []
        for i in range(version.size()):
            #print 'WPS: test loop'
            v_element = version.at(i).toElement()
            #print v_element.text()
            i_element = identifier.at(i).toElement()
            #print i_element.text()
            t_element = title.at(i+1).toElement()
            #print t_element.text()
            a_element = abstract.at(i+1).toElement()
            #print a_element.text()
            itemList = []
            itemList.append(i_element.text())
            itemList.append(t_element.text())
            itemList.append(a_element.text())
            #print i_element.text()
            itemListAll.append(itemList)

        return itemListAll
        """link this to parsing?
        else:
            # raise error ???
            return []
        """

    def getServiceVersion(self):
        """TODO: add doc string"""
        #self.doc = QtXml.QDomDocument()
        #root = self.doc.documentElement()
        return self.launchversion.currentText() #root.attribute("version")

    def initTreeWPSServices(self, taglist):
        """TODO: add doc string"""
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

    def okButton_clicked(self, bool):
        """ Use code to create process gui -
        Create the GUI for a selected WPS process based on the DescribeProcess
       response document. Mandatory inputs are marked as red, default is black
       """
        #print 'WPS: OPEN PROCESS GUI'
        name= self.URLConnect.text()
        item= self.treeWidget.currentItem()

        #self.process = WPSProcessing()
        #self.process.create_process_GUI(self, pName, item)
        ####Will need to move this to class WPSProcessing later when refactoring
        #self.create_process_GUI(self, name, item)
        #def create_process_GUI(self,name, item):

        try:
            self.processIdentifier = item.text(0)
            #print self.processIdentifier
        except:
            QMessageBox.warning(None,'',QCoreApplication.translate("QgsWps",'Please select a Process'))

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
        # Receive the XML process description
        self.pDoc = QtXml.QDomDocument()
        self.pDoc.setContent(self.getServiceXML(self.processName,"DescribeProcess",self.processIdentifier), True)
        DataInputs = self.pDoc.elementsByTagName("Input")
        #print DataInputs.size()
        DataOutputs = self.pDoc.elementsByTagName("Output")
        #print DataOutputs.length()

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

        # Generate the input GUI buttons and widgets
        self.generateProcessInputsGUI(DataInputs)
        # Generate the editable outpt widgets, you can set the output to none if it is not requested
        self.generateProcessOutputsGUI(DataOutputs)

        self.dlgProcessScrollAreaWidgetLayout.setSpacing(10)
        self.dlgProcessScrollAreaWidget.setLayout(self.dlgProcessScrollAreaWidgetLayout)
        self.dlgProcessScrollArea.setWidget(self.dlgProcessScrollAreaWidget)
        self.dlgProcessScrollArea.setWidgetResizable(True)

        self.dlgProcessTabFrameLayout.addWidget(self.dlgProcessScrollArea)
        self.dlgProcessTabFrame.setLayout(self.dlgProcessTabFrameLayout)

        self.addOkCancelButtons()

        self.dlgProcessTab.addTab(self.dlgProcessTabFrame, "Process")

        self.addDocumentationTab(abstract)

        self.dlgProcessLayout.addWidget(self.dlgProcessTab)
        self.dlgProcess.setLayout(self.dlgProcessLayout)
        self.dlgProcess.setGeometry(QRect(190,100,800,600))
        self.dlgProcess.show()

    def generateProcessInputsGUI(self, DataInputs):
        """Generate the GUI for all inputs defined in
        the process description XML file"""
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
                if self.isMimeTypeVector(complexDataFormat["MimeType"]) != None:
                # Vector inputs
                    layerNamesList = self.getLayerNameList(0)
                    if maxOccurs == 1:
                        self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
                    else:
                        self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
                elif self.isMimeTypeText(complexDataFormat["MimeType"]) != None:
                    # Text inputs
                    self.complexInputTextBoxList.append(self.addComplexInputTextBox(title, inputIdentifier, minOccurs))
                elif self.isMimeTypeRaster(complexDataFormat["MimeType"]) != None:
                    # Raster inputs
                    layerNamesList = self.getLayerNameList(1)
                    if maxOccurs == 1:
                        self.complexInputComboBoxList.append(self.addComplexInputComboBox(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
                    else:
                        self.complexInputListWidgetList.append(self.addComplexInputListWidget(title, inputIdentifier, str(complexDataFormat), layerNamesList, minOccurs))
                else:
                    # We assume text inputs in case of an unknown mime type
                    self.complexInputTextBoxList.append(self.addComplexInputTextBox(title, inputIdentifier, minOccurs))

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
                #print "WPS: Checking allowed values " + str(aValues.size())
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
        """Generate the GUI for all complex ouputs
        defined in the process description XML file"""

        if DataOutputs.size() < 1:
            return

        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        groupbox.setTitle("Complex output(s)")
        layout = QVBoxLayout()

        # Add all complex outputs
        for i in range(DataOutputs.size()):
            f_element = DataOutputs.at(i).toElement()

            outputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)
            complexOutput = f_element.elementsByTagName("ComplexOutput")

            # Iterate over all complex inputs and add combo boxes, text boxes or list widgets
            if complexOutput.size() > 0:
                # Das i-te ComplexData Objekt auswerten
                complexOutputTypeElement = complexOutput.at(0).toElement()
                complexOutputFormat = self.getDefaultMimeType(complexOutputTypeElement)
                supportedcomplexOutputFormat = self.getSupportedMimeTypes(complexOutputTypeElement)

                # Store the input formats
                self.outputsMetaInfo[outputIdentifier] = supportedcomplexOutputFormat
                self.outputDataTypeList[outputIdentifier] = complexOutputFormat

                widget, comboBox = self.addComplexOutputComboBox(groupbox, outputIdentifier, title, str(complexOutputFormat))
                self.complexOutputComboBoxList.append(comboBox)
                layout.addWidget(widget)

        # Set the layout
        groupbox.setLayout(layout)
        # Add the outputs
        self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

    def addOkCancelButtons(self):
        """TODO: add doc string"""
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
        """Create the execute request"""
        self.doc.setContent(self.getServiceXML(self.processName,"DescribeProcess",self.processIdentifier))
        dataInputs = self.doc.elementsByTagName("Input")
        dataOutputs = self.doc.elementsByTagName("Output")

        QApplication.setOverrideCursor(Qt.WaitCursor)
        result = self.getServer(self.processName)
        scheme = result["scheme"]
        path = result["path"]
        server = result["server"]

        checkBoxes = self.dlgProcess.findChildren(QCheckBox)

        if len(checkBoxes) > 0:
            useSelected = checkBoxes[0].isChecked()

        postString = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
        postString += "<wps:Execute service=\"WPS\" version=\""+ self.getServiceVersion() + "\"" + \
                   " xmlns:wps=\"http://www.opengis.net/wps/1.0.0\"" + \
                   " xmlns:ows=\"http://www.opengis.net/ows/1.1\"" +\
                   " xmlns:xlink=\"http://www.w3.org/1999/xlink\"" +\
                   " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""\
                   " xsi:schemaLocation=\"http://www.opengis.net/wps/1.0.0" +\
                   " http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd\">"

        postString += "<ows:Identifier>"+self.processIdentifier+"</ows:Identifier>\n"
        postString += "<wps:DataInputs>"

        # text/plain inputs
        for textBox in self.complexInputTextBoxList:

        # Do not add undefined inputs
            if textBox == None or str(textBox.document().toPlainText()) == "":
                continue
            postString += self.xmlExecuteRequestInputStart(textBox.objectName())
            postString += "<wps:ComplexData>" + textBox.document().toPlainText() + "</wps:ComplexData>\n"
            postString += self.xmlExecuteRequestInputEnd()

        # Single raster and vector inputs
        for comboBox in self.complexInputComboBoxList:
        # Do not add undefined inputs
            if comboBox == None or unicode(comboBox.currentText(), 'latin1') == "<None>":
                continue

            postString += self.xmlExecuteRequestInputStart(comboBox.objectName())

            # TODO: Check for more types
            mimeType = self.inputDataTypeList[comboBox.objectName()]["MimeType"]
            schema = self.inputDataTypeList[comboBox.objectName()]["Schema"]
            encoding = self.inputDataTypeList[comboBox.objectName()]["Encoding"]

            if self.isMimeTypeVector(mimeType) != None and mimeType == "text/xml":
                postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + "\" enconding=\"" + encoding + "\">"
                postString += self.createTmpGML(comboBox.currentText(), useSelected).replace("> <","><")
                postString = postString.replace("xsi:schemaLocation=\"http://ogr.maptools.org/ qt_temp.xsd\"", "xsi:schemaLocation=\"http://schemas.opengis.net/gml/3.1.1/base/ gml.xsd\"")
            elif self.isMimeTypeVector(mimeType) != None or self.isMimeTypeRaster(mimeType) != None:
                postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"
                postString += self.createTmpBase64(comboBox.currentText())

            postString += "</wps:ComplexData>\n"
            postString += self.xmlExecuteRequestInputEnd()

        # Multiple raster and vector inputs
        for listWidgets in self.complexInputListWidgetList:
        # Do not add undefined inputs
            if listWidgets == None:
                continue

            mimeType = self.inputDataTypeList[listWidgets.objectName()]["MimeType"]
            schema = self.inputDataTypeList[listWidgets.objectName()]["Schema"]
            encoding = self.inputDataTypeList[listWidgets.objectName()]["Encoding"]

        # Iterate over each seletced item
        for i in range(listWidgets.count()):
            listWidget = listWidgets.item(i)
            if listWidget == None or listWidget.isSelected() == False or str(listWidget.text()) == "<None>":
                continue

            postString += self.xmlExecuteRequestInputStart(listWidgets.objectName())

            # TODO: Check for more types
            if self.isMimeTypeVector(mimeType) != None and mimeType == "text/xml":
                postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + "\" enconding=\"" + encoding + "\">"
                postString += self.tools.createTmpGML(listWidget.text(), useSelected).replace("> <","><").replace("http://ogr.maptools.org/ qt_temp.xsd","http://ogr.maptools.org/qt_temp.xsd")
            elif self.isMimeTypeVector(mimeType) != None or self.isMimeTypeRaster(mimeType) != None:
                postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"
                postString += self.createTmpBase64(listWidget.text())

            postString += "</wps:ComplexData>\n"
            postString += self.xmlExecuteRequestInputEnd()

        # Literal data as combo box choice
        for comboBox in self.literalInputComboBoxList:
            if comboBox == None or comboBox.currentText() == "":
                continue
            postString += self.xmlExecuteRequestInputStart(comboBox.objectName())
            postString += "<wps:LiteralData>"+comboBox.currentText()+"</wps:LiteralData>\n"
            postString += self.xmlExecuteRequestInputEnd()

        # Literal data as combo box choice
        for lineEdit in self.literalInputLineEditList:
            if lineEdit == None or lineEdit.text() == "":
                continue
            postString += self.xmlExecuteRequestInputStart(lineEdit.objectName())
            postString += "<wps:LiteralData>"+lineEdit.text()+"</wps:LiteralData>\n"
            postString += self.xmlExecuteRequestInputEnd()
        postString += "</wps:DataInputs>\n"

        # Attach only defined outputs
        if dataOutputs.size() > 0 and len(self.complexOutputComboBoxList) > 0:
            postString += "<wps:ResponseForm>\n"
            # The server should store the result. No lineage should be returned or status
            postString += "<wps:ResponseDocument lineage=\"false\" storeExecuteResponse=\"true\" status=\"false\">\n"

            # Attach ALL literal outputs
            for i in range(dataOutputs.size()):
                f_element = dataOutputs.at(i).toElement()
                outputIdentifier = f_element.elementsByTagName("ows:Identifier").at(0).toElement().text().simplified()
                literalOutputType = f_element.elementsByTagName("LiteralOutput")

                # Complex data is always requested as reference
                if literalOutputType.size() != 0:
                    postString += "<wps:Output>\n"
                    postString += "<ows:Identifier>"+outputIdentifier+"</ows:Identifier>\n"
                    postString += "</wps:Output>\n"

            # Attach selected complex outputs
            for comboBox in self.complexOutputComboBoxList:
                # Do not add undefined outputs
                if comboBox == None or str(comboBox.currentText()) == "<None>":
                    continue
                outputIdentifier = comboBox.objectName()

                mimeType = self.outputDataTypeList[outputIdentifier]["MimeType"]
                schema = self.outputDataTypeList[outputIdentifier]["Schema"]
                encoding = self.outputDataTypeList[outputIdentifier]["Encoding"]

                postString += "<wps:Output asReference=\"true\" mimeType=\"" + mimeType + "\" schema=\"" + schema + "\">"
                postString += "<ows:Identifier>" + outputIdentifier + "</ows:Identifier>\n"
                postString += "</wps:Output>\n"

            postString += "</wps:ResponseDocument>\n"
            postString  += "</wps:ResponseForm>\n"

        postString += "</wps:Execute>\n"

        # This is for debug purpose only
        if DEBUG == True:
            self.tools.popUpMessageBox("Execute request", postString)
            # Write the request into a file
            outFile = open('/tmp/qwps_execute_request.xml', 'w')
            outFile.write(postString)
            outFile.close()

        f = urllib.urlopen( str(scheme)+"://"+str(server)+""+str(path),
            unicode(postString, "latin1").replace('<wps:ComplexData>\n','<wps:ComplexData>'))

        # Read the results back.
        wpsRequestResult = f.read()
        QApplication.restoreOverrideCursor()
        QApplication .setOverrideCursor(Qt.ArrowCursor)
        self.resultHandler(wpsRequestResult)

    def addDocumentationTab(self, abstract):
        """TODO: add doc string"""
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

    def addComplexOutputComboBox(self, widget, name, title, mimeType):
        """Adds a combobox to select a raster or vector map
        as input to the process tab"""

        groupbox = QGroupBox(widget)
        groupbox.setMinimumHeight(25)
        layout = QHBoxLayout()

        namesList = []
        # Generate a unique name for the layer
        #namesList.append(self.uniqueLayerName(self.processIdentifier + "_" + name + "_"))
        namesList.append("<None>")

        comboBox = QComboBox(groupbox)
        comboBox.setEditable(True)
        comboBox.addItems(namesList)
        comboBox.setObjectName(name)
        comboBox.setMinimumWidth(250)
        comboBox.setMaximumWidth(250)
        comboBox.setMinimumHeight(25)

        myLabel = QLabel(widget)
        myLabel.setObjectName("qLabel"+name)

        string = "[" + name + "] <br>" + title
        myLabel.setText("<font color='Green'>" + string + "</font>" + " <br>(" + mimeType + ")")

        myLabel.setWordWrap(True)
        myLabel.setMinimumWidth(400)
        myLabel.setMinimumHeight(25)

        layout.addWidget(myLabel)
        layout.addStretch(1)
        layout.addWidget(comboBox)

        groupbox.setLayout(layout)

        return groupbox, comboBox

    def addLiteralComboBox(self, title, name, namesList, minOccurs):
        """TODO: add doc string"""
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
        """TODO: add doc string"""
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

    def addCheckBox(self, title, name):
        """TODO: add doc string"""
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
        """TODO: add doc string"""
        inputIdentifier = element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Identifier").at(0).toElement().text().simplified()
        title      = element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Title").at(0).toElement().text().simplified()
        abstract   = element.elementsByTagNameNS("http://www.opengis.net/ows/1.1","Abstract").at(0).toElement().text().simplified()
        return inputIdentifier, title, abstract

    def addIntroduction(self, name, title):
        """TODO: add doc string"""
        groupbox = QGroupBox(self.dlgProcessScrollAreaWidget)
        groupbox.setTitle(name)
        layout = QVBoxLayout()
        # label
        myLabel = QLabel(groupbox)
        myLabel.setObjectName("qLabel"+name)
        myLabel.setText(QString(title))
        myLabel.setMinimumWidth(600)
        myLabel.setMinimumHeight(25)
        myLabel.setWordWrap(True)
        # layout
        layout.addWidget(myLabel)
        groupbox.setLayout(layout)
        self.dlgProcessScrollAreaWidgetLayout.addWidget(groupbox)

    def getDefaultMimeType(self, inElement):
        """TODO: add doc string"""
        myElement = inElement.elementsByTagName("Default").at(0).toElement()
        return self._getMimeTypeSchemaEncoding(myElement)

    def getSupportedMimeTypes(self, inElement):
        """TODO: add doc string"""
        mimeTypes = []
        myElements = inElement.elementsByTagName("Supported").at(0).toElement()
        myFormats = myElements.elementsByTagName('Format')
        for i in range(myFormats.size()):
            myElement = myFormats.at(i).toElement()
            mimeTypes.append(self._getMimeTypeSchemaEncoding(myElement))
        return mimeTypes

    def _getMimeTypeSchemaEncoding(self, Element):
        """TODO: add doc string"""
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
        """TODO: add doc string"""
        myLayerList = []
        if all:
            mapLayers = QgsMapLayerRegistry.instance().mapLayers()
            for (k, layer) in mapLayers.iteritems():
                myLayerList.append(layer.name())
        else:
            #mc=self.iface.mapCanvas()
            mc = QgsMapCanvas()
            nLayers=mc.layerCount()

            for l in range(nLayers):
                # Nur die Layer des gewnschten Datentypes auswhlen 0=Vectorlayer 1=Rasterlayer
                if mc.layer(l).type() == dataType:
                    myLayerList.append(mc.layer(l).name())

        return myLayerList

    def uniqueLayerName(self, name):
        """TO DO: Check the output ports and assign a new unique name to the output layer
        We need to discuss how to go about this"""
        #print 'WPS: output layer'
        mapLayers = QgsMapLayerRegistry.instance().mapLayers()
        i=1
        layerNameList = []
        for (k, layer) in mapLayers.iteritems():
            layerNameList.append(layer.name())

        layerNameList.sort()

        for layerName in layerNameList:
            if layerName == name+unicode(str(i),'latin1'):
                i += 1

        newName = name+unicode(str(i),'latin1')
        return newName

    def allowedValues(self, aValues):
        """TODO: add doc string"""
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

        #print str(valList)
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

    def popUpMessageBox(self, title, detailedText):
        """A message box used for debugging"""
        mbox = WPSMessageBox()
        mbox.setText(title)
        mbox.setDetailedText(detailedText)
        mbox.exec_()

    def xmlExecuteRequestInputStart(self, identifier):
        """TODO: add doc string"""
        string = ""
        string += "<wps:Input>\n"
        string += "<ows:Identifier>"+identifier+"</ows:Identifier>\n"
        string += "<ows:Title>"+identifier+"</ows:Title>\n"
        string += "<wps:Data>\n"
        return string

    def xmlExecuteRequestInputEnd(self):
        """TODO: add doc string"""
        string = ""
        string += "</wps:Data>\n"
        string += "</wps:Input>\n"
        return string

    def createTmpBase64(self, layer):
        """TODO: add doc string"""
        try:
            filename = tempfile.mktemp(prefix="base64")
            rLayer = self.getVLayer(layer)
            infile = open(rLayer.source())
            outfile = open(filename, 'w')
            base64.encode(infile,outfile)
            outfile.close()
            outfile =  open(filename, 'r')
            base64String = outfile.read()
            os.remove(filename)
        except:
            QMessageBox.warning(None, '', "Unable to create temporal file: " + filename + " for base64 encoding")
        return base64String

    def getVLayer(self,name):
        """TODO: add doc string"""
        #   Die sichtbaren Layer der Legende zur weiteren Bearbeitung holen
        for l in range(QgsMapCanvas().layerCount()):
            layer = QgsMapCanvas().layer(l)
            if layer.name() == name:
                return layer

    def createTmpGML(self, layer, processSelection="False"):
        """TODO: add doc string"""
        myQTempFile = QTemporaryFile()
        myQTempFile.open()
        tmpFile = unicode(myQTempFile.fileName(),'latin1')

        vLayer = self.getVLayer(layer)
        fieldList = self.getFieldList(vLayer)

        if vLayer.dataProvider().name() == "postgres":
            encoding = self.getDBEncoding(vLayer.dataProvider())
        else:
            encoding = vLayer.dataProvider().encoding()

        writer = self.createGMLFileWriter(tmpFile, fieldList, vLayer.dataProvider().geometryType(),encoding)

        #print "WPS: TEMP-GML-File Name: "+tmpFile
        provider = vLayer.dataProvider()
        feat = QgsFeature()
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        featureList = vLayer.selectedFeatures()

        if processSelection and vLayer.selectedFeatureCount() > 0:
            for feat in featureList:
                writer.addFeature(feat)
        else:
            while provider.nextFeature(feat):
                writer.addFeature(feat)

        del writer

        myFile = QFile(tmpFile)
        if (not myFile.open(QIODevice.ReadOnly | QIODevice.Text)):
            pass

        myGML = QTextStream(myFile)
        gmlString = ""

        # Overread the first Line of GML Result
        dummy = myGML.readLine()
        gmlString += myGML.readAll()
        myFile.close()
        myQTempFile.close()
        return gmlString.simplified()

    def createGMLFileWriter(self, myTempFile, fields, geometryType, encoding):
        """TODO: add doc string"""
        writer = QgsVectorFileWriter(myTempFile, encoding, fields, geometryType, None, "GML")
        if writer.hasError() != QgsVectorFileWriter.NoError:
            message = self.writerErrorMessage(writer.hasError())
            QMessageBox.warning(None, '', message)
            return 0
        return writer

    def getDBEncoding(self, layerProvider):
        """TODO: add doc string"""
        dbConnection = QgsDataSourceURI(layerProvider.dataSourceUri())
        db = QSqlDatabase.addDatabase("QPSQL","WPSClient")
        db.setHostName(dbConnection.host())
        db.setDatabaseName(dbConnection.database())
        db.setUserName(dbConnection.username())
        db.setPassword(dbConnection.password())
        db.setPort(int(dbConnection.port()))
        db.open()

        query =  "select pg_encoding_to_char(encoding) as encoding "
        query += "from pg_catalog.pg_database "
        query += "where datname = '"+dbConnection.database()+"' "

        result = QSqlQuery(query,db)
        result.first()
        encoding = result.value(0).toString()
        db.close()

        return encoding

    def getFieldList(self, vlayer):
        """Get the Llist of Fields
        Return: QGsFieldMap"""
        fProvider = vlayer.dataProvider()
        feat = QgsFeature()
        allAttrs = fProvider.attributeIndexes()
        # start data retrieval: all attributes for each feature
        fProvider.select(allAttrs, QgsRectangle(), False)
        # retrieve every feature with its attributes
        myFields = fProvider.fields()
        return myFields

    def getDescription(self):
        """TODO: add doc string"""
        pass


class WPSMessageBox(QMessageBox):
    """A resizable message box to show debug info"""
    def __init__(self):
        QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

    def event(self, e):
        result = QMessageBox.event(self, e)

        self.setMinimumHeight(600)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(800)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        textEdit = self.findChild(QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(300)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(300)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return result


class WPSProcessing():
    """TODO: add doc string"""

    def processGUI(self):
        #print 'WPS: process dummy'
        pass

    def processTools(self):
        pass

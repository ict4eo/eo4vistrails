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
"""This module provides an OGC (Open Geospatial Consortium) Web Processing
Service (WPS) Client via pyWPS.

This code is based on ideas and methods from the QGIS WPS Plugin (09/11/2009)

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
from core.modules.module_descriptor import ModuleDescriptor
from core.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.module_registry import get_module_registry
from core.modules.vistrails_module import Module, new_module, NotCacheable,\
    ModuleError
from core.utils import PortAlreadyExists
from core.modules.basic_modules import String
# eo4vistrails
from packages.eo4vistrails.geoinf.datamodels import QgsLayer
from packages.eo4vistrails.geoinf.ogc.PortConfigurationWidget import \
    Port, PortConfigurationWidget
# local
import init


DEBUG = False
# All supported import raster formats
RASTER_MIMETYPES = [{"MIMETYPE":"IMAGE/TIFF", "GDALID":"GTiff"},
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
VECTOR_MIMETYPES = [{"MIMETYPE":"TEXT/XML", "SCHEMA":"GML", "GDALID":"GML"}, \
    {"MIMETYPE":"APPLICATION/XML", "SCHEMA":"GML", "GDALID":"GML"}, \
    {"MIMETYPE":"TEXT/XML", "SCHEMA":"KML", "GDALID":"KML"}, \
    {"MIMETYPE":"APPLICATION/DGN", "SCHEMA":"", "GDALID":"DGN"}, \
    {"MIMETYPE":"APPLICATION/SHP", "SCHEMA":"", "GDALID":"ESRI_Shapefile"}]
# Other constants
DEFAULT_URL = 'http://ict4eo.meraka.csir.co.za/cgi-bin/wps.py'
MAP_LAYER = 'za.co.csir.eo4vistrails:QgsMapLayer:data'

def xmlExecuteRequestInputStart(identifier, namespace=False, title=None):
    """TODO: add doc string"""
    if identifier:
        string = ""
        if namespace:
            string += '<wps:Input xmlns:wps="http://www.opengis.net/wps/1.0.0"\
                      xmlns:ows="http://www.opengis.net/ows/1.1">\n'
        else:
            string += "<wps:Input>\n"
        if not title:
            title = identifier
        string += "<ows:Identifier>" + identifier + "</ows:Identifier>\n"
        string += "<ows:Title>" + title + "</ows:Title>\n"
        string += "<wps:Data>\n"
        return string
    else:
        self.raiseError('Invalid Layer Identifier',\
                        'Unable to create ows:Identifier')


def xmlExecuteRequestInputEnd():
    """TODO: add doc string"""
    string = ""
    string += "</wps:Data>\n"
    string += "</wps:Input>\n"
    return string


def isMimeTypeVector(mimeType):
    """Check for vector input. Zipped shapefiles must be extracted"""
    if DEBUG:
        print "WPS isMimeTypeVector:", mimeType.upper()
    for vectorType in VECTOR_MIMETYPES:
        if mimeType.upper() == vectorType["MIMETYPE"]:
            return vectorType["GDALID"]
    return None


def isMimeTypeText(mimeType):
    """Check for text file input"""
    if DEBUG:
        print "WPS isMimeTypeText:", mimeType.upper()
    if mimeType.upper() == "TEXT/PLAIN":
        return "TXT"
    else:
        return None


def isMimeTypeRaster(mimeType):
    """Check for raster input"""
    if DEBUG:
        print "WPS isMimeTypeRaster:", mimeType.upper()
    for rasterType in RASTER_MIMETYPES:
        if mimeType.upper() == rasterType["MIMETYPE"]:
            return rasterType["GDALID"]
    return None


class WPS(Module):
    """TODO: write doc string
    """

    def __init__(self):
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        if traceback:
            traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))

    def compute(self):
        # "fixed" ports
        self.url = self.getInputFromPort(init.OGC_REQUEST_PORT) #base URL
        self.postString = self.getInputFromPort(init.OGC_POST_DATA_PORT)
        self.processID = self.getInputFromPort(init.WPS_PROCESS_PORT) #name

        if self.postString and self.url:
            #print "\nWPS:165 PRIOR self.postString\n", self.postString, "\n\n"
            # add input port details to POST request
            self.postString = \
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' \
                + self.addInputsToPOST(
                    self.postString,
                    self.processID)
            #print "\nWPS:172 POST self.postString\n", self.postString, "\n\n"
            if DEBUG:
                home = os.getenv("HOME")
                outFile = open(home + '/Desktop/wps_poststring', 'w')
                outFile.write(self.postString)
                outFile.close()

            """
            #TEST POST START
            self.url = 'http://ict4eo.meraka.csir.co.za/cgi-bin/wps.py'
            self.postString = '''<?xml version="1.0" \
                              encoding="UTF-8" standalone="yes"?>
            <wps:Execute service="WPS" version="1.0.0" \
                xmlns:wps="http://www.opengis.net/wps/1.0.0"\
                xmlns:ows="http://www.opengis.net/ows/1.1"\
                xmlns:xlink="http://www.w3.org/1999/xlink"\
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\
                xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 \
                http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd">
                <ows:Identifier>foo2</ows:Identifier>
                <wps:DataInputs>
                    <wps:Input>
                        <ows:Identifier>data</ows:Identifier>
                        <ows:Title>data</ows:Title>
                        <wps:Data>
                            <wps:ComplexData mimeType="text/xml" schema="" \
                                encoding="">
                            <ogr:FeatureCollection xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schemas.opengis.net/gml/3.1.1/base/ gml.xsd" xmlns:ogr="http://ogr.maptools.org/" xmlns:gml="http://www.opengis.net/gml"><gml:boundedBy><gml:Box><gml:coord><gml:X>303314.4493983217</gml:X><gml:Y>6244549.021404636</gml:Y></gml:coord><gml:coord><gml:X>303718.64560866</gml:X><gml:Y>6244692.545970687</gml:Y></gml:coord></gml:Box></gml:boundedBy><gml:featureMember><ogr:qt_temp fid="F0"><ogr:geometryProperty><gml:Point><gml:coordinates>303314.449398321739864,6244692.545970686711371</gml:coordinates></gml:Point></ogr:geometryProperty><ogr:label>gree</ogr:label><ogr:id>2323</ogr:id><ogr:rotatation>0</ogr:rotatation></ogr:qt_temp></gml:featureMember><gml:featureMember><ogr:qt_temp fid="F1"><ogr:geometryProperty><gml:Point><gml:coordinates>303426.941625767154619,6244549.021404636092484</gml:coordinates></gml:Point></ogr:geometryProperty><ogr:label>dwqdqwd</ogr:label><ogr:id>324324</ogr:id><ogr:rotatation>0</ogr:rotatation></ogr:qt_temp></gml:featureMember><gml:featureMember><ogr:qt_temp fid="F2"><ogr:geometryProperty><gml:Point><gml:coordinates>303718.645608660008293,6244565.313382403925061</gml:coordinates></gml:Point></ogr:geometryProperty><ogr:label>nhfgh</ogr:label><ogr:id>34634</ogr:id><ogr:rotatation>0</ogr:rotatation></ogr:qt_temp></gml:featureMember></ogr:FeatureCollection></wps:ComplexData>
                        </wps:Data>
                    </wps:Input>
                    <wps:Input>
                        <ows:Identifier>width</ows:Identifier>
                        <ows:Title>width</ows:Title>
                        <wps:Data>
                            <wps:LiteralData>10</wps:LiteralData>
                        </wps:Data>
                    </wps:Input>
                </wps:DataInputs>
                <wps:ResponseForm>
                    <wps:ResponseDocument lineage="false" storeExecuteResponse="true" status="false">
                        <wps:Output>
                            <ows:Identifier>text</ows:Identifier>
                        </wps:Output>
                        <wps:Output asReference="true" mimeType="text/xml" schema="">
                            <ows:Identifier>buffer</ows:Identifier>
                        </wps:Output>
                    </wps:ResponseDocument>
                </wps:ResponseForm>
            </wps:Execute>'''
            #TEST POST END
            """

            # connect to server
            r = urllib2.Request(self.url, self.postString)
            f = urllib2.urlopen(r)
            # get the results back
            wpsRequestResult = f.read()
            # set the output ports
            self.resultHandler(wpsRequestResult)
        else:
            self.raiseError('Configuration Incomplete',\
                            'Unable to set URL and POST string')

    def addInputsToPOST(self, postStringIn, processID):
        """Insert the input port data as part of the POST request.

        """
        if postStringIn:
            #   iterate through static & dynamic input ports and check for matching type
            #   NB: self.inputPorts only shows "template" (fixed) ports UNLESS
            #       the port is already hooked up to another pipeline input!

            # TO DO - need find a better way to exclude "static" port from iterkeys() ???
            for key in self.inputPorts.iterkeys():
                if not key in [init.OGC_REQUEST_PORT, init.OGC_POST_DATA_PORT, init.WPS_PROCESS_PORT]:
                    #print "244: key", key, self.inputPorts[key]
                    connector = self.inputPorts[key][0]
                    port_port = connector.port
                    port_object = connector.obj
                    identifier = key
                    #print "247: key:port_object", key, ":", port_object, type(port_object)
                    if isinstance(port_object, QgsLayer.QgsVectorLayer):
                        mimeType = "text/xml"  # get from layer???
                        schema = "FOO"
                        encoding = "FOO"
                    elif isinstance(port_object, QgsLayer.QgsRasterLayer):
                        mimeType = "image/tiff"  # get from layer???
                    else:
                        pass

                    # Handle layer input...
                    if isinstance(port_object, QgsLayer.QgsVectorLayer) or \
                        isinstance(port_object, QgsLayer.QgsRasterLayer):
                        layer = port_object
                        # start wrapper
                        postString = xmlExecuteRequestInputStart(identifier, True, layer.name())
                        # check layer type
                        if  mimeType == "text/xml":
                            postString += '<wps:ComplexData mimeType="' + mimeType +\
                                          '" schema="' + schema + \
                                          '" encoding="' + encoding + '">'
                            GML = self.createTmpGML(layer)
                            if GML:
                                postString += GML
                            else:
                                self.raiseError('WPS Error', 'Unable to encode vector to GML')
                        else:
                            postString += '<wps:ComplexData mimeType="' + mimeType +\
                                          '" encoding="base64">'
                            data64 = self.createTmpBase64(layer)
                            if data64:
                                postString += data64
                            else:
                                self.raiseError('WPS Error', 'Unable to encode raster to base64')
                        postString += "</wps:ComplexData>"
                        # end wrapper
                        postString += xmlExecuteRequestInputEnd()
                        # insert new XML into the existing POST string
                        # NB: NO prefix on search node
                        #print "WPS:286 postString", postString
                        postStringIn = self.insertElement(
                            postStringIn,
                            postString,
                            'DataInputs',
                            'http://www.opengis.net/wps/1.0.0')
                        #print "WPS:290 postStringIn POST",postStringIn
                        if DEBUG:
                            home = os.getenv("HOME")
                            outFile = open(home + '/Desktop/post_request.xml', 'w')
                            outFile.write(postStringIn)
                            outFile.close()

                    # Handle string input
                    elif isinstance(port_object, String):
                        # end wrapper
                        postString = xmlExecuteRequestInputStart(identifier, True, "")
                        postString += '<wps:LiteralData>'
                        #bar = port_object.get_output(port_port) #see 454 in vistrails_module.py
                        #print "309:bar",key,type(bar),bar
                        postString += port_object.get_output(port_port) #string.get_output('value')
                        postString += '</wps:LiteralData>'
                        # end wrapper
                        postString += xmlExecuteRequestInputEnd()
                        # insert new XML into the existing POST string
                        postStringIn = self.insertElement(
                            postStringIn,
                            postString,
                            'DataInputs',
                            'http://www.opengis.net/wps/1.0.0')
                    else:
                        self.raiseError('Configuration Incomplete',\
                                'Unable to handle port type for %s', key)

                """
                ######### CODE THAT NEEDS TO BE ADAPTED TO ENHANCE THE ABOVE ##########
                if isMimeTypeVector(mimeType) != None and mimeType == "text/xml":
                    postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + "\" encoding=\"" + encoding + "\">"
                    postString += self.createTmpGML(listWidget.text(), useSelected).replace("> <", "><").replace("http://ogr.maptools.org/ qt_temp.xsd", "http://ogr.maptools.org/qt_temp.xsd")
                elif isMimeTypeVector(mimeType) != None or isMimeTypeRaster(mimeType) != None:
                    postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"
                    postString += self.createTmpBase64(listWidget.text())

                postString += "</wps:ComplexData>\n"
                postString += xmlExecuteRequestInputEnd()

                # Single raster and vector inputs
                for comboBox in self.complexInputComboBoxList:
                # Do not add undefined inputs
                    if comboBox == None or unicode(comboBox.currentText(), 'latin1') == "<None>":
                        continue

                    postString += xmlExecuteRequestInputStart(comboBox.objectName())

                    # TODO: Check for more types
                    mimeType = self.inputDataTypeList[comboBox.objectName()]["MimeType"]
                    schema = self.inputDataTypeList[comboBox.objectName()]["Schema"]
                    encoding = self.inputDataTypeList[comboBox.objectName()]["Encoding"]

                    if isMimeTypeVector(mimeType) != None and mimeType == "text/xml":
                        postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + "\" encoding=\"" + encoding + "\">"
                        postString += self.createTmpGML(comboBox.currentText(), useSelected).replace("> <", "><")
                        postString = postString.replace("xsi:schemaLocation=\"http://ogr.maptools.org/ qt_temp.xsd\"", "xsi:schemaLocation=\"http://schemas.opengis.net/gml/3.1.1/base/ gml.xsd\"")
                    elif isMimeTypeVector(mimeType) != None or isMimeTypeRaster(mimeType) != None:
                        postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"
                        postString += self.createTmpBase64(comboBox.currentText())

                    postString += "</wps:ComplexData>\n"
                    postString += xmlExecuteRequestInputEnd()

                # Multiple raster and vector inputs
                for listWidgets in self.complexInputListWidgetList:
                # Do not add undefined inputs
                    if listWidgets == None:
                        continue

                    mimeType = self.inputDataTypeList[listWidgets.objectName()]["MimeType"]
                    schema = self.inputDataTypeList[listWidgets.objectName()]["Schema"]
                    encoding = self.inputDataTypeList[listWidgets.objectName()]["Encoding"]

                # Iterate over each selected item
                for i in range(listWidgets.count()):
                    listWidget = listWidgets.item(i)
                    if listWidget == None or listWidget.isSelected() == False or str(listWidget.text()) == "<None>":
                        continue

                    postString += xmlExecuteRequestInputStart(listWidgets.objectName())

                    # TODO: Check for more types
                    if isMimeTypeVector(mimeType) != None and mimeType == "text/xml":
                        postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" schema=\"" + schema + "\" encoding=\"" + encoding + "\">"
                        postString += self.createTmpGML(listWidget.text(), useSelected).replace("> <", "><").replace("http://ogr.maptools.org/ qt_temp.xsd", "http://ogr.maptools.org/qt_temp.xsd")
                    elif isMimeTypeVector(mimeType) != None or isMimeTypeRaster(mimeType) != None:
                        postString += "<wps:ComplexData mimeType=\"" + mimeType + "\" encoding=\"base64\">\n"
                        postString += self.createTmpBase64(listWidget.text())

                    postString += "</wps:ComplexData>\n"
                    postString += xmlExecuteRequestInputEnd()
                """

        #print "WPS:365",postStringIn
        return postStringIn

    def resultHandler(self, resultXML, resultType="store"):
        """Handle the result of the WPS Execute request and add the outputs to
        the appropriate ports.
        """
        self.doc = QtXml.QDomDocument()
        self.doc.setContent(resultXML, True)
        resultNodeList = self.doc.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "Output")

        # TODO: Check if the process does not run correctly before
        if resultNodeList.size() > 0:
            for i in range(resultNodeList.size()):
                f_element = resultNodeList.at(i).toElement()

                # Fetch the referenced complex data
                if f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "Reference").size() > 0:
                    identifier = f_element.elementsByTagNameNS(
                        "http://www.opengis.net/ows/1.1", "Identifier").at(0).toElement().text().simplified()
                    reference = f_element.elementsByTagNameNS(
                        "http://www.opengis.net/wps/1.0.0", "Reference").at(0).toElement()

                    # Get the reference
                    fileLink = reference.attribute("href", "0")

                    # Try with namespace if not successful
                    if fileLink == '0':
                        fileLink = reference.attributeNS(
                            "http://www.w3.org/1999/xlink", "href", "0")
                    if fileLink == '0':
                        self.raiseError(str(QCoreApplication.translate(
                            "WPS Error: Unable to download the result of reference: ")) + str(fileLink))
                        return

                    # Get the mime type of the result
                    mimeType = str(reference.attribute("mimeType", "0").toLower())

                    if fileLink != '0':
                        # Set a valid layerName
                        layerName = self.uniqueLayerName(str(self.processID) + "_" + str(identifier))
                        # Layer filename
                        resultFileConnector = urllib.urlretrieve(unicode(fileLink, 'latin1'))
                        resultFile = resultFileConnector[0]
                        # Vector data
                        # TODO: Check for schema GML and KML
                        if isMimeTypeVector(mimeType) != None:
                            vlayer = QgsVectorLayer(resultFile, layerName, "ogr")
                            self.setResult(init.MAP_LAYER_PORT, vlayer)
                        # Raster data
                        elif isMimeTypeRaster(mimeType) != None:
                            # We can directly attach the new layer
                            rLayer = QgsRasterLayer(resultFile, layerName)
                            self.setResult(init.MAP_LAYER_PORT, rLayer)
                        # Text data
                        elif isMimeTypeText(mimeType) != None:
                            text = open(resultFile, 'r').read()
                            self.setResult(init.DATA_RESULT_PORT, text)
                        # Everything else
                        else:
                            # For unsupported mime types we assume text
                            if DEBUG:
                                print "WARNING - result is not a defined MIME type"
                            content = open(resultFile, 'r').read()
                            self.setResult(init.DATA_RESULT_PORT, content)

                elif f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").size() > 0:
                    literalText = f_element.elementsByTagNameNS("http://www.opengis.net/wps/1.0.0", "LiteralData").at(0).toElement().text()
                    # TODO: how to handle this ?
                    #self.popUpMessageBox(QCoreApplication.translate("QgsWps", 'Result'),literalText)
                else:
                    self.raiseError(
                        "WPS Error",
                        "Missing Reference tag, or literal data, in response XML")

            # TODO: how to handle this ?
            #QMessageBox.information(None, QCoreApplication.translate("QgsWps", 'Process result'), QCoreApplication.translate("QgsWps", 'The process finished successful'))
        else:
            self.errorHandler(resultXML)

    def createTmpGML(self, vLayer, processSelection="False"):
        """TODO: add doc string

        * vLayer is an actual QGIS vector layer (not a string)
        """
        myQTempFile = QTemporaryFile()
        myQTempFile.open()
        tmpFile = unicode(myQTempFile.fileName(), 'latin1')

        if vLayer.dataProvider().name() == "postgres":
            encoding = self.getDBEncoding(vLayer.dataProvider())
        else:
            encoding = vLayer.dataProvider().encoding()

        fieldList = self.getFieldList(vLayer)
        writer = self.createGMLFileWriter(tmpFile, fieldList, vLayer.dataProvider().geometryType(), encoding)

        # error = QgsVectorFileWriter.writeAsShapefile(layer, "my_shapes.shp", "CP1250")
        #print "WPS:466 TEMP-GML-File Name: " + tmpFile
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

    def createTmpBase64(self, rLayer):
        """Encode raster data to base64 format, for use in XML POST string.

        * rLayer is an actual QGIS raster layer (not a string)
        """
        import base64
        # disk-based approach with file manipulation
        base64String = None
        layer_source = str(rLayer.source())
        #try:
        filename = tempfile.mktemp(prefix="base64")
        if "http://" in rLayer.source(): #TODO: better test than this !!!
            infile = urllib.urlopen(layer_source) # read from web
        else:
            infile = open(layer_source, 'r') # read from disk
        outfile = open(filename, 'w')
        base64.encode(infile, outfile)
        outfile.close()
        outfile = open(filename, 'r')
        base64String = outfile.read()
        os.remove(filename)
        #except:
        #    QMessageBox.warning(None, '', "Unable to create temporary file: " + filename + " for base64 encoding")
        """
        base64String = base64.encodestring(rLayer) # error: no len() for rLayer
        """
        return base64String

    def errorHandler(self, resultXML):
        """Format the error message from the WPS."""
        errorDoc = QtXml.QDomDocument()
        myResult = errorDoc.setContent(resultXML.strip(), True)

        resultExceptionNodeList = errorDoc.elementsByTagNameNS(
            "http://www.opengis.net/wps/1.0.0", "ExceptionReport")
        exceptionText = ''
        if not resultExceptionNodeList.isEmpty():
            for i in range(resultExceptionNodeList.size()):
                resultElement = resultExceptionNodeList.at(i).toElement()
                exceptionText += resultElement.text()

        resultExceptionNodeList = errorDoc.elementsByTagNameNS(
            "http://www.opengis.net/wps/1.0.0", "ExceptionText")
        if not resultExceptionNodeList.isEmpty():
            for i in range(resultExceptionNodeList.size()):
                resultElement = resultExceptionNodeList.at(i).toElement()
                exceptionText += resultElement.text()

        resultExceptionNodeList = errorDoc.elementsByTagNameNS(
            "http://www.opengis.net/ows/1.1", "ExceptionText")
        if not resultExceptionNodeList.isEmpty():
            for i in range(resultExceptionNodeList.size()):
                resultElement = resultExceptionNodeList.at(i).toElement()
                exceptionText += resultElement.text()

        resultExceptionNodeList = errorDoc.elementsByTagName("Exception")
        if not resultExceptionNodeList.isEmpty():
            resultElement = resultExceptionNodeList.at(0).toElement()
            exceptionText += resultElement.attribute("exceptionCode")

        if len(exceptionText) > 0:
            self.raiseError(resultXML)

    def createGMLFileWriter(self, myTempFile, fields, geometryType, encoding):
        """TODO: add doc string"""
        writer = QgsVectorFileWriter(
            myTempFile,
            encoding,
            fields,
            geometryType,
            None,
            "GML")
        if writer.hasError() != QgsVectorFileWriter.NoError:
            message = self.writerErrorMessage(writer.hasError())
            QMessageBox.warning(None, '', message)
            return 0
        return writer

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

    def insertElement(self, source, element, node, namespace=None):
        """Return updated source with element inserted at a specified node.

        All items must arrive as strings; result is also a string"""
        #print "\nWPS:592 insertElement:\n **Source**", source, "\n**Element**",element, "\n**node**", node
        if node:
            if not ':' in node:
                if element:
                    import xml.etree.ElementTree as xml
                    from xml.parsers.expat import ExpatError
                    if namespace:
                        node = "{%s}%s" % (namespace, node)
                    element = str(element).encode("UTF-8")
                    try:
                        doc = xml.fromstring(source)
                        result = doc.findall('.//' + node)
                        if result:
                            if len(result) > 0:
                                target = result[0]
                            else:
                                target = result
                            #print "WPS:630\n", element
                            new_element = xml.fromstring(element)
                            target.append(new_element)
                            return xml.tostring(doc)
                    except ExpatError:
                        self.raiseError("Expat Error",
                        "Unable to create XML elements from input data.")
            else:
                self.raiseError("WPS insertElement Error",
                    "Cannot use a ':' in an element name.")
        return source

    def uniqueLayerName(self, name):
        """TODO: Check the output ports and assign unique name to output layer
        We need to discuss how to go about this"""
        #print 'WPS:622 output layer'
        mapLayers = QgsMapLayerRegistry.instance().mapLayers()
        i = 1
        layerNameList = []
        for (k, layer) in mapLayers.iteritems():
            layerNameList.append(layer.name())
        layerNameList.sort()
        for layerName in layerNameList:
            if layerName == name + unicode(str(i), 'latin1'):
                i += 1
        newName = name + unicode(str(i), 'latin1')
        return newName


class WPSConfigurationWidgetTabs(QTabWidget):
    """Configuration Tab Widgets
    are added via the addTab method of the QTabWidget

    """
    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent)
        self.setGeometry(QRect(20, 20, 790, 540)) # 20, 20, 990, 740
        self.setTabShape(QTabWidget.Rounded)
        self.setElideMode(Qt.ElideNone)
        self.setObjectName("WPSConfigurationWidgetTabsInstance")


class WPSConfigurationWidget(PortConfigurationWidget):
    """TODO: add doc string"""

    def __init__(self, module, controller, parent=None):
        """ UntupleConfigurationWidget(module: Module,
                                     controller: VistrailController,
                                     parent: QWidget)
                                     -> UntupleConfigurationWidget
        Let StandardModuleConfigurationWidget constructor store the
        controller/module object from the builder and set up the
        configuration widget.
        After StandardModuleConfigurationWidget constructor, all of
        these will be available:
        * self.module : the Module object into the pipeline
        * self.module_descriptor: the descriptor for the type in the registry
        * self.controller: the current vistrail controller

        """
        PortConfigurationWidget.__init__(self, module,
                                        controller, parent)
        self.setObjectName("WpsConfigWidget")
        self.create_config_window()

    def create_config_window(self):
        """Create Qt elements for the configuration dialog
        * hook buttons to methods

        """
        self.setWindowTitle("OGC WPS Configuration Widget")
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumSize(593, 442)
        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)
        self.GroupBox1 = QGroupBox("Server Connections")
        self.mainLayout.addWidget(self.GroupBox1, 0, 0, 1, 1)
        self.mainLayout.setMargin(9)
        self.mainLayout.setSpacing(6)

        spacerItem = QSpacerItem(171, 30, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.mainLayout.addItem(spacerItem, 3, 4, 1, 1)
        self.btnConnect = QPushButton(self.GroupBox1)
        self.btnConnect.setEnabled(True)
        self.btnConnect.setObjectName("btnConnect")
        self.btnConnect.setText("Connect")
        self.mainLayout.addWidget(self.btnConnect, 3, 1, 1, 1)

        #at runtime be will parsing a url
        self.mainLayout.addWidget(QLabel('WPS URL:'), 1, 0, 1, 1)
        self.URLConnect = QLineEdit(DEFAULT_URL)
        self.URLConnect.setEnabled(True) #sets it not to be editable
        self.mainLayout.addWidget(self.URLConnect, 1, 1, 1, -1)

        self.mainLayout.addWidget(QLabel('WPS Version:'), 2, 0, 1, 1)
        self.launchversion = QComboBox()
        self.launchversion.addItems(['1.0.0', ])
        self.mainLayout.addWidget(self.launchversion, 2, 1, 1, 1)

        # tabs
        self.tabWidget = QTabWidget()
        self.tabService = QWidget()
        self.tabProcess = QWidget()
        #tab = QtGui.QWidget()
        self.tabProcessLayout = QVBoxLayout(self.tabProcess)
        self.tabServiceLayout = QVBoxLayout(self.tabService)
        self.tabWidget.addTab(self.tabService, "Process &List")
        self.tabWidget.addTab(self.tabProcess, "Process &Inputs/Outputs")

        # service tree
        self.treeWidgetService = QTreeWidget()
        self.treeWidgetService.setColumnCount(3)
        self.treeWidgetService.setObjectName("treeWidget")
        self.treeWidgetService.setSortingEnabled(True)
        self.treeWidgetService.headerItem().setText(0, "Identifier")
        self.treeWidgetService.headerItem().setText(1, "Title")
        self.treeWidgetService.headerItem().setText(2, "Abstract")
        self.treeWidgetService.sortByColumn(0,0) # column, order (0=ASC)
        self.treeWidgetService.setWordWrap(True) # only wraps at linebreaks
        self.tabServiceLayout.addWidget(self.treeWidgetService)

        # process tree
        self.treeWidgetProcess = QTreeWidget()
        self.treeWidgetProcess.setColumnCount(4)
        self.treeWidgetProcess.setObjectName("treeWidget")
        self.treeWidgetProcess.setSortingEnabled(True)
        self.treeWidgetProcess.headerItem().setText(0, "Type")
        self.treeWidgetProcess.headerItem().setText(1, "Identifier")
        self.treeWidgetProcess.headerItem().setText(2, "Title")
        self.treeWidgetProcess.headerItem().setText(3, "Abstract")
        self.treeWidgetProcess.sortByColumn(0,0) # column, order (0=ASC)
        self.treeWidgetProcess.setWordWrap(True) # only wraps at linebreaks
        self.tabProcessLayout.addWidget(self.treeWidgetProcess)
        self.tabWidget.setTabEnabled(1,False)

        self.mainLayout.addWidget(self.tabWidget, 4, 0, 1, -1)

        #spacerItem1 = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        #self.mainLayout.addItem(spacerItem1, 5, 2, 1, 1)
        self.buttons = QWidget()
        self.buttonLayout = QHBoxLayout(self.buttons)
        #self.buttonLayout.setGeometry(QtCore.QRect(300, 500, 780, 680))
        self.buttonLayout.setMargin(5)
        self.buttonLayout.addStretch(1)

        self.btnCancel = QPushButton('&Cancel', self)
        self.btnCancel.setAutoDefault(False)
        self.btnCancel.setShortcut('Esc')
        self.buttonLayout.addWidget(self.btnCancel)
        self.btnOk = QPushButton('&OK', self)
        self.btnOk.setAutoDefault(False)
        self.buttonLayout.addWidget(self.btnOk)
        self.mainLayout.addWidget(self.buttons, 5, 0, 1, -1)
        #self.layout().addLayout(self.buttonLayout)

        # Connect button
        self.connect(
            self.btnConnect,
            SIGNAL('clicked(bool)'),
            self.connectServer)
        # OK button
        self.connect(
            self.btnOk,
            SIGNAL('clicked(bool)'),
            self.btnOK_clicked)
        # Cancel Button
        self.connect(
            self.btnCancel,
            SIGNAL('clicked(bool)'),
            self.close)
        # Tab
        self.connect(
            self.tabWidget,
            SIGNAL('currentChanged(int)'),
            self.showProcess)

    def connectServer(self, connection):
        """Add items to treeWidget
        see qgswps.py:: createCapabilities Gui"""
        connection = self.URLConnect.text()
        # pass version here
        version = self.launchversion.currentText()
        if not self.webConnectionExists(connection):
            self.tabWidget.setTabEnabled(1,False)
            return 0
        else:
            itemListAll = self.getCapabilities(connection)
            self.initTreeWPSServices(itemListAll)
            self.tabWidget.setTabEnabled(1,True)

    def showProcess(self, selected_index):
        """Display process details when process details tab selected."""
        if selected_index == 1:
            if self.getProcessDescription():
                self.displayProcessDescription()

    def webConnectionExists(self, connection):
        """Return True if server returns GetCapabilities as XML"""
        try:
            xmlString = self.getServiceXML(connection, "GetCapabilities")
            return True
        except:
            QMessageBox.critical(None, '', 'Web Connection Failed')
            return False

    def getServiceXML(self, name, request, identifier=None):
        """ Get server and connection details from Stored Server Connections
        Param: String ConnectionName
        Return: Array Server Information
            (http,www....,/cgi-bin/...,Post||Get,Service Version)
        """
        result = self.getServer(name)
        path = result["path"]
        server = result["server"]
        method = result["method"]
        version = result["version"]
        if identifier:
            myRequest = "?Request=" + request + "&identifier=" + \
                        identifier + "&Service=WPS&Version=" + version
        else:
            myRequest = "?Request=" + request + "&Service=WPS&Version=" +\
                        version

        myPath = path + myRequest
        self.verbindung = HTTPConnection(str(server))
        foo = self.verbindung.request(str(method), str(myPath))
        results = self.verbindung.getresponse()
        return results.read()

    def getServer(self, name):
        """Return server details as a dictionary"""
        settings = QSettings()
        myURL = urlparse(str(name))
        mySettings = "/WPS/" + name
        settings.setValue(mySettings + "/method", QVariant("GET"))
        result = {}
        result["url"] = str(name)
        result["scheme"] = myURL.scheme
        result["server"] = myURL.netloc
        result["path"] = myURL.path
        result["method"] = str(settings.value(mySettings + "/method").toString())
        result["version"] = str(self.launchversion.currentText())
        return result

    def getCapabilities(self, connection):
        """Return Qt list of core metadata from WPS GetCapabilities request"""
        xmlString = self.getServiceXML(connection, "GetCapabilities")
        self.doc = QtXml.QDomDocument()
        test = self.doc.setContent(xmlString, True)
        #test parsing of xml doc
        if DEBUG and test == True:
            print 'WPS: XML document parsed'
        #check version - only handle 1.0.0
        if self.getServiceVersion() != "1.0.0":
            QMessageBox.information(None, 'Error', 'Only WPS Version 1.0.0 is supported')
            return 0
        #key metadata for capabilities
        version = self.doc.elementsByTagNameNS(
            "http://www.opengis.net/wps/1.0.0", "Process")
        title = self.doc.elementsByTagNameNS(
            "http://www.opengis.net/ows/1.1", "Title")
        identifier = self.doc.elementsByTagNameNS(
            "http://www.opengis.net/ows/1.1", "Identifier")
        abstract = self.doc.elementsByTagNameNS(
            "http://www.opengis.net/ows/1.1", "Abstract")
        #store key data in Qt list
        itemListAll = []
        for i in range(version.size()):
            itemList = []
            v_element = version.at(i).toElement()
            i_element = identifier.at(i).toElement()
            t_element = title.at(i + 1).toElement()
            a_element = abstract.at(i + 1).toElement()
            itemList.append(i_element.text())
            itemList.append(t_element.text())
            itemList.append(a_element.text())
            itemListAll.append(itemList)
        return itemListAll

    def getServiceVersion(self):
        """Return WPS Version"""
        return self.launchversion.currentText()

    def initTreeWPSServices(self, taglist):
        """TODO: add doc string"""
        self.treeWidgetService.setColumnCount(self.treeWidgetService.columnCount())
        self.treeWidgetService.clear()
        itemList = []
        for items in taglist:
            item = QTreeWidgetItem()
            ident = unicode(items[0], 'latin1')
            title = unicode(items[1], 'latin1')
            abstract = unicode(items[2], 'latin1')
            item.setText(0, ident.strip())
            item.setText(1, title.strip())
            item.setText(2, abstract.strip())
            itemList.append(item)
        self.treeWidgetService.addTopLevelItems(itemList)

    def getProcessDescription(self):
        """Get and store the selected process meta-data"""
        # Process identifier
        name = self.URLConnect.text()
        item = self.treeWidgetService.currentItem()
        try:
            self.processIdentifier = item.text(0)
        except:
            QMessageBox.warning(None, '',
                QCoreApplication.translate("WPS", 'Please select a Process'))
            return False
        # Data Storage
        self.inputsMetaInfo = {} # input metainfo, key is input identifier
        self.outputsMetaInfo = {} # output metainfo, key is output identifier
        self.inputDataTypeList = {}
        self.outputDataTypeList = {}
        # Receive the XML process description
        self.processName = name
        self.pDoc = QtXml.QDomDocument()
        self.pDoc.setContent(
            self.getServiceXML(
                self.processName,
                "DescribeProcess",
                self.processIdentifier),
            True)
        # Process description attributes
        process_attr = self.pDoc.elementsByTagName("ProcessDescription")
        self.processAttributes = self.getProcessAttributes(process_attr)
        self.dataInputs = self.pDoc.elementsByTagName("Input")
        self.dataOutputs = self.pDoc.elementsByTagName("Output")
        self.tabWidget.setTabText(
            1,"Process "+str(self.processIdentifier)+" &Inputs/Outputs")
        return True

    def displayProcessDescription(self):
        """Use treeWidgetProcess to display the selected process details."""
        # Setup Qt list
        itemList = []
        # Get Descriptions
        for i in range(self.dataOutputs.size()):
            f_element = self.dataOutputs.at(i).toElement()
            identifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)
            item = QTreeWidgetItem()
            item.setText(0, "Output")
            item.setText(1, identifier)
            item.setText(2, title)
            item.setText(3, abstract)
            itemList.append(item)
        for i in range(self.dataInputs.size()):
            f_element = self.dataInputs.at(i).toElement()
            identifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)
            item = QTreeWidgetItem()
            item.setText(0, "Input")
            item.setText(1, identifier)
            item.setText(2, title)
            item.setText(3, abstract)
            itemList.append(item)
        # Add to tree
        self.treeWidgetProcess.clear()
        self.treeWidgetProcess.addTopLevelItems(itemList)

    def btnOK_clicked(self, bool):
        """Create dynamic ports based on process description."""
        self.getProcessDescription()
        # Generate the ports
        self.generateProcessInputPorts(self.dataInputs)
        self.generateProcessOutputPorts(self.dataOutputs)
        # Update VisTrails with new port details for module
        if self.updateVistrail():  # PortConfigurationWidget
            # set default port info (request, processID etc)
            self.getProcessInfo()
            self.emit(SIGNAL('doneConfigure()'))
            self.close()

    def getProcessAttributes(self, process_attr):
        """Return a dictionary containing process description attributes"""
        f_element = process_attr.at(0).toElement()
        if f_element:
            processVersion = f_element.attribute("processVersion") or None
            storeSupported = f_element.attribute("storeSupported") or 'false'
            statusSupported = f_element.attribute("statusSupported") or 'false'
            return {
                'version': str(processVersion),
                'store': str(storeSupported),
                'status': str(statusSupported)}
        else:
            return {}

    def generateProcessInputPorts(self, DataInputs):
        """Generate the ports for all inputs defined in process description
        XML file.

        """
        # Create the complex inputs at first
        for i in range(DataInputs.size()):
            f_element = DataInputs.at(i).toElement()
            inputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)
            complexData = f_element.elementsByTagName("ComplexData")
            minOccurs = int(f_element.attribute("minOccurs"))
            maxOccurs = int(f_element.attribute("maxOccurs"))

            # Iterate over complex inputs and add combo boxes, text boxes or list widgets
            if complexData.size() > 0:
                # Das i-te ComplexData Objekt auswerten
                complexDataTypeElement = complexData.at(0).toElement()
                complexDataFormat = self.getDefaultMimeType(complexDataTypeElement)
                supportedComplexDataFormat = self.getSupportedMimeTypes(complexDataTypeElement)

                # Store the input formats
                self.inputsMetaInfo[inputIdentifier] = supportedComplexDataFormat
                self.inputDataTypeList[inputIdentifier] = complexDataFormat

                #print "WPS:905 Input Port #", i, inputIdentifier, title, str(complexDataFormat)

                # Attach the selected vector or raster maps
                if isMimeTypeVector(complexDataFormat["MimeType"]) != None:
                # Vector inputs
                    if maxOccurs == 1:
                        port = Port(id=inputIdentifier, name=title, type='input')
                        self.addPort(port)  # PortConfigurationWidget
                    else:
                        port = Port(id=inputIdentifier, name=title, type='input', sigstring=MAP_LAYER)
                        self.addPort(port)  # PortConfigurationWidget
                elif isMimeTypeText(complexDataFormat["MimeType"]) != None:
                    port = Port(id=inputIdentifier, name=title, type='input', sigstring=MAP_LAYER)
                    self.addPort(port)  # PortConfigurationWidget
                elif isMimeTypeRaster(complexDataFormat["MimeType"]) != None:
                    # Raster inputs
                    if maxOccurs == 1:
                        port = Port(id=inputIdentifier, name=title, type='input', sigstring=MAP_LAYER)
                        self.addPort(port)  # PortConfigurationWidget
                    else:
                        port = Port(id=inputIdentifier, name=title, type='input', sigstring=MAP_LAYER)
                        self.addPort(port)  # PortConfigurationWidget
                else:
                    # We assume text inputs in case of an unknown mime type
                    port = Port(id=inputIdentifier, name=title, type='input')
                    self.addPort(port)  # PortConfigurationWidget

        # Create the literal inputs as second
        for i in range(DataInputs.size()):
            f_element = DataInputs.at(i).toElement()
            inputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)

            literalData = f_element.elementsByTagName("LiteralData")
            minOccurs = int(f_element.attribute("minOccurs"))
            maxOccurs = int(f_element.attribute("maxOccurs"))

            if literalData.size() > 0:
                allowedValuesElement = literalData.at(0).toElement()
                aValues = allowedValuesElement.elementsByTagNameNS(
                    "http://www.opengis.net/ows/1.1", "AllowedValues")
                dValue = str(allowedValuesElement.elementsByTagName("DefaultValue").at(0).toElement().text())
                #print "WPS:945 Checking allowed values " + str(aValues.size())
                if aValues.size() > 0:
                    valList = self.allowedValues(aValues)
                    if len(valList) > 0:
                        if len(valList[0]) > 0:
                            port = Port(id=inputIdentifier, name=title, type='input')
                            self.addPort(port)  # PortConfigurationWidget
                        else:
                            port = Port(id=inputIdentifier, name=title, type='input')
                            self.addPort(port)  # PortConfigurationWidget

                else:
                    port = Port(id=inputIdentifier, name=title, type='input')
                    self.addPort(port)  # PortConfigurationWidget

        """
        # At last, create the bounding box inputs
        for i in range(DataInputs.size()):
            f_element = DataInputs.at(i).toElement()
            inputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)

            #port = Port(id=inputIdentifier, name=title, type='input')
            #self.addPort(port)  # PortConfigurationWidget


            bBoxData = f_element.elementsByTagName("BoundingBoxData")
            minOccurs = int(f_element.attribute("minOccurs"))
            maxOccurs = int(f_element.attribute("maxOccurs"))

            if bBoxData.size() > 0:
                crsListe = []
                bBoxElement = bBoxData.at(0).toElement()
                defaultCrsElement = bBoxElement.elementsByTagName("Default").at(0).toElement()
                defaultCrs = defaultCrsElement.elementsByTagName("CRS").at(0).toElement().attributeNS(
                    "http://www.w3.org/1999/xlink", "href")
                crsListe.append(defaultCrs)
                self.addLiteralLineEdit(
                    title + "(minx, miny, maxx, maxy)",
                    inputIdentifier,
                    minOccurs)

                supportedCrsElements = bBoxElement.elementsByTagName("Supported")

                for i in range(supportedCrsElements.size()):
                    crsListe.append(
                        supportedCrsElements.at(i).toElement().elementsByTagName("CRS").at(0).toElement().attributeNS("http://www.w3.org/1999/xlink", "href"))
                    self.literalInputComboBoxList.append(self.addLiteralComboBox(
                        "Supported CRS", inputIdentifier, crsListe, minOccurs))
        """

    def generateProcessOutputPorts(self, DataOutputs):
        """Generate the ports for all inputs defined in process description
        XML file.

        """
        if DataOutputs.size() < 1:
            return
        # Add all outputs
        for i in range(DataOutputs.size()):
            f_element = DataOutputs.at(i).toElement()
            outputIdentifier, title, abstract = self.getIdentifierTitleAbstractFromElement(f_element)

            # Iterate over all complex outputs
            complexOutput = f_element.elementsByTagName("ComplexOutput")
            if complexOutput.size() > 0:
                # Das i-te ComplexData Objekt auswerten
                complexOutputTypeElement = complexOutput.at(0).toElement()
                complexOutputFormat = self.getDefaultMimeType(complexOutputTypeElement)
                supportedcomplexOutputFormat = self.getSupportedMimeTypes(complexOutputTypeElement)
                # Store the output formats
                self.outputsMetaInfo[outputIdentifier] = supportedcomplexOutputFormat
                self.outputDataTypeList[outputIdentifier] = complexOutputFormat
                # Create and store port in list
                port = Port(id=outputIdentifier, name=title, type='output')
                self.addPort(port)  # via PortConfigurationWidget

             # Iterate over all literal outputs
            literalOutput = f_element.elementsByTagName("LiteralOutput")
            if literalOutput.size() > 0:
                # Das i-te ComplexData Objekt auswerten
                literalOutputTypeElement = literalOutput.at(0).toElement()
                literalOutputFormat = self.getDefaultMimeType(literalOutputTypeElement)
                supportedliteralOutputFormat = self.getSupportedMimeTypes(literalOutputTypeElement)
                # Store the output formats
                self.outputsMetaInfo[outputIdentifier] = supportedliteralOutputFormat
                self.outputDataTypeList[outputIdentifier] = literalOutputFormat
                # Create and store port in list
                port = Port(id=outputIdentifier, name=title, type='output')
                self.addPort(port)  # via PortConfigurationWidget

    def getProcessInfo(self):
        """Get information about the selected web process"""
        self.doc.setContent(self.getServiceXML(self.processName, "DescribeProcess", self.processIdentifier))
        dataInputs = self.doc.elementsByTagName("Input")
        dataOutputs = self.doc.elementsByTagName("Output")

        #QApplication.setOverrideCursor(Qt.WaitCursor)
        result = self.getServer(self.processName)
        scheme = result["scheme"]
        path = result["path"]
        server = result["server"]

        postString = '<wps:Execute service="WPS" version="' + self.getServiceVersion() + '"' + \
                   ' xmlns:wps="http://www.opengis.net/wps/1.0.0"' + \
                   ' xmlns:ows="http://www.opengis.net/ows/1.1"' +\
                   ' xmlns:xlink="http://www.w3.org/1999/xlink"' +\
                   ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'\
                   ' xsi:schemaLocation="http://www.opengis.net/wpsExecute_request.xsd">'

        postString += '<ows:Identifier>' + self.processIdentifier + '</ows:Identifier>\n'
        postString += '<wps:DataInputs>' + "</wps:DataInputs>\n"

        """
        # MOVED LAYER-RELATED POST INFO TO "WPS compute()"
        # text/plain inputs
        for textBox in self.complexInputTextBoxList:

        # Do not add undefined inputs
            if textBox == None or str(textBox.document().toPlainText()) == "":
                continue
            postString += xmlExecuteRequestInputStart(textBox.objectName())
            postString += "<wps:ComplexData>" + textBox.document().toPlainText() + "</wps:ComplexData>\n"
            postString += xmlExecuteRequestInputEnd()

        # Literal data as combo box choice
        for comboBox in self.literalInputComboBoxList:
            if comboBox == None or comboBox.currentText() == "":
                continue
            postString += xmlExecuteRequestInputStart(comboBox.objectName())
            postString += "<wps:LiteralData>" + comboBox.currentText() + "</wps:LiteralData>\n"
            postString += xmlExecuteRequestInputEnd()

        # Literal data as combo box choice
        for lineEdit in self.literalInputLineEditList:
            if lineEdit == None or lineEdit.text() == "":
                continue
            postString += xmlExecuteRequestInputStart(lineEdit.objectName())
            postString += "<wps:LiteralData>" + lineEdit.text() + "</wps:LiteralData>\n"
            postString += xmlExecuteRequestInputEnd()
        postString += "</wps:DataInputs>\n"
        """

        # Attach only defined outputs
        if dataOutputs.size() > 0:
            postString += "<wps:ResponseForm>\n"
            # The server might store the result. No lineage should be returned or status
            postString += '<wps:ResponseDocument lineage="false" status="false" storeExecuteResponse="%s">\n' % \
                          (self.processAttributes['store'])


            # Attach ALL literal outputs
            for i in range(dataOutputs.size()):
                f_element = dataOutputs.at(i).toElement()
                outputIdentifier = f_element.elementsByTagName("ows:Identifier").at(0).toElement().text().simplified()
                literalOutputType = f_element.elementsByTagName("LiteralOutput")

                # Complex data is always requested as reference
                if literalOutputType.size() != 0:
                    postString += "<wps:Output>\n"
                    postString += "<ows:Identifier>" + outputIdentifier + \
                                  "</ows:Identifier>\n"
                    postString += "</wps:Output>\n"

            """
            # Attach selected complex outputs
            for comboBox in self.complexOutputComboBoxList:
                # Do not add undefined outputs
                if comboBox == None or str(comboBox.currentText()) == "<None>":
                    continue
                outputIdentifier = comboBox.objectName()

                mimeType = self.outputDataTypeList[outputIdentifier]["MimeType"]
                schema = self.outputDataTypeList[outputIdentifier]["Schema"]
                encoding = self.outputDataTypeList[outputIdentifier]["Encoding"]

                postString += "<wps:Output asReference=\"true\" mimeType=\"" +\
                              mimeType + "\" schema=\"" + schema + "\">"
                postString += "<ows:Identifier>" + outputIdentifier + \
                              "</ows:Identifier>\n"
                postString += "</wps:Output>\n"
            """

            postString += "</wps:ResponseDocument>\n"
            postString += "</wps:ResponseForm>\n"

        postString += "</wps:Execute>\n"

        # Determine full execute request URL
        self.requestURL = result["url"] + '?SERVICE=WPS&VERSION=' + \
            self.getServiceVersion() + '&REQUEST=execute&IDENTIFIER=' + \
            self.processIdentifier

        # Fixed ports
        functions = []
        functions.append(
            (init.OGC_REQUEST_PORT, [self.requestURL]),)
        functions.append(
            (init.WPS_PROCESS_PORT, [self.processIdentifier]),)
        functions.append(
            (init.OGC_POST_DATA_PORT, [postString]),)
        self.controller.update_ports_and_functions(
            self.module.id, [], [], functions)

        if DEBUG:
            self.popUpMessageBox("Execute request", postString)
            # Write the request into a file
            home = os.getenv("HOME")
            outFile = open(home + '/Desktop/qwps_execute_request.xml', 'w')
            outFile.write(postString)
            outFile.close()

    def getIdentifierTitleAbstractFromElement(self, element):
        """Return identifier, title, abstract from an element"""
        inputIdentifier = element.elementsByTagNameNS(
            "http://www.opengis.net/ows/1.1", "Identifier").at(0).toElement().text().simplified()
        title = element.elementsByTagNameNS(
            "http://www.opengis.net/ows/1.1", "Title").at(0).toElement().text().simplified()
        abstract = element.elementsByTagNameNS(
            "http://www.opengis.net/ows/1.1", "Abstract").at(0).toElement().text().simplified()
        return inputIdentifier, title, abstract

    def getDefaultMimeType(self, inElement):
        """TODO: add doc string"""
        myElement = inElement.elementsByTagName("Default").at(0).toElement()
        return self.getMimeTypeSchemaEncoding(myElement)

    def getSupportedMimeTypes(self, inElement):
        """TODO: add doc string"""
        mimeTypes = []
        myElements = inElement.elementsByTagName("Supported").at(0).toElement()
        myFormats = myElements.elementsByTagName('Format')
        for i in range(myFormats.size()):
            myElement = myFormats.at(i).toElement()
            mimeTypes.append(self.getMimeTypeSchemaEncoding(myElement))
        return mimeTypes

    def getMimeTypeSchemaEncoding(self, Element):
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
        return {"MimeType": mimeType, "Schema": schema, "Encoding": encoding}

    def allowedValues(self, aValues):
        """TODO: add doc string"""
        valList = []
        # Manage a value list defined by a range
        value_element = aValues.at(0).toElement()
        v_range_element = value_element.elementsByTagNameNS("http://www.opengis.net/ows/1.1", "Range")
        if v_range_element.size() > 0:
            min_val = value_element.elementsByTagNameNS(
                "http://www.opengis.net/ows/1.1", "MinimumValue").at(0).toElement().text()
            max_val = value_element.elementsByTagNameNS(
                "http://www.opengis.net/ows/1.1", "MaximumValue").at(0).toElement().text()
            for n in range(int(min_val), int(max_val) + 1):
                myVal = QString()
                myVal.append(str(n))
                valList.append(myVal)
        # Manage a value list defined by single values
        v_element = value_element.elementsByTagNameNS(
            "http://www.opengis.net/ows/1.1", "Value")
        if v_element.size() > 0:
            for n in range(v_element.size()):
                mv_element = v_element.at(n).toElement()
                valList.append(unicode(mv_element.text(), 'latin1').strip())
        return valList

    def popUpMessageBox(self, title, detailedText):
        """A message box used for debugging"""
        mbox = WPSMessageBox()
        mbox.setText(title)
        mbox.setDetailedText(detailedText)
        mbox.exec_()

    def getDBEncoding(self, layerProvider):
        """TODO: add doc string"""
        dbConnection = QgsDataSourceURI(layerProvider.dataSourceUri())
        db = QSqlDatabase.addDatabase("QPSQL", "WPSClient")
        db.setHostName(dbConnection.host())
        db.setDatabaseName(dbConnection.database())
        db.setUserName(dbConnection.username())
        db.setPassword(dbConnection.password())
        db.setPort(int(dbConnection.port()))
        db.open()

        query = "select pg_encoding_to_char(encoding) as encoding "
        query += "from pg_catalog.pg_database "
        query += "where datname = '" + dbConnection.database() + "' "

        result = QSqlQuery(query, db)
        result.first()
        encoding = result.value(0).toString()
        db.close()

        return encoding


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
        if textEdit != None:
            textEdit.setMinimumHeight(300)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(300)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return result
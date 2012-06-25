# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
###
### This full package extends VisTrails, providing GIS/Earth Observation
### ingestion, pre-processing, transformation, analytic and visualisation
### capabilities . Included is the abilty to run code transparently in
### OpenNebula cloud environments. There are various software
### dependencies, but all are FOSS.
###
### This file may be used under the terms of the GNU General Public
### License version 2.0 as published by the Free Software Foundation
### and appearing in the file LICENSE.GPL included in the packaging of
### this file.  Please review the following to ensure GNU General Public
### Licensing requirements will be met:
### http://www.opensource.org/licenses/gpl-license.php
###
### If you are unsure which license is appropriate for your use (for
### instance, you are interested in developing a commercial derivative
### of VisTrails), please contact us at vistrails@sci.utah.edu.
###
### This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
### WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
###
#############################################################################
"""TODO  Add documentation to this module.
"""

# library
import sys
import os
import os.path
# third party
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
# vistrails
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from core.modules.module_configure import StandardModuleConfigurationWidget
#eo4vistrails
from packages.eo4vistrails.geoinf.geostrings.GeoStrings import GeoJSONString,  WKTString
from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsRasterLayer
import packages.eo4vistrails.tools.visual


QgsApplication.setPrefixPath("/usr", True)
QgsApplication.initQgis()


class SRSChooserDialog(QDialog):
    '''inspired by http://code.google.com/p/qspatialite/source/browse/trunk/dialogSRS.py?spec=svn45&r=45'''
    def __init__(self, title):
        QDialog.__init__(self)
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        self.selector = QgsProjectionSelector(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Close)

        layout.addWidget(self.selector)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
        self.connect(buttonBox, SIGNAL("rejected()"), self.reject)

    def epsg(self):
        return str(self.selector.selectedEpsg())

    def proj4string(self):
        return self.selector.selectedProj4String()

    def getProjection(self):
        if self.selector.selectedEpsg() != 0:
            return self.epsg()

        if not self.selector.selectedProj4String().isEmpty():
            return self.proj4string()

        return QString()


class GetFeatureInfoTool(QgsMapTool):
    """TODO  Add documentation to this class.
    """
    def __init__(self, canvas, callback, button=None):
        QgsMapTool.__init__(self, canvas)
        self.callback = callback
        self.button = button

    def canvasPressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self.pos = self.toMapCoordinates(e.pos())

            llOffsetPointX = e.pos().x() - 1
            llOffsetPointY = e.pos().y() - 1
            urOffsetPointX = e.pos().x() + 1
            urOffsetPointY = e.pos().y() + 1

            self.llOffsetPoint = self.toMapCoordinates(QPoint(llOffsetPointX, llOffsetPointY))
            self.urOffsetPoint = self.toMapCoordinates(QPoint(urOffsetPointX, urOffsetPointY))

    def canvasReleaseEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self.rect = QgsRectangle(self.llOffsetPoint, self.urOffsetPoint)
            self.callback(self.rect)

    def activate(self):
        if self.button:
            self.button.setChecked(True)
        QgsMapTool.activate(self)

    def deactivate(self):
        if self.button:
            self.button.setChecked(False)
        QgsMapTool.deactivate(self)

    def rbcircle(rb, center, edgePoint, N):
        r = sqrt(center.sqrDist(edgePoint))
        rb.reset(True)
        for itheta in range(N + 1):
            theta = itheta * (2.0 * pi / N)
            # Only the QgsRubberband geometry is modified
            rb.addPoint(QgsPoint(center.x() + r * cos(theta),
                                 center.y() + r * sin(theta)))
        return


class FeatureOfInterestDefinerConfigurationWidget(StandardModuleConfigurationWidget):
    """A widget to configure the FeatureOfInterestDefiner Module."""

    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        self.foi_type = module.name
        #self.module = module
        self.setObjectName("FeatureOfInterestDefinerWidget")
        self.parent_widget = module
        self.path_png_icon = packages.eo4vistrails.geoinf.visual.__path__[0]
        self.path_bkgimg = packages.eo4vistrails.geoinf.visual.__path__[0]
        self.create_config_window()

    def create_config_window(self):
        """TO DO - add docstring"""
        self.setWindowTitle(self.foi_type)
        self.setMinimumSize(800, 850)
        self.center()
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        #set up Group Box for organising CRS of FOI
        self.crsGroupBox = QtGui.QGroupBox("Define Projection or Coordinate Reference System")
        self.crsLayout = QtGui.QHBoxLayout()
        self.crsProj4Label = QtGui.QLabel('SRS Proj4: ')
        self.crsTextAsProj4 = QtGui.QLineEdit('4326')
        self.crsChooseButton = QtGui.QPushButton('&Choose SRS')
        self.crsChooseButton.setAutoDefault(False)
        self.crsChooseButton.setToolTip('Choose a Spatial Reference System or Projection')

        self.crsLayout.addWidget(self.crsProj4Label)
        self.crsLayout.addWidget(self.crsTextAsProj4)
        self.crsLayout.addWidget(self.crsChooseButton)

        self.crsGroupBox.setLayout(self.crsLayout)

        #set up Group Box for getting coords of Bounding Box
        self.bbGroupBox = QtGui.QGroupBox("Define Area of Interest via a Bounding Box in units of SRS")
        self.bbLayout = QtGui.QHBoxLayout()

        self.bbMinXLabel = QtGui.QLabel('MinX/Left: ')
        self.bbMinYLabel = QtGui.QLabel('MinY/Bottom: ')
        self.bbMaxXLabel = QtGui.QLabel('MaxX/Right: ')
        self.bbMaxYLabel = QtGui.QLabel('MaxY/Top: ')

        self.bbMinXText = QtGui.QLineEdit('15')
        self.bbMinYText = QtGui.QLineEdit('-35')
        self.bbMaxXText = QtGui.QLineEdit('35')
        self.bbMaxYText = QtGui.QLineEdit('-20')

        self.bbToMapButton = QtGui.QPushButton('&To Map')
        self.bbToMapButton.setAutoDefault(False)
        self.bbToMapButton.setToolTip('Show Bounding Box on Map')

        self.bbLayout.addWidget(self.bbMinXLabel)
        self.bbLayout.addWidget(self.bbMinXText)
        self.bbLayout.addWidget(self.bbMinYLabel)
        self.bbLayout.addWidget(self.bbMinYText)
        self.bbLayout.addWidget(self.bbMaxXLabel)
        self.bbLayout.addWidget(self.bbMaxXText)
        self.bbLayout.addWidget(self.bbMaxYLabel)
        self.bbLayout.addWidget(self.bbMaxYText)
        self.bbLayout.addWidget(self.bbToMapButton)

        self.bbGroupBox.setLayout(self.bbLayout)

        #set up Group Box for getting text representation of a geometry
        self.asTxtGroupBox = QtGui.QGroupBox("Define Area of Interest via a WKT string in units of SRS")
        self.asTxtLayout = QtGui.QVBoxLayout()

        self.asTxtLabel = QtGui.QLabel('WKT String: ')
        self.asTxtText = QtGui.QTextEdit('')
        self.asTxtToMapButton = QtGui.QPushButton('&To Map')
        self.asTxtToMapButton.setAutoDefault(False)
        self.asTxtToMapButton.setToolTip('Show Bounding Box on Map')

        self.asTxtLayout.addWidget(self.asTxtLabel)
        self.asTxtLayout.addWidget(self.asTxtText)
        self.asTxtLayout.addWidget(self.asTxtToMapButton)

        self.asTxtGroupBox.setLayout(self.asTxtLayout)

        #set up Group Box for Map
        self.MapGroupBox = QtGui.QGroupBox("Map Viewer")
        self.MapLayout = QtGui.QHBoxLayout()
        #sz = QtCore.QSize(200, 300)
        #self.MapLayout.setGeometry(QtCore.QRect(300, 700, 780, 680))
        self.MapGroupBox.setLayout(self.MapLayout)

        ## create canvas
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(200, 200, 255))
        #self.mainLayout.addWidget(self.canvas)

        # icons
        actionAddLayer = QAction(QIcon(self.path_png_icon + \
                        "/mActionAddLayer.png"), "Add Layer", self)
        actionZoomIn = QAction(QIcon(self.path_png_icon + \
                        "/mActionZoomIn.png"), "Zoom In", self)
        actionZoomOut = QAction(QIcon(self.path_png_icon + \
                        "/mActionZoomOut.png"), "Zoom Out", self)
        actionPan = QAction(QIcon(self.path_png_icon + \
                        "/mActionPan.png"), "Pan", self)
        actionIdentify = QAction(QIcon(self.path_png_icon + \
                        "/mActionIdentify.png"), "Feature Information", self)

        # create toolbar
        self.toolbar = QToolBar()  # "Canvas actions"
        self.toolbar.addAction(actionAddLayer)
        self.toolbar.addAction(actionZoomIn)
        self.toolbar.addAction(actionZoomOut)
        self.toolbar.addAction(actionPan)
        self.toolbar.addAction(actionIdentify)

        # create layer explorer pane
        self.explorer = QDockWidget("Layers")
        self.explorer.resize(60, 100)
        #~self.explorerListWidget = QtGui.QListWidget()
        #~self.explorerListWidget.setObjectName("listWidget")
        #~self.explorer.setWidget(self.explorerListWidget)

        # create map tools
        self.toolPan = QgsMapToolPan(self.canvas,)
        self.toolPan.setAction(actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False)  # false == in
        self.toolZoomIn.setAction(actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True)  # true == out
        self.toolZoomOut.setAction(actionZoomOut)
        self.toolAOI = QgsMapTool(self.canvas)
        self.toolIdentify = GetFeatureInfoTool(self.canvas, self.gotFeatureForIdentification)
        self.toolIdentify.setAction(actionIdentify)

        # layerList explorer
        self.GroupBoxLyrExplorer = QtGui.QGroupBox("")
        self.vboxLyrExplorer = QtGui.QVBoxLayout()
        self.GroupBoxLyrExplorer.setLayout(self.vboxLyrExplorer)
        self.MapLayout.addWidget(self.GroupBoxLyrExplorer)
        self.label = QtGui.QLabel("")
        self.vboxLyrExplorer.addWidget(self.label)
        self.vboxLyrExplorer.addWidget(self.explorer)

        # toolbar and canvas layout
        self.GroupBoxToolBarMapCanvas = QtGui.QGroupBox("")
        self.vboxToolBarMapCanvas = QtGui.QVBoxLayout()
        self.vboxToolBarMapCanvas.setGeometry(QtCore.QRect(300, 700, 780, 680))
        self.GroupBoxToolBarMapCanvas.setLayout(self.vboxToolBarMapCanvas)
        self.MapLayout.addWidget(self.GroupBoxToolBarMapCanvas)
        self.vboxToolBarMapCanvas.addWidget(self.toolbar)
        self.vboxToolBarMapCanvas.addWidget(self.canvas)

        #global list to hold inputlayers list -> accessible for toggleLayer
        self.mylist = []

        #finalise/cancel buttons
        self.finishGroupBox = QtGui.QGroupBox("Finish")
        self.buttonLayout = QtGui.QHBoxLayout()
        self.finishGroupBox.setLayout(self.buttonLayout)
        self.buttonLayout.setGeometry(QtCore.QRect(300, 500, 780, 680))
        self.buttonLayout.setMargin(5)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setShortcut('Esc')
        self.buttonLayout.addStretch(1)  # force buttons to the right
        self.buttonLayout.addWidget(self.cancelButton)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setAutoDefault(False)
        self.buttonLayout.addWidget(self.okButton)
        self.connect(self.okButton,
                     QtCore.SIGNAL('clicked(bool)'),
                     self.okTriggered)
        self.connect(self.cancelButton,
                     QtCore.SIGNAL('clicked(bool)'),
                     self.close)

        self.mainLayout.addWidget(self.crsGroupBox)
        self.mainLayout.addWidget(self.bbGroupBox)
        self.mainLayout.addWidget(self.asTxtGroupBox)
        self.mainLayout.addWidget(self.MapGroupBox)
        self.mainLayout.addWidget(self.finishGroupBox)

        # set signals
        self.connect(self.crsChooseButton, QtCore.SIGNAL('clicked(bool)'), self.getSRS)
        self.connect(self.bbToMapButton, QtCore.SIGNAL('clicked(bool)'), self.bbToMapBB)
        self.connect(self.asTxtToMapButton, QtCore.SIGNAL('clicked(bool)'), self.bbToMapTxt)
        self.connect(actionAddLayer, SIGNAL("activated()"), self.addLayer)
        self.connect(actionZoomIn, SIGNAL("activated()"), self.zoomIn)
        self.connect(actionZoomOut, SIGNAL("activated()"), self.zoomOut)
        self.connect(actionPan, SIGNAL("activated()"), self.pan)
        self.connect(actionIdentify, QtCore.SIGNAL("triggered()"), self.identifyFeature)

        #load a backdrop layer
        self.mapCanvasLayers = []
        fname = self.path_bkgimg + '/bluemarblemerged.img'
        fileInfo = QFileInfo(fname)
        baseName = fileInfo.baseName()
        self.bmLayer = QgsRasterLayer(fname,  baseName)
        QgsMapLayerRegistry.instance().addMapLayer(self.bmLayer)
        self.cl = QgsMapCanvasLayer(self.bmLayer)
        self.mapCanvasLayers.append(self.cl)
        # Set extent to the extent of our layer
        self.canvas.setExtent(self.bmLayer.extent())
        self.canvas.enableAntiAliasing(True)
        self.canvas.freeze(False)
        self.canvas.setLayerSet(self.mapCanvasLayers)
        self.canvas.refresh()

        #now, add a container layer for our text based/ digitised or selected geoms
        self.addMemoryLayer()

        #self.update()

    def center(self):
        """TO DO - add docstring"""
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def getSRS(self):
        # retruns the description and proj4 string of the chosen SRS, from the SRSDialog
        srsdlg = SRSChooserDialog("Choose SRS")
        if srsdlg.exec_():
            self.crsTextAsProj4.setText(srsdlg.getProjection())

    def bbToMapBB(self):
        self.bbToMap(fullWkt=False)

    def bbToMapTxt(self):
        self.bbToMap(fullWkt=True)

    def bbToMap(self, fullWkt=False):
        '''takes bounding box coords and puts them on the map'''
        #if self.foi_type == "AreaOfInterestDefiner":
        if not fullWkt:
            ix = self.bbMinXText.text()
            iy = self.bbMinYText.text()
            ax = self.bbMaxXText.text()
            ay = self.bbMaxYText.text()

            wkt = "POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))" % \
                  (ix,  iy,  ix,  ay,  ax,  ay,  ax,  iy,  ix,  iy)
        else:
            wkt = self.asTxtText.toPlainText()
        try:
            errnum = 0
            geom = QgsGeometry().fromWkt(wkt)
            print "gotGeom"
            if self.foi_type == "AreaOfInterestDefiner" and geom.type() != 2:
                errnum = 1
            elif self.foi_type == "LineOfInterestDefiner" and geom.type() != 1:
                errnum = 1
            elif self.foi_type == "PointOfInterestDefiner" and geom.type() != 0:
                errnum = 1
            else:
                print "attempting to add geometry to mem layer"
                self.addGeomToMemoryLayer(geom)

            if errnum == 1:
                raise ModuleError(self, "Incorrect Geometry Type chosen")
        except:
            raise ModuleError(self, "Could not generate Geometry from text provided")
        #else:
            #print "Cannot create a Bounding box feature on a line or point layer"
        #add to map

    #map tool functions
    def addLayer(self):
        """TO DO: Add doc string"""
        fileName = QFileDialog.getOpenFileName(
            parent=None,
            caption="Select Vector Overlay Layer",
            filter="Vector Files (*.shp *.geojson *.gml)")

        print fileName
        info = QtCore.QFileInfo(fileName)
        print info.filePath()
        print info.completeBaseName()
        # create layer
        layer = QgsVectorLayer(info.filePath(), info.completeBaseName(),  "ogr")

        if not layer.isValid():
            print "invalid layer"
            return

        # add layer to the registry
        QgsMapLayerRegistry.instance().addMapLayer(layer)

        # set extent to the extent of our layer
        #self.canvas.setExtent(layer.extent())

        # set the map canvas layer set
        cl = QgsMapCanvasLayer(layer)
        self.mapCanvasLayers.insert(len(self.mapCanvasLayers) - 2, cl)
        #layers = [cl]
        self.canvas.setLayerSet(self.mapCanvasLayers)
        print "added Layer"

    def addMemoryLayer(self):
        '''Adds a layer to contain the feature defined by a bounding box, wkt,
        digitised poly|line|point or selection from other layer.
        '''
        foi_type = self.foi_type.lower()
        if foi_type == 'areaofinterestdefiner':
            layer = QgsVectorLayer("Polygon", "Area of Interest",  "memory")
        if foi_type == 'lineofinterestdefiner':
            layer = QgsVectorLayer("Linestring", "Line of Interest",  "memory")
        if foi_type == 'pointofinterestdefiner':
            layer = QgsVectorLayer("Point", "Point of Interest",  "memory")

        if foi_type == 'areaofinterestdefiner':
            sym = QgsSymbol(QGis.Polygon)
            sym.setColor(Qt.black)
            sym.setFillColor(Qt.green)
            sym.setFillStyle(Qt.Dense6Pattern)
            sym.setLineWidth(0.5)
            sr = QgsSingleSymbolRenderer(QGis.Polygon)
        if foi_type == 'lineofinterestdefiner':
            sym = QgsSymbol(QGis.Line)
            sym.setColor(Qt.black)
            sym.setFillColor(Qt.green)
            sym.setFillStyle(Qt.SolidPattern)
            sym.setLineWidth(0.5)
            sr = QgsSingleSymbolRenderer(QGis.Line)
        if foi_type == 'pointofinterestdefiner':
            sym = QgsSymbol(QGis.Point)
            sym.setColor(Qt.black)
            sym.setFillColor(Qt.green)
            sym.setFillStyle(Qt.SolidPattern)
            sym.setLineWidth(0.3)
            sym.setPointSize(4)
            sym.setNamedPointSymbol("hard:triangle")
            sr = QgsSingleSymbolRenderer(QGis.Point)

        sr.addSymbol(sym)
        layer.setRenderer(sr)
        if not layer.isValid():
            print "invalid layer"
            return
        ml_dp = layer.dataProvider()
        ml_dp.addAttributes([QgsField("gid", QVariant.String)])
        # add layer to the registry
        self.mem_layer_obj = QgsMapLayerRegistry.instance().addMapLayer(layer)

        # set extent to the extent of our layer
        #self.canvas.setExtent(layer.extent())

        # set the map canvas layer set
        cl = QgsMapCanvasLayer(layer)
        self.mapCanvasLayers.insert(0, cl)
        #layers = [cl]
        self.canvas.setLayerSet(self.mapCanvasLayers)
        print "added Layer"

    def addGeomToMemoryLayer(self, the_geom, origin=0, delete_when_done=False):
        """TO DO: Add doc string"""
        foi_type = self.foi_type.lower()
        print "got foi_type"
        if self.mem_layer_obj.featureCount() > 0:
            if origin == 1:  # is added by identify operation
                pass
            else:
                print self.mem_layer_obj.featureCount()
                print "there exists a feature, kill it!"
                self.mem_layer_obj.select()
                print "Feature count selcted for deletion:"
                print self.mem_layer_obj.selectedFeatureCount()
                self.mem_layer_obj.deleteSelectedFeatures()
                #self.mem_layer_obj.deleteFeature(0)
                self.mem_layer_obj.commitChanges()
                self.mem_layer_obj.triggerRepaint()

        ml_dp = self.mem_layer_obj.dataProvider()
        print "got DP"
        uuid_gid = QUuid().createUuid().toString()
        print "got uuid"
        fet = QgsFeature()
        print "got feature with id"
        fet.setGeometry(the_geom)
        print "set geometry"
        fet.addAttribute(0, uuid_gid)
        print "set attr "
        ml_dp.addFeatures([fet])
        self.mem_layer_obj.commitChanges()
        print "added layers"
        #self.mem_layer_obj.updateFeatureAttributes(fet)
        #self.mem_layer_obj.updateFeatureGeometry(fet)
        self.mem_layer_obj.updateExtents()
        print "updated extents"
        #self.mem_layer_obj.drawFeature(fet)
        self.mem_layer_obj.triggerRepaint()
        print "trp"
        return fet.id()

    def zoomIn(self):
        """TO DO: Add doc string"""
        self.canvas.setMapTool(self.toolZoomIn)

    def zoomOut(self):
        """TO DO: Add doc string"""
        self.canvas.setMapTool(self.toolZoomOut)

    def pan(self):
        """TO DO: Add doc string"""
        self.canvas.setMapTool(self.toolPan)

    def identifyFeature(self):
        '''getFeatureInfo functionality'''
        self.canvas.setMapTool(self.toolIdentify)
        #print "GFI not yet implemented"

    def gotFeatureForIdentification(self, pos):
        """Show a dialog with road information """
        #pos is a rectangle
        self.mem_layer_obj.select()
        ftr = QgsFeature()
        ftr_ids = []
        while self.mem_layer_obj.nextFeature(ftr):
            if ftr.geometry().intersects(pos):
                ftr_ids.append(ftr.id())
        self.chosenFOIGeoms = []
        self.info = QgsMessageViewer()
        if ftr_ids != []:
            f = QgsFeature()
            foi_type = self.foi_type.lower()
            if foi_type == 'areaofinterestdefiner':
                ftrData = "You have selected the following feature(s) for use as an Area of Interest:\n\n"
            if foi_type == 'lineofinterestdefiner':
                ftrData = "You have selected the following feature(s) for use as a Line of Interest:\n\n"
            if foi_type == 'pointofinterestdefiner':
                ftrData = "You have selected the following feature(s) for use as a Point of Interest:\n\n"
            for fid in ftr_ids:
                self.mem_layer_obj.dataProvider().featureAtId(fid, f,  True)
                ftrData += f.attributeMap()[0].toString()
                ftrData += "\n_____________________________\n"
                self.chosenFOIGeoms.append(f.geometry())
                id_fid = self.addGeomToMemoryLayer(f.geometry())
            self.info.setMessageAsPlainText(ftrData)
        else:
            self.info.setMessageAsPlainText("no data to show")
        self.info.show()
        return

    def makeAOI(self):
        pass

    def makeLOI(self):
        pass

    def makePOI(self):
        pass

    def okTriggered(self):
        the_fet = QgsFeature()
        the_geoms = []
        print self.mem_layer_obj.featureCount()
        self.mem_layer_obj.select()
        while self.mem_layer_obj.nextFeature(the_fet):
            #self.mem_layer_obj.featureAtId(0, the_fet)

            the_geoms.append(str(the_fet.geometry().exportToWkt()))
        print the_geoms
        wktstr = WKTString()
        print wktstr

        wktstr.setValue(the_geoms[0])

        self.controller.update_ports_and_functions(
                self.module.id, [], [], [("WKTGeometry", the_geoms),
                    ("SRS", [self.crsTextAsProj4.text()])])
        self.close()
        #self.controller.update_ports_and_functions(self.module.id, [], [], functions)
        # NB -  functions - array of port tuples - ("portname", array_of_port_values)
        #       port_value MUST be wrapped in an array, as Vistrails allows for
        #       possibility of multiple inputs to a port


class FeatureOfInterestDefiner(Module):
    '''A utility to extract a Feature of Interest expressed as a GeoJSON snippet
    - e.g. use case: an Area-Of-Interest to be used as a cookie cutter
           in subsetting or zonal statistics gathering
    - e.g. use case: defining a Line-Of-Interest transect for use in longitudanal analyses
    - e.g. use case: defining a Point-Of-Interest for time-series extraction at a point

    uses a QGIS Map layer to define a feature that is outputted as the AOI
    - can take a user defined polygon
    - can take a user defined string, e.g. WKT or GeoJSON
    - can take a vector layer, from which a feature must be chosen
    '''

    def __init__(self):
        Module.__init__(self)

    def checkGeom(self,  expected_type):
        '''Check the geom to see if it can be instantiated as the expected type
            - enum of {'point','line','polygon'}'''
        testGeom = QgsGeometry().fromWkt(self.wkt)
        if expected_type == 'point':
            if testGeom.type() == 0:
                return True
            else:
                return False
        if expected_type == 'line':
            if testGeom.type() == 1:
                return True
            else:
                return False
        if expected_type == 'polygon':
            if testGeom.type() == 2:
                return True
            else:
                return False

    def compute(self):
        '''implemented by subclasses'''
        pass


class AreaOfInterestDefiner(FeatureOfInterestDefiner):
    '''

    use case: an Area-Of-Interest to be used as a cookie cutter
    in subsetting or zonal statistics gathering

    uses a QGIS Map layer to define a feature that is outputted as the AOI
    - can take a user defined polygon
    - can take a user defined string, e.g. WKT or GeoJSON
    - can take a vector layer, from which a feature must be chosen
    '''

    def __init__(self):
        FeatureOfInterestDefiner.__init__(self)

    def compute(self):
        ''''''
        if self.hasInputFromPort("WKTGeometry"):
            print "gotwkt"
            self.wkt = self.getInputFromPort("WKTGeometry")
        if self.hasInputFromPort("SRS"):
            self.srs = self.getInputFromPort("SRS")
        if self.checkGeom("polygon"):
            self.setResult('AreaOfInterest', self.wkt)
        else:
            raise ModuleError(self, "Incorrect Geometry Type provided - expected Polygon")


class LineOfInterestDefiner(FeatureOfInterestDefiner):
    '''Define a Line-Of-Interest transect for use in longitudinal analyses

    uses a QGIS Map layer to define a feature that is outputted as the AOI
    - can take a user defined polygon
    - can take a user defined string, e.g. WKT or GeoJSON
    - can take a vector layer, from which a feature must be chosen
    '''

    def __init__(self):
        FeatureOfInterestDefiner.__init__(self)

    def compute(self):
        ''''''
        if self.checkGeom("line"):
            self.setResult('LineOfInterest', self.wkt)
        else:
            raise ModuleError(self, "Incorrect Geometry Type provided - expected Line")


class PointOfInterestDefiner(FeatureOfInterestDefiner):
    '''Define a Point-Of-Interest for time-series extraction at a point

    uses a QGIS Map layer to define a feature that is outputted as the AOI
    - can take a user defined polygon
    - can take a user defined string, e.g. WKT or GeoJSON
    - can take a vector layer, from which a feature must be chosen
    '''

    def __init__(self):
        FeatureOfInterestDefiner.__init__(self)

    def compute(self):
        ''''''
        if self.checkGeom("line"):
            self.setResult('PointOfInterest', self.wkt)
        else:
            raise ModuleError(self, "Incorrect Geometry Type provided - expected Point")



#def initialize(*args, **keywords):
#    """sets everything up"""
#    # We'll first create a local alias for the module_registry so that
#    # we can refer to it in a shorter way.
#    reg = core.modules.module_registry.get_module_registry()
#    reg.add_module(FeatureOfInterestDefiner, configureWidgetType=FeatureOfInterestDefinerWidget,  namespace="utils",  abstract = True)
#    reg.add_module(AreaOfInterestDefiner, configureWidgetType=FeatureOfInterestDefinerWidget, namespace="utils")
#    reg.add_module(LineOfInterestDefiner, configureWidgetType=FeatureOfInterestDefinerWidget, namespace="utils")
#    reg.add_module(PointOfInterestDefiner, configureWidgetType=FeatureOfInterestDefinerWidget, namespace="utils")
#    #input ports
#    ##can you have a module with no input ports?
#    reg.add_input_port(
#        FeatureOfInterestDefiner,
#        "Base Layer",
#        (QgsRasterLayer,  'Base Layer for adding context')
#                       )
#    #output ports
#    reg.add_output_port(
#        FeatureOfInterestDefiner,
#        "FeatureOfInterest",
#        (GeoJSONString, 'Feature as GeoJSON snippet'))
#
#    reg.add_output_port(
#        AreaOfInterestDefiner,
#        "AreaOfInterest",
#        (GeoJSONString, 'Area as GeoJSON snippet'))
#
#    reg.add_output_port(
#        LineOfInterestDefiner,
#        "LineOfInterest",
#        (GeoJSONString, 'Line as GeoJSON snippet'))
#
#    reg.add_output_port(
#        PointOfInterestDefiner,
#        "PointOfInterest",
#        (GeoJSONString, 'Point as GeoJSON snippet'))
#

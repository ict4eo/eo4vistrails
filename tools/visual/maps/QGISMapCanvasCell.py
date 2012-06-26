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
"""This package provides GIS capabilities for eo4vistrails.
This module provides a means for displaying raster and vector data,
using QGIS and SpreadsheetCell capabilities.
"""
# library
import sys
import os
import os.path
# third party
from PyQt4 import QtCore, QtGui
# TODO: remove import * statements !!!
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
# vistrails
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import core.system
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget
# eo4vistrails
#from packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin
# local
import packages.eo4vistrails.tools.visual.maps


path_png_icon = packages.eo4vistrails.tools.visual.__path__[0]
# TODO - move this elsewhere ... higher than local init.py
QgsApplication.setPrefixPath("/usr", True)
QgsApplication.initQgis()


class QGISMapCanvasCell(SpreadsheetCell):  # ( ThreadSafeMixin, SpreadsheetCell):
    """TO DO: Add doc string
    """

    def __init__(self):
        #ThreadSafeMixin.__init__(self)
        SpreadsheetCell.__init__(self)

    def compute(self):
        """ compute() -> None"""
        if self.hasInputFromPort("baselayer"):
            self.base_layer = self.getInputFromPort("baselayer")
            if self.base_layer:
                #print "QGISMapCanvas:74", self.base_layer.results_file
                try:
                    self.crsDest = \
                        QgsCoordinateReferenceSystem(self.base_layer.crs())
                except:
                    self.crsDest = None
                if self.hasInputFromPort("layer"):
                    self.layers = self.getInputListFromPort("layer")
                    # add base layer LAST (last in, first out)
                    self.layers.append(self.base_layer)
                else:
                    self.layers = self.getInputFromPort("baselayer")
                self.cellWidget = self.displayAndWait(QGISMapCanvasCellWidget,
                                                (self.layers, self.crsDest))
            else:
                raise ModuleError(
                    self,
                    'A valid base layer must be defined')
        else:
            raise ModuleError(
                self,
                'The base layer port must be set to valid map layer')


class QGISMapCanvasCellWidget(QCellWidget):
    """TO DO: Add doc string
    """

    def __init__(self, parent=None):
        """TO DO: Add doc string"""
        QCellWidget.__init__(self, parent)

        # set widgets layouts
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)

        # create canvas
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(240, 255, 180))
        #self.mainLayout.addWidget(self.canvas)

        # icons
        actionAddLayer = QAction(QIcon(path_png_icon + \
                        "/mActionAddLayer.png"), "Add Layer", self)
        actionZoomIn = QAction(QIcon(path_png_icon + \
                        "/mActionZoomIn.png"), "Zoom In", self)
        actionZoomOut = QAction(QIcon(path_png_icon + \
                        "/mActionZoomOut.png"), "Zoom Out", self)
        actionPan = QAction(QIcon(path_png_icon + \
                        "/mActionPan.png"), "Pan", self)

        # create toolbar
        self.toolbar = QToolBar()
        self.toolbar.addAction(actionAddLayer)
        self.toolbar.addAction(actionZoomIn)
        self.toolbar.addAction(actionZoomOut)
        self.toolbar.addAction(actionPan)

        # layerList explorer#~
        self.GroupBoxLyrExplorer = QtGui.QGroupBox("")
        self.vboxLyrExplorer = QtGui.QVBoxLayout()
        self.GroupBoxLyrExplorer.setLayout(self.vboxLyrExplorer)
        self.mainLayout.addWidget(self.GroupBoxLyrExplorer)
        self.label = QtGui.QLabel("")
        self.vboxLyrExplorer.addWidget(self.label)
        # create layer explorer dock#~
        self.explorer = QDockWidget("Layers")#~
        self.explorer.resize(60, 100)#~
        self.vboxLyrExplorer.addWidget(self.explorer)
        # create layer explorer pane#~
        self.explorerListWidget = QtGui.QListWidget()#~
        self.explorerListWidget.setObjectName("listWidget")#~
        self.explorer.setWidget(self.explorerListWidget)#~
        # create layer explorer signal#~
        self.explorerListWidget.itemClicked.connect(
            self.on_listWidget_itemClicked)#~

        # create map tools
        self.toolPan = QgsMapToolPan(self.canvas,)
        self.toolPan.setAction(actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False)  # false == in
        self.toolZoomIn.setAction(actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True)  # true == out
        self.toolZoomOut.setAction(actionZoomOut)

        # toolbar and canvas layout
        self.GroupBoxToolBarMapCanvas = QtGui.QGroupBox("")
        self.vboxToolBarMapCanvas = QtGui.QVBoxLayout()
        self.GroupBoxToolBarMapCanvas.setLayout(self.vboxToolBarMapCanvas)
        self.mainLayout.addWidget(self.GroupBoxToolBarMapCanvas)
        self.vboxToolBarMapCanvas.addWidget(self.toolbar)
        self.vboxToolBarMapCanvas.addWidget(self.canvas)

        # set map processing signals
        self.connect(actionAddLayer, SIGNAL("activated()"), self.addLayer)
        self.connect(actionZoomIn, SIGNAL("activated()"), self.zoomIn)
        self.connect(actionZoomOut, SIGNAL("activated()"), self.zoomOut)
        self.connect(actionPan, SIGNAL("activated()"), self.pan)

        #global list to hold inputlayers list -> accessible for toggleLayer
        self.mylist = []

    def addLayer(self):
        """TO DO: Add doc string"""
        QtGui.QMessageBox.information(
            self,
            "INFORMATION:", "Functionality not implemented",
            QtGui.QMessageBox.Ok)

    def zoomIn(self):
        """TO DO: Add doc string"""
        self.canvas.setMapTool(self.toolZoomIn)

    def zoomOut(self):
        """TO DO: Add doc string"""
        self.canvas.setMapTool(self.toolZoomOut)

    def pan(self):
        """TO DO: Add doc string"""
        self.canvas.setMapTool(self.toolPan)

    def updateContents(self, inputPorts):
        """Updates the contents with a new, changed filename

        updateContents(inputPorts: tuple) -> None
        """
        allowedGreyStyles = [QgsRasterLayer.SingleBandGray,
             QgsRasterLayer.MultiBandSingleBandPseudoColor,
             QgsRasterLayer.MultiBandSingleBandGray,
             QgsRasterLayer.SingleBandPseudoColor]
        allowedRgbStyles = [QgsRasterLayer.MultiBandColor]

        (inputLayers, crsDest) = inputPorts
        if type(inputLayers) != list:
            inputLayers = [inputLayers]
        else:
            pass
            #TODO handle the list case.

        # allow "auto" (on the fly) reprojection
        #   transform other layers to same co-ordinate system as base layer
        #   NB raster layers cannot be projected in QGIS 1.6 and earlier
        myrender = self.canvas.mapRenderer()
        myrender.setProjectionsEnabled(True)
        if crsDest:
            myrender.setDestinationCrs(crsDest)

        # Add layers to canvas
        mapCanvasLayers = []
        for layer in inputLayers:
            if layer.isValid():
                # Add layer to the registry (one registry for ALL maps ???)
                QgsMapLayerRegistry.instance().addMapLayer(layer, True)
                # Set up the map canvas layer
                cl = QgsMapCanvasLayer(layer)
                mapCanvasLayers.append(cl)
                # populate mylist with inputLayers's items
                self.mylist.append(layer)
                # test if the layer is a raster from a local file (not a wms)
                if layer.type() == layer.RasterLayer:
                    # and ( not layer.usesProvider() ):
                    # Test if the raster is single band greyscale
                    #layer.setMinimumMaximumUsingLastExtent()
                    #layer.setContrastEnhancementAlgorithm(
                    #   QgsContrastEnhancement.StretchToMinimumMaximum)
                    #layer.setCacheImage( None )
                    #layer.setStandardDeviations( 0.0 )
                    # make sure the layer is redrawn
                    #layer.triggerRepaint()
                    if layer.drawingStyle() in allowedGreyStyles:
                        #Everything looks fine so set stretch and exit
                        #For greyscale layers there is only ever one band
                        # base 1 counting in gdal
                        band = layer.bandNumber(layer.grayBandName())
                        #extentMin = 0.0
                        #extentMax = 0.0
                        generateLookupTableFlag = False
                        # compute the min and max for the current extent
                        #extentMin, extentMax = layer.computeMinimumMaximumEstimates(band)
                        #if extentMin == 0 and extentMax == 0:
                        extentMin = -1
                        extentMax = 1
                        #print "QGISMapCanvas:246 min max color", extentMin, extentMax
                        # set the layer min value for this band
                        layer.setMinimumValue(band, extentMin, generateLookupTableFlag)
                        # set the layer max value for this band
                        layer.setMaximumValue(band, extentMax, generateLookupTableFlag)
                        # ensure that stddev is set to zero
                        layer.setStandardDeviations(0.0)
                        # let the layer know that the min max are user defined
                        layer.setUserDefinedGrayMinimumMaximum(True)
                        # ensure any cached render data for this layer is cleared
                        layer.setCacheImage(None)
                        # make sure the layer is redrawn
                    elif layer.drawingStyle() in allowedRgbStyles:
                        #Everything looks fine so set stretch and exit
                        redBand = layer.bandNumber(layer.redBandName())
                        greenBand = layer.bandNumber(layer.greenBandName())
                        blueBand = layer.bandNumber(layer.blueBandName())
                        extentRedMin = 0.0
                        extentRedMax = 0.0
                        extentGreenMin = 0.0
                        extentGreenMax = 0.0
                        extentBlueMin = 0.0
                        extentBlueMax = 0.0
                        generateLookupTableFlag = False
                        # compute the min and max for the current extent
                        extentRedMin, extentRedMax = layer.computeMinimumMaximumEstimates(redBand)
                        extentGreenMin, extentGreenMax = layer.computeMinimumMaximumEstimates(greenBand)
                        extentBlueMin, extentBlueMax = layer.computeMinimumMaximumEstimates(blueBand)
                        # set the layer min max value for the red band
                        layer.setMinimumValue(redBand, extentRedMin, generateLookupTableFlag)
                        layer.setMaximumValue(redBand, extentRedMax, generateLookupTableFlag)
                        # set the layer min max value for the red band
                        layer.setMinimumValue(greenBand, extentGreenMin, generateLookupTableFlag)
                        layer.setMaximumValue(greenBand, extentGreenMax, generateLookupTableFlag)
                        # set the layer min max value for the red band
                        layer.setMinimumValue(blueBand, extentBlueMin, generateLookupTableFlag)
                        layer.setMaximumValue(blueBand, extentBlueMax, generateLookupTableFlag)
                        # ensure that stddev is set to zero
                        layer.setStandardDeviations(0.0)
                        # let the layer know that the min max are user defined
                        layer.setUserDefinedRGBMinimumMaximum(True)
                        # ensure any cached render data for this layer is cleared
                        layer.setCacheImage(None)
                        # make sure the layer is redrawn
                    layer.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
                    layer.triggerRepaint()
                # Set extent to the extent of our layer
                self.canvas.setExtent(layer.extent())
                layer.triggerRepaint()

        self.set_layer_labels(inputLayers)#~

        # Set extent to the extent of ALL layers
        #self.canvas.zoomFullExtent() ??? not valid function
        self.canvas.enableAntiAliasing(True)
        self.canvas.freeze(False)
        self.canvas.setLayerSet(mapCanvasLayers)
        self.canvas.refresh()
        #self.update()  # ???

    def on_listWidget_itemClicked(self, item):
        """TO DO: Add doc string"""
        if item.listWidget().itemWidget(item) != None:
            if item.checkState() == QtCore.Qt.Checked:
                self.searchLayerIndex(item)
                item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Checked)
                self.searchLayerIndex(item)

    def searchLayerIndex(self, item):
        """TO DO: Add doc string"""
        selected_layer = item.listWidget().itemWidget(item).text()
        for lyrIndex in self.mylist:
            # store the index of layer
            indexValue = self.mylist.index(lyrIndex)
            if selected_layer == str(lyrIndex.name()):
                self.toggleLayer(indexValue)

    def toggleLayer(self, lyrNr):
        """Set layer transparency on/off"""
        lyr = self.canvas.layer(lyrNr)
        if lyr:
            cTran = lyr.getTransparency()
            lyr.setTransparency(0 if cTran > 100 else 255)
            self.canvas.refresh()

    def set_layer_labels(self, inputLayers):
        """Create and display a set of layer labels."""
        self.explorerListWidget.clear()#~
        #print "self.explorerListWidget count", self.explorerListWidget.count()
        # get layernames from inputLayers, and use them as labels in explorerListWidget
        for lyr in inputLayers:
            item = QtGui.QListWidgetItem()
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.explorerListWidget.addItem(item)#~
            self.widget = QtGui.QLabel(lyr.name())
            self.explorerListWidget.setItemWidget(item, self.widget)#~

    '''
    def getLayerNames(self):
        """Return list of names of all layers in QgsMapLayerRegistry"""
        layermap = QgsMapLayerRegistry.instance().mapLayers()
        layerlist = []
        #if mapCanvasLayers == "all":
        for name, layer in layermap.iteritems():
            layerlist.append(layer.name())
            #layerlist.insert(0,layer.name())
        print "layers in QgsMapLayerRegistry in GetLayers Methods"
        for lyr in layerlist:
            x = layerlist.index(lyr)
            print lyr , x
        else:
            for name, layer in layermap.iteritems():
                if layer.type() == QgsMapLayer.VectorLayer:
                    if layer.geometryType() in mapCanvasLayers:
                        layerlist.append(layer.name())
                elif layer.type() == QgsMapLayer.RasterLayer:
                    if "Raster" in inputLayers:
                        layerlist.append(layer.name())
        return layerlist
    '''

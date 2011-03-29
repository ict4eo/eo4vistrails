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
import packages.eo4vistrails.geoinf.visual
# local


path_png_icon = packages.eo4vistrails.geoinf.visual.__path__[0]
QgsApplication.setPrefixPath("/usr", True)
QgsApplication.initQgis()


class QGISMapCanvasCell(SpreadsheetCell):
    """TO DO: Add doc string
    """
    def compute(self):
        """ compute() -> None"""
        if self.hasInputFromPort("baselayer"):
            self.base_layer = self.getInputFromPort("baselayer")
            #print "base_layer id/type/srs :", base_layer.getLayerID(), type(base_layer), base_layer.srs()
            self.crsDest = QgsCoordinateReferenceSystem(self.base_layer.srs())
            if self.hasInputFromPort("layer"):
                self.layers = self.getInputListFromPort("layer")
                # add base layer LAST (last in, first out)
                self.layers.append(self.base_layer)
            else:
                self.layers = self.getInputFromPort("baselayer")
            self.cellWidget = self.displayAndWait(QGISMapCanvasCellWidget,
                                                  (self.layers,self.crsDest))
        else:
            raise ModuleError(
                self,
                'A base layer must be set'
                )


class QGISMapCanvasCellWidget(QCellWidget, QMainWindow):
    """TO DO: Add doc string
    """
    def __init__(self, parent=None):
        """TO DO: Add doc string"""
        QCellWidget.__init__(self, parent)
        QMainWindow.__init__(self)

        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(200,200,255))
        self.canvas.show()
        self.tools = QMainWindow()

        actionAddLayer = QAction(QIcon(path_png_icon + \
                        "/mActionAddLayer.png"), "Add Layer", self.tools)
        actionZoomIn = QAction(QIcon(path_png_icon + \
                        "/mActionZoomIn.png"), "Zoom In", self.tools)
        actionZoomOut = QAction(QIcon(path_png_icon + \
                        "/mActionZoomOut.png"), "Zoom Out", self.tools)
        actionPan = QAction(QIcon(path_png_icon + \
                        "/mActionPan.png"), "Pan", self.tools)

        # toolbar
        self.toolbar = self.tools.addToolBar("Canvas actions")
        self.toolbar.addAction(actionAddLayer)
        self.toolbar.addAction(actionZoomIn)
        self.toolbar.addAction(actionZoomOut)
        self.toolbar.addAction(actionPan)

        # create the map tools
        self.toolPan = QgsMapToolPan(self.canvas,)
        self.toolPan.setAction(actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false == in
        self.toolZoomIn.setAction(actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true == out
        self.toolZoomOut.setAction(actionZoomOut)

        # overall layout
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

        # set signals
        self.connect(actionAddLayer, SIGNAL("activated()"), self.addLayer)
        self.connect(actionZoomIn, SIGNAL("activated()"), self.zoomIn)
        self.connect(actionZoomOut, SIGNAL("activated()"), self.zoomOut)
        self.connect(actionPan, SIGNAL("activated()"), self.pan)

    def addLayer(self):
        """TO DO: Add doc string"""
        QtGui.QMessageBox.information(
            self,
            "INFORMATION:","Functionality not yet implemented",
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
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new, changed filename
        """
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
        myrender.setProjectionsEnabled(True) #print self.canvas.hasCrsTransformEnabled()
        myrender.setDestinationSrs(crsDest)

        mapCanvasLayers = []
        for layer in inputLayers:
            if layer.isValid():
                # Add layer to the registry (one registry for ALL maps ???)
                QgsMapLayerRegistry.instance().addMapLayer(layer, True)
                # Set up the map canvas layer
                cl = QgsMapCanvasLayer(layer)
                mapCanvasLayers.append(cl)
                # Set extent to the extent of our layer
                self.canvas.setExtent(layer.extent())
                self.canvas.enableAntiAliasing(True)
                self.canvas.freeze(False)
                self.canvas.setLayerSet(mapCanvasLayers)
                self.canvas.refresh()
                self.update()

from core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import sys
import os
import core.system
import os.path
import core.modules.module_registry
import packages.eo4vistrails.geoinf.visual


path_png_icon = packages.eo4vistrails.geoinf.visual.__path__[0]
QgsApplication.setPrefixPath("/usr", True)
QgsApplication.initQgis()


class QGISMapCanvasCell(SpreadsheetCell):
    """TO DO: Add doc string
    """
    def compute(self):
        """ compute() -> None
        """
        if self.hasInputFromPort("layer"):
            layers = self.getInputListFromPort("layer")
        else:
            layers = None
        self.cellWidget = self.displayAndWait(QGISMapCanvasCellWidget, (layers,))


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

        actionAddLayer = QAction(QIcon(path_png_icon + "/mActionAddLayer.png"), "Add Layer", self.tools)
        actionZoomIn = QAction(QIcon(path_png_icon + "/mActionZoomIn.png"), "Zoom In", self.tools)
        actionZoomOut = QAction(QIcon(path_png_icon + "/mActionZoomOut.png"), "Zoom Out", self.tools)
        actionPan = QAction(QIcon(path_png_icon + "/mActionPan.png"), "Pan", self.tools)

        self.toolbar = self.tools.addToolBar("Canvas actions")
        self.toolbar.addAction(actionAddLayer)
        self.toolbar.addAction(actionZoomIn)
        self.toolbar.addAction(actionZoomOut)
        self.toolbar.addAction(actionPan)

        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

        self.connect(actionAddLayer, SIGNAL("activated()"), self.addLayer)
        self.connect(actionZoomIn, SIGNAL("activated()"), self.zoomIn)
        self.connect(actionZoomOut, SIGNAL("activated()"), self.zoomOut)
        self.connect(actionPan, SIGNAL("activated()"), self.pan)

        # create the map tools
        self.toolPan = QgsMapToolPan(self.canvas,)
        self.toolPan.setAction(actionPan)

        self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false = in
        self.toolZoomIn.setAction(actionZoomIn)

        self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
        self.toolZoomOut.setAction(actionZoomOut)

    def addLayer(self):
        """TO DO: Add doc string"""
        QtGui.QMessageBox.information(self,"INFOMATION:","Functionality still Under Implementation",QtGui.QMessageBox.Ok)

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
        (inputLayers, ) = inputPorts
        if type(inputLayers) != list:
            #print "One Layer"
            inputLayers = [inputLayers]
        else:
            pass
            #TODO handle the list case.

        mapCanvasLayers = []
        for layer in inputLayers:
            print "Accessing layer" + '*********' + layer.name()
            if not layer.isValid():
                return
            print "Success!"

            file_extension = str(layer.name())
            if file_extension.endswith(".shp"):
                #get the label instance associated with the layer a
                label = layer.label()
                labelAttributes = label.layerAttributes()
                #using first field (specified by index 0) as the label field
                label.setLabelField(QgsLabel.Text,  0)
                # set the colour of the label text
                labelAttributes.setColor(QtCore.Qt.black)
                layer.enableLabels(True)

            # Add layer to the registry
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)

            # Set up the map canvas layer set
            cl = QgsMapCanvasLayer(layer, True)
            mapCanvasLayers.append(cl)

            # Set extent to the extent of our layer
            self.canvas.setExtent(layer.extent())
            self.canvas.enableAntiAliasing(True)
            self.canvas.freeze(False)

            self.canvas.setLayerSet(mapCanvasLayers)
            self.canvas.refresh()
            self.update()

        #QCellWidget.updateContents(self, inputPorts)

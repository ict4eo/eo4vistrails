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


#qgis_prefix = os.getenv("QGISHOME") 

# Initialize qgis libraries 
#QgsApplication.setPrefixPath(qgis_prefix, True) 
QgsApplication.setPrefixPath("/usr", True) 
QgsApplication.initQgis() 


class QGISMapCanvasCell(SpreadsheetCell):
    '''
    '''
        
    def compute(self):
        """ compute() -> None
        Dispatch the HTML contents to the spreadsheet
        """
                
        if self.hasInputFromPort("File"):
            fileValue = self.getInputFromPort("File")
        else:
            fileValue = None

              
        self.cellWidget = self.displayAndWait(QGISMapCanvasCellWidget, (fileValue,))


class QGISMapCanvasCellWidget(QCellWidget, QMainWindow):
    
    def __init__(self, parent=None):
            
        QCellWidget.__init__(self, parent)
        
        QMainWindow.__init__(self)
                       
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(200,200,255))        
        self.canvas.show() 
        
        self.tools = QMainWindow()          
        path_png_icon = "/packages/eovistrails/geoinf/visual/"             
        actionZoomIn = QAction(QIcon( path_png_icon + "mActionZoomIn.png"), "Zoom In", self)        
        actionZoomOut = QAction(QIcon( path_png_icon + "mActionZoomOut.png"), "Zoom Out", self)  
        actionPan = QAction(QIcon( path_png_icon + "mActionPan.png"), "Pan ", self) 
          
            
        self.toolbar = self.tools.addToolBar("Canvas actions")       
        self.toolbar.addAction(actionZoomIn)
        self.toolbar.addAction(actionZoomOut)
        self.toolbar.addAction(actionPan)
                
        self.setLayout(QtGui.QVBoxLayout(self))        
        self.layout().addWidget(self.toolbar)        
        self.layout().addWidget(self.canvas) 
                        
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
    
                
        #File = QFileDialog.getOpenFileName(self, "Open file", ".", "files(*.*)") 
        
        #fileInfo = QFileInfo(File) 
         
        # Add the layer       
        #layer = QgsVectorLayer(File, fileInfo.fileName(), "ogr")
        #layer =  self.getInputFromPort('layer')
              
        print "Accessing layer"
        if not layer.isValid(): 
            return 
        print "Succeeded "
        
        # Add layer to the registry                
        QgsMapLayerRegistry.instance().addMapLayer(layer); 
        
        # Set extent to the extent of our layer 
        self.canvas.setExtent(layer.extent()) 
        
        # Set up the map canvas layer set 
        cl = QgsMapCanvasLayer(layer) 
        layers = [cl] 
        self.canvas.setLayerSet(layers) 
        #self.canvas.setVisible(True)
        
        
    def zoomIn(self):
        self.canvas.setMapTool(self.toolZoomIn)
        
    def zoomOut(self):
        self.canvas.setMapTool(self.toolZoomOut)
        
        
    def pan(self):
        self.canvas.setMapTool(self.toolPan)
    
        
    
    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new changed in filename
        
        """
        (fileValue, ) = inputPorts
        '''
        if fileValue:
            img = QtGui.QImage()
            if img.load(fileValue.name):
                self.originalPix = QtGui.QPixmap.fromImage(img)
                self.tools.setPixmap(self.originalPix.scaled(self.tools.size(),
                                                         QtCore.Qt.KeepAspectRatio,
                                                         QtCore.Qt.SmoothTransformation))
            else:
                self.tools.setText("Invalid image file!")
        '''

        QCellWidget.updateContents(self, inputPorts)
        
        

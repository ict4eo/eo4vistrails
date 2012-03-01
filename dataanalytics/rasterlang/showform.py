#
# Rasterlang (c) Barry Rowlingson 2008
#
#    This file is part of "rasterlang"
#
#    Rasterlang is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Rasterlang is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Rasterlang.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtGui, QtCore

from qgis.core import *
from qgis.gui import *

from interface import Ui_Dialog
import rasters
import lispy
import layers
import treewalk
import nums
import os.path


class RasterDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.parser = lispy.buildParser()
        self.dir = os.path.realpath(os.path.curdir)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("helpRequested()"), self.help)
        QtCore.QObject.connect(self.expressionInput, QtCore.SIGNAL("textEdited(QString)"),self.changed)

    def show(self):
        self.mapLayers = filter(lambda l: l.type()==l.RasterLayer,QgsMapLayerRegistry.instance().mapLayers().values())
        self.layerNames = [str(z.name()) for z in self.mapLayers]
        self.layerLabels = layers.uniqueLabels(self.layerNames)

        self.layerInfo = dict(zip(self.layerLabels,self.mapLayers))

        rasters.setRasters(dict([(k,None) for k in self.layerLabels]))
        
        self.groups = layers.GroupedLayers()
        for layer,label in zip(self.mapLayers,self.layerLabels):
            self.groups.addLayer(layer,label)
        self.setTree(self.groups)

        self.statusLine.setText("status")
        self.buttonBox.buttons()[0].setDisabled(True)
        self.changed(self.expressionInput.text())
        QtGui.QDialog.show(self)

    def accept(self):
        # TODO: plenty of bad things could happen here.
        usedRasters = lispy.rasterList
        setRasters=dict()
        for r in usedRasters:
            setRasters[r] = layers.layerAsArray(self.layerInfo[r])
        rasters.setRasters(setRasters)

        sexpr = self.parser.parseString(str(self.expressionInput.text()))
        e=treewalk.evaluate(sexpr.asList()[0])

        if not nums.isItArray(e):
            QtGui.QMessageBox.information(self,"Error","result not an array, is a <%s ... %s> len=%s with dir=%s" % (str(e)[:10],str(e)[-10:],len(e),str(dir(e))))
            return

        #  use the extent of the first layer referenced:
        extent = layers.Extent(self.layerInfo[list(usedRasters)[0]])

        # now make sure result is numpy/Numeric
        (testFlag,res) = nums.checkSameAs(e,setRasters[list(usedRasters)[0]])
        if not testFlag:
            e = res

        f=QtGui.QFileDialog.getSaveFileName(self,"Save GeoTIFF file",self.dir,"(Tiff (*.tif *.tiff)")
        if len(f) > 0:
            f=os.path.normpath(str(f))
            layers.writeGeoTiff(e,[extent.xMinimum(),extent.yMinimum(),extent.xMaximum(),extent.yMaximum()],f)
            newLayer = QgsRasterLayer(f,os.path.basename(f))
            QgsMapLayerRegistry.instance().addMapLayer(newLayer)
            self.dir = os.path.split(f)[0]
            QtGui.QDialog.accept(self)

    def changed(self,text):
        lispy.rasterList = set([])
        try:
            self.parser.parseString(str(text))
        except:
            self.statusLine.setText("Syntax error.")
            return

        if len(lispy.rasterList) < 1:
            self.statusLine.setText("Expression must contain at least one layer.")
            return
        
        groups = [self.groups.findGroup(self.layerInfo[l]) for l in lispy.rasterList]
        if len(set(groups)) != 1:
            self.statusLine.setText("Only layers from one group.")
            return

        self.buttonBox.buttons()[0].setDisabled(False)
        self.statusLine.setText("ok")

    def reject(self):
        QtGui.QDialog.reject(self)

    def help(self):
        import showText
        import ops
        all = ops.ops()
        opHelp = "\n\n*Operators*\n\nHere is a list of valid operators:\n"+"\n".join([x.helpString() for x in all.values()])
        mainHelp = """
Rasterlang - raster manipulation language

This plugin allows manipulation of raster layers. It will only work on rasters that are based on the same grid size and location.

*Interface*

The interface shows layers grouped by their size and location in a grouped tree structure. Below this is a text entry line for your rasterlang expression. Because raster layer names do not need to be unique in Qgis, the interface assigns a 'label' to each layer. This label is used in expressions to specify the raster layer. By default the label is the same as the name, but if the name is not unique or is not a valid string for a label, then a new label is generated. In Qgis there is nothing stopping you renaming a layer '2', which would be confused with the number '2'.

Below the text entry line is a status indicator. If there are errors in your expression entry then a status message appears here. Possible errors include: the expression is not syntactically correct; it specifies no raster layers; it specifies raster layes from different groups.

Once a correct expression is entered the OK button is enabled. Clicking it runs the calculation and a 'Save' dialog is persented. This will save a GeoTIFF and load as a new layer in Qgis. You may then wish to set the Symbology from the Properties dialog in Qgis.

*Expressions*

Expressions are written in a lisp-like language. For example, to add 10 to all bands of a raster:

(+ layer1 10)

The basic syntax is (op arg arg ...), where each argument can also be an (op arg arg ...) expression. Hence you can build up more complex expressions such as:

(+ (band layer1 0) (* (band layer1 1) 1.3) (* (band layer1 2) 3.2))

which produces a single band from a linear combination of three bands from raster 'layer1'.

"""
        window = QtGui.QDialog()
        ui = showText.Ui_Dialog()
        ui.setupUi(window)
        ui.text.setText(mainHelp+opHelp)
        window.show()
        window.exec_()


    def setTree(self,groups):
        self.rasterTree.clear()
        for group in groups.groups:
            gw = QtGui.QTreeWidgetItem(self.rasterTree)
            gw.setText(0,group.info)
            gw.setFirstColumnSpanned(True)
            gw.setExpanded(True)
            for layer,label in zip(group.layers,group.labels):
                ww = QtGui.QTreeWidgetItem(gw)
                ww.setText(0,str(layer.name()))
                ww.setText(1,label)
                ww.setText(2,str(layer.bandCount()))
    
def setSampleData(tree):
    labels = []
    for i in range(3):
        w = QtGui.QTreeWidgetItem(tree)
        w.setText(0,"Group %s, %sx%s (0,0)-(1,1)"%(i,100*(i+1),50*(i+1)))
        w.setFirstColumnSpanned(True)
        w.setExpanded(True)
        for j in range(3):
            ww=QtGui.QTreeWidgetItem(w)
            ww.setText(0,"Layer%s%s"%(i,j))
            label = "label-%s-%s" % (i,j)
            labels.append(label)
            ww.setText(1,label)
            ww.setText(2,"3")

    rasters.setRasters(dict([(k,None) for k in labels]))
    
def main():
    import sys
    app=QtGui.QApplication(sys.argv)
    rd = RasterDialog()
    setSampleData(rd.rasterTree)
    rd.show()
    app.exec_()

    
if __name__=="__main__":
    main()

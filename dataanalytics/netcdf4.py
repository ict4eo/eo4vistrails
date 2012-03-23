# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 15:12:36 2012

@author: mmtsetfwa
"""

# -*- coding: utf-8 -*-
###########################################################################
##
## Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the ability to run code transparently in
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
'''
add brief description of what this pyDAP client does.
'''
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from PyQt4 import Qt
from core.modules.vistrails_module import Module, ModuleError
from core.modules.module_configure import StandardModuleConfigurationWidget
from netcdf4FormDesign import Ui_netcdf4Form
import netCDF4
import init
import numpy


class netcdf4Reader(Module):
    """Read netcdf4/hdf5 file from OpenDAP server."""
    _input_ports = [('nc4File', '(edu.utah.sci.vistrails.basic:File)'),
                    ('varName', '(edu.utah.sci.vistrails.basic:String)'),
                    ('dimLimits', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('data', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')]
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        try:      
            nc4File = self.getInputFromPort("nc4File")
            varName= self.getInputFromPort("varName")
            dimLimits=self.getInputFromPort("dimLimits")
            self.inputFile=netCDF4.Dataset(str(nc4File.name),'r')                       
            part_1=self.inputFile.variables[str(varName)]
            result = eval("part_1%s"%dimLimits)
            self.setResult("data",result)
            #self.inputFile.close()
        except KeyError:
            print 'Variable not correctly set from input file'
        except IOError,e:
            print 'Failed to open input file',e



class netcdf4ConfigurationWidget(StandardModuleConfigurationWidget):
    """A widget to configure the  netcdf4 Client."""

    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
               
        self.title = module.name        
        self.setObjectName("netcdf4Widget")     
        self.parent_widget = module
        self.ui=Ui_netcdf4Form()        
        self.ui.setupUi(self)
        port_widget = {
            init.nc4File: self.ui.UrlLineEdit
        }        
        for function in self.module.functions:
            if function.name in port_widget:                
                port_widget[function.name].setText(function.params[0].strValue) 

        self.connect(self.ui.fetchVarsButton,QtCore.SIGNAL("clicked()"),self.createRequest)
        self.connect(self.ui.okButton,QtCore.SIGNAL("clicked()"),self.readData)
        self.connect(self.ui.cancelButton,QtCore.SIGNAL("clicked()"),SLOT("close()"))
       
    def createRequest(self):        
        self.myFile=netCDF4.Dataset(str(self.ui.UrlLineEdit.text()),'r')
        self.keys=self.myFile.variables.keys()            
        dimensions=[]
        metadata={}
        listOfTuples=[]        
        i=0
        for varIds in self.keys:
            for dims in self.myFile.variables[str(varIds)].dimensions:
                dimTuple=(dims,[])              
                dimensions.append(dimTuple)                
            myTuple=(varIds,dimensions)
            listOfTuples.append(myTuple)            
            dimensions=[]
            i=i+1       
        self.model = QStandardItemModel()
        self.addItems(self.model, listOfTuples) 
        self.ui.treeView.setModel(self.model)              
        self.model.setHorizontalHeaderLabels([self.tr("File Variables, Dims")])       
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.ui.treeView)       
        
    def addItems(self, parent, elements):        
        count=3
        addColumnTest=False
        for text, children in elements:
            bounds="[0:"          
            item = QtGui.QStandardItem(text)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            limit=[]                    
            parent.appendRow(item)
            if not children:
                shape=self.myFile.variables[str(text)].shape[0]-1
                if shape == 0:
                    bounds="["
                bounds=bounds+str(shape)+"]"
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)                
                addColumnTest=False
            limit.append(QtGui.QStandardItem(bounds))
       
            if children:
                self.addItems(item, children)                
                item.setData(0, QtCore.Qt.CheckStateRole)          
            if bounds != "[0:":
                parent.appendRow(limit)       
        
      
    def readData(self):
        strVarsDims=""
        bounds=""
        allBounds=""
        countCheckedVars=0
       
        rows = self.model.rowCount()               
        for i in range(0,self.model.rowCount()):          
            node=self.model.item(i)            
            if node.checkState()==2:
                
                    retrieveVars=str(node.text())
                    for j in range(0,node.rowCount()/2):
                        bounds=node.child((((j+1)*2)-1))                            
                        allBounds=allBounds+bounds.text()
                    if countCheckedVars == 0:
                        strVarsDims=strVarsDims+retrieveVars+allBounds
                    else:
                        strVarsDims=strVarsDims+","+retrieveVars+allBounds                 
                    countCheckedVars=countCheckedVars+1
                      
        dataStore=[]       
        dataStore.append((init.varName, [str(retrieveVars)]),)
        dataStore.append((init.dimLimits, [str(allBounds)]),)
        self.controller.update_ports_and_functions(
                        self.module.id, [], [],dataStore) 
      
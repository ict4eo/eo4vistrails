# -*- coding: utf-8 -*-
###########################################################################
##
## Copyright (C) 2011 CSIR Meraka Institute. All rights reserved.
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
"""This package is used to access netcdf files from an OpenDAP server.
"""
# library
import os
# third party
import numpy
from PyQt4 import QtCore, QtGui, Qt
# vistrails
from core.modules.vistrails_module import Module, ModuleError
from core.modules.module_configure import StandardModuleConfigurationWidget
# dependent packages
from packages.NumSciPy.Array import NDArray
# eo4vistrails
# local
from pydap.client import open_url, open_dods
from pyDAPForm import Ui_pyDAPForm
import init


DEFAULT_URL = "http://ict4eo.meraka.csir.co.za/eo2h_pydap/netcdfs/trmm_global_cube.nc"
#DEFAULT_URL ="http://ict4eo1.dhcp.meraka.csir.co.za/pydap/ccam_atlas_csiro.210012.nc"
variableNames = []


class pyDAP(Module):
    """TODO: Add docstring"""

    _input_ports = [('url', '(edu.utah.sci.vistrails.basic:String)'),
                    ('dataSlice', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('data', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('latitude', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('longitude', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('alt', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('time', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ]

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        url = self.getInputFromPort("url")
        dataSlice = self.getInputFromPort("dataSlice")
        myDataSet = open_dods(str(url) + '.dods?' + str(dataSlice))
        result = myDataSet.data
        #TODO: should return list of arrays but this will require a new type
        # to be added to eo4vistrails; for instance NDArrayList
        my_first_data_item_key = myDataSet.keys()[0]
        dict_of_arrays = myDataSet.get(my_first_data_item_key)
        for output_port, known_field_name in (('time','time'),
                                              ('latitude','latitude'),
                                              ('longitude','longitude'),
                                              ('data',my_first_data_item_key)):
            outArray = NDArray()
            outArray.set_array(dict_of_arrays.get(known_field_name).data)
            self.setResult(output_port, outArray)
        #self.setResult("data", result)


class pyDAPConfigurationWidget(StandardModuleConfigurationWidget):
    """A widget to configure the pyDAP Client."""

    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        self.title = module.name
        self.setObjectName("pyDAPWidget")
        self.parent_widget = module
        self.ui = Ui_pyDAPForm()
        self.ui.setupUi(self)
        self.ui.UrlLineEdit.setText(DEFAULT_URL)
        self.connect(self.ui.fetchVarsButton,
                     QtCore.SIGNAL("clicked()"),
                     self.createRequest)
        self.connect(self.ui.okButton,
                     QtCore.SIGNAL("clicked()"),
                     self.readData)
        self.connect(self.ui.cancelButton,
                     QtCore.SIGNAL("clicked()"),
                     SLOT("close()"))

    #Populate netcdf file variables and dimensions into list to use to create tree for browsing file structure
    def createRequest(self):
        self.data = open_url(str(self.ui.UrlLineEdit.text()))
        self.dataKeys = self.data.keys()
        del variableNames[:]
        dimensions = []
        metadata = {}
        listOfTuples = []
        i = 0
        for fileKey in self.dataKeys:
            for dims in self.data[self.dataKeys[i]].dimensions:
                dimTuple = (dims, [])
                dimensions.append(dimTuple)
            myTuple = (fileKey, dimensions)
            listOfTuples.append(myTuple)
            dimensions = []
            i = i + 1
        self.ui.textMetadata.setText(str(self.data.attributes))
        self.model = QStandardItemModel()
        self.addItems(self.model, listOfTuples)
        self.ui.treeView.setModel(self.model)
        self.model.setHorizontalHeaderLabels([self.tr("File Variables, Dims")])
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.ui.treeView)

    #create tree from netcdf file variables , dimensions and limits
    def addItems(self, parent, elements):
        count = 3
        addColumnTest = False
        for text, children in elements:
            bounds = "[0:1:"
            item = QtGui.QStandardItem(text)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            limit = []
            parent.appendRow(item)
            if not children:
                shape = self.data[str(text)].shape[0] - 1
                bounds = bounds + str(shape) + "]"
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                addColumnTest = False
            limit.append(QtGui.QStandardItem(bounds))
            if children:
                self.addItems(item, children)
                item.setData(0, QtCore.Qt.CheckStateRole)
            if bounds != "[0:1:":
                parent.appendRow(limit)

    #Construct request to get a slice of the data from remote netcdf file
    def readData(self):
        strVarsDims = ""
        bounds = ""
        allBounds = ""
        countCheckedVars = 0
        rows = self.model.rowCount()
        for i in range(0, self.model.rowCount()):
            node = self.model.item(i)
            if node.checkState() == 2:
                retrieveVars = str(node.text())
                for j in range(0, node.rowCount() / 2):
                    bounds = node.child((((j + 1) * 2) - 1))
                    allBounds = allBounds + bounds.text()
                if countCheckedVars == 0:
                    strVarsDims = strVarsDims + retrieveVars + allBounds
                else:
                    strVarsDims = strVarsDims + "," + retrieveVars + allBounds
                bounds = ""
                allBounds = ""
                countCheckedVars += 1

        dataStore = []
        dataStore.append((init.dataSlice, [str(strVarsDims)]),)
        dataStore.append((init.url, [str(self.ui.UrlLineEdit.text())]),)
        self.controller.update_ports_and_functions(
                        self.module.id, [], [], dataStore)

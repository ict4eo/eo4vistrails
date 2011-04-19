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
"""This module forms part of the rpyc eo4vistrails capabilties;
used to add multicore parallel and distributed processing to vistrails.

This module holds a rpycnode type that can be passed around between modules.
"""

import networkx as nx
from core.modules.vistrails_module import Module

from packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.utils.Array import NDArray
from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsMapLayer

import rasterlang.layers #layerAsArray, writeGeoTiff

class RasterlangModule(ThreadSafeMixin):
    def __init__(self):
        ThreadSafeMixin.__init__(self)

@RPyCSafeModule()
class layerAsArray(RasterlangModule, RPyCModule):
    """ Container class for the connected components command """

    _input_ports  = [('QgsMapLayer', '(za.co.csir.eo4vistrails:QgsMapLayer:data)')]
    _output_ports = [('numpy array', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')]

    def __init__(self):
        RPyCModule.__init__(self)
        RasterlangModule.__init__(self)

    def compute(self):
        layer = self.getInputFromPort('QgsMapLayer')
        
        array = rasterlang.layers.layerAsArray(layer)
        
        ndarray = NDArray()
        ndarray.set_array(array)
        
        self.setResult("numpy array", ndarray)

@RPyCSafeModule()
class arrayAsLayer(RasterlangModule, RPyCModule):
    """ Container class for the connected components command """

    _input_ports  = [('numpy array', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('QgsMapLayer', '(za.co.csir.eo4vistrails:QgsMapLayer:data)')]
    _output_ports = [('raster layer', '(za.co.csir.eo4vistrails:Raster Layer:data)')]

    def __init__(self):
        RPyCModule.__init__(self)
        RasterlangModule.__init__(self)

    def clear(self):
        RPyCModule.clear(self)
        import os
        os.remove(self.fileName)

    def compute(self):        
        ndarray = self.getInputFromPort('numpy array')
        layer = self.getInputFromPort('QgsMapLayer')
                        
        e = layer.extent()
        extent = [e.xMinimum(),e.yMinimum(),e.xMaximum(),e.yMaximum()]

        import random
        random.seed()
        #TODO: make platform independant
        self.number  = str(random.randint(0, 100000))
        self.fileName = "/tmp/rasterlang" + self.number + ".tiff"


        rasterlang.layers.writeGeoTiff(ndarray.get_array(), extent, self.fileName)
        from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsRasterLayer
        
        outlayer = QgsRasterLayer(self.fileName, self.number)
        
        self.setResult("raster layer", outlayer)

@RPyCSafeModule()
class writeGeoTiff(RasterlangModule, RPyCModule):
    """ Container class for the connected components command """

    _input_ports  = [('numpy array', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('QgsMapLayer', '(za.co.csir.eo4vistrails:QgsMapLayer:data)'),
                     ('output file', '(edu.utah.sci.vistrails.basic:File)')]

    def __init__(self):
        RPyCModule.__init__(self)
        RasterlangModule.__init__(self)

    def compute(self):
        outfile = self.getInputFromPort('output file')
        ndarray = self.getInputFromPort('numpy array')
        layer = self.getInputFromPort('QgsMapLayer')
        
        e = layer.extent()
        extent = [e.xMinimum(),e.yMinimum(),e.xMaximum(),e.yMaximum()]
        
        rasterlang.layers.writeGeoTiff(ndarray.get_array(), extent, outfile.name)

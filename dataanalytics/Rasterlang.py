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
"""This module holds a rpycnode type that can be passed around between modules.
"""
#History
#Created by Terence van Zyl

from packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
from packages.eo4vistrails.rpyc.RPyCHelper import RPyCCode
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsRasterLayer
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget
from packages.NumSciPy.Array import NDArray

import gdalnumeric
import gdal

class RasterlangModule(ThreadSafeMixin):
    def __init__(self):
        ThreadSafeMixin.__init__(self)

class RasterLang(RPyCCode):
    """
    This module that executes an arbitrary piece of Python code remotely.
    """
    #TODO: If you want a PythonSource execution to fail, call fail(error_message).
    #TODO: If you want a PythonSource execution to be cached, call cache_this().

    '''
    This constructor is strictly unnecessary. However, some modules
    might want to initialize per-object data. When implementing your
    own constructor, remember that it must not take any extra parameters.
    '''
    
    _input_ports  = [('Prototype', '(za.co.csir.eo4vistrails:Raster Layer:data)')]
    
    def __init__(self):
        RPyCCode.__init__(self)
        self.preCodeString = "from numpy import *\nfrom scipy import *\n"
        self.postCodeString = None
        self.raster_prototype = None
    
    def setInputResults(self, locals_, inputDict):
        
        inputDict = dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])
        del inputDict['source']
        if inputDict.has_key('rpycnode'):
            del inputDict['rpycnode']

        #check that if any are NDArrays we get the numpy array out        
        self.extent = None
        for k in inputDict.iterkeys():
            if type(inputDict[k]) == NDArray or str(type(inputDict[k])) == "<netref class 'packages.NumSciPy.Array.NDArray'>":
                inputDict[k] = inputDict[k].get_array()
            elif type(inputDict[k]) == QgsRasterLayer or str(type(inputDict[k])) == "<netref class 'packages.eo4vistrails.geoinf.datamodels.QgsLayer.QgsRasterLayer'>":
                if self.extent == None:
                    e = inputDict[k].extent()
                    self.extent = [e.xMinimum(),e.yMinimum(),e.xMaximum(),e.yMaximum()]
                    self.raster_prototype = inputDict[k]
                inputDict[k] = gdalnumeric.LoadFile(str(inputDict[k].source()))
        locals_.update(inputDict)
    
    def setOutputResults(self, locals_, outputDict):
        from tempfile import mkstemp
        import numpy
        
        self.raster_prototype = self.forceGetInputFromPort('Prototype', self.raster_prototype)
        
        for k in outputDict.iterkeys():
            if locals_.has_key(k) and locals_[k] != None:                
                if self.getPortType(k) == NDArray:
                    print "got %s"%k
                    outArray = NDArray()
                    outArray.set_array(numpy.array(locals_[k]))
                    self.setResult(k, outArray)
                elif self.getPortType(k) == QgsRasterLayer or str(type(outputDict[k])) == "<netref class 'packages.eo4vistrails.geoinf.datamodels.QgsLayer.QgsRasterLayer'>":
                    #TODO: This should all be done using a gal inmemorybuffer nut
                    #I dont have time now
                    fileDescript, fileName = mkstemp(suffix='.img', text=False)
                    if self.raster_prototype:
                        #use the prototype provided
                        gdalnumeric.SaveArray(locals_[k], fileName, format="HFA", prototype=str(self.raster_prototype.source()))
                    else:
                        #No Prototype
                        gdalnumeric.SaveArray(locals_[k], fileName, format="HFA")
                        
                    outlayer = QgsRasterLayer(fileName, k)
                    self.setResult(k, outlayer)
                else:
                    self.setResult(k, locals_[k])
        
        
class RasterSourceConfigurationWidget(SyntaxSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        displayedComboItems = {'String':True,
                               'Float':True,
                               'Integer':True,
                               'Boolean':True,
                               'Numpy Array': True,
                               'Raster Layer':True}
    
        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "Python", 
                                                 parent=parent,
                                                 displayedComboItems = displayedComboItems)

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
        
        array = gdalnumeric.LoadFile(layer)

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

        from tempfile import mkstemp
        #TODO: make platform independant
        fileDescript, fileName = mkstemp(suffix='img', text=True)

        writeImage(ndarray.get_array(), extent, fileName, format='HFA' )
        
        outlayer = QgsRasterLayer(self.fileName, self.filename)

        self.setResult("raster layer", outlayer)

@RPyCSafeModule()
class SaveArrayToRaster(RasterlangModule, RPyCModule):
    """ Container class for the connected components command """

    _input_ports  = [('numpy array', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('prototype', '(za.co.csir.eo4vistrails:Raster Layer:data)'),
                     ('output file', '(edu.utah.sci.vistrails.basic:File)'),
                     ('format', '(za.co.csir.eo4vistrails:GDAL Format:rasterlang)')]

    _output_ports  = [ ('output file path', '(edu.utah.sci.vistrails.basic:File)')]


    def __init__(self):
        RPyCModule.__init__(self)
        RasterlangModule.__init__(self)

    def compute(self):
        outfile = self.getInputFromPort('output file')
        ndarray = self.getInputFromPort('numpy array')
        prototype = self.getInputFromPort('prototype')
        outformat = self.getInputFromPort('format')
        
        print "protoype nodata", prototype.noDataValue()

        gdalnumeric.SaveArray(ndarray.get_array(), outfile.name, format=outformat, prototype=str(prototype.source()))
        
        self.setResult('output file path', outfile)
        #e = layer.extent()
        #extent = [e.xMinimum(),e.yMinimum(),e.xMaximum(),e.yMaximum()]
#        writeImage(ndarray.get_array(), extent, outfile.name, format='HFA' )

from core.modules import basic_modules
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget

class GDALFormatComboBoxWidget(ComboBoxWidget):
    """TODO Write docstring."""
    _KEY_VALUES = {'HFA': 'HFA', 'GEOTiff':'GEOTiff'}
    
# LinuxComboBox
GDALFormatComboBox = basic_modules.new_constant('GDAL Format',
                                                staticmethod(str),
                                                'HFA',
                                                staticmethod(lambda x: type(x) == str),
                                                GDALFormatComboBoxWidget)

def writeImage(arrayData, extent, path, format, epsg=None):
    """
    write the given array data to the file 'path' with the given extent.
    
    if arrayData shape is of length 3, then we have multibands (nbad,rows,cols), otherwise one band
    """
    
    driver = gdal.GetDriverByName( format )
    metadata = driver.GetMetadata()
    if metadata.has_key(gdal.DCAP_CREATE) \
           and metadata[gdal.DCAP_CREATE] == 'YES':
        pass
    else:
        print 'Driver %s does not support Create() method.' % format
        return False

    # get rows and columns
    dims=arrayData.shape
    if len(dims) == 2:
        rows = dims[0]
        cols = dims[1]
        nbands = 1
    else:
        rows = dims[1]
        cols = dims[2]
        nbands = dims[0]

    # could possible use CreateCopy from one of the input rasters...
    dst_ds = driver.Create(path, cols, rows, nbands, gdal.GDT_Float32 )

    dst_ds.SetGeoTransform( [
        extent[0], (extent[2]-extent[0])/cols, 0,
        extent[3], 0, (extent[1]-extent[3])/rows ] )

    if epsg:
        import osr
        srs = osr.SpatialReference()
        srs.SetProjCS( "EPSG:%s"%epsg )
        dst_ds.SetProjection( srs.ExportToWkt() )
    
    if nbands > 1:
        for i in range(nbands):
            dst_ds.GetRasterBand(i+1).WriteArray(arrayData[i])
    else:
        dst_ds.GetRasterBand(1).WriteArray(arrayData)
        
    return True

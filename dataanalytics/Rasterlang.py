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

from core.modules.vistrails_module import NotCacheable, Module

import gdalnumeric
import gdal
from gdal import gdalconst
import ctypes

class RasterlangModule(ThreadSafeMixin):
    def __init__(self):
        ThreadSafeMixin.__init__(self)

@RPyCSafeModule()
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
    
    _input_ports  = [('prototype', '(za.co.csir.eo4vistrails:Raster Prototype:rasterlang)')]
    
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
            if isinstance(inputDict[k], NDArray):
                inputDict[k] = inputDict[k].get_array()
            elif isinstance(inputDict[k], QgsRasterLayer):
                if self.extent == None:
                    e = inputDict[k].extent()
                    self.extent = [e.xMinimum(),e.yMinimum(),e.xMaximum(),e.yMaximum()]
                    self.raster_prototype = inputDict[k]
                inputDict[k] = gdalnumeric.LoadFile(str(inputDict[k].source()))
        locals_.update(inputDict)
    
    def setOutputResults(self, locals_, outputDict):
        from tempfile import mkstemp
        import numpy
        
        self.raster_prototype = self.forceGetInputFromPort('prototype', self.raster_prototype)
        
        for k in outputDict.iterkeys():
            if locals_.has_key(k) and not locals_[k] is None:
                print "%s == %s  -> %s"%(self.getPortType(k), NDArray, issubclass(NDArray, self.getPortType(k)))
                if issubclass(self.getPortType(k), NDArray):
                    print "got %s of type %s"%(k, type(locals_[k]))
                    outArray = NDArray()
                    outArray.set_array(numpy.asarray(locals_[k]))
                    self.setResult(k, outArray)
                elif issubclass(self.getPortType(k), QgsRasterLayer):
                    #TODO: This should all be done using a gal inmemorybuffer but
                    #I dont have time now
                    fileDescript, fileName = mkstemp(suffix='.img', text=False)
                    if self.raster_prototype:
                        #use the prototype provided
                        writeImage(locals_[k], self.raster_prototype, fileName, "HFA")
                    else:
                        #No Prototype
                        gdalnumeric.SaveArray(locals_[k], fileName, format="HFA")
                        
                    outlayer = QgsRasterLayer(fileName, k)
                    self.setResult(k, outlayer)
                else:
                    self.setResult(k, locals_[k])
    
    def compute(self):
        RPyCCode.compute(self)
        
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

    _input_ports  = [('Raster Layer', '(za.co.csir.eo4vistrails:Raster Layer:data)')]
    _output_ports = [('numpy array', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')]

    def __init__(self):
        RPyCModule.__init__(self)
        RasterlangModule.__init__(self)

    def preCompute(self):
        print "In preCompute"
        layer = self.getInputFromPort('Raster Layer')
        print "layer: %s"%layer
        g = gdal.Open(str(layer.source()))
        print "g: %s"%g
        #TODO: Need to check the ctype that the image is
        print "trying to allocate shared memory"
        self.allocateSharedMemoryArray('numpy array', ctypes.c_float, (g.RasterYSize,g.RasterXSize))
    
    def compute(self):
        layer = self.getInputFromPort('Raster Layer')
        
        g = gdal.Open(str(layer.source()))
        g.ReadAsArray(buf_obj=self.sharedMemOutputPorts['numpy array'][0])

        self.setResult("numpy array", None, asNDArray=True)

class RasterPrototype(RasterlangModule, Module):
    """ Container class for the connected components command """

    _input_ports  = [('(XMin,YMax,XMax,YMin) Extent', '(edu.utah.sci.vistrails.basic:Float,edu.utah.sci.vistrails.basic:Float,edu.utah.sci.vistrails.basic:Float,edu.utah.sci.vistrails.basic:Float)'),
                     ('(Rows, Cols) Pixel Count', '(edu.utah.sci.vistrails.basic:Integer,edu.utah.sci.vistrails.basic:Integer)'),
                     ('No Data Value', '(edu.utah.sci.vistrails.basic:Float)'),
                     ('Spatial Reference System', '(za.co.csir.eo4vistrails:WKTString:data)')]
                     #('Cordinate Reference System', '(za.co.csir.eo4vistrails:EPSG Code:data)')]
    _output_ports = [('self', '(za.co.csir.eo4vistrails:Raster Prototype:rasterlang)')]
    
    def __init__(self):
        Module.__init__(self)
        RasterlangModule.__init__(self)

    def compute(self):
        self.wkt = self.forceGetInputFromPort('Spatial Reference System', None)
                
        self.noDatavalue = self.forceGetInputFromPort('No Data Value', None)
        
        (self.xmin,self.ymax,self.xmax,self.ymin) = self.getInputFromPort('(XMin,YMax,XMax,YMin) Extent')
        (self.yrows, self.xcols) = self.getInputFromPort('(Rows, Cols) Pixel Count')
        
        self.xres=(self.xmax-self.xmin)/float(self.xcols)
        self.yres=(self.ymax-self.ymin)/float(self.yrows)
        
        self.geotransform=(self.xmin,self.xres,0,self.ymax,0,-self.yres)

@RPyCSafeModule()
class arrayAsLayer(RasterlangModule, RPyCModule):
    """ Container class for the connected components command """

    _input_ports  = [('numpy array', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('prototype', '(za.co.csir.eo4vistrails:Raster Prototype:rasterlang)')]
    _output_ports = [('raster layer', '(za.co.csir.eo4vistrails:Raster Layer:data)')]

    def __init__(self):
        RPyCModule.__init__(self)
        RasterlangModule.__init__(self)

    def clear(self):
        RPyCModule.clear(self)

    def compute(self):
        ndarray = self.getInputFromPort('numpy array')
        prototype = self.getInputFromPort('prototype')
        
        tmpFile = self.interpreter.filePool.create_file(suffix='.img')
        writeImage(ndarray.get_array(), prototype, tmpFile.name, 'HFA')
        
        outlayer = QgsRasterLayer(tmpFile.name, tmpFile.name)
                
        self.setResult("raster layer", outlayer)

@RPyCSafeModule()
class SaveArrayToRaster(NotCacheable, RasterlangModule, RPyCModule):
    """ Container class for the connected components command """

    _input_ports  = [('numpy array', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('prototype', '(za.co.csir.eo4vistrails:Raster Prototype:rasterlang)'),
                     ('output file', '(edu.utah.sci.vistrails.basic:File)'),
                     ('format', '(za.co.csir.eo4vistrails:GDAL Format:rasterlang)')]

    _output_ports  = [ ('output file path', '(edu.utah.sci.vistrails.basic:File)')]


    def __init__(self):
        RPyCModule.__init__(self)
        RasterlangModule.__init__(self)

    def compute(self):
        print 'output file'
        outfile = self.getInputFromPort('output file')
        print 'numpy array'
        ndarray = self.getInputFromPort('numpy array')
        print 'prototype'
        prototype = self.getInputFromPort('prototype')
        print 'format'
        outformat = self.getInputFromPort('format')
        
        if prototype.noDatavalue:
            print "protoype nodata", prototype.noDatavalue
        
        writeImage(ndarray.get_array(), prototype, outfile.name, outformat)
        
        self.setResult('output file path', outfile)

from core.modules import basic_modules
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget

class GDALFormatComboBoxWidget(ComboBoxWidget):
    """TODO Write docstring."""
    _KEY_VALUES = {'HFA': 'HFA', 'GEOTiff':'GTiff'}

# LinuxComboBox
GDALFormatComboBox = basic_modules.new_constant('GDAL Format',
                                                staticmethod(str),
                                                'HFA',
                                                staticmethod(lambda x: type(x) == str),
                                                GDALFormatComboBoxWidget)
                                           
def writeImage(arrayData, prototype, path, format):
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

    #lookup the data type from the array and do the mapping
    print "----------------------------------------------"
    print "arraytype:  %s dtype: %s, type: %s, gdaltype: %s"%(type(arrayData), arrayData.dtype, arrayData.dtype.type, gdalnumeric.NumericTypeCodeToGDALTypeCode(arrayData.dtype.type))
    dst_ds = driver.Create(path, cols, rows, nbands, gdalnumeric.NumericTypeCodeToGDALTypeCode(arrayData.dtype.type) )

    dst_ds.SetGeoTransform( prototype.geotransform )
    
    if prototype.wkt:
        dst_ds.SetProjection( prototype.wkt )
    
    if nbands > 1:
        for i in range(nbands):
            dst_ds_rb = dst_ds.GetRasterBand(i+1)
            dst_ds_rb.WriteArray(arrayData[i])
            if prototype.noDatavalue:
                dst_ds_rb.SetNoDataValue(prototype.nodatavalue)
    else:
        dst_ds_rb = dst_ds.GetRasterBand(1)
        if prototype.noDatavalue:
            dst_ds_rb.SetNoDataValue(prototype.noDatavalue)
        dst_ds_rb.SetColorInterpretation(gdalconst.GCI_GrayIndex)
        dst_ds_rb.SetColorTable(gdal.ColorTable(gdalconst.GPI_Gray))
        dst_ds_rb.WriteArray(arrayData)
    
    dst_ds = None
        
    return True

def fixLayerMinMax(layer):
    allowedGreyStyles = [ QgsRasterLayer.SingleBandGray,
         QgsRasterLayer.MultiBandSingleBandPseudoColor,
         QgsRasterLayer.MultiBandSingleBandGray,
         QgsRasterLayer.SingleBandPseudoColor ]
    allowedRgbStyles = [ QgsRasterLayer.MultiBandColor ]        

    # test if the layer is a raster from a local file (not a wms)
    if layer.type() == layer.RasterLayer: # and ( not layer.usesProvider() ):
        # Test if the raster is single band greyscale
        if layer.drawingStyle() in allowedGreyStyles:
            #Everything looks fine so set stretch and exit
            #For greyscale layers there is only ever one band
            band = layer.bandNumber( layer.grayBandName() ) # base 1 counting in gdal
            extentMin = 0.0
            extentMax = 0.0
            generateLookupTableFlag = False
            # compute the min and max for the current extent
            extentMin, extentMax = layer.computeMinimumMaximumEstimates( band )
            print "min max color", extentMin, extentMax
            # set the layer min value for this band
            layer.setMinimumValue( band, extentMin, generateLookupTableFlag )
            # set the layer max value for this band
            layer.setMaximumValue( band, extentMax, generateLookupTableFlag )
            # ensure that stddev is set to zero
            layer.setStandardDeviations( 0.0 )
            # let the layer know that the min max are user defined
            layer.setUserDefinedGrayMinimumMaximum( True )
            # ensure any cached render data for this layer is cleared
            layer.setCacheImage( None )
        elif layer.drawingStyle() in allowedRgbStyles:
            #Everything looks fine so set stretch and exit
            redBand = layer.bandNumber( layer.redBandName() )
            greenBand = layer.bandNumber( layer.greenBandName() )
            blueBand = layer.bandNumber( layer.blueBandName() )
            extentRedMin = 0.0
            extentRedMax = 0.0
            extentGreenMin = 0.0
            extentGreenMax = 0.0
            extentBlueMin = 0.0
            extentBlueMax = 0.0
            generateLookupTableFlag = False
            # compute the min and max for the current extent
            extentRedMin, extentRedMax = layer.computeMinimumMaximumEstimates( redBand )
            extentGreenMin, extentGreenMax = layer.computeMinimumMaximumEstimates( greenBand )
            extentBlueMin, extentBlueMax = layer.computeMinimumMaximumEstimates( blueBand )
            # set the layer min max value for the red band
            layer.setMinimumValue( redBand, extentRedMin, generateLookupTableFlag )
            layer.setMaximumValue( redBand, extentRedMax, generateLookupTableFlag )
            # set the layer min max value for the red band
            layer.setMinimumValue( greenBand, extentGreenMin, generateLookupTableFlag )
            layer.setMaximumValue( greenBand, extentGreenMax, generateLookupTableFlag )
            # set the layer min max value for the red band
            layer.setMinimumValue( blueBand, extentBlueMin, generateLookupTableFlag )
            layer.setMaximumValue( blueBand, extentBlueMax, generateLookupTableFlag )
            # ensure that stddev is set to zero
            layer.setStandardDeviations( 0.0 )
            # let the layer know that the min max are user defined
            layer.setUserDefinedRGBMinimumMaximum( True )
            # ensure any cached render data for this layer is cleared
            layer.setCacheImage( None )

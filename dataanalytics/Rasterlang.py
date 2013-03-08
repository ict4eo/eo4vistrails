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

# library
import ctypes
# third party
import gdalnumeric
import gdal
from gdal import gdalconst
# vistrails
from core.modules.vistrails_module import ModuleError, NotCacheable, Module
from packages.NumSciPy.Array import NDArray
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
from packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.tools.utils.synhigh import \
    SyntaxSourceConfigurationWidget
from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsRasterLayer
from packages.eo4vistrails.tools.utils.ModuleHelperMixin import ModuleHelperMixin

DEBUG = False


class RasterLangCode(NotCacheable, ModuleHelperMixin, ThreadSafeMixin, RPyCModule):
    """
    This module that executes an arbitrary piece of Python code remotely.
    
    .. todo:: This code is not threadsafe. Terence van Zyl needs to fix it
    """
    #TODO: If you want a PythonSource execution to fail, call fail(error_message).
    #TODO: If you want a PythonSource execution to be cached, call cache_this().

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        RPyCModule.__init__(self)
        self.preCodeString = None
        self.postCodeString = None

    def run_code_common(self, locals_, execute, code_str, use_input, use_output,
                        pre_code_string, post_code_string):
        """TODO: Write docstring.
        """
        import core.packagemanager

        def fail(msg):
            raise ModuleError(self, msg)

        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True

        if use_input:
            inputDict = None
            self.setInputResults(locals_, inputDict)

        outputDict = None
        if use_output:
            outputDict = dict([(k, None) for k in self.outputPorts])
            del outputDict['self']
            locals_.update(outputDict)

        #TODO:Figure out how we get a registry and a package manager
        try:
            _m = core.packagemanager.get_package_manager()
        except VistrailsInternalError:
            _m = None

        from core.modules.module_registry import get_module_registry
        try:
            reg = get_module_registry()
        except VistrailsInternalError:
            reg = None

        locals_.update({'fail': fail,
                        'package_manager': _m,
                        'cache_this': cache_this,
                        'registry': reg,
                        'self': self})

        if pre_code_string:
            execute(pre_code_string)
        execute(code_str)
        if post_code_string:
            execute(post_code_string)

        if use_output:
            self.setOutputResults(locals_, outputDict)

    def setInputResults(self, locals_, inputDict):
        """TODO: Add docstring.
        """
        from packages.NumSciPy.Array import NDArray

        inputDict = dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])
        del inputDict['source']
        if 'rpycnode' in inputDict:
            del inputDict['rpycnode']

        #check that if any are NDArrays we get the numpy array out
        for k in inputDict.iterkeys():
            if isinstance(inputDict[k], NDArray):
                inputDict[k] = inputDict[k].get_array()
        locals_.update(inputDict)

    def setOutputResults(self, locals_, outputDict):
        """TODO: Add docstring.
        """
        from packages.NumSciPy.Array import NDArray

        for k in outputDict.iterkeys():
            try:
                if k in locals_ and locals_[k] != None:
                    if issubclass(self.getPortType(k), NDArray):
                        outArray = NDArray()
                        outArray.set_array(locals_[k])
                        self.setResult(k, outArray)
                    else:
                        self.setResult(k, locals_[k])
            except AttributeError:
                self.setResult(k, locals_[k])

    def run_code_orig(self, code_str, use_input, use_output, pre_code_string, post_code_string):
        """Runs a piece of code as a VisTrails module.
        
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the execution.
        """

        locals_ = locals()

        def execute(s):
            exec s in locals_

        if DEBUG: print "Starting executing in main thread"
        self.run_code_common(locals_, execute, code_str, use_input, use_output,
                             pre_code_string, post_code_string)
        if DEBUG: print "Finished executing in main thread"

#    def _original_compute(self):
    def compute(self):
        """Vistrails Module Compute; refer to Vistrails Docs
        """
        #self.sharedMemOutputPorts = {}
        #isRemote, self.conn, v = self.getConnection()

        from core.modules import basic_modules
        s = basic_modules.urllib.unquote(str(self.forceGetInputFromPort('source', '')))

        if s == '':
            return

        self.run_code_orig(s, True, True, self.preCodeString, self.postCodeString)


@RPyCSafeModule()
class RasterLang(RasterLangCode):
    """This module remotely executes an arbitrary piece of Python code.
    """
    #TODO: If you want PythonSource execution to fail, call fail(error_message)
    #TODO: If you want a PythonSource execution to be cached, call cache_this()

    '''
    This constructor is strictly unnecessary. However, some modules
    might want to initialize per-object data. When implementing your
    own constructor, remember that it must not take any extra parameters.
    '''

    _input_ports = [('prototype',
                     '(za.co.csir.eo4vistrails:RasterPrototype:scripting|raster)')]

    def __init__(self):
        RasterLangCode.__init__(self)
        self.preCodeString = "from numpy import *\nfrom scipy import *\n"
        self.postCodeString = None
        self.raster_prototype = None

    def setInputResults(self, locals_, inputDict):

        inputDict = dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])
        del inputDict['source']
        if 'rpycnode' in inputDict:
            del inputDict['rpycnode']

        #check that if any are NDArrays we get the numpy array out
        self.extent = None
        for k in inputDict.iterkeys():
            if isinstance(inputDict[k], NDArray):
                inputDict[k] = inputDict[k].get_array()
            elif isinstance(inputDict[k], QgsRasterLayer):
                if self.extent == None:
                    e = inputDict[k].extent()
                    self.extent = [e.xMinimum(), e.yMinimum(),
                                   e.xMaximum(), e.yMaximum()]
                    self.raster_prototype = inputDict[k]
                inputDict[k] = gdalnumeric.LoadFile(str(inputDict[k].source()))
        locals_.update(inputDict)

    def setOutputResults(self, locals_, outputDict):
        from tempfile import mkstemp
        import numpy

        self.raster_prototype = self.forceGetInputFromPort('prototype', self.raster_prototype)

        for k in outputDict.iterkeys():
            if k in locals_ and not locals_[k] is None:
                if DEBUG:
                    print "%s == %s  -> %s" % \
                          (self.getPortType(k), NDArray, issubclass(NDArray, \
                           self.getPortType(k)))
                if issubclass(self.getPortType(k), NDArray):
                    if DEBUG:
                        print "NDArray, got %s of type %s" % \
                              (k, type(locals_[k]))
                    outArray = NDArray()
                    outArray.set_array(numpy.asarray(locals_[k]))
                    self.setResult(k, outArray)
                elif issubclass(self.getPortType(k), QgsRasterLayer):
                    if DEBUG:
                        print "QgsRasterLayer, got %s of type %s" % \
                              (k, type(locals_[k]))
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
                    if DEBUG:
                        print "???, got %s of type %s" % (k, type(locals_[k]))
                    self.setResult(k, locals_[k])

    def compute(self):
        RasterLangCode.compute(self)


class RasterSourceConfigurationWidget(SyntaxSourceConfigurationWidget):

    def __init__(self, module, controller, parent=None):
        displayedComboItems = {'String': True,
                               'Float': True,
                               'Integer': True,
                               'Boolean': True,
                               'Numpy Array': True,
                               'RasterLayer': True}

        SyntaxSourceConfigurationWidget.__init__(self,
            module, controller, "Python", parent=parent,
            displayedComboItems=displayedComboItems)


@RPyCSafeModule()
class layerAsArray(ThreadSafeMixin, RPyCModule):
    """ Container class for the connected components command """

    _input_ports = [('RasterLayer',
                     '(za.co.csir.eo4vistrails:RasterLayer:data)')]
    _output_ports = [('numpy array',
                      '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')]

    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)

    def preCompute(self):
        if DEBUG:
            print "In preCompute"
        layer = self.getInputFromPort('RasterLayer')
        if DEBUG:
            print "layer: %s" % layer
        g = gdal.Open(str(layer.source()))
        if DEBUG:
            print "g: %s" % g
        #TODO: Need to check the ctype that the image is
        if DEBUG:
            print "trying to allocate shared memory"
        self.allocateSharedMemoryArray('numpy array', ctypes.c_float,
                                       (g.RasterYSize, g.RasterXSize))

    def compute(self):
        layer = self.getInputFromPort('RasterLayer')

        g = gdal.Open(str(layer.source()))
        g.ReadAsArray(buf_obj=self.sharedMemOutputPorts['numpy array'][0])

        self.setResult("numpy array", None, asNDArray=True)


class RasterPrototype(ThreadSafeMixin, Module):
    """ Container class for the connected components command """

    _input_ports = [('(XMin,YMax,XMax,YMin) Extent',
                     '(edu.utah.sci.vistrails.basic:Float,edu.utah.sci.vistrails.basic:Float,edu.utah.sci.vistrails.basic:Float,edu.utah.sci.vistrails.basic:Float)'),
                    ('(Rows, Cols) Pixel Count',
                     '(edu.utah.sci.vistrails.basic:Integer,edu.utah.sci.vistrails.basic:Integer)'),
                    ('No Data Value',
                     '(edu.utah.sci.vistrails.basic:Float)'),
                    ('Spatial Reference System',
                     '(za.co.csir.eo4vistrails:WKTString:data|geostrings)')]
                     #('Cordinate Reference System',
                     #'(za.co.csir.eo4vistrails:EPSG Code:data)')]
    _output_ports = [('self',
                      '(za.co.csir.eo4vistrails:RasterPrototype:scripting|raster)')]

    def __init__(self):
        Module.__init__(self)
        ThreadSafeMixin.__init__(self)

    def compute(self):
        self.wkt = self.forceGetInputFromPort('Spatial Reference System', None)

        self.noDatavalue = self.forceGetInputFromPort('No Data Value', None)

        (self.xmin, self.ymax, self.xmax, self.ymin) = \
            self.getInputFromPort('(XMin,YMax,XMax,YMin) Extent')
        (self.yrows, self.xcols) = \
            self.getInputFromPort('(Rows, Cols) Pixel Count')

        self.xres = (self.xmax - self.xmin) / float(self.xcols)
        self.yres = (self.ymax - self.ymin) / float(self.yrows)

        self.geotransform = (self.xmin, self.xres, 0, self.ymax, 0, -self.yres)


@RPyCSafeModule()
class arrayAsLayer(ThreadSafeMixin, RPyCModule):
    """ Container class for the connected components command """

    _input_ports = [('numpy array',
                     '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                    ('prototype',
                     '(za.co.csir.eo4vistrails:RasterPrototype:scripting|raster)')]
    _output_ports = [('raster layer',
                      '(za.co.csir.eo4vistrails:RasterLayer:data)')]

    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)

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
class SaveArrayToRaster(NotCacheable, ThreadSafeMixin, RPyCModule):
    """ Container class for the connected components command """

    _input_ports = [('numpy array',
                     '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                    ('prototype',
                     '(za.co.csir.eo4vistrails:RasterPrototype:scripting|raster)'),
                    ('output file',
                     '(edu.utah.sci.vistrails.basic:File)'),
                    ('format',
                     '(za.co.csir.eo4vistrails:GDAL Format:scripting|raster)')]

    _output_ports = [('output file path',
                      '(edu.utah.sci.vistrails.basic:File)')]

    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)

    def compute(self):
        if DEBUG:
            print 'output file'
        outfile = self.getInputFromPort('output file')
        if DEBUG:
            print 'numpy array'
        ndarray = self.getInputFromPort('numpy array')
        if DEBUG:
            print 'prototype'
        prototype = self.getInputFromPort('prototype')
        if DEBUG:
            print 'format'
        outformat = self.getInputFromPort('format')

        if prototype.noDatavalue:
            if DEBUG:
                print "protoype nodata", prototype.noDatavalue

        writeImage(ndarray.get_array(), prototype, outfile.name, outformat)

        self.setResult('output file path', outfile)

from core.modules import basic_modules
from packages.eo4vistrails.tools.utils.DropDownListWidget import ComboBoxWidget


class GDALFormatComboBoxWidget(ComboBoxWidget):
    """TODO: Write docstring."""
    _KEY_VALUES = {'HFA': 'HFA', 'GEOTiff': 'GTiff'}

# LinuxComboBox
GDALFormatComboBox = basic_modules.new_constant('GDAL Format',
                                                staticmethod(str),
                                                'HFA',
                                                staticmethod(lambda x: type(x) == str),
                                                GDALFormatComboBoxWidget)


def writeImage(arrayData, prototype, path, format):
    """Write the given array data to the file 'path' with the given extent.
    
    If arrayData shape is of length 3, then we have multibands (nbad,rows,cols),
    otherwise one band
    """

    driver = gdal.GetDriverByName(format)
    metadata = driver.GetMetadata()
    if gdal.DCAP_CREATE in metadata and metadata[gdal.DCAP_CREATE] == 'YES':
        pass
    else:
        print 'Driver %s does not support Create() method.' % format
        return False

    # get rows and columns
    dims = arrayData.shape
    if len(dims) == 2:
        rows = dims[0]
        cols = dims[1]
        nbands = 1
    else:
        rows = dims[1]
        cols = dims[2]
        nbands = dims[0]

    #lookup the data type from the array and do the mapping
    if DEBUG:
        print "arraytype:  %s dtype: %s, type: %s, gdaltype: %s" % \
            (type(arrayData),
             arrayData.dtype,
             arrayData.dtype.type,
             gdalnumeric.NumericTypeCodeToGDALTypeCode(arrayData.dtype.type))
    dst_ds = driver.Create(path, cols, rows, nbands,
                           gdalnumeric.NumericTypeCodeToGDALTypeCode(arrayData.dtype.type))

    dst_ds.SetGeoTransform(prototype.geotransform)

    if prototype.wkt:
        dst_ds.SetProjection(prototype.wkt)

    if nbands > 1:
        for i in range(nbands):
            dst_ds_rb = dst_ds.GetRasterBand(i + 1)
            dst_ds_rb.WriteArray(arrayData[i])
            if prototype.noDatavalue:
                dst_ds_rb.SetNoDataValue(prototype.nodatavalue)
    else:
        dst_ds_rb = dst_ds.GetRasterBand(1)
        #if prototype.noDatavalue:
        #    dst_ds_rb.SetNoDataValue(prototype.noDatavalue)
        #dst_ds_rb.SetRasterColorInterpretation(gdalconst.GCI_GrayIndex)
        #dst_ds_rb.SetRasterColorTable(gdal.ColorTable(gdalconst.GPI_Gray))
        dst_ds_rb.WriteArray(arrayData)

    dst_ds = None

    return True

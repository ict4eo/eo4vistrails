# -*- coding: utf-8 -*-
###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
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
"""The `datacube` module ???
"""
debug = True
# library
import os.path
# third party
import h5py
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.NumSciPy.Array import NDArray
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from threading import Lock

class CubeReaderHandle(Module):
    """HDF data cube initialisation."""

    _input_ports = [('cubefile', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('CubeReaderHandle',
                      '(za.co.csir.eo4vistrails:CubeReaderHandle:datacube)')]

    def __init__(self):
        Module.__init__(self)
        
    def cubeInit(self):        
        cubefile = self.getInputFromPort('cubefile')
        cubefile_path = cubefile.name
        if not os.path.isfile(cubefile_path):
            return False

        self.cube = h5py.File(cubefile_path, 'r')
        self.imgWidth = self.cube.attrs['WIDTH']
        self.imgHeight = self.cube.attrs['HEIGHT']
        self.band = None
        return True

    def compute(self):
        if self.cubeInit():
            self.setResult('CubeReaderHandle', self)

@RPyCSafeModule()
class ModisCubeReaderHandle(ThreadSafeMixin, CubeReaderHandle):
    """MODIS HDF data cube initialisation.

    Assumes that the cube contains a single band, initialises both it
    and the time band.
    """

    #moduleLock = Lock()
    
    _input_ports = [('cubefile', '(edu.utah.sci.vistrails.basic:File)'),
                    ('band', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('CubeReaderHandle', '(za.co.csir.eo4vistrails:CubeReaderHandle:datacube)'),
                     ('timeBand', '(edu.utah.sci.vistrails.basic:List)')]

    def __init__(self):
        CubeReaderHandle.__init__(self)
        ThreadSafeMixin.__init__(self)

    def compute(self):
        #with ModisCubeReaderHandle.alock:
        if debug: print self, "in compute"
        if self.cubeInit():
            self.band = self.getInputFromPort('band')
            self.time = self.cube['/TIME'][0]
            self.data = self.cube[self.band]
            self.setResult('CubeReaderHandle', self)
            self.setResult('timeBand', self.time)
        if debug: print self, "out compute"


@RPyCSafeModule()
class CubeReader(ThreadSafeMixin, Module):
    """HDF data cube reader."""

    _input_ports = [('cubereader',
                     '(za.co.csir.eo4vistrails:CubeReaderHandle:datacube)'),
                    ('band',
                     '(edu.utah.sci.vistrails.basic:String)', {'optional': True}),
                    ('offset', '(edu.utah.sci.vistrails.basic:List)'), ]
    
    _output_ports = [('timeseries', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')]

    def __init__(self):
        Module.__init__(self)
        ThreadSafeMixin.__init__(self)        

    def getData(self, cube, offset):
        return cube.data[offset]

    def compute(self):
        cube = self.getInputFromPort('cubereader')
        if 'band' in self.inputPorts:
            band = self.getInputFromPort('band')
        else:
            band = None
        offset = self.getInputFromPort('offset')

        # Reassign band if provided and different from the cube's current band
        if not band is None and band != '' and band != cube.band:
            cube.band = band
            cube.data = cube.cube[band]
        outArray = NDArray()
        outArray.set_array(self.getData(cube, offset))
        
        self.setResult('timeseries', outArray)


class PostGISCubeReader(CubeReader):
    """HDF data cube reader using PostGIS offsets."""

    _input_ports = [('cubereader', '(za.co.csir.eo4vistrails:CubeReaderHandle:datacube)'),
                    ('band', '(edu.utah.sci.vistrails.basic:String)', {'optional': True}),
                    ('offset', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('generate_ids', '(edu.utah.sci.vistrails.basic:Boolean)', {'optional': True})]
    _output_ports = [('timeseries', '(edu.utah.sci.vistrails.basic:List)'),
                     ('id_list', '(edu.utah.sci.vistrails.basic:List)')]

    def getData(self, cube, offset):
        pgOffset = offset
        offset -= offset / 4801
        timeseries = cube.data[offset]
        if bool(self.getInputFromPort('generate_ids')):
            id_list = [pgOffset for x in range(len(timeseries))]
            self.setResult('id_list', id_list)
        return timeseries


#@RPyCSafeModule()
class CubeDateConverter(Module):
    """Converts dates from a data cube to JDN (Julian Day Number) dates."""

    _input_ports = [('dates', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('dates_JDN', '(edu.utah.sci.vistrails.basic:List)')]

    def __init__(self):
        #ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        dates = self.getInputFromPort('dates')
        # TODO: Convert dates to JDN
        self.setResult('dates_JDN', dates)

# -*- coding: utf-8 -*-
import h5py
import os.path

# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin

@RPyCSafeModule()
class CubeReaderHandle(ThreadSafeMixin, Module):
    """HDF data cube initialisation."""

    _input_ports = [('cubefile', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('CubeReaderHandle', '(za.co.csir.eo4vistrails:CubeReaderHandle:datacube)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
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

class ModisCubeReaderHandle(CubeReaderHandle):
    """MODIS HDF data cube initialisation.

    Assumes that the cube contains a single band, initialises it and the time band."""

    _input_ports = [('cubefile', '(edu.utah.sci.vistrails.basic:File)'),
                    ('band', '(edu.utah.sci.vistrails.basic:String)')]

    def compute(self):
        if self.cubeInit():
            self.band = self.getInputFromPort('band')
            self.time = self.cube['/TIME'][0]
            self.data = self.cube[self.band]
            self.setResult('CubeReaderHandle', self)

@RPyCSafeModule()
class CubeReader(ThreadSafeMixin, Module):
    """HDF data cube reader."""

    _input_ports = [('cubereader', '(za.co.csir.eo4vistrails:CubeReaderHandle:datacube)'),
                    ('band', '(edu.utah.sci.vistrails.basic:String)', {'optional': True}),
                    ('offset', '(edu.utah.sci.vistrails.basic:Integer)'),]
    _output_ports = [('timeseries', '(edu.utah.sci.vistrails.basic:List)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def getData(self, cube, offset):
        return cube.data[offset]

    def compute(self):
        cube = self.getInputFromPort('cubereader')
        if 'band' in self.inputPorts:
            band = self.getInputFromPort('band')
        else:
            band = None
        offset = self.getInputFromPort('offset')

        # Reassign band if it's provided and different from the cube's current band
        if not band is None and band != '' and band != cube.band:
            cube.band = band
            cube.data = cube.cube[band]
        self.setResult('timeseries', self.getData(cube, offset))

class PostGISCubeReader(CubeReader):
    """HDF data cube reader using PostGIS offsets."""

    def getData(self, cube, offset):
        offset -= offset / 4801
        return cube.data[offset]

@RPyCSafeModule()
class CubeDateConverter(ThreadSafeMixin, Module):
    """Converts dates from a data cube to JDN (Julian Day Number) dates."""

    _input_ports = [('dates', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('dates_JDN', '(edu.utah.sci.vistrails.basic:List)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        dates = self.getInputFromPort('dates')
        # TODO: Convert dates to JDN
        self.setResult('dates_JDN', dates)

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
    """HDF data cube reader.

    Requires:
     *  TODO

    Returns:
     *  TODO
    """

    _input_ports = [('cubefile', '(edu.utah.sci.vistrails.basic:File)'),
                    ('band', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('CubeReaderHandle', '(za.co.csir.eo4vistrails:CubeReaderHandle:utils)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        cubefile = self.getInputFromPort('cubefile')
        band = self.getInputFromPort('band')
        cubefile_path = cubefile.name

        if os.path.isfile(cubefile_path):
            self.cube = h5py.File(cubefile_path, 'r')
            self.img_width = cube.attrs['WIDTH']
            self.img_height = cube.attrs['HEIGHT']
            self.time = cube['/TIME'][0]
            self.data = cube[band]

            self.setResult('CubeReaderHandle', self)

@RPyCSafeModule()
class CubeReader(ThreadSafeMixin, Module):

    _input_ports = [('cubereader', '(za.co.csir.eo4vistrails:CubeReaderHandle:utils)'),
                    ('offset', '(edu.utah.sci.vistrails.basic:Integer)')]
    _output_ports = [('timeseries', '(edu.utah.sci.vistrails.basic:List)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        cube = self.getInputFromPort('cubereader')
        offset = self.getInputFromPort('offset')
        self.setResult('timeseries', cube.data[offset])

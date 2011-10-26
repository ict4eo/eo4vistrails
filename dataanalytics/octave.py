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
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget

from core.modules.vistrails_module import ModuleError, NotCacheable, Module
from core.modules.basic_modules import File

from script import Script

from subprocess import call
from tempfile import mkstemp
from os import fdopen, remove
import urllib

@RPyCSafeModule()
class OctaveScript(Script):
    """
       Executes a Octave Script 
       Writes output to output files and reads input from inout files
    """
    _input_ports = [
                   # ('inputDataFiles', '(edu.utah.sci.vistrails.basic:File)')
                   #,('inputNumpyArray', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')
                   ]

    _output_ports = [
                     ('self', '(edu.utah.sci.vistrails.basic:Module)')
                    ]

    def __init__(self):
        Script.__init__(self)

    def compute(self):
        """Will need to fetch a object on its input port
        Overrides supers method"""
        import scipy.io
        import numpy
        from packages.NumSciPy.Array import NDArray
        
        octave_script = urllib.unquote(str(self.forceGetInputFromPort('source', '')))

        inputDict = dict([(k, self.getInputFromPort(k))
                          for k in self.inputPorts])

        for k in inputDict.iterkeys():
            if type(inputDict[k]) == NDArray:
                inputDict[k] = inputDict[k].get_array()
                    
        matInFileName = self.interpreter.filePool.create_file(suffix='.mat')
        scipy.io.savemat(matInFileName.name, inputDict)
        octave_preScript = "load %s"%matInFileName.name        
        
        matOutFileName = self.interpreter.filePool.create_file(suffix='.mat')
        octave_postScript = "save -v7 %s"%matOutFileName.name
        
        self.write_script_to_file(octave_script, preScript=octave_preScript, postScript=octave_postScript, suffix='.m')
        
        #Execute the command
        args = ["octave", self.scriptFileName]
        a = call(args)
        
        if a == 0:
            scriptResult = scipy.io.loadmat(matOutFileName.name, chars_as_strings=True, squeeze_me=True, struct_as_record=True)        
            outputDict = dict([(k, None)
                               for k in self.outputPorts])
            for k in outputDict.iterkeys():
                if scriptResult.has_key(k) and scriptResult[k] != None:
                    if type(scriptResult[k]) == numpy.ndarray:
                        outArray = NDArray()
                        outArray.set_array(scriptResult[k])
                        self.setResult(k, outArray)
                    else:
                        self.setResult(k, scriptResult[k])
        else:
            raise ModuleError, (OctaveScript, "Could not execute PovRay Script")

class OctaveSourceConfigurationWidget(SyntaxSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        displayedComboItems = {'String':True,
                               'Float':True,
                               'Integer':True,
                               'Boolean':True,
                               'Numpy Array':True}
                               #'File':True}
    
        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "octave", 
                                                 parent=parent,
                                                 displayedComboItems = displayedComboItems)

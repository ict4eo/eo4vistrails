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
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget
from packages.eo4vistrails.utils.ModuleHelperMixin import ModuleHelperMixin
from core.modules.vistrails_module import ModuleError, Module

from subprocess import call
from tempfile import mkstemp
from os import fdopen
import urllib

class OctaveScript(Module, ModuleHelperMixin):
    """
       Executes a Octave Script 
       Writes output to output files and reads input from inout files
    """
    _input_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    _output_ports = [
                     ('self', '(edu.utah.sci.vistrails.basic:Module)')
                    ]

    def __init__(self):
        Module.__init__(self)

    def write_script_to_file(self, script, preScript=None, postScript=None, suffix='.e4v'):
        #Get a temp file to write the script into
        self.scriptFileDescript, self.scriptFileName = mkstemp(suffix=suffix, text=True)
        #Write the script to the file
        scriptFile = fdopen(self.scriptFileDescript, 'w')
        if preScript:
            scriptFile.write(preScript)
            scriptFile.write("\n")
        scriptFile.write(script)        
        if postScript:
            scriptFile.write("\n")
            scriptFile.write(postScript)
        scriptFile.close()

    def compute(self):
        """Will need to fetch a object on its input port
        Overrides supers method"""
        import scipy.io
        import numpy
        from packages.NumSciPy.Array import NDArray
        
        # Lets get the script fromn theinput port named source
        octave_script = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        
        #Lets get the list of input ports so we can get there values
        inputDict = dict([(k, self.getInputFromPort(k))
                          for k in self.inputPorts])
        
        # remove the script from the list
        del inputDict['source']
        if inputDict.has_key('rpycnode'):
            del inputDict['rpycnode']
        
        #check that if any are NDArrays we get the numpy array out        
        for k in inputDict.iterkeys():
            if type(inputDict[k]) == NDArray:
                inputDict[k] = inputDict[k].get_array()
        
        #Get a temp file to place the matclab data in
        matInFileName = self.interpreter.filePool.create_file(suffix='.mat')
        
        #save the current python values for the scripts inputs to a matlab file
        scipy.io.savemat(matInFileName.name, inputDict)
        #run the following at the begining of the octave script
        #this loads the file with all the input values into octave
        octave_preScript = "load %s"%matInFileName.name    
        
        #create a temp file for the returned results
        matOutFileName = self.interpreter.filePool.create_file(suffix='.mat')
        #run the following at the end of the octave script
        #this writes out the results of running begining the script
        octave_postScript = "save -v7 %s"%matOutFileName.name
        
        #write the script out
        self.write_script_to_file(octave_script, preScript=octave_preScript, postScript=octave_postScript, suffix='.m')
        
        #Execute the script
        args = ["octave", self.scriptFileName]
        a = call(args)
        
        if a == 0:
            #load the results of the script running back into the python input variables
            scriptResult = scipy.io.loadmat(matOutFileName.name, chars_as_strings=True, squeeze_me=True, struct_as_record=True)        
            outputDict = dict([(k, None)
                               for k in self.outputPorts])
            del(outputDict['self'])

            for k in outputDict.iterkeys():
                if scriptResult.has_key(k) and scriptResult[k] != None:                    
                    if self.getPortType(k) == NDArray:
                        outArray = NDArray()
                        outArray.set_array(scriptResult[k])
                        self.setResult(k, outArray)
                    else:
                        if scriptResult[k].ndim == 0:
                            self.setResult(k, scriptResult[k].item())
                        else:
                            self.setResult(k, scriptResult[k][0])
        else:
            raise ModuleError, (OctaveScript, "Could not execute Octave Script")



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

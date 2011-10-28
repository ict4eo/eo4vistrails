# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 09:55:33 2011

@author: tvzyl
"""

#History
#Created by Terence van Zyl
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget

from core.modules.vistrails_module import ModuleError

from script import Script

import urllib

@RPyCSafeModule()
class RScript(Script):
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
        from packages.NumSciPy.Array import NDArray
        import numpy
        import rpy2.robjects as robjects
        import rpy2.robjects.numpy2ri
        rpy2.robjects.numpy2ri.activate()

        # Lets get the script fromn theinput port named source
        r_script = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        
        #Lets get the list of input ports so we can get there values
        inputDict = dict([(k, self.getInputFromPort(k))
                          for k in self.inputPorts])
        
        # remove the script from the list
        del(inputDict['source'])
        
        #check that if any are NDArrays we get the numpy array out
        for k in inputDict.iterkeys():
            if type(inputDict[k]) == NDArray:
                inputDict[k] = inputDict[k].get_array()
            robjects.globalenv[k] = inputDict[k]

        #try:
        #Execute the script
        robjects.r(r_script)
    
        outputDict = dict([(k, None)
                           for k in self.outputPorts])
        del(outputDict['self'])

        for k in outputDict.iterkeys():
            if k in robjects.globalenv.keys() and robjects.globalenv[k] != None:
                if self.getPortType(k) == NDArray:
                    outArray = NDArray()
                    outArray.set_array(numpy.array(robjects.globalenv[k]))
                    self.setResult(k, outArray)
                else:
                    self.setResult(k, robjects.globalenv[k][0])
        #except:
        #    raise ModuleError, (RScript, "Could not execute R Script")

    def getPortType(self, portName, portType="output"):
        for i in self.moduleInfo['pipeline'].module_list:
            if i.id == self.moduleInfo['moduleId']:
                for j in i.port_specs:
                    if i.port_specs[j].type == portType and i.port_specs[j].name == portName:
                        return i.port_specs[j].signature[0][0]


class RSourceConfigurationWidget(SyntaxSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        displayedComboItems = {'String':True,
                               'Float':True,
                               'Integer':True,
                               'Boolean':True,
                               'Numpy Array':True}
                               #'File':True}
    
        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "r", 
                                                 parent=parent,
                                                 displayedComboItems = displayedComboItems)

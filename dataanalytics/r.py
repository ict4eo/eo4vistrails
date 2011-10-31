# -*- coding: utf-8 -*-

"""This module holds a rpycnode type that can be passed around between modules.
"""
#History
#Created by Mugu Mtsetfwa on 27-10-2011
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget

from core.modules.vistrails_module import ModuleError, NotCacheable, Module
from core.modules.basic_modules import File

from script import Script

from subprocess import call
import urllib
import pickle

@RPyCSafeModule()
class RScriptExec(Script):
    """
       Executes an R Script 
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
        
        # Lets get the script from the input port named source
        scriptFile = self.forceGetInputFromPort('source', '')
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

        
        #write the script out
        self.write_script_to_file(r_script, preScript="", postScript="", suffix='.R')
        
        
        
        #args = ["Rscript", self.scriptFileName]
        args = ["Rscript", scriptFile]
        a = call(args)#Execute the script
        
        
        if a == 0:
            f=open('/home/mmtsetfwa/RScripts/workfile.txt', 'wb')                  
            outputDict = dict([(k, None)
                               for k in self.outputPorts])
            #pickle.dump(outputDict,f)\
            # Pickle the list using the highest protocol available.
            pickle.dump(outputDict, f, -1)
            f.close()
            
        else:
            raise ModuleError, (RScriptExec, "Could not execute Script)
#Dropdown of available datatypes
class RSourceConfigurationWidget(SyntaxSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        displayedComboItems = {'String':True,
                               'Float':True,
                               'Integer':True,
                               'Boolean':True,
                               'Numpy Array':True}
                               #'File':True}
    
        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "Rscript", 
                                                 parent=parent,
                                                 displayedComboItems = displayedComboItems)

# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 11:23:35 2011

@author: mmtsetfwa
"""

from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget
import core.modules
from core.modules.vistrails_module import ModuleError
from script import Script
import urllib
import numpy
from packages.NumSciPy.Array import NDArray
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
try:
    rpy2.robjects.numpy2ri.activate()
except:
    pass
r=robjects.r         

class Rpy2Script(Script):
    """
       Run R scripts using rpy2 interface
    """
    _input_ports = [
                   # ('inputDataFiles', '(edu.utah.sci.vistrails.basic:File)')
                   #,('inputNumpyArray', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')
                   ]

    _output_ports = [
                     ('self', '(edu.utah.sci.vistrails.basic:Module)')
                     #('myDict', '(edu.utah.sci.vistrails.basic:Dictionary)')
                    ]

    def __init__(self):
        Script.__init__(self)       

        
    def compute(self):
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

        #Execute the script
        try:
            resultVar=r(r_script)
        except:
            raise ModuleError, (Rpy2Script, "Could not execute R Script")
                
        #Converting R result to Python type
        rResult=self.rPyConversion(resultVar)
        
        
        outputDict = dict([(k, None)
                           for k in self.outputPorts])
        del(outputDict['self'])
        #assigning converted R result to output port
        for k in outputDict.iterkeys():             
               if isinstance(rResult,dict) and str(self.getPortType(k))=="<class 'core.modules.vistrails_module.Dictionary'>":
                   self.setResult(k,rResult)
               elif isinstance(rResult,numpy.ndarray) and str(self.getPortType(k))=="<class 'packages.eo4vistrails.utils.Array.NDArray'>":
                   self.setResult(k,rResult)
               elif isinstance(rResult,numpy.ndarray) and str(self.getPortType(k))=="<class 'core.modules.vistrails_module.String'>":
                   self.setResult(k,rResult)
               elif isinstance(rResult,str) and str(self.getPortType(k))=="<class 'core.modules.vistrails_module.String'>":
                   self.setResult(k,rResult)
               elif isinstance(rResult,float) and str(self.getPortType(k))=="<class 'core.modules.vistrails_module.Integer'>":
                   self.setResult(k,rResult)
               elif isinstance(rResult,bool) and str(self.getPortType(k))=="<class 'core.modules.vistrails_module.Boolean'>":
                   self.setResult(k,rResult)                                 
               elif self.getPortType(k)==type(rResult):
                   self.setResult(k,rResult)                   
#               else:
#                    self.setResult(k, robjects.globalenv[k])      
      
        

    def getPortType(self, portName, portType="output"):
        for i in self.moduleInfo['pipeline'].module_list:
            if i.id == self.moduleInfo['moduleId']:
                for j in i.port_specs:
                    if i.port_specs[j].type == portType and i.port_specs[j].name == portName:
                        return i.port_specs[j].signature[0][0]
    
    
    #Converting R result to a Python Type.
    def rPyConversion(self,data):
        try:
            if isinstance(data,rpy2.robjects.vectors.ListVector):
               pyDict = {}        
               for name,value in zip([i for i in rpy2.robjects.r.names(data)],[i for i in data]):
                   if len(value) == 1: 
                       pyDict[name] = value[0]
                   else: pyDict[name] = [i for i in value]
               return pyDict            
            elif (isinstance(data,robjects.vectors.FloatVector) or isinstance(data,robjects.vectors.IntVector) or
                isinstance(data,robjects.vectors.BoolVector)  or isinstance(data,robjects.vectors.ComplexVector) or (data,robjects.vectors.StrVector)) and (len(data)>1):
               return numpy.array(data)            
            elif (isinstance(data,robjects.vectors.FloatVector) or isinstance(data,robjects.vectors.IntVector) or
                isinstance(data,robjects.vectors.BoolVector)  or isinstance(data,robjects.vectors.ComplexVector) or isinstance(data,robjects.vectors.StrVector)) and (len(data)==1):
               return data[0]
            elif isinstance(data,rpy2.robjects.vectors.Vector):
               return numpy.array(data)
            elif isinstance(data,rpy2.robjects.vectors.DataFrame):
               return data
            elif isinstance(data,rpy2.rinterface.RNULLType):
               return None
            elif data=="":
               return None
        except:
            raise ModuleError, (Rpy2Script, "Could not convert R type to Python type")

class RSourceConfigurationWidget(SyntaxSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        displayedComboItems = {'String':True,
                               'Float':True,
                               'Integer':True,
                               'Boolean':True,
                               'Numpy Array':True,
                               'List':True,
                               'Dictionary':True,                               
                               'File':True}
    
        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "Rpy2Script", 
                                                 parent=parent,
                                                 displayedComboItems = displayedComboItems)
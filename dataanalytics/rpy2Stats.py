# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 11:23:35 2011

@author: mmtsetfwa
"""

#from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget

from core.modules.vistrails_module import ModuleError

from script import Script

import urllib
import numpy
from packages.NumSciPy.Array import NDArray
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
r=robjects.r 
        
 #Converting R output to a Python Type.
def rPyConversion(data):    
    if isinstance(data,rpy2.robjects.vectors.ListVector):
       pyDict = {}        
       for name,value in zip([i for i in rpy2.robjects.r.names(data)],[i for i in data]):
           if len(value) == 1: 
               pyDict[name] = value[0]
           else: pyDict[name] = [i for i in value]
       return pyDict
            
    elif (isinstance(data,robjects.vectors.FloatVector) or isinstance(data,robjects.vectors.IntVector) or
        isinstance(data,robjects.vectors.BoolVector)  or isinstance(data,robjects.vectors.ComplexVector)) and (len(data)>1):
           return numpy.array(data)
            
    elif (isinstance(data,robjects.vectors.FloatVector) or isinstance(data,robjects.vectors.IntVector) or
        isinstance(data,robjects.vectors.BoolVector)  or isinstance(data,robjects.vectors.ComplexVector)) and (len(data)==1):
           return data[0]
    elif isinstance(data,rpy2.robjects.vectors.Vector):
           return numpy.array(data)
    elif isinstance(data,rpy2.robjects.vectors.DataFrame):
           return data  
        
        

#@RPyCSafeModule()
class Rpy2Script(Script):
    """
       Run R using rpy2 interface
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
        resultVar=r(r_script)
        x=type(resultVar)
        #testing purposes
        f=open('/home/mmtsetfwa/RScripts/rpy2Results.txt', 'w')
        f.write(str(x))        
        f.close()
        
        mylist=rPyConversion(resultVar)
        #testing purposes
        if mylist !=None:           
            #test writing converted result to file
            f2=open('/home/mmtsetfwa/RScripts/testType.txt', 'w')
            f2.write(str(mylist))
            f2.close()
            
        
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
        #    raise ModuleError, (Rpy2Script, "Could not execute R Script")

        

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
                               'Numpy Array':True,
                               'List':True,
                               'Dictionary':True,                               
                               'File':True}
    
        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "Rpy2Script", 
                                                 parent=parent,
                                                 displayedComboItems = displayedComboItems)
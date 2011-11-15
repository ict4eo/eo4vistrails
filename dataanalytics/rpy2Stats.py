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
"""This module ???
"""
# library
from script import Script
import urllib
import numpy
# third-party
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri
try:
    rpy2.robjects.numpy2ri.activate()
except:
    pass
r = robjects.r
# vistrails
import core.modules
from core.modules.vistrails_module import ModuleError
from packages.NumSciPy.Array import NDArray
# eo4vistrails
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget


class Rpy2Script(Script):
    """
       Run R scripts using rpy2 interface
    """
    _input_ports = [
                    # ('inputDataFiles', '(edu.utah.sci.vistrails.basic:File)')
                   #,('inputNumpyArray', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')
                   ]

    _output_ports = [('self', '(edu.utah.sci.vistrails.basic:Module)')
                     #('myDict', '(edu.utah.sci.vistrails.basic:Dictionary)')
                     ]

    def __init__(self):
        Script.__init__(self)

    def compute(self):
        # Get the script fromn theinput port named source
        r_script = urllib.unquote(str(self.forceGetInputFromPort('source', '')))

        # Get the list of input ports so we can get there values
        inputDict = dict([(k, self.getInputFromPort(k))
                          for k in self.inputPorts])

        # Remove the script from the list
        del(inputDict['source'])

        # Check that if any are NDArrays we get the numpy array out
        for k in inputDict.iterkeys():
            if type(inputDict[k]) == NDArray:
                inputDict[k] = inputDict[k].get_array()
            elif type(inputDict[k]) == dict:
                tempDict = robjects.DataFrame(inputDict[k])
                #tempDicttoR=robjects.r('x<-tempDict')
                tempDicttoPy = self.rPyConversion(tempDict)
                inputDict[k] = tempDicttoPy
            elif type(inputDict[k]) == list:
                myListArr = numpy.array(inputDict[k])
                inputDict[k] = myListArr
            robjects.globalenv[k] = inputDict[k]

        # Execute the script
        try:
            resultVar = r(r_script)
        except:
            raise ModuleError(Rpy2Script, "Could not execute R Script")
        #Converting R result to Python type
        rResult = self.rPyConversion(resultVar)

        #Converting R result to Python type
        mylist = self.rPyConversion(resultVar)
        #testing purposes

        outputDict = dict([(k, None)
                           for k in self.outputPorts])
        del(outputDict['self'])
        #assigning converted R result to output port
        for k in outputDict.iterkeys():
            if k in robjects.globalenv.keys() and robjects.globalenv[k] != None:
                    if str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.Dictionary'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'packages.eo4vistrails.utils.Array.NDArray'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.String'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k) ) == "<class 'core.modules.vistrails_module.Integer'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.Float'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.Boolean'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.List'>":
                        self.setResult(k, numpy.array(robjects.globalenv[k]))
                    elif self.getPortType(k) == type(rResult):
                        self.setResult(k, rResult)
#                   else:
#                       self.setResult(k, robjects.globalenv[k])

    def getPortType(self, portName, portType="output"):
        for i in self.moduleInfo['pipeline'].module_list:
            if i.id == self.moduleInfo['moduleId']:
                for j in i.port_specs:
                    if i.port_specs[j].type == portType and i.port_specs[j].name == portName:
                        return i.port_specs[j].signature[0][0]

    #Converting R result to a Python Type.
    def rPyConversion(self, data):
        try:
#            if type(data)==rpy2.robjects.vectors.ListVector:
#                return numpy.array(data)
            if isinstance(data, rpy2.robjects.vectors.ListVector):
                pyDict = {}
                for name, value in zip([i for i in rpy2.robjects.r.names(data)],
                                       [i for i in data]):
                    if len(value) == 1:
                        pyDict[name] = value[0]
                    else:
                        pyDict[name] = [i for i in value]
                return pyDict
            elif (isinstance(data, robjects.vectors.FloatVector) or \
                  isinstance(data, robjects.vectors.IntVector) or \
                  isinstance(data, robjects.vectors.BoolVector)  or \
                  isinstance(data, robjects.vectors.ComplexVector) or
                  isinstance(data, robjects.vectors.StrVector)) and \
                  (len(data) > 1):
                return numpy.array(data)
            elif (isinstance(data, robjects.vectors.FloatVector) or \
                  isinstance(data, robjects.vectors.IntVector) or
                  isinstance(data, robjects.vectors.BoolVector) or \
                  isinstance(data, robjects.vectors.ComplexVector) or \
                  isinstance(data, robjects.vectors.StrVector)) and \
                  (len(data) == 1):
                return data[0]
            elif isinstance(data, rpy2.robjects.vectors.Vector):
                return numpy.array(data)
            elif isinstance(data, rpy2.robjects.vectors.DataFrame):
                return data
            elif isinstance(data, rpy2.rinterface.RNULLType):
                return None
            elif isinstance(data, rpy2.robjects.vectors.Array):
                return numpy.array(data)
            elif data == "":
                return None
        except:
            raise ModuleError(Rpy2Script, "Could not convert R type to Python type")


class RSourceConfigurationWidget(SyntaxSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        displayedComboItems = {'String': True,
                               'Float': True,
                               'Integer': True,
                               'Boolean': True,
                               'Numpy Array': True,
                               'List': True,
                               'Dictionary': True}

        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "Rpy2Script",
                                                 parent=parent,
                                                 displayedComboItems=displayedComboItems)

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
debug = False
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
from core.modules.vistrails_module import ModuleError
from core.modules.basic_modules import List
from vistrails.packages.NumSciPy.Array import NDArray
# eo4vistrails
from vistrails.packages.eo4vistrails.tools.utils.synhigh import \
    SyntaxSourceConfigurationWidget
from vistrails.packages.eo4vistrails.tools.utils.ModuleHelperMixin import \
    ModuleHelperMixin
from vistrails.packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule


@RPyCSafeModule()
class Rpy2Script(Script, ModuleHelperMixin):
    """Run R scripts using rpy2 interface
    """
    _input_ports = []
    _output_ports = [('self', '(edu.utah.sci.vistrails.basic:Module)')]

    def __init__(self):
        Script.__init__(self)

    def compute(self):
        #cleanup robjects mem before we start
        #cleanup pythons mem as well
        import gc
        robjects.r.gc()
        gc.collect()

        # Get the script fromn theinput port named source
        r_script = urllib.unquote(str(self.forceGetInputFromPort('source', '')))

        # Get the list of input ports so we can get there values
        inputDict = dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])

        # Remove the script and node from the list
        if 'source' in inputDict:
            del(inputDict['source'])
        if 'rpycnode' in inputDict:
            del(inputDict['rpycnode'])

#        for p in self.inputPorts:
#            for conn in self.inputPorts[p]:
#                portType = self.getPortType(p, "input")
#                print "input port %s has type %s"%(p, portType)
#                print "object type %s"%type(inputDict[p])
#                if not portType is None:
#                    if isinstance(inputDict[p], list):
#                        if not isinstance(portType, List) and not isinstance(inputDict[p], portType):
#                            #worklist case
#                            pass

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
                myListArr = numpy.asarray(inputDict[k])
                inputDict[k] = myListArr
            robjects.globalenv[k] = inputDict[k]

        # Execute the script
        try:
            resultVar = r(r_script)
        except:
            raise ModuleError(Rpy2Script, "Could not execute R Script")
        #Converting R result to Python type
        rResult = self.rPyConversion(resultVar)

        outputDict = dict([(k, None) for k in self.outputPorts])

        del(outputDict['self'])
        #assigning converted R result to output port
        for k in outputDict.iterkeys():
            if k in robjects.globalenv.keys() and robjects.globalenv[k] != None:
                    if str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.Dictionary'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'packages.eo4vistrails.tools.utils.Array.NDArray'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.String'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.Integer'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.Float'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.Boolean'>":
                        self.setResult(k, robjects.globalenv[k][0])
                    elif str(self.getPortType(k)) == "<class 'core.modules.vistrails_module.List'>" \
                    or str(self.getPortType(k)) == "<class 'packages.NumSciPy.Array.NDArray'>":
                        if debug:
                            print "setting output numpy array"
                        outArray = NDArray()
                        outArray.set_array(numpy.asarray(robjects.globalenv[k]))
                        self.setResult(k, outArray)
                    elif self.getPortType(k) == type(rResult):
                        self.setResult(k, rResult)
#                   else:
#                       self.setResult(k, robjects.globalenv[k])
        #cleanup robjects mem after we end
        #cleanup pythons mem as well
        import gc
        robjects.r.gc()
        gc.collect()

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
                return numpy.asarray(data)
            elif (isinstance(data, robjects.vectors.FloatVector) or \
                  isinstance(data, robjects.vectors.IntVector) or
                  isinstance(data, robjects.vectors.BoolVector) or \
                  isinstance(data, robjects.vectors.ComplexVector) or \
                  isinstance(data, robjects.vectors.StrVector)) and \
                  (len(data) == 1):
                return data[0]
            elif isinstance(data, rpy2.robjects.vectors.Vector):
                return numpy.asarray(data)
            elif isinstance(data, rpy2.robjects.vectors.DataFrame):
                return data
            elif isinstance(data, rpy2.rinterface.RNULLType):
                return None
            elif isinstance(data, rpy2.robjects.vectors.Array):
                return numpy.asarray(data)
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

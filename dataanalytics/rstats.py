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
# third-party
# vistrails
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget
from packages.eo4vistrails.utils.ModuleHelperMixin import ModuleHelperMixin
# local


@RPyCSafeModule()
class RScript(Script, ModuleHelperMixin):
    """
       Executes a Octave Script
       Writes output to output files and reads input from inout files
    """

    _output_ports = [('self', '(edu.utah.sci.vistrails.basic:Module)')]

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
        if 'rpycnode' in inputDict:
            del(inputDict['rpycnode'])

        #check that if any are NDArrays we get the numpy array out
        for k in inputDict.iterkeys():
            if type(inputDict[k]) == NDArray or \
               str(type(inputDict[k])) == "<netref class 'packages.NumSciPy.Array.NDArray'>":
                inputDict[k] = inputDict[k].get_array()
            robjects.globalenv[k] = inputDict[k]

        #try:
        #Execute the script
        robjects.r(r_script)

        outputDict = dict([(k, None) for k in self.outputPorts])
        del(outputDict['self'])

        for k in outputDict.iterkeys():
            if k in robjects.globalenv.keys() and robjects.globalenv[k] != None:
                if str(self.getPortType(k)) == str(NDArray):
                    print k, robjects.globalenv[k]
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
        displayedComboItems = {'String': True,
                               'Float': True,
                               'Integer': True,
                               'Boolean': True,
                               'Dictionary': True,
                               'Numpy Array': True}
                               #'File':True}

        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "r",
                                                 parent=parent,
                                                 displayedComboItems=displayedComboItems)

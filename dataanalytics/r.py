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
# library
import pickle
from script import Script
from subprocess import call
import urllib
# third-party

# vistrails
from core.modules.vistrails_module import ModuleError, NotCacheable, Module
from core.modules.basic_modules import File
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget


@RPyCSafeModule()
class RScriptExec(Script):
    """
       Executes an R Script passed as arg or runs R code on the fly

    """
    _input_ports = [
    #('inputRFile', '(edu.utah.sci.vistrails.basic:String)')
    ]

    _output_ports = [('self', '(edu.utah.sci.vistrails.basic:Module)')]

    def __init__(self):
        Script.__init__(self)

    def compute(self):
        """Will need to fetch a object on its input port
        Overrides supers method"""
        import scipy.io
        import numpy
        from packages.NumSciPy.Array import NDArray

        r_script = urllib.unquote(str(self.forceGetInputFromPort('source', '')))

        # Lets get the list of input ports so we can get their values
        inputDict = dict([(k, self.getInputFromPort(k))
                          for k in self.inputPorts])

        # Remove the script from the list
        del(inputDict['source'])

        # Check that if any are NDArrays we get the numpy array out
        for k in inputDict.iterkeys():
            if type(inputDict[k]) == NDArray:
                inputDict[k] = inputDict[k].get_array()

        # Write the script out
        self.write_script_to_file(r_script, preScript="", postScript="", suffix='.R')

        args = ["Rscript", self.scriptFileName]
        #args = ["Rscript", directScript]
        a = call(args)  # Execute the script

        if a == 0:
            f = open('workfile.txt', 'wb')
            outputDict = dict([(k, None)
                               for k in self.outputPorts])
            #pickle.dump(outputDict,f)\
            # Pickle the list using the highest protocol available.
            pickle.dump(outputDict, f, -1)
            f.close()

        else:
            raise ModuleError(RScriptExec, "Could not execute Script")


# Dropdown of available datatypes
class RSourceConfigurationWidget(SyntaxSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        displayedComboItems = {'String': True,
                               'Float': True,
                               'Integer': True,
                               'Boolean': True,
                               'Numpy Array': True}
                               #'File':True}

        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "Rscript",
                                                 parent=parent,
                                                 displayedComboItems=displayedComboItems)

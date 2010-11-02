###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation 
## ingestion, pre-processing, transformation, analytic and visualisation 
## capabilities. Included is the abilty to run code transparently in 
## OpenNebula cloud environments. There are various software 
## dependencies, but all are FOSS.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""This module provides a base class for the dataAnalytics.statistics 
An eo4Vistrails statistical computing base class, doing initial argument
parsing. Inherited by all statistical classes
"""

# NOTES
# Calls to 'external' packages like R will be persistent session hosted
# Extends the base class Compute, which splits into this and mathCompute class

import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError

# We'll first create a local alias for the module_registry so that
# we can refer to it in a shorter way. This right?
    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(statsCompute)


class statsCompute (Module):
    def __init__(self):
    # Is this the python constructor?'''
        pass
    
    def compute(self):
    # Starts with a big switch statement usually, to parse the input port args'''
    ''' Below, to be done by classes that inherit this one
      case library call (numpy/scipy, whatever...)
      case R: Have to figure out how to inherit a Session class in python
         if R session running
            send to it
         else // instantiate a Session
            statsSession =  Session(); So easy in C++, sigh...
    '''
       pass

    #Set up input ports for arguments
    #reg.add_input_port(statsModule, bla, bla)

    #Set up output ports
    #reg.add_output_port(statsModule, bla, bla)

# I know nothing about python. Is above right?


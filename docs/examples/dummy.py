# -*- coding: utf-8 -*-
###########################################################################
##
## Copyright (C) 2011 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the abilty to run code transparently in
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
"""This module ???
"""

# library

# third-party

# vistrails
from core.modules.vistrails_module import Module, ModuleError, ModuleErrors
# eo4vistrails
#from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
#from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
# local


#@RPyCSafeModule()
class Dummy(Module):
    """TODO Add class description."""

    _input_ports = [('foo', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('bar', '(edu.utah.sci.vistrails.basic:String)')]

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        self.setResult('bar', result)

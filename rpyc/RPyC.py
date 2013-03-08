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
"""This module provides access to either actual RPyC modules or, if the package
is not available, "dummy" modules that allow other code to continue to work.
"""

from core.modules import basic_modules
from core.modules.vistrails_module import Module
import core.packagemanager


class RPyCModule(Module):
    """
    This forms the basis for ensuring that rpyc-based modules have the correct
    input ports.
    """

    def __init__(self):
        Module.__init__(self)


class RPyCSafeModule():
    """
    RPyCSafeModule executes the compute method on a RPyC node.

    This annotation mixes in the code needed to ensure both threadsafe
    execution and rpyc safe execution.
    """

    def __init__(self, requiredVisPackages=[]):
        pass

    def __call__(self, clazz):
        return clazz


# import either actual, or "dummy" rpyc modules
manager = core.packagemanager.get_package_manager()
if manager.has_package('za.co.csir.rpyc4vistrails'):
    from packages.rpyc4vistrails.RPyC import RPyCModule, RPyCSafeModule
"""
else:
    RPyCModule = _RPyCModule
    RPyCSafeModule = _RPyCSafeModule
"""

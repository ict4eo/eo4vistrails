###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## This full package extends VisTrails, providing GIS/Earth Observation 
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
"""This full package extends VisTrails, providing GIS/Earth Observation 
ingestion, pre-processing, transformation, analytic and visualisation 
capabilities . Included is the abilty to run code transparently in 
OpenNebula cloud environments.
"""

identifier = 'za.co.csir.eo4vistrails.openenbula'
#name = 'eo4vistrails.openenbula'
version = '0.0.1'


def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('owslib'):
        raise core.requirements.MissingRequirement('owslib')

from RPyC import RPyC

import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import core.cache.hasher
from core.modules import module_configure
from core.modules.module_registry import get_module_registry
from core.modules import port_configure
from core.modules import vistrails_module
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
from core.modules.python_source_configure import PythonSourceConfigurationWidget
from core.modules.tuple_configuration import TupleConfigurationWidget, \
    UntupleConfigurationWidget
from core.modules.constant_configuration import StandardConstantWidget, \
    PathChooserWidget, FileChooserWidget, DirectoryChooserWidget, ColorWidget, \
    ColorChooserButton, BooleanWidget
from core.system import vistrails_version
from core.utils import InstanceObject
from core.modules.paramexplore import make_interpolator, \
     QFloatLineEdit, QIntegerLineEdit, FloatLinearInterpolator, \
     IntegerLinearInterpolator
from PyQt4 import QtGui

import core.system
from itertools import izip
import os
import os.path
try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new
import zipfile
import urllib
import sys


###############################################################################
# the function initialize is called for each package, after all
# packages have been loaded. It is used to register the module with
# the VisTrails runtime.

def initialize(*args, **keywords):

    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()

    # VisTrails cannot currently automatically detect your derived
    # classes, and the ports that they support as input and
    # output. Because of this, you as a module developer need to let
    # VisTrails know that you created a new module. This is done by calling
    # function addModule:
    reg.add_module(RPyC,
                    configureWidgetType=PythonSourceConfigurationWidget)

    reg.add_input_port(RPyC, 'rPyCServer', (core.modules.basic_modules.String, 
                                            'The RPyC Server IP'))    
    reg.add_input_port(RPyC, 'source', core.modules.basic_modules.String, True)    
    reg.add_output_port(RPyC, 'self', core.modules.basic_modules.Module)

    reg.add_module(RPyCDiscover)
    reg.add_output_port(RPyCDiscover, "RPyCSlaves",
                     (core.modules.basic_modules.Tuple, 'RPyCSlaves'))


    # In a similar way, you need to report the ports the module wants
    # to make available. This is done by calling addInputPort and
    # addOutputPort appropriately. These calls only show how to set up
    # one-parameter ports. We'll see in later tutorials how to set up
    # multiple-parameter plots.
    reg.add_module(OneAbstract)
    reg.add_input_port(OneAbstract, "server",
                     (core.modules.basic_modules.String, 'OpenNebula Server Name'))
    reg.add_input_port(OneAbstract, "username",
                     (core.modules.basic_modules.String, 'UserName'))
    reg.add_input_port(OneAbstract, "password",
                     (core.modules.basic_modules.String, 'PassWord'))
    reg.add_output_port(OneAbstract, "stdout",
                     (core.modules.basic_modules.List, 'StdOut'))
    reg.add_output_port(OneAbstract, "stderr",
                     (core.modules.basic_modules.List, 'StdErr'))                     
    
    reg.add_module(OneCmd)
    reg.add_input_port(OneCmd, "operation",
                     (core.modules.basic_modules.String, 'The Operation'))

    reg.add_module(OneVM_List)
    reg.add_output_port(OneAbstract, "VM List",
                     (core.modules.basic_modules.List, 'StdErr'))
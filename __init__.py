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
## Authors:
    # Terence van Zyl (tvanzyl)
    # Graeme McFerren (gmcferren)
    # Bheki C'wele (bcwele)
    # Derek Hohls (dhohls)
    # Petrus Shabangu (pshabangu)
    # Bolelang Sibolla (bsibolla)
    # Mugu Mtsetfwa (mmtsetfwa)
############################################################################
"""This full package extends VisTrails, providing GIS/Earth Observation
ingestion, pre-processing, transformation, analytic and visualisation
capabilities.

Also included is the ability to run code transparently in OpenNebula cloud
environments.
"""
identifier = 'za.co.csir.eo4vistrails'
name = 'EO4VisTrails'
revision = 7
version = '0.1.%s' % revision
author_list = 'tvanzyl,gmcferren,bcwele,dhohls,pshabangu,bsibolla,mmtsetfwa'
flags = {}

import sys
import os.path
#import resource - LINUX specific; causes error under Windows
from core.system import packages_directory

# BELOW CAUSES ERROR IN Sphinx documentation
sys.path = [os.path.join(packages_directory(), 'eo4vistrails/lib')] + sys.path
# BELOW CAUSES ERROR - TODO - check under Windows and Linux
# resource.setrlimit(resource.RLIMIT_NOFILE,(resource.getrlimit(
#  resource.RLIMIT_NOFILE)[1], 4096))


def set_flag(module_name):
    """Set a flag if a module is missing."""
    flags[module_name] = False


def package_requirements():
    import core.requirements
    # WARNING
    if not core.requirements.python_module_exists('owslib'):
        print "%s is missing" % 'owslib'  # ??? still true
    # MUST EXIST
    if not core.requirements.python_module_exists('qgis'):
        raise core.requirements.MissingRequirement('qgis')
    if not core.requirements.python_module_exists('osgeo'):
        raise core.requirements.MissingRequirement('osgeo')
    if not core.requirements.python_module_exists('numpy'):
        raise core.requirements.MissingRequirement('numpy')
    # OPTIONAL (test in local init files to ensure that modules are not activated)
    if not core.requirements.python_module_exists('psycopg2'):
        set_flag('psycopg2')
    if not core.requirements.python_module_exists('pysal'):
        set_flag('pysal')
    if not core.requirements.python_module_exists('rpyc'):
        set_flag('rpyc')
    if not core.requirements.python_module_exists('octave'):
        set_flag('octave')
    if not core.requirements.python_module_exists('rpy2stats'):
        set_flag('rpy2stats')
    if not core.requirements.python_module_exists('pyDAP'):
        set_flag('pyDAP')
    if not core.requirements.python_module_exists('netcdf4'):
        set_flag('netcdf4')
    if not core.requirements.python_module_exists('xlrd'):
        set_flag('xlrd')
    if not core.requirements.python_module_exists('xlwt'):
        set_flag('xlwt')

    #if not core.requirements.python_module_exists('qtermwidget'):
    #    raise core.requirements.MissingRequirement('qtermwidget')


def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('za.co.csir.rpyc4vistrails'):
        return ['za.co.csir.rpyc4vistrails',
                'edu.utah.sci.vistrails.spreadsheet',
                'edu.utah.sci.vistrails.numpyscipy',
                'edu.utah.sci.vistrails.control_flow']
    else:
        return ['edu.utah.sci.vistrails.spreadsheet',
                'edu.utah.sci.vistrails.numpyscipy',
                'edu.utah.sci.vistrails.control_flow']

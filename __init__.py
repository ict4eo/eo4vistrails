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
"""This full package extends VisTrails, providing GIS/Earth
Observation ingestion, pre-processing, transformation,
analytic and visualisation capabilities.

Also included is the ability to run code transparently in
OpenNebula cloud environments.
"""
# Authors:
    # Terence van Zyl
    # Graeme McFerren
    # Bheki C'wele
    # Derek Hohls
    # Petrus Shabangu
    # Bolelang Sibolla

identifier = 'za.co.csir.eo4vistrails'
name = 'eo4vistrails'
version = '0.1.0'
author_list = 'tvanzyl,bcwele,gmcferren,dhohls,pshabangu,bsibolla'


def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('owslib'):
        raise core.requirements.MissingRequirement('owslib')
    if not core.requirements.python_module_exists('qgis'):
        raise core.requirements.MissingRequirement('qgis')
    if not core.requirements.python_module_exists('psycopg2'):
        raise core.requirements.MissingRequirement('psycopg2')
    if not core.requirements.python_module_exists('pysal'):
        raise core.requirements.MissingRequirement('pysal')
    if not core.requirements.python_module_exists('networkx'):
        raise core.requirements.MissingRequirement('networkx')
    if not core.requirements.python_module_exists('numpy'):
        raise core.requirements.MissingRequirement('numpy')
    if not core.requirements.python_module_exists('rpyc'):
        raise core.requirements.MissingRequirement('rpyc')
    if not core.requirements.python_module_exists('osgeo'):
        raise core.requirements.MissingRequirement('osgeo')


def package_dependencies():
    return ['edu.utah.sci.vistrails.spreadsheet',
            'edu.utah.sci.vistrails.numpyscipy']
#    import core.packagemanager
#    manager = core.packagemanager.get_package_manager()
#    if manager.has_package('edu.utah.sci.vistrails.spreadsheet'):
#        return ['edu.utah.sci.vistrails.spreadsheet']
#    else:
#        return []

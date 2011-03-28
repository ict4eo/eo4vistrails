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
version = '0.0.1'
author_list = 'tvanzyl,bcwele'

def package_dependencies():
    return ['edu.utah.sci.vistrails.spreadsheet','edu.utah.sci.vistrails.numpyscipy']
#    import core.packagemanager
#    manager = core.packagemanager.get_package_manager()
#    if manager.has_package('edu.utah.sci.vistrails.spreadsheet'):
#        return ['edu.utah.sci.vistrails.spreadsheet']
#    else:
#        return []

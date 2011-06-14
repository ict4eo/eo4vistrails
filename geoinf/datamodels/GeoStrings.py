###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
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
"""This abstract module provides string specialisations that allow modules to
understand what kind of data is being passed into a method as a string.
"""
from core.modules import basic_modules
from core.modules.source_configure import SourceConfigurationWidget
GeoString = basic_modules.new_constant('GeoString',
                                        staticmethod(str),
                                        None,
                                        staticmethod(lambda x: type(x) == str),
                                        None)


class GMLString(GeoString):
    pass


class GeoJSONString(GeoString):
    pass
    #TODO:  this needs to be upgraded to 1.6.1 to take advantage of the ability
    #       to specify the  port which receives the output


class GeoStringConfigurationWidget(SourceConfigurationWidget):
    """TODO Add doc string"""

    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, None,
                                           False, False, parent)

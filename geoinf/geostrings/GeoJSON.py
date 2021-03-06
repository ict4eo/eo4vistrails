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
"""This module holds a GeoJSON type that can be passed around between modules.
"""
# library
# third-party
from geojson import Feature
# vistrails
from core.modules.vistrails_module import Module
# eo4vistrails


class GeoJSONModule(Module):
    """TOD: Write docstring."""
    pass


class GJFeature(GeoJSONModule, Feature):
    """ Container class for the geojson.Feature class."""

    def __init__(self):
        Module.__init__(self)
        Feature.__init__(self)

    def compute(self):
        self.feature = self.forceGetInputFromPort('feature')
        self.setResult("value", self)

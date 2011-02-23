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
"""
Created on Wed Feb 23 10:08:10 2011

@author: dhohls

Module forms part of the vistrails capabilties, used to add geojson data holding
capacity to vistrails.

This Module holds a geojson type that can be passed around between modules.

"""
#History
#Derek Hohls, 23 Feb 2011, Version 0.1.1

from core.modules.vistrails_module import Module

class GeoJSONModule(object):
    pass

import geojson

class GJFeature(GeoJSONModule, Module, geojson.Feature):
    """ Container class for the geojson.Feature class """
    def __init__(self):
        Module.__init__(self)
        geojson.Feature.__init__(self)

    def compute(self):
        self.feature = self.forceGetInputFromPort('feature')
        self.setResult("value", self)

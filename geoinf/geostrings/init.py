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
"""This module is the called by higher level inits to ensure that registration
with VisTrails takes place
"""


def initialize(*args, **keywords):
    """
    Set everything up for vistrails; called from the top level initialize
    """
    import os
    # third party
    import qgis.core
    # vistrails
    from core.modules.module_registry import get_module_registry
    from core.modules.basic_modules import String, File
    # eo4vistrails

    # local
    from GeoStrings import GMLString, GeoJSONString, GeoString, WKTString, \
        GeoStringConstantWidget, Proj4String

    # Vistrails
    reg = get_module_registry()
    mynamespace = "data|geostrings"

    # GeoString
    reg.add_module(GeoString,
                   namespace=mynamespace,
                   abstract=True)
    reg.add_module(GMLString,
                   configureWidgetType=GeoStringConstantWidget,
                   namespace=mynamespace)
    reg.add_module(GeoJSONString,
                   configureWidgetType=GeoStringConstantWidget,
                   namespace=mynamespace)
    reg.add_module(WKTString,
                   configureWidgetType=GeoStringConstantWidget,
                   namespace=mynamespace)

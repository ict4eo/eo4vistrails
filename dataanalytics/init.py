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
"""This module forms part of the rpyc vistrails capabilties, and is used to add
multicore parallel and distributed processing to VisTrails.
"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

#Input ports
dataSlice = "dataSlice"
url = "url"
nc4File = "nc4File"
varName = "varName"
dimLimits = "dimLimits"


def initialize(*args, **keywords):
    """Called by higher level inits to ensure that registration with
    VisTrails takes place."""
    from core.modules.module_registry import get_module_registry
    import PySAL

    reg = get_module_registry()
    mynamespace = "pysal"

    #Add PySAL
    reg.add_module(PySAL.W,
                   namespace=mynamespace)

    import Rasterlang
    mynamespace = "rasterlang"

    #Add Rasterlang
    reg.add_module(Rasterlang.GDALFormatComboBox,
                   namespace=mynamespace,
                   abstract=True)
    reg.add_module(Rasterlang.RasterPrototype,
                   name="Raster Prototype",
                   namespace=mynamespace)
    reg.add_module(Rasterlang.layerAsArray,
                   name="Layer As Array",
                   namespace=mynamespace)
    reg.add_module(Rasterlang.SaveArrayToRaster,
                   name="Save Array To Raster",
                   namespace=mynamespace)
    reg.add_module(Rasterlang.arrayAsLayer,
                   name="Array As Layer",
                   namespace=mynamespace)
    reg.add_module(Rasterlang.RasterLang,
                   name="RasterLang",
                   configureWidgetType=Rasterlang.RasterSourceConfigurationWidget,
                   namespace=mynamespace)

    #TODO: Move Networkx to own package
    #import Networkx
    #mynamespace = "networkx"

     #Add Networkx
    #reg.add_module(Networkx.Graph,
    #               namespace=mynamespace)

    #reg.add_module(Networkx.connected_components,
    #               namespace=mynamespace)

    import script
    mynamespace = "utils"
    reg.add_module(script.Script,
                   name="Script",
                   namespace=mynamespace,
                   abstract=True)

    #TODO: Move povray to own package
    #import povray
    #mynamespace = "povray"
    #reg.add_module(povray.PovRayScript,
    #               name="povRay Script",
    #               namespace=mynamespace,
    #               configureWidgetType=povray.PovRaySourceConfigurationWidget)
    #reg.add_module(povray.PovRayConfig,
    #               name="povRay Config",
    #               namespace=mynamespace)

    import octave
    mynamespace = "octave"
    reg.add_module(octave.OctaveScript,
                   name="Octave Script",
                   namespace=mynamespace,
                   configureWidgetType=octave.OctaveSourceConfigurationWidget)

    import rpy2Stats
    mynamespace = "r"
    reg.add_module(rpy2Stats.Rpy2Script,
                   name="Rpy2 Script",
                   namespace=mynamespace,
                   configureWidgetType=rpy2Stats.RSourceConfigurationWidget)

    import pyDAP
    mynamespace = "pyDAP"
    reg.add_module(pyDAP.pyDAP,
                   name="pyDAP Client",
                   namespace=mynamespace,
                   configureWidgetType=pyDAP.pyDAPConfigurationWidget)

    import netcdf4
    mynamespace = "netcdf4"
    reg.add_module(netcdf4.netcdf4Reader,
                   name="netcdf4 Client",
                   namespace=mynamespace,
                   configureWidgetType=netcdf4.netcdf4ConfigurationWidget)

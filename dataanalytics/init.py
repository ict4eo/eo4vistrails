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
"""This module forms part of the eo4vistrails capabilties, and is used to add
data analytics (including scripting) to VisTrails.
"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

#Input ports
dataSlice = "dataSlice"
url = "url"
nc4File = "nc4File"
varName = "varName"
dimLimits = "dimLimits"


def missing(package_name, module_name):
    print "WARNING: %s package not installed; %s Module disabled" % \
        (package_name, module_name)


def initialize(*args, **keywords):
    """Called by higher level inits to ensure that registration with
    VisTrails takes place."""
    from core.modules.module_registry import get_module_registry
    import core.requirements
    from core.modules import basic_modules

    reg = get_module_registry()

    if core.requirements.python_module_exists('pysal'):
        import PySAL
        pysal_namespace = "scripting|pysal"
        #Add PySAL
        reg.add_module(PySAL.W,
                       namespace=pysal_namespace)
    else:
        missing('pysal', 'PySAL')

    import Rasterlang
    raster_namespace = "scripting|raster"

    #Add RasterlangCode
    reg.add_module(Rasterlang.RasterLangCode,
                   namespace=raster_namespace,
                   abstract=True)
    reg.add_input_port(Rasterlang.RasterLangCode, 'source',
                        basic_modules.String)
    reg.add_output_port(Rasterlang.RasterLangCode, 'self',
                        basic_modules.Module)

    #Add Rasterlang
    reg.add_module(Rasterlang.GDALFormatComboBox,
                   namespace=raster_namespace,
                   abstract=True)
    reg.add_module(Rasterlang.RasterPrototype,
                   name="RasterPrototype",
                   namespace=raster_namespace)
    reg.add_module(Rasterlang.layerAsArray,
                   name="LayerAsArray",
                   namespace=raster_namespace)
    reg.add_module(Rasterlang.SaveArrayToRaster,
                   name="SaveArrayToRaster",
                   namespace=raster_namespace)
    reg.add_module(Rasterlang.arrayAsLayer,
                   name="ArrayAsLayer",
                   namespace=raster_namespace)
    reg.add_module(Rasterlang.RasterLang,
                   name="RasterLang",
                   configureWidgetType=Rasterlang.RasterSourceConfigurationWidget,
                   namespace=raster_namespace)

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
    #pov_namespace = "povray"
    #reg.add_module(povray.PovRayScript,
    #               name="povRay Script",
    #               namespace=pov_namespace,
    #               configureWidgetType=povray.PovRaySourceConfigurationWidget)
    #reg.add_module(povray.PovRayConfig,
    #               name="povRay Config",
    #               namespace=pov_namespace)

    import octave
    octave_namespace = "scripting|octave"
    reg.add_module(octave.OctaveScript,
                   name="OctaveScript",
                   namespace=octave_namespace,
                   configureWidgetType=octave.OctaveSourceConfigurationWidget)

    if core.requirements.python_module_exists('rpy2'):
        import rpy2Stats
        r_namespace = "scripting|r"
        reg.add_module(rpy2Stats.Rpy2Script,
                       name="Rpy2Script",
                       namespace=r_namespace,
                       configureWidgetType=rpy2Stats.RSourceConfigurationWidget)
    else:
        missing('rpy2', 'Rpy2Script')

    if core.requirements.python_module_exists('pydap'):
        import pyDAP
        pydap_namespace = "data|datacube"
        reg.add_module(pyDAP.pyDAP,
                       name="pyDAPClient",
                       namespace=pydap_namespace,
                       configureWidgetType=pyDAP.pyDAPConfigurationWidget)
    else:
        missing('pydap', 'pyDAPClient')

    if core.requirements.python_module_exists('netCDF4'):
        import netcdf4
        netcdf_namespace = "data|datacube"
        reg.add_module(netcdf4.netcdf4Reader,
                       name="netcdf4Client",
                       namespace=netcdf_namespace,
                       configureWidgetType=netcdf4.netcdf4ConfigurationWidget)
    else:
        missing('netCDF4', 'netcdf4Client')

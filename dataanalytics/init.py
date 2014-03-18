# -*- coding: utf-8 -*-
############################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
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

from core.bundles import py_import
from core import debug

"""This auto-import does not work because net NOT in Ubuntu repo: March 2013"""
try:
    pkg_dict = {'linux-ubuntu': 'python-networkx',
                'linux-fedora': 'python-networkx'}
    Networkx = py_import('networkx', pkg_dict)
except Exception, e:
    debug.critical("Exception: %s" % e)


"""This auto-import does not work because pydap NOT in Ubuntu repo: March 2013
try:
    pkg_dict = {'linux-ubuntu': 'python-pydap',
                'linux-fedora': 'python-pydap'}
    pydap = py_import('pydap', pkg_dict)
except Exception, e:
    debug.critical("Exception: %s" % e)
"""

"""This auto-import does not work because netCDF4 NOT in Ubuntu repo: March 2013
try:
    pkg_dict = {'linux-ubuntu': 'python-netCDF4',
                'linux-fedora': 'python-netCDF4'}
    netCDF4 = py_import('netCDF4', pkg_dict)
except Exception, e:
    debug.critical("Exception: %s" % e)
"""

"""This auto-import does not work because pysal NOT in Ubuntu repo: March 2013
try:
    pkg_dict = {'linux-ubuntu': 'python-pysal',
                'linux-fedora': 'python-pysal'}
    pysal = py_import('pysal', pkg_dict)
except Exception, e:
    debug.critical("Exception: %s" % e)
"""

#Input ports
dataSlice = "dataSlice"
url = "url"
ncFile = "ncFile"
varName = "varName"
dimLimits = "dimLimits"


def missing(package_name, module_name):
    print "WARNING: %s package not installed; %s Module disabled" % \
        (package_name, module_name)


def warning(package_name, module_name):
    print "WARNING: %s package not installed; %s Module has reduced functionality" % \
        (package_name, module_name)


def initialize(*args, **keywords):
    """Called by higher level inits to ensure that registration with
    VisTrails takes place."""
    from core.modules.module_registry import get_module_registry
    import core.requirements
    from core.modules import basic_modules

    reg = get_module_registry()

    if core.requirements.python_module_exists('pysal'):
        import PySAL  # filename of Vistrails module
        pysal_namespace = "scripting|pysal"
        #Add PySAL
        reg.add_module(PySAL.W,
                       namespace=pysal_namespace)
    else:
        missing('pysal', 'PySAL')

    import Rasterlang  # filename of Vistrails module
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

    import script  # filename of Vistrails module
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
        try:
            from rpy2 import robjects  # test if R (R_HOME) installed/defined
            import rpy2Stats  # filename of Vistrails module
            r_namespace = "scripting|r"
            reg.add_module(rpy2Stats.Rpy2Script,
                       name="Rpy2Script",
                       namespace=r_namespace,
                       configureWidgetType=rpy2Stats.RSourceConfigurationWidget)
        except ImportError:
            missing('R', 'Rpy2Script')
        except RuntimeError:
            missing('R', 'Rpy2Script')
    else:
        missing('rpy2', 'Rpy2Script')

    if core.requirements.python_module_exists('pydap'):
        import pyDAP  # filename of Vistrails module
        pydap_namespace = "data|datacube"
        reg.add_module(pyDAP.pyDAP,
                       name="pyDAPClient",
                       namespace=pydap_namespace,
                       configureWidgetType=pyDAP.pyDAPConfigurationWidget)
    else:
        missing('pydap', 'pyDAPClient')

    if not core.requirements.python_module_exists('netCDF4'):
        warning('netCDF4', 'netcdfClient')
    # module still usable with fallback to scipy reader (only ver. 3 format)
    import netcdf4  # filename of Vistrails module
    netcdf_namespace = "data|datacube"
    reg.add_module(netcdf4.netcdf4Reader,
                   name="netcdfClient",
                   namespace=netcdf_namespace,
                   configureWidgetType=netcdf4.netcdf4ConfigurationWidget)

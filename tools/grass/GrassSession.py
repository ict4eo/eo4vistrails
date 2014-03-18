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
"""This module provides a Session object for defining a connection to GRASS.
It defines a temporary GRASS location on either a local or cloud machine. It
also defines and maintains a list of the layers available.

Also see:
*   `<http://grass.osgeo.org/programming6/pythonlib.html>`_
*   `<http://grass.osgeo.org/wiki/GRASS_and_Python>`_
"""
#export GISBASE="/usr/local/grass-6.4.svn/"
#export PATH="$PATH:$GISBASE/bin:$GISBASE/scripts"
#export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$GISBASE/lib"
## for parallel session management, we use process ID (PID) as lock file number
#export GIS_LOCK=$$
## path to GRASS settings file
#export GISRC="$HOME/.grassrc6"

# library
# third-party
# vistrails
from vistrails.packages.eo4vistrails.tools.utils.session import Session
# eo4vistrails
from vistrails.packages.eo4vistrails.geoinf.SpatialTemporalConfigurationWidget import \
    SpatialTemporalConfigurationWidget
# local


class GrassSession(Session):
    """TO DO - add docstring"""
    def __init__(self):
        self.layers = {'vector': [], 'raster': []}

    def compute(self):
        pass

    def updateLayers(self, layername, layertype):
        """Updates info on layers available in current GRASS location
        requires a string for the layername and a string, one of{'v', 'r'}
        to denote the type"""
        if layername.lower() == 'v':
            self.layers['vector'].append(layername)
        if layername.lower() == 'r':
            self.layers['raster'].append(layername)

    def readLayers(self, layertype):
        """Reads info on layers available in current GRASS location
        requires a string for the layername and a string, one of{'v', 'r'}
        to denote the type"""
        if layername.lower() == 'v':
            return tuple(self.layers['vector'])
        if layername.lower() == 'r':
            return tuple(self.layers['raster'])


class GrassSessionConfigurationWidget(SpatialTemporalConfigurationWidget):
    """TO DO - add docstring"""
    def __init__(self):
        pass

    """TO DO - add docstring"""
    def compute(self):
        pass


def initialize(*args, **keywords):
    """Add module to the VisTrails registry."""
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(GrassSession)

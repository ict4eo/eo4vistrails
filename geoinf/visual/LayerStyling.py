# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
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
"""This package provides GIS capabilities for eo4vistrails.
This module provides a means for styling QGIS Map Layers.
"""

# library
# third party
import qgis.core
import qgis.gui
from PyQt4 import QtCore, QtGui
# vistrails
from core.modules.basic_modules import File, String, Boolean
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError, NotCacheable, \
                                          InvalidOutput
import core.system
# eo4vistrails
from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsVectorLayer,\
    QgsRasterLayer
import packages.eo4vistrails.geoinf.visual
from packages.eo4vistrails.geoinf.datamodels.TemporalVectorLayer import \
    TemporalVectorLayer
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin


class LayerStyling(Module):
    """Provide common routines and data for all styling modules."""

    def RGBToHTMLColor(self, rgb_tuple):
        """Convert an (R,G,B) tuple with floating point values to #RRGGBB """
        int_tuple = (int(rgb_tuple[0] * 255),
                     int(rgb_tuple[1] * 255),
                     int(rgb_tuple[2] * 255))
        hexcolor = '#%02x%02x%02x' % int_tuple
        # that's it! '%02x' means zero-padded, 2-digit hex values
        return hexcolor

    def compute(self):
        pass


class VectorLayerStyling(LayerStyling):
    """Provides styling options for a vector layer.

    Input ports:
        vector_layer:
            the layer to be styled
        layer_name:
            the display name for the layer
        opacity:
            the percentage transparency for the layer (100 is no transparency)
        fill_color:
            the color with which to fill the layer

    See also:
        http://www.qgis.org/pyqgis-cookbook/vector.html
    """

    def compute(self):
        vector_layer = self.getInputFromPort('vector_layer')
        opacity = self.forceGetInputFromPort('opacity', 100)
        layer_name = self.forceGetInputFromPort('name', None)
        rgb_fill_color = self.forceGetInputFromPort('fill_color', None)
        if rgb_fill_color:
            symbol_color = self.RGBToHTMLColor(rgb_fill_color.tuple)
        else:
            symbol_color = (0.0, 0.0, 0.0)
        symbol_opacity = min(100, max(0, opacity)) / 100.0

        # assumes QGIS > 1.4 (start of usage of RendererV2)
        layer_symbol = qgis.core.QgsSymbolV2.defaultSymbol(
            vector_layer.geometryType())
        # set symbol properties
        layer_symbol.setColor(QtGui.QColor(symbol_color))
        layer_symbol.setAlpha(symbol_opacity)
        # TODO - find a way to add fill styling; might be different for point/line/poly
        # set layer renderer
        renderer_V2 = qgis.core.QgsSingleSymbolRendererV2(layer_symbol)
        vector_layer.setRendererV2(renderer_V2)
        # layer props
        if layer_name:
            vector_layer.setLayerName(layer_name)

        self.setResult('vector_layer', vector_layer)


class RasterLayerStyling(LayerStyling):
    """Provides styling options for a raster layer.

    See:
        http://www.qgis.org/pyqgis-cookbook/raster.html
    """

    def compute(self):
        raster_layer = self.getInputFromPort('raster_layer')
        #TO DO - create ports; read values; style layer
        self.setResult('raster_layer', raster_layer)

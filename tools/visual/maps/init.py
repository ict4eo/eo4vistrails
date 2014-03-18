###########################################################################
##
## Copyright (C) 2011 CSIR Meraka Institute. All rights reserved.
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


def initialize(*args, **keywords):
    """TO DO: Add doc string"""

    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules

    from packages.spreadsheet import basic_widgets

    from vistrails.packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsMapLayer,\
        QgsVectorLayer, QgsRasterLayer
    from vistrails.packages.eo4vistrails.geoinf.datamodels.TemporalVectorLayer import \
        TemporalVectorLayer
    from vistrails.packages.eo4vistrails.tools.visual.maps.QGISMapCanvasCell import \
        QGISMapCanvasCell
    from vistrails.packages.eo4vistrails.tools.visual.maps.SOSMobile import SOSMobile
    from vistrails.packages.eo4vistrails.tools.visual.maps.LayerStyling import \
        LayerStyling, VectorLayerStyling, RasterLayerStyling, \
        QgsRasterLayerDrawingStyleComboBox

    reg = get_module_registry()
    mynamespace = 'visualisation|maps'

    # ==========================================================================
    # Abstract Modules - these MUST appear FIRST
    # ==========================================================================

    reg.add_module(LayerStyling,
                   namespace=mynamespace,
                   abstract=True)

    # abstract modules - drop-down lists
    reg.add_module(QgsRasterLayerDrawingStyleComboBox,
                   namespace=mynamespace,
                   abstract=True)

    # ==========================================================================
    # Standard Modules - without ports OR with locally defined ports
    # ==========================================================================

    #MapCanvas
    reg.add_module(QGISMapCanvasCell, namespace=mynamespace)
    reg.add_input_port(QGISMapCanvasCell, 'baselayer', (QgsMapLayer,
                       'The base layer from which the CRS is derived.'))
    reg.add_input_port(QGISMapCanvasCell, 'layer', (QgsMapLayer,
                       'Other layers appearing on the canvas'))
    reg.add_input_port(QGISMapCanvasCell, 'Location',
                       basic_widgets.CellLocation)
    reg.add_output_port(QGISMapCanvasCell, 'self', QGISMapCanvasCell)  # ControlFlow

    #SOSMobile
    reg.add_module(SOSMobile, namespace=mynamespace)
    reg.add_input_port(SOSMobile, 'temporal_vector_layer',
                       TemporalVectorLayer)
    reg.add_input_port(SOSMobile, 'mobile_format',
                       basic_modules.String)
    reg.add_output_port(SOSMobile, 'temporal_vector_layer',
                        TemporalVectorLayer)

    #VectorLayerStyling
    reg.add_module(VectorLayerStyling, namespace=mynamespace)

    #RasterLayerStyling
    reg.add_module(RasterLayerStyling, namespace=mynamespace)

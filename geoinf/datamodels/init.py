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
    from packages.eo4vistrails.utils.WebRequest import WebRequest, DataRequest
    from packages.eo4vistrails.geoinf.datamodels.FeatureImport import \
        FeatureImport, FeatureImportConfigurationWidget
    from packages.eo4vistrails.geoinf.datamodels.RasterImport import \
        RasterImport, RasterImportConfigurationWidget
    # local
    from Feature import FeatureModel, FileFeatureModel, MemFeatureModel
    from Raster import RasterModel
    from GeoStrings import GMLString, GeoJSONString, GeoString,  WKTString, \
        GeoStringConstantWidget, Proj4String
    from TemporalVectorLayer import TemporalVectorLayer
    import QgsLayer
    import QgsLayerWriter

    # QGIS
    # export set PYTHONPATH=/usr/lib/python2.6
    # Environment variable QGISHOME must be set to the install directory
    # before running this application
    qgis_prefix = "/usr"  # os.getenv("QGISHOME")  # TO DO - add to install
    qgis.core.QgsApplication.setPrefixPath(qgis_prefix, True)
    qgis.core.QgsApplication.initQgis()

    # Vistrails
    reg = get_module_registry()
    mynamespace = "data"

    # Features
    reg.add_module(FeatureModel,
                   namespace=mynamespace,
                   abstract=True)  # abstract
    #reg.add_module(FeatureImport,
    #               configureWidgetType=FeatureImportConfigurationWidget,
    #               namespace="broken")

    # EPSG Code Constant
    reg.add_module(QgsLayer.EPSGCode,
                   namespace=mynamespace)

    # QgsMapLayer
    reg.add_module(QgsLayer.QgsMapLayer,
                   namespace=mynamespace,
                   abstract=True)
    reg.add_input_port(QgsLayer.QgsMapLayer, "file", File)
    reg.add_input_port(QgsLayer.QgsMapLayer, "datarequest", DataRequest)
    #reg.add_output_port(QgsLayer.QgsMapLayer, "value", QgsLayer.QgsMapLayer)

    # QgsLayers

    # ... vector
    reg.add_module(QgsLayer.QgsVectorLayer,
                   name="Vector Layer",
                   namespace=mynamespace)
    reg.add_output_port(QgsLayer.QgsVectorLayer, "value",
                        QgsLayer.QgsVectorLayer)

    # ... raster
    reg.add_module(QgsLayer.QgsRasterLayer,
                   name="Raster Layer",
                   namespace=mynamespace)
    reg.add_output_port(QgsLayer.QgsRasterLayer, "value",
                        QgsLayer.QgsRasterLayer)

    # ... temporal
    reg.add_module(TemporalVectorLayer,
                   name="Temporal Vector Layer",
                   namespace=mynamespace)
    reg.add_output_port(TemporalVectorLayer, "value",
                        TemporalVectorLayer)

    # QgsLayerWriter
    reg.add_module(QgsLayerWriter.QgsLayerWriter,
                   namespace=mynamespace)
    reg.add_input_port(QgsLayerWriter.QgsLayerWriter, "value",
                       QgsLayer.QgsVectorLayer)
    reg.add_input_port(QgsLayerWriter.QgsLayerWriter, "file",
                       File)

    # misc.
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

    # MemFeatureModel
    reg.add_module(MemFeatureModel,
                   namespace=mynamespace,
                   abstract=True)
    reg.add_input_port(MemFeatureModel, "source_file", String)
    reg.add_input_port(MemFeatureModel, "dbconn", String)
    reg.add_input_port(MemFeatureModel, "sql", String)
    reg.add_input_port(MemFeatureModel, "webrequest", WebRequest)
    reg.add_input_port(MemFeatureModel, "gstring", GeoString)
    reg.add_output_port(MemFeatureModel, "feature_dataset", MemFeatureModel)

    # FileFeatureModel
    reg.add_module(FileFeatureModel,
                   name="OGR Transform",
                   namespace=mynamespace)
    reg.add_input_port(FileFeatureModel, "source_file", String)
    reg.add_input_port(FileFeatureModel, "source_feature_dataset",
                       MemFeatureModel)
    reg.add_input_port(FileFeatureModel, "webrequest", WebRequest)
    reg.add_input_port(FileFeatureModel, "output_type", String)

    # RasterModel
    reg.add_module(RasterModel,
                   namespace=mynamespace,
                   abstract=True)  # abstract
    reg.add_module(RasterImport,
                   configureWidgetType=RasterImportConfigurationWidget,
                   namespace=mynamespace)

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
    import numpy
    import os
    # third party
    import qgis.core
    # vistrails
    from core.modules.module_registry import get_module_registry
    from core.modules.basic_modules import Boolean, String, File, Variant, Integer
    # eo4vistrails
    from vistrails.packages.eo4vistrails.geoinf.datamodels.FeatureImport import \
        FeatureImport, FeatureImportConfigurationWidget
    from vistrails.packages.eo4vistrails.geoinf.datamodels.RasterImport import \
        RasterImport, RasterImportConfigurationWidget
    from vistrails.packages.eo4vistrails.geoinf.geostrings.GeoStrings import GeoString
    from vistrails.packages.eo4vistrails.tools.utils.Array import NDArrayEO
    # local
    from DataRequest import DataRequest
    from Feature import FeatureModel, FileFeatureModel, MemFeatureModel
    from Raster import RasterModel
    from TemporalVectorLayer import TemporalVectorLayer
    from WebRequest import WebRequest
    import QgsLayer
    import QgsLayerWriter
    from PostGISRequest import PostGISRequest

    # QGIS
    # export set PYTHONPATH=/usr/lib/python2.6
    # Environment variable QGISHOME must be set to the install directory
    # before running this application
    qgis_prefix = "/usr"  # os.getenv("QGISHOME")  # TO DO - add to install
    qgis.core.QgsApplication.setPrefixPath(qgis_prefix, True)
    qgis.core.QgsApplication.initQgis()

    # Vistrails
    reg = get_module_registry()
    data_namespace = "data"
    metadata_namespace = "data|metadata"

    # =========================================================================
    # Abstract Modules - these MUST appear FIRST
    # =========================================================================

    reg.add_module(DataRequest,
                   namespace=data_namespace,
                   abstract=True)

    # Features
    reg.add_module(FeatureModel,
                   namespace=data_namespace,
                   abstract=True)  # abstract
    #reg.add_module(FeatureImport,
    #               configureWidgetType=FeatureImportConfigurationWidget,
    #               namespace="broken")

    # EPSG Code Constant
    reg.add_module(QgsLayer.EPSGCode,
                   namespace=metadata_namespace)

    # =========================================================================
    # Standard Modules - Ports defined here
    # =========================================================================

    # WebRequest
    reg.add_module(WebRequest,
                   namespace=data_namespace)
    reg.add_input_port(
        WebRequest,
        'request',
        (WebRequest, 'WebRequest'))
    reg.add_input_port(
        WebRequest,
        'runRequest',
        (Boolean, 'Run The Request?'))
    reg.add_input_port(
        WebRequest,
        'urls',
        (String, 'URL for the request'))
    reg.add_input_port(
        WebRequest,
        'data',
        (String, 'Data for a POST request'))
    reg.add_output_port(
        WebRequest,
        'value',
        WebRequest)
    reg.add_output_port(
        WebRequest,
        'out',
        Variant)


    # PostGISRequest
    reg.add_module(PostGISRequest,
                   namespace=data_namespace)
    reg.add_output_port(PostGISRequest, 'value', PostGISRequest)


    # QgsMapLayer
    reg.add_module(QgsLayer.QgsMapLayer,
                   namespace=data_namespace,
                   abstract=True)
    reg.add_input_port(QgsLayer.QgsMapLayer, "file", File)
    reg.add_input_port(QgsLayer.QgsMapLayer, "datarequest", DataRequest)
    #reg.add_output_port(QgsLayer.QgsMapLayer, "value", QgsLayer.QgsMapLayer)

    # QgsLayers

    # ... vector
    reg.add_module(QgsLayer.QgsVectorLayer,
                   name="VectorLayer",
                   namespace=data_namespace)
    reg.add_output_port(QgsLayer.QgsVectorLayer, "value",
                        QgsLayer.QgsVectorLayer)

    # ... raster
    reg.add_module(QgsLayer.QgsRasterLayer,
                   name="RasterLayer",
                   namespace=data_namespace)
    reg.add_input_port(QgsLayer.QgsRasterLayer, "band",
                       (Integer, 'Raster image band number'))
    reg.add_output_port(QgsLayer.QgsRasterLayer, "value",
                        QgsLayer.QgsRasterLayer)
    reg.add_output_port(QgsLayer.QgsRasterLayer, 'numpy_data_array',
                        (NDArrayEO, "Raster data as numpy array"))   

    # ... temporal
    reg.add_module(TemporalVectorLayer,
                   name="TemporalVectorLayer",
                   namespace=data_namespace)
    reg.add_output_port(TemporalVectorLayer, "value",
                        TemporalVectorLayer)

    # QgsLayerWriter
    reg.add_module(QgsLayerWriter.QgsLayerWriter,
                   namespace=data_namespace)
    reg.add_input_port(QgsLayerWriter.QgsLayerWriter, "value",
                       QgsLayer.QgsVectorLayer)
    reg.add_input_port(QgsLayerWriter.QgsLayerWriter, "file",
                       File)

    # MemFeatureModel
    reg.add_module(MemFeatureModel,
                   namespace=data_namespace,
                   abstract=True)
    reg.add_input_port(MemFeatureModel, "source_file", String)
    reg.add_input_port(MemFeatureModel, "dbconn", String)
    reg.add_input_port(MemFeatureModel, "sql", String)
    reg.add_input_port(MemFeatureModel, "webrequest", WebRequest)
    reg.add_input_port(MemFeatureModel, "gstring", GeoString)
    reg.add_output_port(MemFeatureModel, "feature_dataset", MemFeatureModel)

    # FileFeatureModel
    reg.add_module(FileFeatureModel,
                   name="OGRTransform",
                   namespace=data_namespace)
    reg.add_input_port(FileFeatureModel, "source_file", String)
    reg.add_input_port(FileFeatureModel, "source_feature_dataset",
                       MemFeatureModel)
    reg.add_input_port(FileFeatureModel, "webrequest", WebRequest)
    reg.add_input_port(FileFeatureModel, "output_type", String)

    # RasterModel
    reg.add_module(RasterModel,
                   namespace=data_namespace,
                   abstract=True)  # abstract
    reg.add_module(RasterImport,
                   configureWidgetType=RasterImportConfigurationWidget,
                   namespace=data_namespace)

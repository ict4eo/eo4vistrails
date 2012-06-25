# NB These constants are used throughout the ogc module:
#  1. DO NOT REMOVE!
#  2. If changed; use VisTrails upgrade method to track changes

# input ports
OGC_LAYERNAME_PORT = "LayerName"
OGC_POST_DATA_PORT = "PostData"
OGC_GET_REQUEST_PORT = "GetRequest"
OGC_REQUEST_PORT = "RequestURL"
OGC_URL_PORT = "OGC_URL"
WPS_PROCESS_PORT = "WPS_process"
CONFIGURATION_PORT = "Configuration"  # store user choices from config dialog
OGC_CAPABILITIES_PORT = "Capabilities"  # store XML from GetCaps: local "cache"

# output ports
URL_PORT = "URL"
DATA_PORT = "OGC_data"
FILE_PORT = "OGC_file"
WEB_REQUEST_PORT = "web_request"
RASTER_PORT = "QgsRasterLayer"
VECTOR_PORT = "QgsVectorLayer"
TEMPORAL_VECTOR_PORT = "TemporalVectorLayer"
MAP_LAYER_PORT = "QgsMapLayer"
DATA_RESULT_PORT = "WPS_data"


def initialize(*args, **keywords):
    """TO DO: Add doc string"""
    from core.modules.module_registry import get_module_registry
    from core.modules.basic_modules import File, Float, String, Dictionary
    import core

    from packages.eo4vistrails.geoinf.datamodels.QgsLayer import \
        QgsMapLayer, QgsVectorLayer, QgsRasterLayer
    from packages.eo4vistrails.geoinf.datamodels.TemporalVectorLayer import \
        TemporalVectorLayer
    from packages.eo4vistrails.geoinf.ogc.WPS import WPS, \
        WPSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.WFS import WFS, \
        WFSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.WCS import WCS, \
        WCSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.SOS import SOS, \
        SOSConfigurationWidget
    from packages.eo4vistrails.utils.WebRequest import WebRequest

    reg = get_module_registry()
    ogc_namespace = "data|ogc"

    reg.add_module(WPS,
                   configureWidgetType=WPSConfigurationWidget,
                   namespace=ogc_namespace)
    reg.add_module(WFS,
                   configureWidgetType=WFSConfigurationWidget,
                   namespace=ogc_namespace)
    reg.add_module(SOS,
                   configureWidgetType=SOSConfigurationWidget,
                   namespace=ogc_namespace)
    reg.add_module(WCS,
                   configureWidgetType=WCSConfigurationWidget,
                   namespace=ogc_namespace)

    # SOS MODULE
    reg.add_input_port(
        SOS,
        OGC_POST_DATA_PORT,
        (String, 'POST Data'))  # , True)
    reg.add_input_port(
        SOS,
        OGC_URL_PORT,
        (String, 'Request URL'))  # , True)
    reg.add_input_port(
        SOS,
        CONFIGURATION_PORT,
        (Dictionary, 'Configuration'))  #, optional=True (String,String,String,String)
    reg.add_input_port(
        SOS,
        OGC_CAPABILITIES_PORT,
        (String, 'Capabilities'))  #, optional=True (String,String,String,String)

    reg.add_output_port(
        SOS,
        URL_PORT,
        (String, 'URL String'))  # ,True)
    reg.add_output_port(
        SOS,
        DATA_PORT,
        (String, 'OGC Data String'))  # ,True)
    reg.add_output_port(
        SOS,
        FILE_PORT,
        (File, 'OGC Data File'))  # ,True)
    reg.add_output_port(
        SOS,
        WEB_REQUEST_PORT,
        WebRequest)  # ,True)
    reg.add_output_port(
        SOS,
        TEMPORAL_VECTOR_PORT,
        (TemporalVectorLayer, 'Temporal Vector Layer'))  # ,True)

    # WPS MODULE
    # This module will also be able to have dynamically configured ports,
    #   (created in code) by inheriting from the PortConfigurationWidget
    reg.add_input_port(
        WPS,
        OGC_REQUEST_PORT,
        (String, 'Configured GET Request'),
         optional=True)
    reg.add_input_port(
        WPS,
        OGC_POST_DATA_PORT,
        (String, 'POST Data'), optional=True)
    reg.add_input_port(
        WPS,
        WPS_PROCESS_PORT,
        (String, 'WPS Process'), optional=True)

    # WFS MODULE
    reg.add_input_port(
        WFS,
        OGC_LAYERNAME_PORT,
        (String, 'Layer Name'))  # ,False)
    reg.add_input_port(
        WFS,
        OGC_GET_REQUEST_PORT,
        (String, 'Configured GET Request'))  # , True)
    reg.add_input_port(
        WFS,
        OGC_URL_PORT,
        (String, 'Request URL'))  # , True)

    reg.add_output_port(
        WFS,
        VECTOR_PORT,
        (QgsVectorLayer, 'QGIS Vector Layer'))  # ,True)
    reg.add_output_port(
        WFS,
        URL_PORT,
        (String, 'URL String'))  # ,True)
    reg.add_output_port(
        WFS,
        WEB_REQUEST_PORT,
        WebRequest)  # ,True)
    reg.add_output_port(
        WFS,
        DATA_PORT,
        (String, 'Data Result'))  # ,True)

    # WCS MODULE
    reg.add_input_port(
        WCS,
        OGC_LAYERNAME_PORT,
        (String, 'Layer Name'))  # ,False)
    reg.add_input_port(
        WCS,
        OGC_GET_REQUEST_PORT,
        (String, 'Configured GET Request'))  # , True)
    reg.add_input_port(
        WCS,
        OGC_URL_PORT,
        (String, 'Request URL'))  # , True)

    reg.add_output_port(
        WCS,
        RASTER_PORT,
        (QgsRasterLayer, 'QGIS Raster Layer'))  # ,True)
    reg.add_output_port(
        WCS,
        URL_PORT,
        (String, 'URL String'))  # ,True)
    reg.add_output_port(
        WCS,
        WEB_REQUEST_PORT,
        WebRequest)  # ,True)

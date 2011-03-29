OGC_LAYERNAME_PORT = "LayerName"
OGC_POST_DATA_PORT = "PostData"
OGC_GET_REQUEST_PORT = "GetRequest"
OGC_URL_PORT = "OGC_URL"
URL_PORT = "URL"
DATA_PORT = "OGC_data"
WEB_REQUEST_PORT = "web_request"
VECTOR_PORT = "QgsVectorLayer"
RASTER_PORT = "QgsRasterLayer"
MAP_LAYER_PORT = "QgsMapLayer"

def initialize(*args, **keywords):
    """TO DO: Add doc string"""
    from core.modules.module_registry import get_module_registry

    import core

    from packages.eo4vistrails.geoinf.datamodels.QgsLayer import \
        QgsMapLayer, QgsVectorLayer, QgsRasterLayer
    from packages.eo4vistrails.geoinf.ogc.WPS import WPS, WPSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.WFS import WFS, WFSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.WCS import WCS, WCSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.SOS import SOS, SOSConfigurationWidget
    from packages.eo4vistrails.utils.WebRequest import WebRequest

    reg = get_module_registry()
    ogc_namespace = "ogc"

    reg.add_module(WPS, configureWidgetType=WPSConfigurationWidget, namespace=ogc_namespace)
    reg.add_module(WFS, configureWidgetType=WFSConfigurationWidget, namespace=ogc_namespace)
    reg.add_module(SOS, configureWidgetType=SOSConfigurationWidget, namespace=ogc_namespace)
    reg.add_module(WCS, configureWidgetType=WCSConfigurationWidget, namespace=ogc_namespace)

    # WPS MODULE
    reg.add_input_port(
        WPS,
        MAP_LAYER_PORT,
        (QgsMapLayer, 'QGIS Map Layer'))

    # WFS MODULE
    reg.add_input_port(
        WFS,
        OGC_LAYERNAME_PORT,
        (core.modules.basic_modules.String, 'Layer Name'))#,False)
    reg.add_input_port(
        WFS,
        OGC_GET_REQUEST_PORT,
        (core.modules.basic_modules.String, 'Configured GET Request'))#, True)
    reg.add_input_port(
        WFS,
        OGC_URL_PORT,
        (core.modules.basic_modules.String, 'Request URL'))#, True)
    reg.add_output_port(
        WFS,
        VECTOR_PORT,
        (QgsVectorLayer, 'QGIS Vector Layer'))#,True)
    reg.add_output_port(
        WFS,
        URL_PORT,
        (core.modules.basic_modules.String, 'URL String'))#,True)
    reg.add_output_port(
        WFS,
        WEB_REQUEST_PORT,
        WebRequest)#,True)

    # WCS MODULE
    reg.add_input_port(
        WCS,
        OGC_LAYERNAME_PORT,
        (core.modules.basic_modules.String, 'Layer Name'))#,False)
    reg.add_input_port(
        WCS,
        OGC_GET_REQUEST_PORT,
        (core.modules.basic_modules.String, 'Configured GET Request'))#, True)
    reg.add_input_port(
        WCS,
        OGC_URL_PORT,
        (core.modules.basic_modules.String, 'Request URL'))#, True)
    reg.add_output_port(
        WCS,
        RASTER_PORT,
        (QgsRasterLayer, 'QGIS Raster Layer'))#,True)
    reg.add_output_port(
        WCS,
        URL_PORT,
        (core.modules.basic_modules.String, 'URL String'))#,True)
    reg.add_output_port(
        WCS,
        WEB_REQUEST_PORT,
        WebRequest)#,True)

    # SOS MODULE
    reg.add_input_port(
        SOS,
        OGC_POST_DATA_PORT,
        (core.modules.basic_modules.String, 'POST Data'))#, True)
    reg.add_input_port(
        SOS,
        OGC_URL_PORT,
        (core.modules.basic_modules.String, 'Request URL'))#, True)
    reg.add_output_port(
        SOS,
        URL_PORT,
        (core.modules.basic_modules.String, 'URL String'))#,True)
    reg.add_output_port(
        SOS,
        DATA_PORT,
        (core.modules.basic_modules.String, 'Data String'))#,True)
    reg.add_output_port(
        SOS,
        WEB_REQUEST_PORT,
        WebRequest)#,True)

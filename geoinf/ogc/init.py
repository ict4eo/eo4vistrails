OGC_POST_REQUEST_PORT = "ConfiguredPostRequest"
OGC_GET_REQUEST_PORT = "ConfiguredGetRequest"
OGC_URL_PORT = "OGC_URL"
URL_PORT = "URL"
DATA_PORT = "OGC_data"

def initialize(*args, **keywords):
    """TO DO: Add doc string"""
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules

    import core
    from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel,  FileFeatureModel
    from packages.eo4vistrails.geoinf.datamodels.Raster import RasterModel
    from packages.eo4vistrails.geoinf.ogc.Common import OgcService
    from packages.eo4vistrails.geoinf.ogc.WFS import WFS, WFSConfigurationWidget, WFSCommonWidget
    from packages.eo4vistrails.geoinf.ogc.WCS import WCS, WCSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.SOS import SOS, SOSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.OgcConfigurationWidget import OgcConfigurationWidget
    from packages.eo4vistrails.geoinf.datamodels.FeatureImport import FeatureImport, FeatureImportConfigurationWidget

    reg = get_module_registry()

    # TO DO => change output ports to WebRequest type - how to handle URL & data ???

    # WFS MODULE
    reg.add_input_port(WFS, OGC_GET_REQUEST_PORT,
                     (core.modules.basic_modules.String, 'Configured GET Request'))#, True)
    reg.add_input_port(WFS, OGC_URL_PORT,
                     (core.modules.basic_modules.String, 'Request URL'))#, True)
    reg.add_output_port(WFS, URL_PORT,
                      (core.modules.basic_modules.String, 'URL String'))#,True)

    # WCS MODULE
    reg.add_input_port(WCS, OGC_GET_REQUEST_PORT,
                     (core.modules.basic_modules.String, 'Configured GET Request'))#, True)
    reg.add_input_port(WCS, OGC_URL_PORT,
                     (core.modules.basic_modules.String, 'Request URL'))#, True)
    reg.add_output_port(WCS, URL_PORT,
                      (core.modules.basic_modules.String, 'URL String'))#,True)

    # SOS MODULE
    reg.add_input_port(SOS, OGC_POST_REQUEST_PORT,
                     (core.modules.basic_modules.String, 'Configured POST Request'))#, True)
    reg.add_input_port(SOS, OGC_URL_PORT,
                     (core.modules.basic_modules.String, 'Request URL'))#, True)
    reg.add_output_port(SOS, URL_PORT,
                      (core.modules.basic_modules.String, 'URL String'))#,True)
    reg.add_output_port(SOS, DATA_PORT,
                      (core.modules.basic_modules.String, 'Data String'))#,True)
OGC_POST_REQUEST_PORT = "ConfiguredRequest"
OGC_URL_PORT = "OGC_URL"
OGC_RESULT_PORT = "ServiceOutput"

def initialize(*args, **keywords):
    """TO DO: Add doc string"""
    from core.modules.module_registry import get_module_registry

    from core.modules import basic_modules

    import core
    from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel,  FileFeatureModel
    from packages.eo4vistrails.geoinf.datamodels.Raster import RasterModel
    from packages.eo4vistrails.geoinf.ogc.Common import OgcService
    from packages.eo4vistrails.geoinf.ogc.WFS import WFS, WFSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.WCS import WCS, WCSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.SOS import SOS, SOSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.OgcConfigurationWidget import OgcConfigurationWidget
    from packages.eo4vistrails.geoinf.datamodels.FeatureImport import FeatureImport, FeatureImportConfigurationWidget

    reg = get_module_registry()

    # WFS MODULE
    reg.add_input_port(WFS, OGC_POST_REQUEST_PORT,
                     (core.modules.basic_modules.String, 'Configured Request'))#, True)
    reg.add_input_port(WFS, OGC_URL_PORT,
                     (core.modules.basic_modules.String, 'Request URL'))#, True)
    reg.add_output_port(WFS, OGC_RESULT_PORT,
                      (core.modules.basic_modules.String, 'Service Output String'))#,True)

    # SOS MODULE
    reg.add_input_port(SOS, OGC_POST_REQUEST_PORT,
                     (core.modules.basic_modules.String, 'Configured Request'))#, True)
    reg.add_input_port(SOS, OGC_URL_PORT,
                     (core.modules.basic_modules.String, 'Request URL'))#, True)
    reg.add_output_port(SOS, OGC_RESULT_PORT,
                      (core.modules.basic_modules.String, 'Service Output String'))#,True)


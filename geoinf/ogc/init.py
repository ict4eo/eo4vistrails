def initialize(*args, **keywords):
    """TO DO: Add doc string"""
    from core.modules.module_registry import get_module_registry

    from core.modules import basic_modules

    import core
    from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel,  FileFeatureModel
    from packages.eo4vistrails.geoinf.datamodels.Raster import RasterModel
    from packages.eo4vistrails.geoinf.ogc.Common import OgcService
    from packages.eo4vistrails.geoinf.ogc.WFS import WFS,  WFSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.WCS import WCS,  WCSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.SOS import SOS,  SOSConfigurationWidget
    from packages.eo4vistrails.geoinf.ogc.OgcConfigurationWidget import OgcConfigurationWidget
    from packages.eo4vistrails.geoinf.datamodels.FeatureImport import FeatureImport, FeatureImportConfigurationWidget

    reg = get_module_registry()

    # WFS MODULE
    reg.add_input_port(WFS, "ConfiguredRequest",
                     (core.modules.basic_modules.String, 'Configured Request'))#, True)
    reg.add_output_port(WFS, "ServiceOutput",
                      (core.modules.basic_modules.String, 'Service Output String'))#,True)

    # SOS MODULE
    reg.add_input_port(SOS, "ConfiguredRequest",
                     (core.modules.basic_modules.String, 'Configured Request'))#, True)
    reg.add_output_port(SOS, "ServiceOutput",
                      (core.modules.basic_modules.String, 'Service Output String'))#,True)

    """
    # these ports will not be used/required in the OGC services modules ...
    # Graeme to explain ...
    reg.add_input_port(WFS, "Operation",
                     (core.modules.basic_modules.String, 'available operations'))#, True)
    reg.add_input_port(WFS, "TypeName",
                     (core.modules.basic_modules.String, 'the layer names'))#, True)
    reg.add_input_port(WFS, "minX",
                     (core.modules.basic_modules.String, 'top_left_X'))#,True)
    reg.add_input_port(WFS, "minY",
                     (core.modules.basic_modules.Float, 'top_left_Y'))#,True)
    reg.add_input_port(WFS, "maxX",
                     (core.modules.basic_modules.Float, 'bottom_right_X'))#,True)
    reg.add_input_port(WFS, "maxY",
                     (core.modules.basic_modules.Float, 'bottom_right_Y'))#,True)
    reg.add_input_port(WFS, "SRS",
                      (core.modules.basic_modules.String, 'ESPG Code'))#,True)
    reg.add_input_port(WFS, "maxFeatures",
                      (core.modules.basic_modules.String, 'Maximum Features'))#,True)
    #reg.add_input_port(WFS, "DescribeFeature",
    #                 (core.modules.basic_modules.String, 'DescribeFeature Request'),True)
    reg.add_output_port(WFS, "GetCapabilitiesDoc",
                      (core.modules.basic_modules.String, 'GetCapabilities String Output'))#,True)
    reg.add_output_port(WFS, "GetCapabilitiesXMLfile",
                      (core.modules.basic_modules.File, 'GetCapabilities XML file output'))#,True)
    """

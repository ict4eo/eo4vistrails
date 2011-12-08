def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules
    from core.modules.basic_modules import File, Float, String
    from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsRasterLayer
    from packages.eo4vistrails.geoinf.datamodels.GeoStrings import GeoJSONString,  WKTString
    from AOI_Utils import FeatureOfInterestDefiner, \
                          FeatureOfInterestDefinerConfigurationWidget, \
                          AreaOfInterestDefiner, LineOfInterestDefiner, \
                          PointOfInterestDefiner

    reg = get_module_registry()
    helpers_namespace = "helpers"

    # ==========================================================================
    # Abstract Modules - these MUST appear FIRST
    # ==========================================================================

    reg.add_module(FeatureOfInterestDefiner,
                   namespace=helpers_namespace,
                   abstract = True)

    reg.add_input_port(
        FeatureOfInterestDefiner,
        "BaseLayer",
        QgsRasterLayer)

    reg.add_input_port(
        FeatureOfInterestDefiner,
        "SRS",
        String)

    reg.add_input_port(
        FeatureOfInterestDefiner,
        "WKTGeometry",
        WKTString)

#    reg.add_input_port(
#        FeatureOfInterestDefiner,
#        "QgsGeometry",
#        String)

    # ==========================================================================
    # Standard Modules
    # ==========================================================================


    reg.add_module(AreaOfInterestDefiner,
                   configureWidgetType=FeatureOfInterestDefinerConfigurationWidget,
                   namespace=helpers_namespace)

    reg.add_output_port(
        AreaOfInterestDefiner,
        "AreaOfInterest",
        (WKTString, 'Area as WKT snippet'))

    reg.add_module(LineOfInterestDefiner,
                   configureWidgetType=FeatureOfInterestDefinerConfigurationWidget,
                   namespace=helpers_namespace)

    reg.add_output_port(
        LineOfInterestDefiner,
        "LineOfInterest",
        (WKTString, 'Line as WKT snippet'))


    reg.add_module(PointOfInterestDefiner,
                   configureWidgetType=FeatureOfInterestDefinerConfigurationWidget,
                   namespace=helpers_namespace)

    reg.add_output_port(
        PointOfInterestDefiner,
        "PointOfInterest",
        (WKTString, 'Point as WKT snippet'))

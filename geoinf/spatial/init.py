def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules
    from core.modules.basic_modules import File, Float, String, Boolean
    from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsVectorLayer

    from Buffer import Buffer

    reg = get_module_registry()
    tools_namespace = "tools"
    tools_test_namespace = "tools|tests"

    # =========================================================================
    # Abstract Modules - these MUST appear FIRST
    # =========================================================================

#    reg.add_input_port(
#        FeatureOfInterestDefiner,
#        "QgsGeometry",
#        String)

    # =========================================================================
    # Standard Modules
    # =========================================================================

    # Buffer
    reg.add_module(Buffer,
                   namespace=tools_namespace)
    reg.add_input_port(
        Buffer,
        'layer',
        QgsVectorLayer)
    reg.add_input_port(
        Buffer,
        'distance',
        basic_modules.Float)
    reg.add_input_port(
        Buffer,
        'dissolve',
        basic_modules.Boolean)

    reg.add_output_port(
        Buffer,
        'shapefile',
        (basic_modules.File, 'Buffered shape file'))

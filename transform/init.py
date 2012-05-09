def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules

    #modules in this package
    from TemporalLayerTransformer import SpatialTemporalTransform
    from Transformer import Transform

    reg = get_module_registry()
    transform_namespace = "transform"
    transform_test_namespace = "transform|tests"

    # =========================================================================
    # Abstract Modules - these MUST appear FIRST
    # =========================================================================

    reg.add_module(Transform,
                   namespace=transform_namespace,
                   abstract=True)

    # =========================================================================
    # Simple Modules - without ports
    # =========================================================================

    # =========================================================================
    # Standard Modules
    # =========================================================================

    reg.add_module(SpatialTemporalTransform,
                   namespace=transform_namespace)

    """
    # Foo with ports
    reg.add_module(Foo,
                   namespace=transform_namespace)
    reg.add_input_port(
        Fork,
        'modules',
        basic_modules.Module)
    reg.add_output_port(
        PostGISRequest,
        'value',
        PostGISRequest)
    """

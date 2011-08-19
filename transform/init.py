def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules

    from session import Session

    reg = get_module_registry()
    transform_namespace = "transform"
    transform_test_namespace = "transform|tests"

    # =========================================================================
    # Abstract Modules - these MUST appear FIRST
    # =========================================================================

    """
    reg.add_module(Foo,
                   namespace=utils_namespace,
                   abstract=True)
    """

    # =========================================================================
    # Standard Modules
    # =========================================================================

    """
    # Fork
    reg.add_module(Fork,
                   namespace=utils_namespace)
    reg.add_input_port(
        Fork,
        'modules',
        basic_modules.Module)
    reg.add_output_port(
        PostGISRequest,
        'value',
        PostGISRequest)
    """

    # =========================================================================
    # Simple Modules - without ports
    # =========================================================================

    """
    reg.add_module(CsvWriter,
                   namespace=utils_namespace)
    """

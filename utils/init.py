def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules

    from ThreadSafe import Fork, ThreadTestModule
    from session import Session
    import DropDownListWidget
    from WebRequest import WebRequest
    from DataRequest import DataRequest, PostGISRequest
    from Array import NDArray
    from CsvUtils import CsvWriter, CsvReader, ListDirContent, CsvFilter
    from Random import Random
    from Command import Command
    from ListFilter import ListFilter
    from DataTransformations import InputStream,  pgSQLMergeInsert

    reg = get_module_registry()
    utils_namespace = "utils"
    utils_test_namespace = "utils|tests"

    # ==========================================================================
    # Abstract Modules - these MUST appear FIRST
    # ==========================================================================

    reg.add_module(Session,
                   namespace=utils_namespace,
                   abstract=True)

    reg.add_module(DataRequest,
                   namespace=utils_namespace,
                   abstract=True)

    # ==========================================================================
    # Standard Modules
    # ==========================================================================

    # LinuxComboBox
    LinuxDemoComboBox = basic_modules.new_constant('LinuxDemoComboBox',
                                                   staticmethod(eval),
                                                   (1, 1),
                                                   staticmethod(lambda x: type(x) == tuple),
                                                   DropDownListWidget.LinuxDemoComboBoxWidget)
    reg.add_module(LinuxDemoComboBox,
                   namespace=utils_test_namespace)

    # NDArray
    reg.add_module(NDArray,
                   name="Numpy Array",
                   namespace=utils_namespace,
                   abstract=True)
    reg.add_output_port(
        NDArray,
        "self",
        (NDArray, 'self'))

    # Fork
    reg.add_module(Fork,
                   namespace=utils_namespace)
    reg.add_input_port(
        Fork,
        'modules',
        basic_modules.Module)


    # ListFilter
    reg.add_module(ListFilter,
                   namespace=utils_namespace)
    reg.add_input_port(
        ListFilter,
        'list_in',
        basic_modules.List)
    reg.add_input_port(
        ListFilter,
        'subset',
        basic_modules.String)

    reg.add_output_port(
        ListFilter,
        'string',
        (basic_modules.String, 'String representation of sub-setted list'))
    reg.add_output_port(
        ListFilter,
        'list_out',
        (basic_modules.List, 'sub-setted list'))


    # ThreadTest
    reg.add_module(ThreadTestModule,
                   namespace=utils_test_namespace)
    reg.add_input_port(
        ThreadTestModule,
        'someModuleAboveMe',
        basic_modules.Module)

    # PostGISRequest
    reg.add_module(PostGISRequest,
                   namespace=utils_namespace)
    reg.add_output_port(
        PostGISRequest,
        'value',
        PostGISRequest)

    # WebRequest
    reg.add_module(WebRequest,
                   namespace=utils_namespace)
    reg.add_input_port(
        WebRequest,
        'request',
        (WebRequest, 'Web Request'))
    reg.add_input_port(
        WebRequest,
        'runRequest',
        (basic_modules.Boolean, 'Run The Request?'))
    reg.add_input_port(
        WebRequest,
        'urls',
        (basic_modules.String, 'URL for the request'))
    reg.add_input_port(
        WebRequest,
        'data',
        (basic_modules.String, 'Data for a POST request'))
    reg.add_output_port(
        WebRequest,
        'value',
        WebRequest)
    reg.add_output_port(
        WebRequest,
        'out',
        basic_modules.Variant)

    # ==========================================================================
    # Simple Modules - without ports OR with locally defined ports
    # ==========================================================================

    reg.add_module(CsvWriter,
                   namespace=utils_namespace)

    reg.add_module(CsvReader,
                   namespace=utils_namespace)

    reg.add_module(CsvFilter,
                   namespace=utils_namespace)

    reg.add_module(ListDirContent,
                   namespace=utils_namespace)

    reg.add_module(Random,
                   namespace=utils_namespace)

    reg.add_module(Command,
                   namespace=utils_namespace)

    reg.add_module(InputStream,
                   namespace=utils_namespace)

    reg.add_module(pgSQLMergeInsert,
                   namespace=utils_namespace)

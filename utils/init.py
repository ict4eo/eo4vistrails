from core.modules.module_registry import get_module_registry

###############################################################################
# A useful register function for control modules                              #
###############################################################################


def registerControl(module):
    """Register the control modules so that all have the same style & shape."""

    reg = get_module_registry()
    utils_namespace = "utils"
    reg.add_module(module,
                   moduleRightFringe=[(0.0, 0.0), (0.25, 0.5), (0.0, 1.0)],
                   moduleLeftFringe=[(0.0, 0.0), (0.0, 1.0)],
                   namespace=utils_namespace)


def initialize(*args, **keywords):
    from core.modules import basic_modules
    from core.modules.vistrails_module import Module

    import DropDownListWidget

    from Array import NDArrayEO
    from Command import Command
    from CsvUtils import CsvWriter, CsvReader, ListDirContent, CsvFilter
    from DataRequest import DataRequest, PostGISRequest
    from DataTransformations import InputStream,  pgSQLMergeInsert
    from DataWriter import TextDataWriter, \
        DataWriterTypeComboBox
    from Experiment import Timer
    from FTP import FTPReader
    from ListFilter import ListFilter
    from Random import Random
    from session import Session
    from ThreadSafe import Fork, ThreadTestModule, ThreadSafeFold, \
        ThreadSafeMap
    from WebRequest import WebRequest

    reg = get_module_registry()
    utils_namespace = "utils"
    utils_test_namespace = "utils|tests"

    # =========================================================================
    # Abstract Modules - these MUST appear FIRST
    # =========================================================================

    reg.add_module(Session,
                   namespace=utils_namespace,
                   abstract=True)

    reg.add_module(DataRequest,
                   namespace=utils_namespace,
                   abstract=True)

    # drop-down lists
    reg.add_module(DataWriterTypeComboBox,
                   namespace=utils_namespace,
                   abstract=True)

    # =========================================================================
    # ComboBox definitions
    # =========================================================================

    # LinuxComboBox
    LinuxDemoComboBox = basic_modules.new_constant('LinuxDemoComboBox',
                                    staticmethod(eval),
                                    (1, 1),
                                    staticmethod(lambda x: type(x) == tuple),
                                    DropDownListWidget.LinuxDemoComboBoxWidget)

    reg.add_module(LinuxDemoComboBox,
                   namespace=utils_test_namespace)

    # DateFormatComboBox
    DateFormatComboBox = basic_modules.new_constant('Date Format',
                                    staticmethod(str),
                                    's',
                                    staticmethod(lambda x: type(x) == str),
                                    DropDownListWidget.DateFormatComboBoxWidget)

    reg.add_module(DateFormatComboBox,
                   namespace=utils_namespace)

    # =========================================================================
    # Standard Modules - Ports defined here
    # =========================================================================

    # Experiment
    reg.add_module(Timer,
               name="Workflow Timer",
               namespace=utils_namespace)

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

    # NDArray
    reg.add_module(NDArrayEO,
                   name="EO Numpy Array",
                   namespace=utils_namespace,
                   abstract=True)
    reg.add_output_port(
        NDArrayEO,
        "self",
        (NDArrayEO, 'self'))

    # PostGISRequest
    reg.add_module(PostGISRequest,
                   namespace=utils_namespace)
    reg.add_output_port(
        PostGISRequest,
        'value',
        PostGISRequest)

    # ThreadTest
    reg.add_module(ThreadTestModule,
                   namespace=utils_test_namespace)
    reg.add_input_port(
        ThreadTestModule,
        'someModuleAboveMe',
        basic_modules.Module)

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

    # =========================================================================
    # Control Flow Modules -
    # =========================================================================

    registerControl(ThreadSafeFold)
    registerControl(ThreadSafeMap)

    reg.add_input_port(ThreadSafeFold, 'FunctionPort', (Module, ""))
    reg.add_input_port(ThreadSafeFold, 'InputList', (basic_modules.List, ""))
    reg.add_input_port(ThreadSafeFold, 'InputPort', (basic_modules.List, ""))
    reg.add_input_port(ThreadSafeFold, 'OutputPort', (basic_modules.String, ""))
    reg.add_output_port(ThreadSafeFold, 'Result', (basic_modules.Variant, ""))

    # =========================================================================
    # Other Modules - without ports OR with locally defined ports
    # =========================================================================

    reg.add_module(Command,
                   namespace=utils_namespace)

    reg.add_module(CsvWriter,
                   namespace=utils_namespace)

    reg.add_module(CsvReader,
                   namespace=utils_namespace)

    reg.add_module(CsvFilter,
                   namespace=utils_namespace)

    # FTP
    reg.add_module(FTPReader,
                   namespace=utils_namespace)

    reg.add_module(InputStream,
                   namespace=utils_namespace)

    reg.add_module(ListDirContent,
                   namespace=utils_namespace)

    reg.add_module(pgSQLMergeInsert,
                   namespace=utils_namespace)

    reg.add_module(Random,
                   namespace=utils_namespace)

    reg.add_module(TextDataWriter,
                   namespace=utils_namespace)

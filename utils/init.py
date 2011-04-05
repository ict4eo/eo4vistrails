def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules

    from ThreadSafe import Fork, ThreadTestModule
    from session import Session
    import DropDownListWidget
    from WebRequest import WebRequest
    from DataRequest import DataRequest, PostGISRequest
    from Array import NDArray

    reg = get_module_registry()
    utils_namespace = "utils"
    utils_test_namespace = "utils|tests"

    reg.add_module(NDArray, name="Numpy Array", namespace=utils_namespace, abstract=True)
    reg.add_output_port(NDArray, "self", (NDArray, 'self'))

    #Add ComboBox
    LinuxDemoComboBox = basic_modules.new_constant('LinuxDemoComboBox',
                                                   staticmethod(eval),
                                                   (1,1),
                                                   staticmethod(lambda x: type(x) == tuple),
                                                   DropDownListWidget.LinuxDemoComboBoxWidget)
    
    reg.add_module(LinuxDemoComboBox,
                   namespace = utils_test_namespace)

    #Add Fork
    reg.add_module(Fork, namespace = utils_namespace)
    reg.add_input_port(Fork,
                       'modules',
                       basic_modules.Module)

    #Add ThreadSafeTest
    reg.add_module(ThreadTestModule, namespace = utils_test_namespace)
    reg.add_input_port(ThreadTestModule,
                       'someModuleAboveMe',
                       basic_modules.Module)
   
    #Add Session
    reg.add_module(Session, namespace = utils_namespace, abstract=True)

    reg.add_module(DataRequest, namespace = utils_namespace, abstract=True)

    reg.add_module(PostGISRequest, namespace = utils_namespace)
    reg.add_output_port(
        PostGISRequest,
        'value',
        PostGISRequest)

    #Add WebRequest
    reg.add_module(WebRequest, namespace = utils_namespace)
    reg.add_input_port(
        WebRequest,
        'request',
        (WebRequest,'Web Request'))
    reg.add_input_port(
        WebRequest,
        'runRequest',
        (basic_modules.Boolean,'Run The Request?'))
    reg.add_input_port(
        WebRequest,
        'urls',
        (basic_modules.String,'URL for the request'))
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
def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules
    from core.vistrail.port import PortEndPoint

    from ThreadSafe import Fork, ThreadTestModule
    from Parallel import MultiProcessTestModule
    from session import Session
    import DropDownListWidget
    from WebRequest import WebRequestModule

    reg = get_module_registry()
    utils_namespace = "utils"

    #Add ComboBox
    LinuxDemoComboBox = basic_modules.new_constant('LinuxDemoComboBox',
                                                   staticmethod(str),
                                                   None,
                                                   staticmethod(lambda x: type(x) == str),
                                                   DropDownListWidget.LinuxDemoComboBoxWidget)
    reg.add_module(LinuxDemoComboBox, namespace = utils_namespace)

    #Add ThreadSafe
    #reg.add_module(ThreadSafe.ThreadSafe,
    #               namespace = utils_namespace)

    #Add Fork
    reg.add_module(Fork, namespace = utils_namespace)
    reg.add_input_port(
        Fork,
        'threadSafeModules',
        basic_modules.Module)

    #Add ThreadSafeTest
    reg.add_module(ThreadTestModule, namespace = utils_namespace)
    reg.add_input_port(
        ThreadTestModule,
        'someModuleAboveMe',
        basic_modules.Module)


    #Add MultiProcessSafe
    #reg.add_module(Parallel.MultiProcessSafe,
    #               namespace = utils_namespace)

    #Add MultiProcessTest
    reg.add_module(MultiProcessTestModule, namespace = utils_namespace)
    reg.add_input_port(
        MultiProcessTestModule,
        'someModuleAboveMe',
        basic_modules.Module)
    reg.add_input_port(
        MultiProcessTestModule,
        'someStringAboveMe',
        basic_modules.String)
    reg.add_output_port(
        MultiProcessTestModule,
        'someString',
        basic_modules.String)

    #Add Session
    reg.add_module(Session, namespace = utils_namespace)

    #Add WebRequest
    # TO DO => change input port to WebRequest type
    reg.add_module(WebRequestModule, namespace = utils_namespace)
    reg.add_input_port(
        WebRequestModule,
        'request',
        (WebRequestModule,'Web Request'))
    reg.add_input_port(
        WebRequestModule,
        'urls',
        (basic_modules.String,'URL for the request'))
    reg.add_input_port(
        WebRequestModule,
        'data',
        (basic_modules.String, 'Data for a POST request'))
    reg.add_output_port(
        WebRequestModule,
        'output',
        basic_modules.Variant)

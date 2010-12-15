def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules.python_source_configure import PythonSourceConfigurationWidget
    from core.modules import basic_modules
    
    from core.vistrail.port import PortEndPoint    
    
    import RPyC, RPyCNode, RPyCHelper, RPyCTestModule
    
    """
    sets everything up called from the top level initialize
    """
    reg = get_module_registry()
    mynamespace = "rpyc"

    #Add RPyC
    reg.add_module(RPyCNode.RPyCNode,
                   namespace=mynamespace)
    reg.add_input_port(RPyCNode.RPyCNode, 'ip',
                       basic_modules.String)
    reg.add_input_port(RPyCNode.RPyCNode, 'port',
                       basic_modules.Integer)
    reg.add_output_port(RPyCNode.RPyCNode, "value", 
                        (RPyCNode.RPyCNode, 'value'))
                        
    #Dummy Module Mixed into all RPYCSafeModules to get a possible RPyC Node
    RPyCModule_descriptor = reg.add_module(RPyCNode.RPyCModule,
                   namespace=mynamespace)
    reg.add_input_port(RPyCNode.RPyCModule, 'rpycnode',
                       (RPyCNode.RPyCNode, 'IP Address and Port of RPyC Node'))
    #RPyCModule_descriptor.portVisible.add((PortEndPoint.Destination, 'rpycnode'))

    #Add RPyC Code
    reg.add_module(RPyCHelper.RPyCCode,
                   configureWidgetType=PythonSourceConfigurationWidget,
                   namespace=mynamespace)
    reg.add_input_port(RPyCHelper.RPyCCode, 'source',
                       basic_modules.String)
    reg.add_output_port(RPyCHelper.RPyCCode, 'self',
                        basic_modules.Module)

    #Add RPyCDiscover
    reg.add_module(RPyCHelper.RPyCDiscover,
                   configureWidgetType=RPyCHelper.RPyCConfigurationWidget,
                   namespace=mynamespace)
    reg.add_output_port(RPyCHelper.RPyCDiscover, 'rpycslaves',
                       (RPyCNode.RPyCNode, 'IP Address and Port of RPyC Node'))
    reg.add_output_port(RPyCHelper.RPyCDiscover, 'self',
                        basic_modules.Module)

    #Add RPyC
    reg.add_module(RPyCTestModule.RPyCTestModule,
                   namespace=mynamespace)
    reg.add_input_port(RPyCTestModule.RPyCTestModule, 'input',
                       basic_modules.String)

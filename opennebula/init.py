def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules.python_source_configure import PythonSourceConfigurationWidget
    from core.modules import basic_modules
    import RPyC
    
    """
    sets everything up called from the top level initialize
    """
    reg = get_module_registry()
    mynamespace = "opennebula"
    
    #Add RPyC
    reg.add_module(RPyC.RPyC, 
                   configureWidgetType=PythonSourceConfigurationWidget, 
                   namespace=mynamespace)
    reg.add_input_port(RPyC.RPyC, 'rpycslave', 
                       [(basic_modules.String, "IP Address and Port of Slave"), basic_modules.String])    
    reg.add_input_port(RPyC.RPyC, 'source', 
                       basic_modules.String)    
    reg.add_output_port(RPyC.RPyC, 'self', 
                        basic_modules.Module)
                        
    #Add RPyCDiscover
    reg.add_module(RPyC.RPyCDiscover, 
                   configureWidgetType=RPyC.RPyCConfigurationWidget,
                   namespace=mynamespace)
    reg.add_output_port(RPyC.RPyCDiscover, 'rpycslaves', 
                       [(basic_modules.String, "IP Address and Port of Slaves"), basic_modules.String])
    reg.add_output_port(RPyC.RPyCDiscover, 'self', 
                        basic_modules.Module)
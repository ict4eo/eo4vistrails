def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules
    from core.vistrail.port import PortEndPoint


    import ThreadSafe
    import Parallel
    import session
   
    reg = get_module_registry()
    utils_namespace = "utils"
    
    #Add ThreadSafe
    #reg.add_module(ThreadSafe.ThreadSafe, 
    #               namespace = utils_namespace)
        
    #Add Fork
    reg.add_module(ThreadSafe.Fork, 
                   namespace = utils_namespace)
    reg.add_input_port(ThreadSafe.Fork, 'threadSafeModules', 
                        basic_modules.Module)
                        
    #Add ThreadSafeTest
    reg.add_module(ThreadSafe.ThreadTestModule, 
                   namespace = utils_namespace)
    reg.add_input_port(ThreadSafe.ThreadTestModule, 'someModuleAboveMe', 
                        basic_modules.Module)
    
    
    #Add MultiProcessSafe
    #reg.add_module(Parallel.MultiProcessSafe, 
    #               namespace = utils_namespace)
                        
    #Add MultiProcessTest
    reg.add_module(Parallel.MultiProcessTestModule,
                   namespace = utils_namespace)
    reg.add_input_port(Parallel.MultiProcessTestModule, 'someModuleAboveMe', 
                        basic_modules.Module)
    reg.add_input_port(Parallel.MultiProcessTestModule, 'someStringAboveMe', 
                        basic_modules.String)
    reg.add_output_port(Parallel.MultiProcessTestModule, 'someString', 
                        basic_modules.String)                  
    
    #Add Session
    reg.add_module(session.Session,  namespace = utils_namespace)

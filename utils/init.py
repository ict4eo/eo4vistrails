def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules
    #import ThreadSafe
    import ThreadSafe
    import session
   
    reg = get_module_registry()
    utils_namespace = "utils"
    
    #Add ThreadSafe
    reg.add_module(ThreadSafe.ThreadSafe, 
                   namespace = utils_namespace)
                        
    #Add Fork
    reg.add_module(ThreadSafe.Fork, 
                   namespace = utils_namespace)
    reg.add_input_port(ThreadSafe.Fork, 'threadSafeModules', 
                        basic_modules.Module)
                        
    #Add ThreaedSafeTest
    reg.add_module(ThreadSafe.ThreadTestModule, 
                   namespace = utils_namespace)
    reg.add_input_port(ThreadSafe.ThreadTestModule, 'someModuleAboveMe', 
                        basic_modules.Module)
                        
    #Add Session
    reg.add_module(session.Session,  namespace = utils_namespace)

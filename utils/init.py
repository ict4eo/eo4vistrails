def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules
    import ThreadSafe
    
    reg = get_module_registry()
    mynamespace = "utils"
    
    #Add ThreadSafe
    reg.add_module(ThreadSafe.ThreadSafe, 
                   namespace=mynamespace)
                        
    #Add Fork
    reg.add_module(ThreadSafe.Fork, 
                   namespace=mynamespace)

    #Add ThreaedSafeTest
    reg.add_module(ThreadSafe.ThreadTestModule, 
                   namespace=mynamespace)


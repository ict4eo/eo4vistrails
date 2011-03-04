###############################################################################
## the function initialize is called for each package, after all
## packages have been loaded. It is used to register the module with
## the VisTrails runtime.
## to register module

def initialize(*args, **keywords):
    """TO DO: Add doc string"""
    from core.modules.module_registry import get_module_registry

    import core
    
    from packages.eo4vistrails.geoinf.ogc.processing.WPS import WPS, WPSConfigurationWidget
    
    utils_namespace = "processing"


    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()

    # VisTrails cannot currently automatically detect your derived
    # classes, and the ports that they support as input and
    # output. Because of this, you as a module developer need to let
    # VisTrails know that you created a new module. This is done by calling
    # function addModule:
    reg.add_module(WPS, configureWidgetType=WPSConfigurationWidget, namespace = utils_namespace)
    

    # In a similar way, you need to report the ports the module wants
    # to make available. This is done by calling addInputPort and
    # addOutputPort appropriately. These calls only show how to set up
    # one-parameter ports. We'll see in later tutorials how to set up
    # multiple-parameter plots.
    ##reg.add_input_port(PythonWmsWidget, "WMS url",
                     ##(core.modules.basic_modules.String, 'the wms url'))
    
    ##reg.add_output_port(PythonWmsWidget, "result",
                      ##(core.modules.basic_modules.String, 'the result'))

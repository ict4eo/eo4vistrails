import core
from geoinf.ogc.WFS import WFSed
from geoinf.ogc.WFS import WFS
from opennebula.RPyC import RPyC
from geoinf.ogc.OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.python_source_configure import PythonSourceConfigurationWidget

def initialize(*args, **keywords):
    '''sets everything up'''
    
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    
    #reg.add_module(WFS)
    #input ports
    reg.add_module(WFSed, configureWidgetType=OgcConfigurationWidget)
    reg.add_module(WFS, configureWidgetType=OgcConfigurationWidget)
    
    #reg.add_input_port(FeatureModel, "service_version", (core.modules.basic_modules.String, 'Web Map Service version - default 1.1.1'))   
    #output ports
    #reg.add_output_port(FeatureModel, "OGRDataset", (ogr.Dataset, 'Feature data in OGR Dataset'))

    # VisTrails cannot currently automatically detect your derived
    # classes, and the ports that they support as input and
    # output. Because of this, you as a module developer need to let
    # VisTrails know that you created a new module. This is done by calling
    # function addModule:
    reg.add_module(RPyC,
                    configureWidgetType=PythonSourceConfigurationWidget)

    reg.add_input_port(RPyC, 'rPyCServer', (core.modules.basic_modules.String, 
                                            'The RPyC Server IP'))    
    reg.add_input_port(RPyC, 'source', core.modules.basic_modules.String, True)    
    reg.add_output_port(RPyC, 'self', core.modules.basic_modules.Module)

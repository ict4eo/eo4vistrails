from core.modules.module_registry import get_module_registry
from core.modules import basic_modules
#from core.modules import basic_widgets
import core
from packages.eo4vistrails.geoinf.visual.QGISMapCanvasCell import QGISMapCanvasCell
#from packages.spreadsheet.basicwidgets import CellLocation

def widgetName():
    """ widgetName() -> str
    Return the name of this widget plugin
    
    """
    return 'QGIS Map Canvas'

def registerWidget(reg, basicModules, basicWidgets):
    """ registerWidget(reg: module_registry,
                       basicModules: python package,
                       basicWidgets: python package) -> None
    Register all widgets in this package to VisTrails module_registry
    
    """
    
    reg.add_module(QGISMapCanvasCell)
    reg.add_input_port(QGISMapCanvasCell, "Location", basicWidgets.CellLocation)
    reg.add_input_port(QGISMapCanvasCell, "File", basicModules.File)    

def initialize(*args, **keywords):

    """TO DO: Add doc string"""

    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules
    #from core.modules import basic_widgets

    import core

    from packages.eo4vistrails.geoinf.visual.QGISMapCanvasCell import QGISMapCanvasCell
    from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel, FileFeatureModel
    from packages.spreadsheet import basic_widgets

    reg = get_module_registry()
    #global basicWidgets
    reg.add_module(QGISMapCanvasCell)
    reg.add_input_port(QGISMapCanvasCell, "Location", basic_widgets.CellLocation)
    reg.add_input_port(QGISMapCanvasCell, "File", basic_modules.File)    



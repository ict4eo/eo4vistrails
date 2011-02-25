from QGISMapCanvasCell import QGISMapCanvasCell

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

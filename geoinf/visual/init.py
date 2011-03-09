def initialize(*args, **keywords):

    """TO DO: Add doc string"""

    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules

    from packages.eo4vistrails.geoinf.visual.QGISMapCanvasCell import QGISMapCanvasCell
    from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsMapLayer
    from packages.spreadsheet import basic_widgets

    reg = get_module_registry()
    #global basicWidgets
    reg.add_module(QGISMapCanvasCell)
    reg.add_input_port(QGISMapCanvasCell, "Location", basic_widgets.CellLocation)
    reg.add_input_port(QGISMapCanvasCell, "layer", QgsMapLayer)    
    
     
    



def initialize(*args, **keywords):

    from core.modules.module_registry import get_module_registry
    from packages.pylab.plot import MplPlot, MplPlotConfigurationWidget
    from packages.eo4vistrails.lib.plots.standard.plot import \
        ParentPlot, SinglePlot, Histogram, MultiPlot, \
        MatplotlibDateFormatComboBox, \
        MatplotlibMarkerComboBox, MatplotlibPlotTypeComboBox, \
        MatplotlibLineStyleComboBox, MatplotlibHistogramTypeComboBox

    reg = get_module_registry()
    namespace = "plots"

    # abstract modules - drop-down lists
    reg.add_module(MatplotlibDateFormatComboBox, namespace=namespace, abstract=True)
    reg.add_module(MatplotlibMarkerComboBox, namespace=namespace, abstract=True)
    reg.add_module(MatplotlibPlotTypeComboBox, namespace=namespace, abstract=True)
    reg.add_module(MatplotlibLineStyleComboBox, namespace=namespace, abstract=True)
    reg.add_module(MatplotlibHistogramTypeComboBox, namespace=namespace, abstract=True)

    # abstract modules
    reg.add_module(ParentPlot, namespace=namespace, abstract=True)

    # active modules
    reg.add_module(SinglePlot, namespace=namespace,
                   configureWidgetType=MplPlotConfigurationWidget)
    reg.add_module(Histogram, namespace=namespace,
                   configureWidgetType=MplPlotConfigurationWidget)
    reg.add_module(MultiPlot, namespace=namespace,
                   configureWidgetType=MplPlotConfigurationWidget)


    """
    THIS CODE APPEARS IN THE ORIGINAL istrails.packages.pylab.init FILE...

#    reg.add_input_port(MplPlot, 'source', String, True)
    reg.add_input_port(MplPlot, 'Hide Toolbar', Boolean, True)
    reg.add_output_port(MplPlot, 'source', String)

    reg.add_module(MplFigureManager)

    reg.add_module(MplFigure)
    reg.add_input_port(MplFigure, 'Script', String)
    reg.add_output_port(MplFigure, 'FigureManager', MplFigureManager)
    reg.add_output_port(MplFigure, 'File', File)

    # Register a figure cell type if the spreadsheet is up
    if reg.has_module('edu.utah.sci.vistrails.spreadsheet',
                               'SpreadsheetCell'):
        from figure_cell import MplFigureCell
        reg.add_module(MplFigureCell)
        reg.add_input_port(MplFigureCell, 'FigureManager', MplFigureManager)
    """

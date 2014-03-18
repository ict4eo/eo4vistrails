def initialize(*args, **keywords):

    from core.modules.module_registry import get_module_registry
    from packages.matplotlib.bases import MplPlot, MplPlotConfigurationWidget
    from vistrails.packages.eo4vistrails.tools.visual.plots.standard.plot import \
        ParentPlot, SinglePlot, Histogram, MultiPlot, \
        MatplotlibMarkerComboBox, MatplotlibPlotTypeComboBox, \
        MatplotlibLineStyleComboBox, MatplotlibHistogramTypeComboBox

    reg = get_module_registry()
    namespace = "visualisation|plots"

    # abstract modules - drop-down lists
    reg.add_module(MatplotlibMarkerComboBox,
                   namespace=namespace,
                   abstract=True)
    reg.add_module(MatplotlibPlotTypeComboBox,
                   namespace=namespace,
                   abstract=True)
    reg.add_module(MatplotlibLineStyleComboBox,
                   namespace=namespace,
                   abstract=True)
    reg.add_module(MatplotlibHistogramTypeComboBox,
                   namespace=namespace,
                   abstract=True)

    # abstract modules - other
    reg.add_module(ParentPlot,
                   namespace=namespace,
                   abstract=True)

    # active modules
    reg.add_module(SinglePlot, namespace=namespace,
                   configureWidgetType=MplPlotConfigurationWidget)
    reg.add_module(Histogram, namespace=namespace,
                   configureWidgetType=MplPlotConfigurationWidget)
    reg.add_module(MultiPlot, namespace=namespace,
                   configureWidgetType=MplPlotConfigurationWidget)

def initialize(*args, **keywords):

    from core.modules.module_registry import get_module_registry
    from packages.pylab.plot import MplPlot, MplPlotConfigurationWidget
    from packages.eo4vistrails.lib.plots.standard.plot import \
        ParentPlot, SinglePlot, Histogram, MultiPlot, \
        MatplotlibMarkerComboBox, MatplotlibPlotTypeComboBox, \
        MatplotlibLineStyleComboBox, MatplotlibHistogramTypeComboBox

    reg = get_module_registry()
    namespace = "plots"

    # abstract modules - drop-down lists
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

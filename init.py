
#brings in cloud modules
try:
    from rpyc import init as rpyc_init
except:
    import rpyc.init as rpyc_init

#brings in threading and session modules
try:
    from utils import init as utils_init
except:
    import utils.init as utils_init

#brings in PostGIS modules
try:
    from geoinf.postgis import init as postgis_init
except:
    import geoinf.postgis.init as postgis_init

#brings in ogc modules
try:
    from geoinf.ogc import init as ogc_init
except:
    import geoinf.ogc.init as ogc_init

#brings in datamodels modules
try:
    from geoinf.datamodels import init as datamodels_init
except:
    import geoinf.datamodels.init as datamodels_init

#brings in dataanalytics modules
try:
    from dataanalytics import init as dataanalytics_init
except:
    import dataanalytics.init as dataanalytics_init

# brings in visual widgets
try:
    from geoinf.visual import init as visual_init
except:
    import geoinf.visual.init as visual_init

# brings in transformers
try:
    from transform import init as transform_init
except:
    import transform.init as transform_init

# brings in datacube
try:
    from datacube import init as datacube_init
except:
    import datacube.init as datacube_init

# brings in helpers
try:
    from geoinf.helpers import init as helpers_init
except:
    import geoinf.helpers.init as helpers_init

# brings in tools
try:
    from geoinf.tools import init as tools_init
except:
    import geoinf.tools.init as tools_init

# brings in plots
try:
    from lib.plots.standard import init as plots_init
except:
    import  lib.plots.standard.init as plots_init


def initialize(*args, **keywords):
    '''sets everything up'''
    # VisTrails cannot currently automatically detect your derived
    # classes, and the ports that they support as input and
    # output. Because of this, you as a module developer, need to let
    # VisTrails know that you created a new module.
    # This is done by calling function addModule()

    # Isolate the registration of the modules

    # NOTE! order does count
    rpyc_init.initialize(*args, **keywords)
    utils_init.initialize(*args, **keywords)
    datamodels_init.initialize(*args, **keywords)
    ogc_init.initialize(*args, **keywords)
    postgis_init.initialize(*args, **keywords)
    visual_init.initialize(*args, **keywords)
    dataanalytics_init.initialize(*args, **keywords)
    transform_init.initialize(*args, **keywords)
    datacube_init.initialize(*args, **keywords)
    helpers_init.initialize(*args, **keywords)
    tools_init.initialize(*args, **keywords)
    plots_init.initialize(*args, **keywords)


#brings in cloud modules; will use dummy wrappers if rpyc not installed
try:
    from rpyc import init as rpyc_init
except:
    import rpyc.init as rpyc_init

#brings in geo constants
try:
    from geoinf.geostrings import init as geostrings_init
except:
    import geoinf.geostrings.init as geostrings_init

#brings in threading and session modules
try:
    from tools.utils import init as utils_init
except:
    import tools.utils.init as utils_init

#brings in datamodels modules
try:
    from geoinf.datamodels import init as datamodels_init
except:
    import geoinf.datamodels.init as datamodels_init

#brings in ogc and other web-based modules
try:
    from geoinf.web import init as web_init
except:
    import geoinf.web.init as web_init

#brings in dataanalytics modules
try:
    from dataanalytics import init as dataanalytics_init
except:
    import dataanalytics.init as dataanalytics_init

# brings in transformers
try:
    from tools.transform import init as transform_init
except:
    import tools.transform.init as transform_init

# brings in helpers
try:
    from geoinf.helpers import init as helpers_init
except:
    import geoinf.helpers.init as helpers_init

# brings in spatial
try:
    from tools.spatial import init as spatial_init
except:
    import tools.spatial.init as spatial_init

# brings in file
try:
    from tools.file import init as file_init
except:
    import tools.file.init as file_init

# brings in csv
try:
    from tools.csv import init as csv_init
except:
    import tools.csv.init as csv_init

# brings in excel
try:
    from tools.excel import init as excel_init
except:
    import tools.excel.init as excel_init

# brings in plots
try:
    from tools.visual.plots.standard import init as plots_init
except:
    import tools.visual.plots.standard.init as plots_init

# brings in maps
try:
    from tools.visual.maps import init as maps_init
except:
    import  tools.visual.maps.init as maps_init


def initialize(*args, **keywords):
    import core.requirements
    '''sets everything up'''
    # VisTrails cannot currently automatically detect your derived
    # classes, and the ports that they support as input and
    # output. Because of this, you as a module developer, need to let
    # VisTrails know that you created a new module.
    # This is done by calling function addModule()
    # Isolate the registration of the modules
    # NOTE! order does count

    rpyc_init.initialize(*args, **keywords)
    geostrings_init.initialize(*args, **keywords)
    utils_init.initialize(*args, **keywords)
    datamodels_init.initialize(*args, **keywords)
    web_init.initialize(*args, **keywords)
    transform_init.initialize(*args, **keywords)
    helpers_init.initialize(*args, **keywords)
    spatial_init.initialize(*args, **keywords)
    plots_init.initialize(*args, **keywords)
    maps_init.initialize(*args, **keywords)
    csv_init.initialize(*args, **keywords)
    excel_init.initialize(*args, **keywords)
    file_init.initialize(*args, **keywords)
    if core.requirements.python_module_exists('psycopg2'):
        #brings in PostGIS modules
        try:
            from geoinf.postgis import init as postgis_init
        except:
            import geoinf.postgis.init as postgis_init
        postgis_init.initialize(*args, **keywords)
    dataanalytics_init.initialize(*args, **keywords)

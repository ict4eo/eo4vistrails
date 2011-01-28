import core
from geoinf.datamodels.Feature import FeatureModel,  FileFeatureModel,  MemFeatureModel
from geoinf.datamodels.Raster import RasterModel
from geoinf.ogc.Common import OgcService
from geoinf.ogc.WFS import WFS,  WFSConfigurationWidget
from geoinf.ogc.WCS import WCS,  WCSConfigurationWidget
from geoinf.ogc.SOS import SOS,  SOSConfigurationWidget
from geoinf.ogc.OgcConfigurationWidget import OgcConfigurationWidget
#from geoinf.datamodels.FeatureImport import FeatureImport, FeatureImportConfigurationWidget
#from utils.session import Session
#from geoinf.postgis.PostGIS import PostGisSession,  PostGisCursor,  PostGisFeatureReturningCursor,  PostGisBasicReturningCursor,  PostGisNonReturningCursor,  SQLSourceConfigurationWidget



#brings in threading and session modules
try:
    from utils import init as utils_init
except:
    import utils.init as utils_init

#Brings in cloud modules
try:
    from rpyc import init as rpyc_init
except:
    import rpyc.init as rpyc_init

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



def initialize(*args, **keywords):
    '''sets everything up'''
    # VisTrails cannot currently automatically detect your derived
    # classes, and the ports that they support as input and
    # output. Because of this, you as a module developer need to let
    # VisTrails know that you created a new module. This is done by calling
    # function addModule:


    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()

    #input ports
    reg.add_module(FeatureModel) #abstract

    reg.add_module(FileFeatureModel)
    reg.add_input_port(FileFeatureModel,  "source_file", core.modules.basic_modules.String )
    reg.add_input_port(FileFeatureModel,  "output_type", core.modules.basic_modules.String )

    reg.add_module(MemFeatureModel)
    reg.add_input_port(MemFeatureModel,  "source_file", core.modules.basic_modules.String )
    #reg.add_input_port(MemFeatureModel,  "output_type", core.modules.basic_modules.String )
    reg.add_input_port(MemFeatureModel,  "dbconn", core.modules.basic_modules.String )
    reg.add_input_port(MemFeatureModel,  "sql", core.modules.basic_modules.String )
    reg.add_input_port(MemFeatureModel,  "uri", core.modules.basic_modules.String )
    reg.add_input_port(MemFeatureModel,  "uri_data", core.modules.basic_modules.String)
    reg.add_output_port(MemFeatureModel, "feature_dataset", MemFeatureModel)


    reg.add_module(RasterModel) #abstract
    reg.add_module(WFS, configureWidgetType=WFSConfigurationWidget)
    reg.add_module(SOS, configureWidgetType=SOSConfigurationWidget)
    reg.add_module(WCS, configureWidgetType=WCSConfigurationWidget)

    #reg.add_module(FeatureImport, configureWidgetType=FeatureImportConfigurationWidget)


    #reg.add_input_port(FeatureModel, "service_version", (core.modules.basic_modules.String, 'Web Map Service version - default 1.1.1'))
    #output ports
    #reg.add_output_port(FeatureModel, "OGRDataset", (ogr.Dataset, 'Feature data in OGR Dataset'))


    #Isolate the registration of the modules
    #Note order does count

    ogc_init.initialize(*args, **keywords)  # looks like no-one is willing to mess up this file, so have created ogc specific init.py as well.
    utils_init.initialize(*args, **keywords)
    postgis_init.initialize(*args,  **keywords)
    rpyc_init.initialize(*args, **keywords)



    #reg.add_module(RPyC, configureWidgetType=PythonSourceConfigurationWidget)
    #reg.add_input_port(RPyC, 'rPyCServer', (core.modules.basic_modules.String, 'The RPyC Server IP'))
    #reg.add_input_port(RPyC, 'source', core.modules.basic_modules.String, True)
    #reg.add_output_port(RPyC, 'self', core.modules.basic_modules.Module)

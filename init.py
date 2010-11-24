import core
from geoinf.datamodels.Feature import FeatureModel,  FileFeatureModel
from geoinf.datamodels.Raster import RasterModel
from geoinf.ogc.Common import OgcService
from geoinf.ogc.WFS import WFS,  WFSConfigurationWidget
from geoinf.ogc.WCS import WCS,  WCSConfigurationWidget
from geoinf.ogc.SOS import SOS,  SOSConfigurationWidget
from geoinf.ogc.OgcConfigurationWidget import OgcConfigurationWidget
from utils.session import Session
from geoinf.postgis.PostGIS import PostGisSession,  PostGisCursor,  PostGisFeatureReturningCursor,  PostGisBasicReturningCursor,  PostGisNonReturningCursor,  SQLSourceConfigurationWidget
#from geoinf.postgis import *

import packages.eo4vistrails.opennebula.init
import packages.eo4vistrails.utils.init

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
    
    #reg.add_module(WFS)
    #input ports
    reg.add_module(FeatureModel) #abstract
    reg.add_module(FileFeatureModel)
    reg.add_module(RasterModel) #abstract
    
    reg.add_module(WFS, configureWidgetType=WFSConfigurationWidget)
    reg.add_module(SOS, configureWidgetType=SOSConfigurationWidget)
    reg.add_module(WCS, configureWidgetType=WCSConfigurationWidget)
    
    #reg.add_input_port(FeatureModel, "service_version", (core.modules.basic_modules.String, 'Web Map Service version - default 1.1.1'))   
    #output ports
    #reg.add_output_port(FeatureModel, "OGRDataset", (ogr.Dataset, 'Feature data in OGR Dataset'))

    #should try to do this in own package...
    reg.add_module(Session)
    reg.add_module(PostGisSession)
    reg.add_input_port(PostGisSession, 'postgisHost', (core.modules.basic_modules.String, 
        'The hostname or IP address of the machine hosting your database'))    
    reg.add_input_port(PostGisSession, 'postgisPort', (core.modules.basic_modules.String, 
        'The port postgres is using on the machine hosting your database. Default 5432'))   
    reg.add_input_port(PostGisSession, 'postgisUser', (core.modules.basic_modules.String, 
        'The username for accessing your database'))    
    reg.add_input_port(PostGisSession, 'postgisPassword', (core.modules.basic_modules.String, 
        'The password for user for accessing your database'))    
    reg.add_input_port(PostGisSession, 'postgisDatabase', (core.modules.basic_modules.String, 
        'The actual database you will work with'))  
    reg.add_output_port(PostGisSession, 'self', PostGisSession)#supports passing of session object around

    #reg.add_module(PostGisCursor)
    
    reg.add_module(PostGisFeatureReturningCursor,  configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisFeatureReturningCursor,  "PostGisSessionObject",  PostGisSession)
    reg.add_input_port(PostGisFeatureReturningCursor,  "source",  core.modules.basic_modules.String)
    reg.add_output_port(PostGisFeatureReturningCursor, 'self', PostGisFeatureReturningCursor)#supports ControlFlow ExecuteInOrder
    
    reg.add_module(PostGisBasicReturningCursor,  configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisBasicReturningCursor,  "PostGisSessionObject",  PostGisSession)
    reg.add_input_port(PostGisBasicReturningCursor,  "source",  core.modules.basic_modules.String)
    reg.add_output_port(PostGisBasicReturningCursor, 'records', core.modules.basic_modules.List)
    reg.add_output_port(PostGisBasicReturningCursor, 'self', PostGisBasicReturningCursor)#supports ControlFlow ExecuteInOrder
    
    reg.add_module(PostGisNonReturningCursor,  configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisNonReturningCursor,  "PostGisSessionObject",  PostGisSession)
    reg.add_input_port(PostGisNonReturningCursor,  "source",  core.modules.basic_modules.String)
    reg.add_output_port(PostGisNonReturningCursor, 'status', core.modules.basic_modules.List)
    reg.add_output_port(PostGisNonReturningCursor, 'self', PostGisNonReturningCursor)#supports ControlFlow ExecuteInOrder
    
        
    #Isolate the registration of the modules
    #Note order does count
    packages.eo4vistrails.utils.init.initialize(*args, **keywords)
    packages.eo4vistrails.opennebula.init.initialize(*args, **keywords)
    
    #reg.add_module(RPyC, configureWidgetType=PythonSourceConfigurationWidget)
    #reg.add_input_port(RPyC, 'rPyCServer', (core.modules.basic_modules.String, 'The RPyC Server IP'))    
    #reg.add_input_port(RPyC, 'source', core.modules.basic_modules.String, True)    
    #reg.add_output_port(RPyC, 'self', core.modules.basic_modules.Module)

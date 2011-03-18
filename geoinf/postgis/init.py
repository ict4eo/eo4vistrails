###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation 
## ingestion, pre-processing, transformation, analytic and visualisation 
## capabilities . Included is the abilty to run code transparently in 
## OpenNebula cloud environments. There are various software 
## dependencies, but all are FOSS.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""This package provides GIS capabilities for eo4vistrails.
In particular, provides PostGIS clients via psycopg2.
This is not a SQL Builder - it assumes you know SQL
and in particular, spatial SQL as provided by PostGIS. 
You will need to write raw sql by hand. Provsions a session
a.k.a. a postgis connection and allows random queries to be
executed against the chosen database. 
"""
import core
#from core.modules.python_source_configure import PythonSourceConfigurationWidget
#from utils.session import Session
from PostGIS import PostGisSession,  PostGisCursor,  PostGisFeatureReturningCursor,  PostGisBasicReturningCursor,  PostGisNonReturningCursor,  SQLSourceConfigurationWidget
from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsVectorLayer

def initialize(*args, **keywords):
    """Sets up PostGIS modules"""
    print "in my postgis init process"
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    postgis_namespace = "PostGIS"
    

    reg.add_module(PostGisSession,  namespace = postgis_namespace)
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
    #reg.add_output_port(PostGisSession, 'self', PostGisSession)#supports passing of session object around
    reg.add_output_port(PostGisSession, 'PostGisSession', PostGisSession)#supports passing of session object around
    #reg.add_module(PostGisCursor)
    
    reg.add_module(PostGisFeatureReturningCursor,  namespace = postgis_namespace,  configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisFeatureReturningCursor,  "PostGisSessionObject",  PostGisSession)
    reg.add_input_port(PostGisFeatureReturningCursor,  "source",  core.modules.basic_modules.String)
    reg.add_output_port(PostGisFeatureReturningCursor,  "QgsVectorLayer",  QgsVectorLayer)
    reg.add_output_port(PostGisFeatureReturningCursor, 'self', PostGisFeatureReturningCursor)#supports ControlFlow ExecuteInOrder
    
    reg.add_module(PostGisBasicReturningCursor,  namespace = postgis_namespace,  configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisBasicReturningCursor,  "PostGisSessionObject",  PostGisSession)
    reg.add_input_port(PostGisBasicReturningCursor,  "source",  core.modules.basic_modules.String)
    reg.add_output_port(PostGisBasicReturningCursor, 'records', core.modules.basic_modules.List)
    reg.add_output_port(PostGisBasicReturningCursor, 'self', PostGisBasicReturningCursor)#supports ControlFlow ExecuteInOrder
    
    reg.add_module(PostGisNonReturningCursor,  namespace = postgis_namespace,  configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisNonReturningCursor,  "PostGisSessionObject",  PostGisSession)
    reg.add_input_port(PostGisNonReturningCursor,  "source",  core.modules.basic_modules.String)
    reg.add_output_port(PostGisNonReturningCursor, 'status', core.modules.basic_modules.List)
    reg.add_output_port(PostGisNonReturningCursor, 'self', PostGisNonReturningCursor)#supports ControlFlow ExecuteInOrder

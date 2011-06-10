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

import core
#from core.modules.python_source_configure import PythonSourceConfigurationWidget
#from utils.session import Session
from PostGIS import *
from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsVectorLayer
from packages.eo4vistrails.utils.DataRequest import PostGISRequest

from packages.NumSciPy.Array import NDArray


def initialize(*args, **keywords):
    """Sets up PostGIS modules"""
    print "in my postgis init process"
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    postgis_namespace = "postGIS"

    reg.add_module(PostGisSession, namespace=postgis_namespace)
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

    reg.add_module(PostGisFeatureReturningCursor, name="Feature Returning Query", namespace=postgis_namespace, configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisFeatureReturningCursor, 'PostGisSessionObject', PostGisSession)
    reg.add_input_port(PostGisFeatureReturningCursor, 'source', core.modules.basic_modules.String)
    reg.add_output_port(PostGisFeatureReturningCursor, 'PostGISRequest', PostGISRequest)
    reg.add_output_port(PostGisFeatureReturningCursor, 'QgsVectorLayer', QgsVectorLayer)
    reg.add_output_port(PostGisFeatureReturningCursor, 'self', PostGisFeatureReturningCursor)#supports ControlFlow ExecuteInOrder

    reg.add_module(PostGisNumpyReturningCursor, name="Numpy Returning Query", namespace=postgis_namespace, configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisNumpyReturningCursor, "PostGisSessionObject", PostGisSession)
    reg.add_input_port(PostGisNumpyReturningCursor, "source", core.modules.basic_modules.String)
    reg.add_output_port(PostGisNumpyReturningCursor, 'nummpyArray', NDArray)
    reg.add_output_port(PostGisNumpyReturningCursor, 'self', PostGisNumpyReturningCursor)#supports ControlFlow ExecuteInOrder


    reg.add_module(PostGisBasicReturningCursor, name="Basic Returning Query", namespace=postgis_namespace, configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisBasicReturningCursor, "PostGisSessionObject", PostGisSession)
    reg.add_input_port(PostGisBasicReturningCursor, "source", core.modules.basic_modules.String)
    reg.add_output_port(PostGisBasicReturningCursor, 'records', core.modules.basic_modules.List)
    reg.add_output_port(PostGisBasicReturningCursor, 'self', PostGisBasicReturningCursor)#supports ControlFlow ExecuteInOrder

    reg.add_module(PostGisNonReturningCursor, name="Non Returning Query", namespace=postgis_namespace, configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisNonReturningCursor, "PostGisSessionObject", PostGisSession)
    reg.add_input_port(PostGisNonReturningCursor, "source", core.modules.basic_modules.String)
    reg.add_output_port(PostGisNonReturningCursor, 'status', core.modules.basic_modules.List)
    reg.add_output_port(PostGisNonReturningCursor, 'self', PostGisNonReturningCursor)#supports ControlFlow ExecuteInOrder

    reg.add_module(PostGisCopyFrom, name="Copy From File To Table", namespace=postgis_namespace)
    reg.add_module(PostGisCopyTo, name="Copy From Table To File", namespace=postgis_namespace)

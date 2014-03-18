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

# library
import core
# vistrails
from vistrails.packages.NumSciPy.Array import NDArray
# eo4vistrails
from vistrails.packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsVectorLayer
# local#from utils.session import Session
#moved to datamodelsfrom PostGISRequest import PostGISRequest
from vistrails.packages.eo4vistrails.geoinf.datamodels.PostGISRequest import PostGISRequest
from PostGIS import *
from pgLoadersDumpers import *
from DataTransformations import InputStream, pgSQLMergeInsert


def initialize(*args, **keywords):
    """Sets up PostGIS modules"""
    #print "in my postgis init process"
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    postgis_namespace = "data|postGIS"

    """ #moved to datamodels
    # PostGISRequest
    reg.add_module(PostGISRequest,
                   namespace=postgis_namespace)
    reg.add_output_port(PostGISRequest, 'value', PostGISRequest)
    """

    # PostGisSession
    reg.add_module(PostGisSession,
                   namespace=postgis_namespace)
    reg.add_input_port(PostGisSession, 'postgisHost',
                       (core.modules.basic_modules.String,
        'The hostname or IP address of the machine hosting your database'))
    reg.add_input_port(PostGisSession, 'postgisPort',
                       (core.modules.basic_modules.String,
        'The port postgres is using on the machine hosting your database. Default 5432'))
    reg.add_input_port(PostGisSession, 'postgisUser',
                       (core.modules.basic_modules.String,
        'The username for accessing your database'))
    reg.add_input_port(PostGisSession, 'postgisPassword',
                       (core.modules.basic_modules.String,
        'The password for user for accessing your database'))
    reg.add_input_port(PostGisSession, 'postgisDatabase',
                       (core.modules.basic_modules.String,
        'The actual database you will work with'))
    #supports passing of session object around
    reg.add_output_port(PostGisSession, 'PostGisSession', PostGisSession)

    # PostGisReturningCursor
    reg.add_module(PostGisFeatureReturningCursor,
                   name="FeatureReturningQuery",
                   namespace=postgis_namespace,
                   configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisFeatureReturningCursor,
                       'PostGisSessionObject', PostGisSession)
    reg.add_input_port(PostGisFeatureReturningCursor,
                       'source', core.modules.basic_modules.String)
    reg.add_output_port(PostGisFeatureReturningCursor,
                        'PostGISRequest', PostGISRequest)
    reg.add_output_port(PostGisFeatureReturningCursor,
                        'QgsVectorLayer', QgsVectorLayer)
    #supports ControlFlow ExecuteInOrder
    reg.add_output_port(PostGisFeatureReturningCursor,
                        'self', PostGisFeatureReturningCursor)

    # PostGisNumpyReturningCursor
    reg.add_module(PostGisNumpyReturningCursor,
                   name="NumpyReturningQuery",
                   namespace=postgis_namespace,
                   configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisNumpyReturningCursor,
                       "PostGisSessionObject", PostGisSession)
    reg.add_input_port(PostGisNumpyReturningCursor,
                       "source", core.modules.basic_modules.String)
    reg.add_output_port(PostGisNumpyReturningCursor,
                        'nummpyArray', NDArray)
    #supports ControlFlow ExecuteInOrder
    reg.add_output_port(PostGisNumpyReturningCursor,
                        'self', PostGisNumpyReturningCursor)

    # PostGisBasicReturningCursor
    reg.add_module(PostGisBasicReturningCursor,
                   name="BasicReturningQuery",
                   namespace=postgis_namespace,
                   configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisBasicReturningCursor,
                       "PostGisSessionObject", PostGisSession)
    reg.add_input_port(PostGisBasicReturningCursor,
                       "source", core.modules.basic_modules.String)
    reg.add_output_port(PostGisBasicReturningCursor,
                        'records', core.modules.basic_modules.List)
    #supports ControlFlow ExecuteInOrder
    reg.add_output_port(PostGisBasicReturningCursor,
                        'self', PostGisBasicReturningCursor)

    # PostGisNonReturningCursor
    reg.add_module(PostGisNonReturningCursor,
                   name="NonReturningQuery",
                   namespace=postgis_namespace,
                   configureWidgetType=SQLSourceConfigurationWidget)
    reg.add_input_port(PostGisNonReturningCursor,
                       "PostGisSessionObject", PostGisSession)
    reg.add_input_port(PostGisNonReturningCursor,
                       "source", core.modules.basic_modules.String)
    reg.add_output_port(PostGisNonReturningCursor,
                        'status', core.modules.basic_modules.List)
    #supports ControlFlow ExecuteInOrder
    reg.add_output_port(PostGisNonReturningCursor,
                        'self', PostGisNonReturningCursor)

    # PostGisCopyFrom
    reg.add_module(PostGisCopyFrom,
                   name="CopyFromFileToTable",
                   namespace=postgis_namespace)

    # PostGisCopyTo
    reg.add_module(PostGisCopyTo,
                   name="CopyFromTableToFile",
                   namespace=postgis_namespace)

    #for canned queries
    reg.add_module(reprojectPostGISTable,
                   name="ReprojectPostGISTable",
                   namespace=postgis_namespace)
    reg.add_input_port(reprojectPostGISTable,
                       "PostGisSessionObject", PostGisSession)
    reg.add_input_port(reprojectPostGISTable,
                       "target_table", core.modules.basic_modules.String)
    reg.add_input_port(reprojectPostGISTable,
                       "new_srs", core.modules.basic_modules.Integer)
    reg.add_output_port(reprojectPostGISTable,
                        'status', core.modules.basic_modules.List)

    #for the loaders/dumpers
    reg.add_module(Shape2PostGIS,
                   name="ShapefileLoader",
                   namespace=postgis_namespace)
    reg.add_input_port(Shape2PostGIS,
                       "PostGisSessionObject", PostGisSession)
    reg.add_input_port(Shape2PostGIS,
                       "InputShapefile", core.modules.basic_modules.String)
    reg.add_input_port(Shape2PostGIS,
                       "TableName", core.modules.basic_modules.String)
    reg.add_input_port(Shape2PostGIS,
                       "EPSG_SRS", core.modules.basic_modules.String)
    reg.add_input_port(Shape2PostGIS,
                       "Index", core.modules.basic_modules.Boolean)
    reg.add_input_port(Shape2PostGIS,
                       "Simplify", core.modules.basic_modules.Boolean)
    reg.add_input_port(Shape2PostGIS,
                       "Encoding", core.modules.basic_modules.String,
                       optional=True)

    # Data records from file data
    reg.add_module(InputStream,
                   namespace=postgis_namespace)

    reg.add_module(pgSQLMergeInsert,
                   namespace=postgis_namespace)

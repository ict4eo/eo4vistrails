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
import psycopg2
from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel,  MemFeatureModel
from packages.eo4vistrails.utils.session import Session
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
from core.modules.source_configure import SourceConfigurationWidget
import urllib

class PostGisSession(Session):
    """Responsible for making a connection to a postgis database.
    Ultimately, objects of this class will need to be passed from
    execution step to execution step, so may need to be a constant?
    """
    def __init__(self):
        Session.__init__(self)

    def compute(self):
        '''fetches psycopg connection'''
        host = self.forceGetInputFromPort('postgisHost', 'localhost')
        port = self.forceGetInputFromPort('postgisPort', '5432')
        user = self.forceGetInputFromPort('postgisUser', 'default')
        pwd =  self.forceGetInputFromPort('postgisPassword', 'default')
        database = self.forceGetInputFromPort('postgisDatabase', 'default')

        self.connectstr = "host=" + host+ " dbname=" + database + " user=" + user + " password=" + pwd
        #PG:"dbname='databasename' host='addr' port='5432' user='x' password='y'"
        #PG:'host=myserver.velocet.ca user=postgres dbname=warmerda'
        self.ogr_connectstr = "PG:host='%s' port='%s' dbname='%s' user='%s' password='%s'" % (host,  port,  database,  user,  pwd)
        try:
            self.pgconn = psycopg2.connect(self.connectstr)
        except:
            raise ModuleError,  (self, "cannot access a PostGIS connection")
            
        self.setResult("PostGisSession",  self)

    def __del__(self):
        try:
            if self.pgconn:
                self.pgconn.close()
        except:
            pass


class PostGisCursor():
    """MixIn class responsible for opening a cursor
        on the PostGisSession/ connection"""

    def __init__(self,  conn_type = "psycopg2"):

        if conn_type == "ogr":
            self.conn_type = "ogr"
        else:
            self.conn_type = "psycopg2"
            
            

    def cursor(self,  PostGisSessionObj):
        
        if self.conn_type == "psycopg2":
            try:
                self.curs = PostGisSessionObj.pgconn.cursor()
                return True
            except:
                return False
        else:
            return True
            #below is not necessary, I suspect
            try:
                self.curs = ogr.Open(PostGisSessionObj.ogr_connectstr)
                return True
            except:
                return False
                

    def __del__(self):
        try:
            if self.curs:
                if self.conn_type == "psycopg2":
                    self.curs.close()
                else:
                    self.curs.ReleaseResultLayer(0)
                    self.curs.Destroy()
        except:
            pass


class PostGisFeatureReturningCursor(PostGisCursor, MemFeatureModel):
    """Returns data in the form of a eo4vistrails FeatureModel"""
    #multi inheritance of module subclasses is a problem
    def __init__(self):
        PostGisCursor.__init__(self,   conn_type = "ogr")
        MemFeatureModel.__init__(self)
        

    def compute(self):
        """Will need to fetch a PostGisSession object on its input port
        Overrides supers method"""
        if self.cursor(self.getInputFromPort("PostGisSessionObject")) == True:
            print "got cursor"
            try:
                sql_input = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
                sql_input = sql_input.split(";")[0]#ogr does not want a trailing ';'
                print "got sql input"
                ogr_conn = self.getInputFromPort("PostGisSessionObject").ogr_connectstr               
                print "checking connection: connectstr: %s, sql: %s" % (ogr_conn,  sql_input)
                self.loadContentFromDB(ogr_conn, sql_input)
                
            except:
                raise ModuleError,  (PostGisFeatureReturningCursor,  "Could not execute SQL Statement")
            #do stuff with this return list -> make it into an OGR dataset
            #see (http://trac.osgeo.org/postgis/wiki/UsersWikiOGR, http://www.gdal.org/ogr/drv_memory.htm, ogr memory driver python in google)
            #for now, to test, print to stdout
            #could be implemented directy via OGR's SQL capability
            #print "data are: "
            #print self.sql_return_list


class PostGisBasicReturningCursor(Module, PostGisCursor):
    """
    Returns data in the form of a python list (as per psycopg2).
    Only one dataset per module is allowed, defined by the SQL 
    statement in the editor
    """

    def __init__(self):
        Module.__init__(self)
        PostGisCursor.__init__(self)

    def compute(self):
        """Will need to fetch a PostGisSession object on its input port
        Overrides supers method"""
        if self.cursor(self.getInputFromPort("PostGisSessionObject")) == True:
            try:
                port_input = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
                self.curs.execute(port_input)
                self.sql_return_list = self.curs.fetchall()
                self.setResult('records',  self.sql_return_list)
                self.curs.close()
            except:
                raise ModuleError,  (PostGisFeatureReturningCursor,  "Could not execute SQL Statement")
                #set output port to receive this list


class PostGisNonReturningCursor(Module, PostGisCursor):
    """Returns a list of result strings to indicate success or failure; usually to be
    used as a way to do an insert, update, delete operation on the
    database, for example

    Unlike the 'returning' cursors, can support multiple SQL 
    statements, separated by the ';', as expected by PostgreSQL
    """
    
    def __init__(self):
        Module.__init__(self)
        PostGisCursor.__init__(self)

    def compute(self):
        """Will need to fetch a PostGisSession object on its input port
        Overrides supers method"""
        if self.cursor(self.getInputFromPort("PostGisSessionObject")) == True:
            try:
                #we could be dealing with multiple requests here, so parse string and execute requests one by one
                resultstatus =[]
                port_input = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
                port_input = port_input.rstrip()
                port_input = port_input.lstrip()
                for query in port_input.split(";"):
                    if len(query) != 0:
                        if query[len(query)-1] != ";": query = query + ";"
                        #print "about to execute: " + query
                        self.curs.execute(query)
                        resultstatus.append(self.curs.statusmessage)

                self.setResult('status', resultstatus)
                self.curs.close()
            except:
                raise ModuleError,  (PostGisFeatureReturningCursor,  "Could not execute SQL Statement")


class SQLSourceConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, None,
                                           False, False, parent)

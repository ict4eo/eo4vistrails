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
In particular, this module provides PostGIS clients via psycopg2.
This is not a SQL Builder - it assumes you know SQL and, in particular,
spatial SQL as provided by PostGIS.
You will need to write raw sql by hand. Provides a session a.k.a. a postgis
connection and allows random queries to be executed against the chosen database.
"""

# library
# third party
import psycopg2
from psycopg2 import ProgrammingError

from packages.eo4vistrails.geoinf.datamodels.QgsLayer import QgsVectorLayer
from packages.eo4vistrails.utils.DataRequest import PostGISRequest
from packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.utils.Array import NDArray
from packages.eo4vistrails.utils.session import Session

from core.modules.vistrails_module import ModuleError, NotCacheable
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
        self.host = self.forceGetInputFromPort('postgisHost', 'localhost')
        self.port = self.forceGetInputFromPort('postgisPort', '5432')
        self.user = self.forceGetInputFromPort('postgisUser', 'default')
        self.pwd =  self.forceGetInputFromPort('postgisPassword', 'default')
        self.database = self.forceGetInputFromPort('postgisDatabase', 'default')

        self.connectstr = "host=" + self.host+ " dbname=" + self.database + \
                          " user=" + self.user + " password=" + self.pwd

        self.setResult("PostGisSession",  self)


@RPyCSafeModule()
class PostGisNumpyReturningCursor(ThreadSafeMixin, RPyCModule):
    """Returns data in the form of a eo4vistrails FeatureModel if user binds to self output port"""
    #multi inheritance of module subclasses is a problem
    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)
        
    def compute(self):
        """Will need to fetch a PostGisSession object on its input port
        Overrides supers method"""
        pgsession = self.getInputFromPort("PostGisSessionObject")
        
        try:
            import random
            random.seed()
            
            pgconn = psycopg2.connect(pgsession.connectstr)
            
            curs = pgconn.cursor('VISTRAILS'+str(random.randint(0,10000)))

            sql_input = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
            '''here we substitute input port values within the source'''
            
            parameters = {}
            for k in self.inputPorts:
                if k not in ['source', 'PostGisSessionObject', 'rpycnode', 'self']:
                    v = self.getInputFromPort(k)
                    parameters[k] = v
                       
            curs.execute(sql_input, parameters)
            
            import numpy

            rec = curs.fetchone()
            
            if rec:
                dtype = []                
                i = 0
                sameType = True
                firstType = type(rec[0])
                for item in rec:
                    #If they not all the same type just remeber as False
                    sameType = sameType and (type(item) == firstType)
                    #TODO: What about dates? How should they be handled.
                    dtype.append((curs.description[i][0], type(item)))
                    i += 1
                    
                curs.scroll(-1)
                
                out = NDArray()

                npRecArray = numpy.fromiter(curs, dtype=dtype)
                
                #QUESTION: Is this meaningfull in all cases, should we be doing this
                if sameType:
                    npArray = npRecArray.view(dtype=firstType).reshape(-1,len(npRecArray[0]))               
                    out.set_array(npArray)
                else:
                    out.set_array(npRecArray)
                
                print out
            
                self.setResult('nummpyArray', out)
                
            else:
                raise ModuleError,  (PostGisNumpyReturningCursor,  "no records returned")
                
        except Exception as ex:
            print ex
            raise ModuleError,  (PostGisNumpyReturningCursor,  "Could not execute SQL Statement")
        finally:
            curs.close()
            pgconn.close()

@RPyCSafeModule()
class PostGisFeatureReturningCursor(ThreadSafeMixin, RPyCModule):
    """Returns data in the form of a eo4vistrails FeatureModel
    if user binds to self output port
    """
    #multi inheritance of module subclasses is a problem
    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)

    def compute(self):
        """Will need to fetch a PostGisSession object on its input port
        Overrides supers method"""
        pgsession = self.getInputFromPort("PostGisSessionObject")
        
        try:

            sql_input = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
            
            '''here we substitute input port values within the source'''
            for k in self.inputPorts:
                if k not in ['source', 'PostGisSessionObject', 'rpycnode', 'self']:
                    value = self.getInputFromPort(k)
                    sql_input = sql_input.replace(k, value.__str__())

            postGISRequest = PostGISRequest()
            postGISRequest.setConnection(pgsession.host,
                              pgsession.port,
                              pgsession.database,
                              pgsession.user,
                              pgsession.pwd)
            postGISRequest.setDataSource('',                 #schema must be blank
                              '('+sql_input+')',
                              'the_geom',         #TODO: assuming the_geom, this mus be looked up
                              '',                 #where clause must be blank
                              'gid')              #TODO: assuming gid, this mus be looked up

            #select * from ba_modis_giglio limit 10000
            #TODO: make sure that the user can select a layer name or we generate a random one
            qgsVectorLayer = QgsVectorLayer(
                postGISRequest.get_uri(),
                postGISRequest.get_layername(),
                postGISRequest.get_driver())

            self.setResult('PostGISRequest', postGISRequest)
            self.setResult('QgsVectorLayer', qgsVectorLayer)

        except Exception as ex:
            print ex
            raise ModuleError,  (PostGisFeatureReturningCursor, \
                                 "Could not execute SQL Statement")

@RPyCSafeModule()
class PostGisBasicReturningCursor(ThreadSafeMixin, RPyCModule):
    """
    Returns data in the form of a python list (as per psycopg2).
    Only one dataset per module is allowed, defined by the SQL
    statement in the editor
    """

    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)

    def compute(self):
        """Fetches and executes a PostGisSession object on the input port

        Overrides supers method"""
        pgsession = self.getInputFromPort("PostGisSessionObject")

        try:
            pgconn = psycopg2.connect(pgsession.connectstr)
        
            curs = pgconn.cursor()
            
            sql_input = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
            
            '''here we substitute input port values within the source'''
            parameters = {}
            for k in self.inputPorts:
                if k not in ['source', 'PostGisSessionObject', 'rpycnode', 'self']:
                    v = self.getInputFromPort(k)
                    parameters[k] = v
            
            print curs.mogrify(sql_input, parameters)
            curs.execute(sql_input, parameters)
            
            sql_return_list = curs.fetchall()
            
            self.setResult('records',  sql_return_list)
            
        except Exception as ex:
            print ex
            raise ModuleError,  (PostGisFeatureReturningCursor,\
                                 "Could not execute SQL Statement")
        finally:
            curs.close()
            pgconn.close()
            #set output port to receive this list

@RPyCSafeModule()
class PostGisNonReturningCursor(NotCacheable, ThreadSafeMixin, RPyCModule):
    """Returns a list of result strings to indicate success or failure.

    Usually to be used as a way to do an insert, update, delete operation
    on the database, for example

    Unlike the 'returning' cursors, can support multiple SQL statements,
    separated by a ';' (as expected by PostgreSQL)
    """

    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)

    def compute(self):
        """Will need to fetch a PostGisSession object on its input port
        Overrides supers method"""
        pgsession = self.getInputFromPort("PostGisSessionObject")
        print pgsession
        try:
            # we could be dealing with multiple requests here,
            #   so parse string and execute requests one by one            
            pgconn = psycopg2.connect(pgsession.connectstr)
            
            curs = pgconn.cursor()
            
            resultstatus =[]
            sql_input = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
            #sql_input = sql_input.rstrip()
            #sql_input = sql_input.lstrip()
            for query in sql_input.split(";"):
                if len(query) > 0:
                    values = {}
                    for k in self.inputPorts:
                        if k not in ['source', 'PostGisSessionObject', 'rpycnode', 'self']:
                            values[k] = self.getInputFromPort(k)
                    
                    theLen = 0
                    for k, v in values.items():
                        if type(v) in [list]:
                            if theLen == 0 and len(v) > 0:
                                theLen = len(v)
                            if theLen > 0 and len(v) != theLen:
                                print k, v, theLen
                                raise ModuleError,  (PostGisNonReturningCursor,\
                                         "All list like params must have same length")
                    if theLen > 0:
                        parameters = [{} for x in xrange(theLen)]
                        for i in range(theLen):
                            for k, v in values.items():
                                if type(v) in [list]:
                                    parameters[i][k] = v[i]
                                else:
                                    parameters[i][k] = v
                        
                        curs.executemany(query+";", parameters)                        
                        pgconn.commit()
                        resultstatus.append(curs.statusmessage)
                    else:
                        parameters = {}
                        for k, v in values.items():
                            parameters[k] = v
                        
                        curs.execute(query+";", parameters)
                        
                        resultstatus.append(curs.statusmessage)
            
            pgconn.commit()
            
            self.setResult('status', resultstatus)
            
        except Exception as ex:
            print ex
            raise ModuleError,  (PostGisFeatureReturningCursor,\
                                 "Could not execute SQL Statement")
        finally:
            curs.close()
            pgconn.close()
            

class SQLSourceConfigurationWidget(SourceConfigurationWidget):
    """NOT IN USE"""
    pass
    '''removed by tvz so as to allow for parameterisation of SQL queries'''
    #def __init__(self, module, controller, parent=None):
    #    SourceConfigurationWidget.__init__(self, module, controller, None,
    #                                       False, False, parent)

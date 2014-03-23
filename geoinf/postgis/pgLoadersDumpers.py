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
"""This module provides PostGIS Loader/ Dumper functionality.

These modules rely on the presence of psql, and essentially wrap:

*    shp2pgsql -> vector data (as shapefile) loader
*    pgsql2shp -> vector data to shapefile dumper
*    wktRaster loader
*    wktRaster dumper

.. note::
    In future, maybe add a multidimensional loader?
"""


from PyQt4 import QtCore, QtGui
# vistrails
from core.modules.vistrails_module import ModuleError, NotCacheable, Module
from gui.modules.source_configure import SourceConfigurationWidget
from core.modules import basic_modules
# eo4vistrails
from vistrails.packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin
from vistrails.packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
# local
from subprocess import call, Popen, PIPE


class Shape2PostGIS(Module):
    """A wrapper for the PostGIS utility shp2pgsql
    
    Takes a PostGIS Session object to extract connection info
    
    Requires:
    
    *   a shapefile (be sure that when you choose the shapefile,
        delete the .shp extension
    *   a tablename
    
    Optionally:

    *   choose to spatially index
    *   choose a character encoding (defaults to LATIN1)
    *   choose to simplify geometries
    *   choose a SRS (defaults to WGS84 Lat/Lon, a.k.a. EPSG:4326)
    '"""

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        pg_session = self.getInputFromPort("PostGisSessionObject")
        self.host = pg_session.host
        self.port = pg_session.port
        self.db = pg_session.database
        self.user = pg_session.user
        self.pwd = pg_session.pwd

        self.shp_name = self.forceGetInputFromPort("InputShapefile", None)
        self.table_name = self.forceGetInputFromPort("TableName", None)
        self.epsg_srs = self.forceGetInputFromPort("EPSG_SRS", "4326")
        self.index = self.forceGetInputFromPort("Index",  False)
        self.simplify = self.forceGetInputFromPort("Simplify",  False)
        self.encoding = self.forceGetInputFromPort("Encoding",  "LATIN1")
        if self.buildSQL():
            self.loadSQL()

    def buildSQL(self):
        if self.shp_name is None or self.table_name is None:
            raise ModuleError(self, "Shapefile path or Tablename not supplied")
        params = [' -s ', self.epsg_srs]
        if self.index:
            params.append(' -I')
        if self.simplify:
            params.append(' -S')
        params.append(' -W %s' % self.encoding)
        params.append(" " + self.shp_name)
        params.append(" " + self.table_name)
        params.append(" " + self.db)
        #TODO:use vistrails tmpfile framework
        params.append(" > ")
        self.sqlfile = self.interpreter.filePool.create_file(
            prefix=self.table_name, suffix=".sql")
        #self.sqlfile = "/tmp/" + self.table_name + ".sql"
        params.append(self.sqlfile.name)
        params_as_str = ""
        for param in params:
            params_as_str += param

        buildercommand = "shp2pgsql " + params_as_str

        call(buildercommand, shell=True)
        return True

    def loadSQL(self):
        loadercommand = "psql -d %s -h %s -p %s -U %s -w -f %s" % (
            self.db, self.host, self.port, self.user, self.sqlfile.name)
        print "About to load: %s" % self.sqlfile.name
        psql_env = dict(PGPASSWORD='%s' % (self.pwd))
        p = Popen([loadercommand], env=psql_env, stdin=PIPE, stdout=PIPE,
                  stderr=PIPE, shell=True)
        data = p.stdout.read()
        err = p.stderr.read()
        p.terminate()
#        print "about to delete sqlfile: %s" % self.sqlfile.name
#        rmcommand = "rm " + self.sqlfile.name
#        print rmcommand
#        call(rmcommand, shell=True)
        return True

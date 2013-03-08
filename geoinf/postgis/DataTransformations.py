# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
###
### This full package extends VisTrails, providing GIS/Earth Observation
### ingestion, pre-processing, transformation, analytic and visualisation
### capabilities . Included is the abilty to run code transparently in
### OpenNebula cloud environments. There are various software
### dependencies, but all are FOSS.
###
### This file may be used under the terms of the GNU General Public
### License version 2.0 as published by the Free Software Foundation
### and appearing in the file LICENSE.GPL included in the packaging of
### this file.  Please review the following to ensure GNU General Public
### Licensing requirements will be met:
### http://www.opensource.org/licenses/gpl-license.php
###
### If you are unsure which license is appropriate for your use (for
### instance, you are interested in developing a commercial derivative
### of VisTrails), please contact us at vistrails@sci.utah.edu.
###
### This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
### WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
###
#############################################################################
"""This module provides tools to transform data into a format suitable for
insertion into a PostgreSQL database.
"""
# library
# third-party
import psycopg2
from psycopg2 import ProgrammingError
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin
# local


#@RPyCSafeModule()
class InputStream(Module):
    """TODO: add documentation"""

    _input_ports = [('in_datalist', '(edu.utah.sci.vistrails.basic:List)'),
                    ('in_python_datatype',
                     '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('datalist', '(edu.utah.sci.vistrails.basic:List)'),
                    ('python_datatype',
                     '(edu.utah.sci.vistrails.basic:String)')]

    def __init__(self):
        #ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        d = self.getInputFromPort('in_datalist')
        t = self.getInputFromPort('in_python_datatype')
        if not d is None and len(d):
            self.setResult('datalist', d)
        if t:
            self.setResult('python_datatype', t)


#@RPyCSafeModule()
class pgSQLMergeInsert(Module):
    """Take a set of lists of data and zip them into a set of records.
    
    These records can be inserted into a PostgreSQL database.
    """

    _input_ports = [('input_streams', '(edu.utah.sci.vistrails.basic:List)'),
                    ('dbsession',
                     '(za.co.csir.eo4vistrails:PostGisSession:data|postGIS)'),
                    ('table', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('result', '(edu.utah.sci.vistrails.basic:String)')]

    def __init__(self):
        #ThreadSafeMixin.__init__(self)
        Module.__init__(self)
        self.tblmeta = []

    def compute(self):
        input_streams = self.getInputListFromPort('input_streams')
        db_session = self.getInputFromPort("dbsession")
        tbl = self.getInputFromPort("table")
        try:
            pgconn = psycopg2.connect(db_session.connectstr)
            curs = pgconn.cursor()
            if self.tblmeta == []:
                curs.execute("select column_name, data_type, column_default \
                from information_schema.columns where table_name='%s';" % tbl)
                self.tblmeta = curs.fetchall()

            colnames = ""
            default_vals = []
            for metaitem in self.tblmeta:
                colnames = colnames + metaitem[0] + ","
                if not metaitem[2] is None:
                    default_vals.append(self.tblmeta.index(metaitem))
            colnames = colnames[:len(colnames) - 1]

            ziprecords = zip(*input_streams)
            insert_stmt = "INSERT INTO %s (%s) VALUES " % (tbl, colnames)
            records = []
            if default_vals != []:
                for record in ziprecords:
                    record_as_list = list(record)
                    for dv in default_vals:
                        record_as_list.insert(dv, 'DEFAULT')
                        records.append(str(tuple(record_as_list)))
            else:
                for record in ziprecords:
                    records.append(str(record))

            insert_stmt += ", ".join(records) + ";"
            insert_stmt = insert_stmt.replace("'DEFAULT'", "DEFAULT")
            #print insert_stmt

            curs.execute(insert_stmt)
            pgconn.commit()
            self.setResult('result', curs.statusmessage)

        except Exception as ex:
            #print "DataTranformations:123", ex
            raise ModuleError(pgSQLMergeInsert, \
                              "Could not execute SQL Statement: %s" % ex)
        finally:
            curs.close()
            pgconn.close()

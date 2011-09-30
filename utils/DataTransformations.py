# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin


@RPyCSafeModule()
class InputStream(ThreadSafeMixin, Module):
    ''''''
    _input_ports = [('in_datalist', '(edu.utah.sci.vistrails.basic:List)'),
                    ('in_python_datatype', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('datalist', '(edu.utah.sci.vistrails.basic:List)'),
                    ('python_datatype', '(edu.utah.sci.vistrails.basic:String)')]                
    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)
    
    def compute(self):
        d = self.getInputFromPort('in_datalist')
        t = self.getInputFromPort('in_python_datatype')
        if d:
            self.setResult('datalist', d)
        if t:
            self.setResult('python_datatype', t)
            
            
@RPyCSafeModule()            
class pgSQLMergeInsert(ThreadSafeMixin, Module):
    '''A Module for taking a set of lists of data and zipping them into a set of records that can be inserted into a SQL database'''
    _input_ports = [('input_streams', '(za.co.csir.eo4vistrails:InputStream:utils)'),  \
                            ('dbsession', '(za.co.csir.eo4vistrails:PostGisSession:postGIS)'),  \
                            ('table', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('result', '(edu.utah.sci.vistrails.basic:String)')]                
    
    
    def __init__(self):
        ThreadSafeMixin.__init__(self)
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
                curs.execute("select column_name, data_type, column_default from \
                information_schema.columns where table_name = '%s';" % tbl)
                self.tblmeta = curs.fetchall()
                
            colnames = ""  
            default_vals = []
            for metaitem in self.tblmeta:
                colnames = colnames + metaitem[0] + ","
                if metaitem[2] != "":
                    default_vals.append(self.tblmeta.index(metaitem))
                
            colnames = colnames[:len(colnames) -1]
            
            
            ziprecords = zip(*input_streams)
            
            insert_stmt  = "INSERT INTO %s (%s) VALUES " % (tbl,  colnames)
            if default_vals != []:
               
                for record in ziprecords:
                    record_as_list = list(record)
                    for dv in default_vals:
                        record_as_list.insert(dv, 'DEFAULT')
                    
                        insert_stmt = insert_stmt + str(tuple(record_as_list)) + ", "
            else:
                
                for record in ziprecords:
                    insert_stmt = insert_stmt + str(record) + ", "
            
            insert_stmt = insert_stmt[:len(insert_stmt)-1] + ";"
            
            curs.execute(insert_stmt)
            pgconn.commit()
            self.setResult('result', curs.statusmessage)
            
        except Exception as ex:
            #print "PostGIS:292 ",ex
            raise ModuleError, (SQLMergeInsert, \
                                 "Could not execute SQL Statement")
        finally:
            curs.close()
            pgconn.close()
            
            

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
"""This module forms part of the eo4vistrails capabilities - it is used to
handle write csv files to a given location with or without headers.
"""
import csv
import os,  os.path
from core.modules.vistrails_module import Module,  ModuleError
from core.modules import basic_modules
from core.modules.basic_modules import Module
from packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin

@RPyCSafeModule()
class CsvWriter(ThreadSafeMixin,  Module):
    
    _input_ports  = [('directorypath', '(edu.utah.sci.vistrails.basic:String)'), 
                               ('filename',  '(edu.utah.sci.vistrails.basic:String)'), 
                               ('column_header_list',  '(edu.utah.sci.vistrails.basic:List)'),
                               ('data_values_listoflists',  '(edu.utah.sci.vistrails.basic:List)') 
                               ]
    _output_ports = [('created_file', '(edu.utah.sci.vistrails.basic:String)')]
    
    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)
        
        
        
    def compute (self) :
        fn = self.getInputFromPort('filename') 
        dp = self.getInputFromPort('directorypath')
        chl = self.getInputFromPort('column_header_list')
        dvll = self.getInputFromPort('data_values_listoflists')
        
        if not os.path.isdir(dp):
            os.mkdir(dp)
            
        newfile = os.path.join(dp, fn)
        try:
            csvfile = csv.writer(open(newfile, 'w'),  delimiter=',',  quotechar="'")
            
            if chl != []:
                csvfile.writerow(chl)
            if dvll != []:
                csvfile.writerows(dvll)
            self.setResult('created_file', newfile)
        
        except:
            
            pass
            #raise an error
        csvfile = None #flush to disk
    
    
    

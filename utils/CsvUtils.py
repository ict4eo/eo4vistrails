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

from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin

@RPyCSafeModule()
class ListDirContent(ThreadSafeMixin,  Module):
    '''A utility for walking a directory to discover csv files with specified filenames 
    Returns a list of full filenames. Runs on RPyC nodes, and in such a case would 
    refer to that remote filesystem
    '''
    _input_ports  = [('directorypath', '(edu.utah.sci.vistrails.basic:String)'),
                               ('file_extensions',  '(edu.utah.sci.vistrails.basic:List)')
                               ]
    _output_ports = [('csv_list', '(edu.utah.sci.vistrails.basic:List)')]    

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)
        
    def compute(self):
        filename_list = []
        dp = self.getInputFromPort('directorypath')
        fel = self.getInputFromPort('file_extensions')
        
        def _index(directory):
            #stack = [directory]
            files = []
            #while stack:
                #directory = stack.pop()
            for filename in os.listdir(directory):
                fullname = os.path.join(directory,  filename)
                files.append(fullname)
                    #if os.path.isdir(fullname) and not os.path.islink(fullname):
                    #    stack.append(fullname)
            return files
            
        for fname in _index(dp):
            try:
                if fname.split(".")[-1] in fel:
                    filename_list.append(fname)
            except:
                #likely a directory, ignore
                pass
        
        self.setResult('csv_list',  filename_list)
    
@RPyCSafeModule()
class CsvReader(ThreadSafeMixin,  Module):
    
    _input_ports  = [('fullfilename',  '(edu.utah.sci.vistrails.basic:String)'), 
                               ('column_header_list',  '(edu.utah.sci.vistrails.basic:List)'),
                               ('known_delimiter',  '(edu.utah.sci.vistrails.basic:String)') 
                               ]
    _output_ports = [('read_data_listoflists', '(edu.utah.sci.vistrails.basic:List)')]
    
    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)
        
    def compute (self) :
        fn = self.getInputFromPort('fullfilename') 
        chl = self.getInputFromPort('column_header_list')
        kd = self.getInputFromPort('known_delimiter')
        if kd == "":
            #assume ','
            kd = ','
            
        list_of_lists = []

        if os.path.isfile(fn):
            try:
                if len(chl) > 0:
                    list_of_lists.append(chl)
                csvfile = csv.reader(open(fn, 'r'),  delimiter = kd)
                for row in csvfile:
                     list_of_lists.append(row)
                self.setResult('read_data_listoflists', list_of_lists)
            except Exception, ex:
                print ex
            csvfile = None
 
        
        
        
@RPyCSafeModule()
class CsvWriter(ThreadSafeMixin,  Module):
    '''Simple csv file writer utility, taking in a directory path where 
    the file will be written to,  a filename , a column headings list 
    (which can be an empty list) and a list of  lists containing the 
    rows of data to write to file. Returns the full pathname to the 
    file created if succesful. Runs on RPyC nodes, and in such a case 
    would refer to that remote filesystem'''
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
            
            if len(chl) > 0:
                csvfile.writerow(chl)
            if len(dvll) > 0:
                csvfile.writerows(dvll)
            
            self.setResult('created_file', newfile)
        
        except Exception, ex:
            print ex

            #raise an error
        csvfile = None #flush to disk
    
    
    

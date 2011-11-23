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
"""This module forms part of the eo4vistrails capabilities. It is used to
handle reading, writing and filtering CSV files, with or without headers.
"""
# library
import csv
import os
import os.path
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin


@RPyCSafeModule()
class ListDirContent(ThreadSafeMixin, Module):
    """A utility for walking a directory to discover csv files with specified
    filenames.

    Returns:
     *  A list of full filenames. On RPyC nodes, will refer to files on that
        remote filesystem.
    """

    _input_ports = [('directorypath', '(edu.utah.sci.vistrails.basic:String)'),
                    ('file_extensions', '(edu.utah.sci.vistrails.basic:List)')]
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
                fullname = os.path.join(directory, filename)
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

        self.setResult('csv_list', filename_list)


@RPyCSafeModule()
class CsvReader(ThreadSafeMixin, Module):
    """Simple csv file reader utility.

    Requires:

    Input ports:
     *  a full directory path and filename to be read
     *  an optional list of column headers
     *  an optional item delimiter (defaults to a ",")

    Returns:

    Output ports:
     *  a list of lists, containing all data from the file
    """

    _input_ports = [('fullfilename', '(edu.utah.sci.vistrails.basic:String)'),
                    ('column_header_list', '(edu.utah.sci.vistrails.basic:List)'),
                    ('known_delimiter', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('read_data_listoflists', '(edu.utah.sci.vistrails.basic:List)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        fn = self.getInputFromPort('fullfilename')
        chl = self.forceGetInputFromPort('column_header_list', "")
        kd = self.forceGetInputFromPort('known_delimiter', ",")

        list_of_lists = []

        if os.path.isfile(fn):
            try:
                if len(chl) > 0:
                    list_of_lists.append(chl)
                csvfile = csv.reader(open(fn, 'r'), delimiter=kd)
                for row in csvfile:
                    list_of_lists.append(row)
                self.setResult('read_data_listoflists', list_of_lists)
            except Exception, e:
                self.raiseError('Cannot create output list: %s' % str(e))
            csvfile = None


@RPyCSafeModule()
class CsvWriter(ThreadSafeMixin, Module):
    """Simple csv file writer utility.

    Requires:
     *  a directory path to which the file will be written
     *  a filename
     *  a column headings list (which can be an empty)
     *  a list of lists containing the rows of data to write to file

    Returns:
     *  a full pathname to the file created, if successful. On RPyC nodes,
        will refer to files on that remote filesystem.
    """

    _input_ports = [('directorypath', '(edu.utah.sci.vistrails.basic:String)'),
                    ('filename', '(edu.utah.sci.vistrails.basic:String)'),
                    ('column_header_list', '(edu.utah.sci.vistrails.basic:List)'),
                    ('data_values_listoflists', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('created_file', '(edu.utah.sci.vistrails.basic:String)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        fn = self.getInputFromPort('filename')
        dp = self.getInputFromPort('directorypath')
        chl = self.getInputFromPort('column_header_list')
        dvll = self.getInputFromPort('data_values_listoflists')

        if not os.path.isdir(dp):
            os.mkdir(dp)

        newfile = os.path.join(dp, fn)
        try:
            csvfile = csv.writer(open(newfile, 'w'),
                                 delimiter=',',
                                 quotechar="'")
            if len(chl) > 0:
                csvfile.writerow(chl)
            if len(dvll) > 0:
                csvfile.writerows(dvll)
            self.setResult('created_file', newfile)
        except Exception, e:
            self.raiseError('Cannot set create CSV: %s' % str(e))

        csvfile = None  # flush to disk


@RPyCSafeModule()
class CsvFilter(ThreadSafeMixin, Module):
    """Read CSV file and filter data according to specific parameters.

    Input ports:
        fullfilename:
            a full directory path and filename to be read
        sample_set:
            switch to enable output of a maximum of the first 10 rows  (default False)
        transpose:
            switch to enable output of a transposed set of data (default False)
        delimiter:
            an optional item delimiter (defaults to a ",")
        output_rows:
            an optional specification of which rows appear in the output
        output_rows:
            an optional specification of which rows appear in the output

    The "output_" specification uses the following syntax:
     *  N: a single row/col
     *  N-M: a range of rows/cols
     *  N, M: two different rows/cols (chain additional singles or ranges)

    Output ports
        csv_file:
            a CSV file, containing all filtered data from the file
        dataset:
            a list of lists, containing all filtered data from the file
        datagroup:
            a grouped list of lists, containing all filtered data from the file
        html:
            an HTML 'view' string, containing all filtered data from the file
    """

    _input_ports = [('fullfilename', '(edu.utah.sci.vistrails.basic:String)'),
                    ('delimiter', '(edu.utah.sci.vistrails.basic:String)'),
                    ('sample_set', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('transpose', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('output_rows', '(edu.utah.sci.vistrails.basic:String)'),
                    ('output_cols', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('csv_file', '(edu.utah.sci.vistrails.basic:File)'),
                    ('dataset', '(edu.utah.sci.vistrails.basic:List)'),
                    ('datagroups', '(edu.utah.sci.vistrails.basic:List)'),
                    ('html', '(edu.utah.sci.vistrails.basic:String)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def html_table(self, list):
        """Create an HTML table string from a 'list of lists'."""
        table = '<table>'
        for sublist in list:
            table = table + '\n' + '  <tr><td>'
            table = table + '</td><td>'.join(sublist)
            table = table + '</td></tr>' + '\n'
        table = table + '</table>'
        return table

    def create_csv(self, list):
        """Create an output CSV from a 'list of lists'."""
        newfile = self.interpreter.filePool.create_file(suffix='.foo')
        #print "csvutils.245:", newfile, type(newfile)
        try:
            csvfile = csv.writer(open(newfile, 'w'),
                                 delimiter=',',
                                 quotechar="'")
            if len(list) > 0:
                csvfile.writerows(list)
            return newfile
        except Exception, e:
            self.raiseError('Cannot create CSV file: %s' % str(e))
            return None

    def get_output_specs(self, items):
        """Return a list of values from an input string.

        Accepts:

        A single string, with a specification that uses the following syntax:
         *  N: a single integer; or a single Excel column letter
         *  N-M: a range of integers; or a range of Excel column letters
         *  N, M, ...: multiple different single/range values

        Returns:

         *  A list of integers

        """

        def to_int(index):
            s = 0
            pow = 1
            try:
                return int(index)
            except:
                pass
            for letter in index[::-1]:
                d = int(letter,36) - 9
                s += pow * d
                pow *= 26
            # excel starts column numeration from 1
            return s

        list = []
        if items:
            try:
                item_list = items.split(',')
                for item in item_list:
                    if '-' in item:
                        _range = item.split('-')
                        _short = [x for x in range(to_int(_range[0]),
                                                   to_int(_range[1]) + 1)]
                        list = list + _short
                    else:
                        list.append(to_int(item))
            except Exception, e:
                self.raiseError('Cannot process output specifications: %s' % str(e))
                return []
        if list:
            return set(list)  # remove duplicates
        else:
            return list  # empty list


    def compute(self):
        fullname = self.getInputFromPort('fullfilename')
        delimiter = self.forceGetInputFromPort('delimiter', ",")
        sample = self.forceGetInputFromPort("sample_set", False)
        transpose = self.forceGetInputFromPort("transpose", False)
        output_rows = self.forceGetInputFromPort("output_rows", "")
        output_cols = self.forceGetInputFromPort("output_cols", "")

        list_of_lists = []
        column_list = self.get_output_specs(output_cols)
        row_list = self.get_output_specs(output_rows)
        #print "csvutils.315: ", column_list, row_list

        if os.path.isfile(fullname):
            try:
                csvfile = csv.reader(open(fullname, 'r'), delimiter=delimiter)
                for key, row in enumerate(csvfile):
                    #print "csvutils.321: ", key, row
                    if sample and key > 9:
                        break
                    else:
                        if not column_list:
                            if not row_list:
                                list_of_lists.append(row)
                            else:
                                if row + 1 in row_list:
                                    list_of_lists.append(row)
                        else:
                            if row_list and not row + 1 in row_list:
                                pass
                            else:
                                row_out = []
                                # filter each column
                                for key, c in enumerate(row):
                                    if key + 1 in column_list:
                                        row_out.append(c)
                                list_of_lists.append(row_out)
                self.setResult('dataset', list_of_lists)
                if 'html' in self.outputPorts:
                    self.setResult('html', self.html_table(list_of_lists))
                if 'csv_file' in self.outputPorts:
                    self.setResult('csv_file', self.create_csv(list_of_lists))
            except Exception, ex:
                print ex
            csvfile = None

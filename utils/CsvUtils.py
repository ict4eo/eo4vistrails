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

    Input ports:
        directory path:
            place in which files are to be discovered
        file_extensions:
            a list of types of files to be discovered

    Output ports:
        csv_list:
            A list of full filenames. On RPyC nodes, will refer to files on
            that remote filesystem.

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

    Input ports:
        fullfilename:
            name of input file (including a full directory path)
        column_header_list:
            optional list of column headings
        delimiter:
            an optional item delimiter (defaults to a ",")

    Output ports:
        read_data_listoflists:
            a list of lists, containing all data from the file

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
                raise ModuleError(self, 'Cannot create output list: %s' % str(e))
            csvfile = None


@RPyCSafeModule()
class CsvWriter(ThreadSafeMixin, Module):
    """Simple csv file writer utility.

    Input ports:
        directory path:
            place to which the file will be written
        filename:
            name of output file
        column_header_list:
            optional list of column headings
        data_values_listoflists:
            list of lists contain the rows of data to write to file

    Output ports:
        created_file:
            a full pathname to the file created, if successful. On RPyC nodes,
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
            raise ModuleError(self, 'Cannot set create CSV: %s' % str(e))

        csvfile = None  # flush to disk


@RPyCSafeModule()
class CsvFilter(ThreadSafeMixin, Module):
    """Read CSV file and filter data according to specific parameters.

    Input ports:
        fullfilename:
            a full directory path and filename to be read
        delimiter:
            an optional item delimiter (defaults to a ",")
        sample_set:
            switch to enable output of a maximum of the first 10 rows
            (default False)
        transpose:
            switch to enable output of a transposed set of data (default False)
        header_in:
            switch to indicate if the first row in the input data set contains
            header data (default False); this header row is then ignored for
            data import
        header_out:
            switch to indicate if the first row (likely containing headers)
            should be written to output (default True)
        filter_rows:
            an optional specification of which rows appear in the output (this
            notation assumes a starting row number of '1')
        filter_cols:
            an optional specification of which columns appear in the output
            (this notation assumes a starting column number of '1')
        pairs:
            x,y pairs, in a semi-colon delimited string, representing desired
            output tuples (see the `datapairs` output port) to be extracted
            from incoming lists; each X or Y represents a different list (this
            notation assumes a starting list number of '1')

    The "filter_" specification uses the following syntax:
     *  N: a single integer; or a single Excel column letter
     *  N-M: a range of integers; or a range of Excel column letters
     *  N, M, ...: multiple different single/range values

    Output ports:
        csv_file:
            a CSV file, containing all filtered data from the file
        dataset:
            a list of lists, containing all filtered data from the file
        datapairs:
            a paired list of tuples, containing all filtered data from the file
            in the form: [(X1,Y1), (X2,Y2), ... (Xn,Yn)]
        html:
            an HTML 'view' string, containing all filtered data from the file

    """

    _input_ports = [('fullfilename', '(edu.utah.sci.vistrails.basic:String)'),
                    ('delimiter', '(edu.utah.sci.vistrails.basic:String)'),
                    ('sample_set', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('transpose', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('header_in', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('header_out', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('filter_rows', '(edu.utah.sci.vistrails.basic:String)'),
                    ('filter_cols', '(edu.utah.sci.vistrails.basic:String)'),
                    ('pairs', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [('csv_file', '(edu.utah.sci.vistrails.basic:File)'),
                    ('dataset', '(edu.utah.sci.vistrails.basic:List)'),
                    ('datapairs', '(edu.utah.sci.vistrails.basic:List)'),
                    ('html_file', '(edu.utah.sci.vistrails.basic:File)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))

    def transpose_array(self, lists):
        """Swap rows and columns from a 'list of lists'.

        This works for equal length and unequal length arrays. See:
        http://code.activestate.com/recipes/410687-transposing-a-list-of-lists-with-different-lengths/
        """
        if not lists:
            return []
        return map(lambda *row: list(row), *lists)

    def create_html(self, lists, heading=False, delimiter=','):
        """Create a file with an HTML table from a 'list of lists'."""
        table = '<table border="1">'
        for key, list in enumerate(lists):
            if heading and not key:
                table = table + '\n' + '  <tr><th>'
                table = table + '</th><th>'.join(str(column) for column in list)
                table = table + '</th></tr>'
            else:
                table = table + '\n' + '  <tr><td>'
                table = table + '</td><td>'.join(str(column) for column in list)
                table = table + '</td></tr>'
        table = table + '\n' + '</table>'
        #print  "csvutils.293:", table

        try:
            output_file = self.interpreter.filePool.create_file(suffix='.html')
            f = open(str(output_file.name), "w")
            f.write(table)
            f.close()
            return output_file
        except Exception, e:
            self.raiseError('Cannot create CSV file: %s' % str(e))
            return None

    def create_csv(self, data_list, heading=False, delimiter=','):
        """Create a CSV file from a 'list of lists'."""
        output_file = self.interpreter.filePool.create_file(suffix='.csv')
        try:
            csvfile = csv.writer(open(output_file.name, 'w'),
                                 delimiter=delimiter,
                                 quotechar="'")
            if len(data_list) > 0:
                csvfile.writerows(data_list)
            return output_file
        except Exception, e:
            self.raiseError('Cannot create CSV file: %s' % str(e))
            return None

    def create_paired_tuples(self, pairs, lists):
        """Create a list of paired tuples from a 'list of lists'.

        Accepts:

         *  pairs - a string, that uses the  syntax:
             *  N,M: a single paired set of values
             *  N,M; O,P; ...: multiple paired values
            (where positional numbering starts from `1`)
         *  lists - a list of lists

        Returns:
         *  A list of paired tuples if valid inputs, else None

        """
        pair_list = []
        if pairs:
            try:
                item_list = pairs.split(';')
                #print "csv:339", item_list
                for key, item in enumerate(item_list):
                    if ',' in item:
                        pair_values = item.split(',')
                        #print "   csv:343", item, pair_values
                        x = lists[int(pair_values[0]) - 1]
                        y = lists[int(pair_values[1]) - 1]
                        for key, i in enumerate(x):
                            pair_list.append((i, y[key]))
                    else:
                        pass
            except Exception, e:
                self.raiseError('Cannot create pairs of tuples: %s' % str(e))
                return None  # fail
        if pair_list:
            return pair_list
        else:
            return None  # fail

    def get_filter_specs(self, items):
        """Create a list of values from numeric ranges defined in a string.

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
                d = int(letter, 36) - 9
                s += pow * d
                pow *= 26
            # excel starts column numbering from 1
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
        header_in = self.forceGetInputFromPort("header_in", False)
        header_out = self.forceGetInputFromPort("header_out", True)
        filter_rows = self.forceGetInputFromPort("filter_rows", "")
        filter_cols = self.forceGetInputFromPort("filter_cols", "")
        pairs = self.forceGetInputFromPort("pairs", "")

        list_of_lists = []
        cols_list = self.get_filter_specs(filter_cols)
        rows_list = self.get_filter_specs(filter_rows)
        #print "csvutils.421: ", cols_list, rows_list
        if not header_in:
            header_out = False  # cannot process a row that is not there...

        if os.path.isfile(fullname):
            try:
                csvfile = csv.reader(open(fullname, 'r'), delimiter=delimiter)
                #print "csvutils.422:", header_in, header_out
                for key, row in enumerate(csvfile):
                    if key == 0 and header_in and not header_out:
                        # skip header row
                        #print "csvutils:432 - skip header_out", key
                        pass
                    elif key > 9  and sample:
                        # have the sample data now...
                        break
                    else:
                        #print "csvutils.438: data", key, row
                        if not cols_list:
                            if not rows_list:
                                list_of_lists.append(row)
                            else:
                                if row + 1 in rows_list:
                                    list_of_lists.append(row)
                        else:
                            if rows_list and not row + 1 in rows_list:
                                pass
                            else:
                                row_out = []
                                # filter each column
                                for key, c in enumerate(row):
                                    if key + 1 in cols_list:
                                        row_out.append(c)
                                list_of_lists.append(row_out)
                #print "csvutils.455:pre_transpose ", list_of_lists
                if transpose:
                    list_of_lists = self.transpose_array(list_of_lists)
                #print "csvutils.458:post_transpose ", list_of_lists
                self.setResult('dataset', list_of_lists)
                if 'html_file' in self.outputPorts:
                    self.setResult('html_file', self.create_html(
                                                    list_of_lists,
                                                    header_out, delimiter))
                if 'csv_file' in self.outputPorts:
                    self.setResult('csv_file', self.create_csv(
                                                    list_of_lists,
                                                    header_out, delimiter))
                if 'datapairs' in self.outputPorts:
                    self.setResult('datapairs', self.create_paired_tuples(
                                                    pairs, list_of_lists))
            except Exception, e:
                self.raiseError('Unable to run compute: %s' % str(e))
            csvfile = None

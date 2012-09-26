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
handle reading, writing and filtering Excel files.
"""
# library
import os
import os.path
import sys
from datetime import date, datetime, time
# third-party
import xlrd
import xlwt
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin
# local
from readexcel import read_excel


@RPyCSafeModule()
class ExcelExtractor(ThreadSafeMixin, Module):
    """Read Excel file and extract data either as a dictionary or a list.

    Input ports:
        file_in:
            input Excel file
        sheets:
            A list of worksheet numbers, or names, that must be displayed.
            If None, then all sheets will be processed.

    Output ports:
        data_list:
            Excel data as a list of lists; each item in the outer list
            corresponds to one worksheet; each inner lists contains the data
            from that worksheet.
        dictionary
            Excel data as a dictionary of dictionaries; each outer dictionary
            is keyed with the name of the Excel worksheet name; and each inner
            dictionary contains the data from that worksheet.
    """

    _input_ports = [('file_in', '(edu.utah.sci.vistrails.basic:File)'),
                    ('sheets', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('data_list', '(edu.utah.sci.vistrails.basic:List)'),
                     ('data_dictionary', '(edu.utah.sci.vistrails.basic:Dictionary)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ': %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def compute(self):
        file_in = self.getInputFromPort('file_in')
        sheets = self.forceGetInputFromPort('sheets', None)

        if file_in:
            try:
                _list = []
                _dict = {}
                xls = read_excel(file_in.name)
                xls.set_sheet_list(sheets)
                if not xls.sheet_list:
                    self.raiseError('Invalid list of "sheets"; please check Excel file')
                    return None
                else:
                    # create outputs per selected sheet name
                    for sheet_name in xls.sheet_list:
                        _list.append(xls.iter_list(sheet_name))
                        _dict[sheet_name] = xls.iter_dict(sheet_name)
                    self.setResult('data_list', _list)
                    self.setResult('data_dictionary', _dict)
            except Exception, e:
                self.raiseError('Unable to run compute: %s' % str(e))
            csvfile = None
        else:
            self.raiseError('Invalid or missing input file/filename')


@RPyCSafeModule()
class ExcelSplitter(ThreadSafeMixin, Module):
    """Read Excel file and create a new file according to specific parameters.

    """

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        pass


@RPyCSafeModule()
class ExcelChopper(ThreadSafeMixin, Module):
    """Read Excel file and remove rows/columns according to parameters.

    Note that only values will be reproduced in the new file; all formatting
    (e.g. alignment and colors) will be lost.

    Input ports:
        file_in:
            input Excel file
        sheets:
            A list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed.
        rows:
            A list of row numbers that must be removed. If None, then no
            rows will be removed.
        columns:
            A list of column numbers that must be removed. If None, then no
            columns will be removed.
        file_name_out:
            an optional full directory path and filename to be writte; if None
            then a temporary file will be created

    Output ports:
        file_out:
            output Excel file
    """

    _input_ports = [('file_in', '(edu.utah.sci.vistrails.basic:File)'),
                    ('sheets', '(edu.utah.sci.vistrails.basic:List)'),
                    ('rows', '(edu.utah.sci.vistrails.basic:List)'),
                    ('columns', '(edu.utah.sci.vistrails.basic:List)'),
                    ('file_name_out', '(edu.utah.sci.vistrails.basic:String)'),]
    _output_ports = [('file_out', '(edu.utah.sci.vistrails.basic:File)'),]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ': %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def compute(self):
        file_in = self.forceGetInputFromPort('file_in', None)
        file_name_out = self.forceGetInputFromPort('file_name_out', "")
        sheets = self.forceGetInputFromPort('sheets', None)
        remove_rows = self.forceGetInputFromPort("rows", None)
        remove_cols = self.forceGetInputFromPort("columns", None)

        if file_in:
            try:
                xls = read_excel(file_in.name)
                xls.set_sheet_list(sheets)
                if not xls.sheet_list:
                    self.raiseError('Invalid list of "sheets"; please check Excel file')
                    return
                results = {}
                # create output dict; entry per selected sheet name
                for sheet_name in xls.sheet_list:
                    sheet = xls.book.sheet_by_name(sheet_name)
                    out_list = []
                    for row in range(sheet.nrows):
                        if remove_rows and row in remove_rows:
                            pass  # do not add to output
                        else:
                            row_list = xls._parse_row(sheet, row,
                                                      date_as_tuple=True)
                            if remove_cols:
                                for col in range(sheet.ncols):
                                    if col in remove_cols:
                                        row_list[col].delete
                            out_list.append(row_list)
                    # results
                    results[sheet_name] = out_list
                    #print "excelutils 199", result[sheet_name]
                if results:
                    # create output file
                    if not file_name_out:
                        new_file = self.interpreter.filePool.create_file(suffix='.xls')
                    else:
                        try:
                            new_file = open(str(file_name_out), "w")
                        except:
                            self.raiseError('Invalid output filename!')
                            return
                    # create data in Excel file
                    workbook = xlwt.Workbook()
                    for key in results.iterkeys():
                        worksheet = workbook.add_sheet(key)
                        # add row/col data
                        for row_index, row in enumerate(results[key]):
                            for col_index, value in enumerate(row):
                                worksheet.write(row_index, col_index, value)
                    workbook.save(new_file.name)
                    # port
                    self.setResult('file_out', new_file)

            except Exception, e:
                self.raiseError('Unable to run compute: %s' % str(e))
            csvfile = None
        else:
            self.raiseError('Invalid or missing input file/filename')


@RPyCSafeModule()
class ExcelReplacer(ThreadSafeMixin, Module):
    """Read Excel file and create a new file according to specific parameters.
    """

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        pass


@RPyCSafeModule()
class ExcelFiller(ThreadSafeMixin, Module):
    """Read Excel file and fill in data according to specific parameters.

    Input ports:
        file_in:
            an optional file object to be read
        filename_in:
            an optional full directory path and filename to be read
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
        flatten:
            switch to indicate if nested lists should be combined into one
            single list (default False); only works for one "level" of nesting
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
            a list of lists, containing all filtered data from the file (or
            a single list, if flatten option selected)
        datapairs:
            a paired list of tuples, containing all filtered data from the file
            in the form: [(X1,Y1), (X2,Y2), ... (Xn,Yn)]
        html:
            an HTML 'view' string, containing all filtered data from the file

    """

    _input_ports = [('file_in', '(edu.utah.sci.vistrails.basic:File)'),
                    ('delimiter', '(edu.utah.sci.vistrails.basic:String)'),
                    ('sample_set', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('transpose', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('header_in', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('header_out', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('filter_rows', '(edu.utah.sci.vistrails.basic:String)'),
                    ('filter_cols', '(edu.utah.sci.vistrails.basic:String)'),
                    ('flatten', '(edu.utah.sci.vistrails.basic:Boolean)'),
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
        if error:
            raise ModuleError(self, msg + ': %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def compute(self):
        file_in = self.forceGetInputFromPort('file_in', None)
        fullname = self.forceGetInputFromPort('filename_in', "")
        delimiter = self.forceGetInputFromPort('delimiter', ",")
        sample = self.forceGetInputFromPort("sample_set", False)
        transpose = self.forceGetInputFromPort("transpose", False)
        header_in = self.forceGetInputFromPort("header_in", False)
        header_out = self.forceGetInputFromPort("header_out", True)
        filter_rows = self.forceGetInputFromPort("filter_rows", "")
        filter_cols = self.forceGetInputFromPort("filter_cols", "")
        flatten = self.forceGetInputFromPort("flatten", False)
        pairs = self.forceGetInputFromPort("pairs", "")

        if file_in:
            try:
                pass
            except Exception, e:
                self.raiseError('Unable to run compute: %s' % str(e))
            csvfile = None
        else:
            self.raiseError('Invalid or missing input file/filename')

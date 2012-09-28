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

DATE_FORMAT = 'YYYY/MM/DD'


@RPyCSafeModule()
class ExcelBase(ThreadSafeMixin, Module):
    """Read Excel file and allow for operations according to parameters.

    Input ports:
        file_in:
            input Excel file
        sheets:
            A list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed.
        rows:
            A list of row numbers. Uses the following formats:
             *  N: single number; removes the first N rows
             *  N, M: two numbers; removes from row N to row M
             *  N, M, P, ...: three or more numbers; removes numbered rows
        columns:
            A list of column numbers. Uses the following formats:
             *  N: single number; removes the first N columns
             *  N, M: two numbers; removes from column N to column M
             *  N, M, P, ...: three or more numbers; removes numbered columns
        file_name_out:
            an optional full directory path and filename to be writte; if None
            then a temporary file will be created

    Output ports:
        file_out:
            output Excel file
    """

    # NOTE: inheriting class MUST set:  _xxx_ports = self.xxx_ports
    _input_ports = [
                    ('file_in', '(edu.utah.sci.vistrails.basic:File)'),
                    ('sheets', '(edu.utah.sci.vistrails.basic:List)'),
                    ('rows', '(edu.utah.sci.vistrails.basic:List)'),
                    ('columns', '(edu.utah.sci.vistrails.basic:List)'),
                    ('file_name_out', '(edu.utah.sci.vistrails.basic:String)')]
    _output_ports = [
                    ('file_out', '(edu.utah.sci.vistrails.basic:File)')]

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

    def excel_list(self, items, reverse=False, sort=False, zero_base=False):
        """Create (sorted) list of values from a "range" input List.

        Args:
            items: List of numbers
            reverse:  Sort final list in reverse order
            sort:  Sort final list
            zero_base:  if true, List numbering starts from 0

        Assumes list numbering starts from 1, and alters this, if needed, to a
        0-based numbering:
        *  [N]: single number;
           returns a list from 0 to N-1
        *  [N, M]: two numbers;
           returns a list from N-1 to M-1
        *  [N, M, P, ...]: three or more numbers;
           returns a list [N-1, M-1, P-1, ...]
        """
        #print "excelutils:67", items, len(items)
        offset = 1
        if zero_base:
            offset = 0
        try:
            #print "excelutils:72", items
            if len(items) == 1:
                list_items = [x for x in range(offset, items[0] + offset)]
            elif len(items) == 2:
                list_items = [x for x in range(items[0], items[1] + offset)]
            else:
                list_items = items
            if list_items:
                list_items = [x - offset for x in list_items]
            #print "excelutils:81", list_items
            if reverse:
                return sorted(list_items, reverse=True)
            elif sort:
                return sorted(list_items)
            else:
                return list_items
        except:
            return []

    def excel_write(self, results, date_style=None, file_name_out=None):
        """Write an Excel book, based on a dictionary with a list of lists.

        Args:
            results: dictionary
                each dictionary item corresponds to a worksheet (the key is the
                name); that contains rows of column values
            style:
                an XFStyle object, in whihc to write dates
            file_name_out: string
                if None, a temp file is created
        """
        if not file_name_out:
            new_file = self.interpreter.filePool.create_file(suffix='.xls')
        else:
            try:
                new_file = open(str(file_name_out), "w")
            except:
                return None
        if not date_style:
            # set date format
            date_style = xlwt.XFStyle()
            date_style.num_format_str = DATE_FORMAT
        # create data in Excel file
        workbook = xlwt.Workbook()
        for key in results.iterkeys():
            worksheet = workbook.add_sheet(key)
            # add row/col data
            for row_index, row in enumerate(results[key]):
                for col_index, value in enumerate(row):
                    #print "excelutils:316", row_index, col_index, value
                    if isinstance(value, (list, tuple)):  # date
                        dt = datetime(*value)
                        worksheet.write(row_index, col_index,
                                        dt, date_style)
                    else:
                        worksheet.write(row_index, col_index,
                                        value)
        workbook.save(new_file.name)
        return new_file

    def compute(self):
        """inheriting class should extend this via:
            super(NewClassName, self).compute()
            # other code....
        """
        # process port inputs
        self.file_in = self.forceGetInputFromPort('file_in', None)
        self.file_name_out = self.forceGetInputFromPort('file_name_out', "")
        try:
            _sheets = self.getInputListFromPort('sheets')
            if isinstance(_sheets[0], (list, tuple)):
                _sheets = _sheets[0]  # remove Vistrails "wrapper"
        except:
            _sheets = []
        try:
            _rows = self.getInputListFromPort("rows")
            if isinstance(_rows[0], (list, tuple)):
                _rows = _rows[0]  # remove "wrapper" that Vistrails may add
        except:
            _rows = []
        try:
            _cols = self.getInputListFromPort("columns")
            if isinstance(_cols[0], (list, tuple)):
                _cols = _cols[0]  # remove "wrapper" that Vistrails may add
        except:
            _cols = []
        #store lists to be processed
        self.sheets = _sheets
        self.process_rows = self.excel_list(_rows)
        # allow for "popping" in a loop
        self.process_cols = self.excel_list(_cols, reverse=True)
        #set up dict/list to process files
        if self.file_in:
            try:
                self.xls = read_excel(self.file_in.name)
            except:
                self.raiseError('Invalid Excel file')
            self.xls.set_sheet_list(self.sheets)
            if not self.xls.sheet_list:
                self.raiseError('Invalid "sheets"; please check Excel file')
        else:
            self.raiseError('Invalid or missing input file/filename')


@RPyCSafeModule()
class ExcelExtractor(ExcelBase):
    """Read Excel file and extract data either as a dictionary or a list.

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

    _input_ports = [
            ('file_in', '(edu.utah.sci.vistrails.basic:File)'),
            ('sheets', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [
            ('data_list', '(edu.utah.sci.vistrails.basic:List)'),
            ('data_dictionary', '(edu.utah.sci.vistrails.basic:Dictionary)')]

    def __init__(self):
        ExcelBase.__init__(self)

    def compute(self):
        super(ExcelExtractor, self).compute()
        try:
            _list = []
            _dict = {}
            for sheet_name in self.xls.sheet_list:
                _list.append(self.xls.iter_list(sheet_name))
                _dict[sheet_name] = self.xls.iter_dict(sheet_name)
            self.setResult('data_list', _list)
            self.setResult('data_dictionary', _dict)
        except Exception, e:
            self.raiseError('Unable to run compute: %s' % str(e))


@RPyCSafeModule()
class ExcelSplitter(ExcelBase):
    """Read Excel file and create a new file according to specific parameters.
    """

    def __init__(self):
        ExcelBase.__init__(self)

    def compute(self):
        super(ExcelSplitter, self).compute()
        # TODO - complete process...


@RPyCSafeModule()
class ExcelChopper(ExcelBase):
    """Read Excel file and remove rows/columns according to parameters.

    Note that only values will be reproduced in the new file; all formatting
    (e.g. alignment, font style and colors) will be lost.

    Input ports:
        rows:
            If None, then no rows will be removed.
        columns:
            If None, then no columns will be removed.
    """

    def __init__(self):
        ExcelBase.__init__(self)

    def compute(self):
        super(ExcelChopper, self).compute()
        results = {}
        # create output dict; one entry per selected sheet name
        for sheet_name in self.xls.sheet_list:
            sheet = self.xls.book.sheet_by_name(sheet_name)
            out_list = []
            for row in range(sheet.nrows):
                if self.process_rows and row in self.process_rows:
                    pass  # do not add to output
                else:
                    row_list = self.xls._parse_row(sheet, row,
                                              date_as_tuple=True)
                    for col in self.process_cols:  # reverse order
                        try:
                            row_list.pop(col)  # not in output
                        except:
                            pass  # ignore invalid cols
                    out_list.append(row_list)
            results[sheet_name] = out_list
            #print "excelutils:349", result[sheet_name]
        if results:
            # create output file
            new_file = self.excel_write(results, self.file_name_out)
            if new_file:
                self.setResult('file_out', new_file)  # port
            else:
                self.raiseError('Unable to create output file!')


@RPyCSafeModule()
class ExcelReplacer(ExcelBase):
    """Read Excel file and replace values according to specific parameters.
    """

    def __init__(self):
        ExcelBase.__init__(self)

    def compute(self):
        super(ExcelReplacer, self).compute()
        # TODO - complete process...


@RPyCSafeModule()
class ExcelFiller(ExcelBase):
    """Read Excel file and fill in data according to specific parameters.
    """

    def __init__(self):
        ExcelBase.__init__(self)

    def compute(self):
        super(ExcelFiller, self).compute()
        # TODO - complete process...


@RPyCSafeModule()
class NotUsed(ThreadSafeMixin, Module):
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

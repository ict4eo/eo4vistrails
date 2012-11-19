# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
###
### This full package extends VisTrails, providing GIS/Earth Observation
### ingestion, pre-processing, transformation, analytic and visualisation
### capabilities . Included is the ability to run code transparently in
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
from core.modules.basic_modules import File, String, Boolean, new_constant
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.tools.utils.DropDownListWidget import ComboBoxWidget
from packages.eo4vistrails.tools.utils.listutils import check_if_equal
# local
from readexcel import read_excel

DATE_FORMAT = 'YYYY-MM-DDTHH:MM:SS'
SHEET_NAME_SIZE = 27  # maximum length of an Excel worksheet name (i.e. 31 - 4)


@RPyCSafeModule()
class ExcelBase(ThreadSafeMixin, Module):
    """An abstract VisTrails class for reading and processing an Excel file.

    This base class contains common methods and properties.

    The compute() method initialises data for ports that are common to all
    classes; but should be extended (via super) to perform processing specific
    to the inherited class.

    Input ports:
        file_in:
            input Excel file
        file_name_out:
            an optional full directory path and filename to be written; if None
            then a temporary file will be created
        sheets:
            a list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed. Sheet numbering starts
            from 1.
        rows:
            values:
                a list of row numbers. Row numbering starts from 1.
            range:
                a Boolean indicating if the row numbers specify a range.

            If range is `False`, the row values are just numbers of individual
            rows. If range is `True`, the following notation applies:
                 *  N: the first N rows
                 *  N, M: all rows from N to M inclusive
                 *  N, M, P: every "Pth" row, between N to M inclusive
        columns:
            values:
                a list of column numbers. Column numbering starts from 1.
            range:
                a Boolean indicating if the column numbers specify a range.

            If range is `False`, the column values are just numbers of
            individual columns. If range is `True`, the following notation
            applies:
                 *  N: the first N columns
                 *  N, M: all columns from N to M inclusive
                 *  N, M, P: every "Pth" column, between N to M inclusive
    Output ports:
        file_out:
            output Excel file
    """

    _input_ports = [
        ('file_in', '(edu.utah.sci.vistrails.basic:File)'),
        ('sheets', '(edu.utah.sci.vistrails.basic:List)'),
        ('rows', '(edu.utah.sci.vistrails.basic:List,\
edu.utah.sci.vistrails.basic:Boolean)',
            {"defaults": str([[], False]),
             "labels": str(["values", "range"])}),
        ('columns', '(edu.utah.sci.vistrails.basic:List,\
edu.utah.sci.vistrails.basic:Boolean)',
                    {"defaults": str([[], False]),
                     "labels": str(["values", "range"])}),
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

    def make_list(self, lst=None):
        """"Return a list from any given single element."""
        if not lst:
            return []
        if hasattr(lst, '__iter__'):
            return list(lst)
        else:
            return [lst]

    def create_excel_file(self):
        """Create a new Excel output file; named or temporary"""
        if not self.file_name_out:
            new_file = self.interpreter.filePool.create_file(suffix='.xls')
        else:
            try:
                new_file = open(str(self.file_name_out), "w")
            except:
                return None
        return new_file

    def excel_list(self, items, ranged=False, reverse=False, sort=False,
                   zero_base=False):
        """Create (sorted) list of values from a numeric input list.

        Args:
            items: a List of numbers
            ranged: if True, create a ranged list
            reverse:  if True, sort final list in reverse order
            sort:  if True, sort final list
            zero_base:  if True, List numbering starts from 0

        Assumes list numbering starts from 1, and alters this, if needed, to a
        0-based numbering.

        If ranged is `True`, the following notation applies:
         *  N: a list from 0 to N
         *  N, M: a list from N-1 to M-1
         *  N, M, P: a list from N to M, with an interval of P
        """
        #print "excelutils:166", items, len(items), type(items[0]), ranged
        offset = 1
        if zero_base:
            offset = 0
        try:
            if ranged and len(items) == 1:
                list_items = [x for x in range(offset, items[0] + offset)]
            elif ranged and len(items) == 2:
                list_items = [x for x in range(items[0], items[1] + offset)]
            elif ranged and len(items) == 3:
                list_items = [x for x in range(items[0], items[1] + offset,
                                               items[2])]
            else:
                list_items = items
            if list_items:
                list_items = [x - offset for x in list_items]
                if reverse:
                    return sorted(list_items, reverse=True)
                elif sort:
                    return sorted(list_items)
                else:
                    return list_items
            else:
                return list_items
        except:
            return []

    def excel_write(self, results, date_style=None):
        """Write an Excel workbook, based on a dictionary with a list of lists.

        Args:
            results: dictionary
                each dictionary item corresponds to a worksheet (the key is the
                name); that contains arrays of column values
            date_style:
                an XFStyle object, in which format to write dates
        """
        new_file = self.create_excel_file()
        if new_file:
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
                        #print "excelutils:218", row_index, col_index, value
                        if isinstance(value, (list, tuple)):  # date OR time
                            try:
                                _date = datetime(*value)
                                worksheet.write(row_index, col_index,
                                                _date, date_style)
                            except ValueError:
                                try:
                                    _time = time(*value[3:])
                                    worksheet.write(row_index, col_index,
                                                    _time, date_style)
                                except:
                                    self.raiseError(
                                        'Date "%s" format error in cell (%s, %s)' %
                                        (value, row_index, col_index))
                        else:
                            worksheet.write(row_index, col_index,
                                            value)
            workbook.save(new_file.name)
        return new_file

    def save_results(self, results):
        """Save results into designated output file and assign to a port."""
        if results:
            new_file = self.excel_write(results, self.file_name_out)
            if new_file:
                self.setResult('file_out', new_file)  # port
            else:
                self.raiseError('Unable to create output file!')

    def compute(self):
        """inheriting class should extend this via:
            super(NewClassName, self).compute()
            # other code... e.g. to read/change the Excel file
        """
        # process port inputs
        self.file_in = self.forceGetInputFromPort('file_in', None)
        self.file_name_out = self.forceGetInputFromPort('file_name_out', "")
        self.sheets = self.make_list(self.forceGetInputListFromPort('sheets'))
        # rows and cols
        if self.forceGetInputFromPort('rows'):
            _rows, self.row_range = self.forceGetInputFromPort('rows')
            _rows = self.make_list(_rows)
        else:
            _rows, self.row_range = [], False
        #print "excelutils:253", type(_rows), _rows, self.row_range
        if self.forceGetInputFromPort('columns'):
            _cols, self.col_range = self.forceGetInputFromPort('columns')
            _cols = self.make_list(_cols)
        else:
            _cols, self.col_range = [], False
        self.rows = _rows
        self.cols = _cols
        #store lists to be processed
        self.process_rows = self.excel_list(_rows, ranged=self.row_range)
        # allow for "popping" in a loop
        self.process_cols = self.excel_list(_cols, ranged=self.col_range,
                                            reverse=True)
        #set-up connection to Excel file (but does not read the contents here!)
        if self.file_in:
            try:
                self.xls = read_excel(self.file_in.name)
            except:
                self.raiseError('Invalid Excel file')
            self.xls.set_sheet_list(self.sheets)
            if not self.xls.sheet_list:
                self.raiseError('Invalid "sheets"; please check Excel file')
        else:
            self.raiseError('Invalid or missing input file')


@RPyCSafeModule()
class ExcelExtractor(ExcelBase):
    """Read Excel file and extract all data either as a dictionary or a list.

        file_in:
            input Excel file
        sheets:
            a list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed. Sheet numbering starts
            from 1.

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
class ExcelMerger(ExcelBase):
    """Read Excel file and merge values from adajacent rows/columns according
    to specific parameters.

    ExcelMerger will combine items in the set of columns specified and replace
    the item in the first column (of the set) with the combined result.  This
    will be repeated for all of the specified rows of the specified sheets.
    If no columns are specified, then no merger will occur.

    Input ports:
        file_in:
            input Excel file
        file_name_out:
            an optional full directory path and filename to be write; if None
            then a temporary file will be created
        sheets:
            a list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed. Sheet numbering starts
            from 1.
        rows:
            values:
                a list of row numbers to be processed.  If None, then all rows
                will be processed. Row numbering starts from 1.
            range:
                a Boolean indicating if the row numbers specify a range.

            If range is `False`, the row values are just numbers of individual
            rows. If range is `True`, the following notation applies:
                 *  N: the first N rows
                 *  N, M: all rows from N to M inclusive
                 *  N, M, P: every "Pth" row, between N to M inclusive
        columns:
            values:
                a list of column numbers to be processed. If None, then NO
                columns will be processed. Column numbering starts from 1.
            range:
                a Boolean indicating if the column numbers specify a range.

            If range is `False`, the column values are just numbers of
            individual columns. If range is `True`, the following notation
            applies:
                 *  N: the first N columns
                 *  N, M: all columns from N to M inclusive
                 *  N, M, P: every "Pth" column, between N to M inclusive
        cell_joiner: string
            the string that is to be used as a spacer between the merged cell
            values (defaults to a single space)

    Output ports:
        file_out:
            output Excel file
    """

    _input_ports = [
        ('cell_joiner', '(edu.utah.sci.vistrails.basic:String)'),
    ]

    def __init__(self):
        ExcelBase.__init__(self)

    def compute(self):
        super(ExcelMerger, self).compute()
        cell_joiner = self.forceGetInputFromPort('cell_joiner', " ")
        results = {}
        # create output dict; one entry per selected sheet name
        for sheet_name in self.xls.sheet_list:
            sheet = self.xls.book.sheet_by_name(sheet_name)
            out_list = []
            if self.process_cols:
                # process all rows by default
                if not self.process_rows:
                    self.process_rows = range(sheet.nrows)
                for row in self.process_rows:
                    row_list = self.xls._parse_row(sheet, row,
                                               date_as_tuple=True)
                    items = [row_list[col] for col in self.process_cols \
                                           if row_list[col] is not None]
                    try:
                        new_value = cell_joiner.join(items)
                        row_list[col] = new_value
                    except TypeError:
                        self.raiseError('Unable to merge numeric values!')
                    out_list.append(row_list)
                results[sheet_name] = out_list
        self.save_results(results)


@RPyCSafeModule()
class ExcelSplitter(ExcelBase):
    """Read Excel file and create a new file according to specific parameters.

    The new file will have a set of worksheets, created by splitting existing
    sheets along row/columns. For example, if a sheet is split by rows and
    columns, then each "block" within the split will form a new worksheet.

    Input ports:
        file_in:
            input Excel file
        file_name_out:
            an optional full directory path and filename to be written; if None
            then a temporary file will be created
        sheets:
            a list of worksheet numbers, or "names", that must be processed.
            If None, then all sheets will be processed. Sheet numbering starts
            from 1.
        rows:
            values:
                a list of row numbers on which to split a worksheet. Row
                numbering starts from 1.
            range:
                a Boolean indicating if the row numbers specify a range.

            If range is `False`, the row values are just numbers of individual
            rows. If range is `True`, the following notation applies:
                 *  N: the first N rows
                 *  N, M: all rows from N to M inclusive
                 *  N, M, P: every "Pth" row, between N to M inclusive

            If the list is empty, the sheet will be split according to the
            type of 'cell_match'.
        columns:
            values:
                a list of column numbers on which to split a worksheet. Column
                numbering starts from 1.
            range:
                a Boolean indicating if the column numbers specify a range.

            If range is `False`, the column values are just numbers of
            individual columns. If range is `True`, the following notation
            applies:
                 *  N: the first N columns
                 *  N, M: all columns from N to M inclusive
                 *  N, M, P: every "Pth" column, between N to M inclusive

            If the list is empty, the sheet will be split according to the
            type of 'cell_match'.
        cell_match:
            type:
                the type of cell value on which the split will take place.
                ('Is Blank' will split on blank rows & columns instead of a
                value)
            value:
                the cell value (string) on which the split will take place (if
                'cell_match' is not 'Is Blank')

                for date value, the format used must be 'YYYY-MM-DD HH:MM:SS.x'
                for example, to find all dates in November 2010, use a value of
                2010-11, and a "Contains" `type`
            case_sensitive:
                a Boolean switch to determine if the `cell_match` is case
                sensitive or not (the default is *not* case sensitive)
        split_offset:
            the number of rows, or rows and columns, away from the split point,
            at which the split must take place.

    Output ports:
        file_out:
            output Excel file
    """

    _input_ports = [
        ('cell_match', '(za.co.csir.eo4vistrails:Excel Match:tools|excel,\
edu.utah.sci.vistrails.basic:String,edu.utah.sci.vistrails.basic:Boolean)',
            {"defaults": str(['contains', "", False]),
             "labels": str(["type", "value", "case_sensitive"])}),
        ('split_offset', '(edu.utah.sci.vistrails.basic:Integer,\
edu.utah.sci.vistrails.basic:Integer)',
                    {"defaults": str([0, 0]),
                     "labels": str(["rows", "columns"])}),
    ]

    def __init__(self):
        ExcelBase.__init__(self)

    def add_block(self, row, col):
        """Add new unique block and alter limits of existing blocks.

        Blocks are used to track which sections of an incoming worksheet need
        to be split into a new worksheet in the outgoing file.

        Each block is an array composed of:
         *  sheet_name
         *  top_left_row, top_left_col: cell co-ordinates array
         *  bottom_left_row, bottom_left_col: cell co-ordinates array
         *  row_flag, col_flag: Boolean array
                flags indicate if the bottom limits have already been reset
                (by default, each block extends to the edge of the worksheet)
        """
        candidate = [self.sheet.name, [row, col],
                     [self.sheet.nrows, self.sheet.ncols], [True, True]]
        duplicate = False
        for block in self.blocks:
            # alter limits on unaltered existing blocks
            if block[1][0] < row and block[3][0]:
                block[2][0] = row - 1
                block[3][0] = False
            if block[1][1] < col and block[3][1]:
                block[2][1] = col - 1
                block[3][1] = False
            if [row, col] == block[1]:
                duplicate = True  # can only be one block per top,left cell
        if not duplicate:
            self.blocks.append(candidate)

    def process_row(self, row_no, row_list):
        """Find matching elements in a row; add new block/s when matched.

        Args:
            row_no: integer
                current row
            row_list: list
                list of (value, type) entries for a row
        """
        for col_no, col_value in enumerate(row_list):
            # get column value as search-able type
            if col_value[1] == 1:  # text
                value = col_value[0]
            elif col_value[1] == 2:  # float
                value = str(col_value[0])
            elif col_value[1] == 3:  # date
                value = str(col_value[0])  # eg. '2012-11-16 09:40:37.75'
            elif col_value[1] == 4:  # bool
                if col_value[0]:
                    value = 'true'
                else:
                    value = 'false'
            elif col_value[1] == 5:
                value = xlrd.error_text_from_code[col_value[0]]
            elif col_value[1] == 0:  # empty
                value = ""
            else:
                value = col_value[0]
            # switch for case-sensitive
            cell_value = self.cell_value
            if not self.case_sensitive:
                try:
                    value = value.lower()
                    cell_value = self.cell_value.lower()
                except:
                    pass
            # change row/col split locations according to split_offset
            split_row, split_col = row_no, col_no
            col_offset, row_offset = None, None
            if self.split_offset and len(self.split_offset) >= 2:  # col value
                try:
                    col_offset = int(self.split_offset[1])
                except:
                    self.raiseError('Column offset is not an integer.')
            if self.split_offset and len(self.split_offset) > 0:  # row value
                try:
                    row_offset = int(self.split_offset[0])
                except:
                    self.raiseError('Row offset is not an integer.')
            if col_offset:  # col
                if col_offset < 0:
                    split_col = max(split_col + col_offset, 0)
                if col_offset > 0:
                    split_col = min(split_col + col_offset, self.sheet.ncols)
            if row_offset:  # row
                if row_offset < 0:
                    split_row = max(split_row + row_offset, 0)
                if row_offset > 0:
                    split_row = min(split_row + row_offset, self.sheet.nrows)
            # perform value comparison
            #print "excelutils:526", row_no, col_no, split_row, split_col
            if self.cell_match == 'exact' and value == cell_value:
                self.add_block(split_row, split_col)
            elif self.cell_match == 'starts' and \
                value[0:len(cell_value)] == cell_value:
                self.add_block(split_row, split_col)
            elif self.cell_match == 'contains' and cell_value in value:
                self.add_block(split_row, split_col)

    def compute(self):
        super(ExcelSplitter, self).compute()
        # class-specific ports
        if self.forceGetInputFromPort('cell_match'):
            self.cell_match, self.cell_value, self.case_sensitive = \
                self.forceGetInputFromPort('cell_match')
        else:
            self.cell_match, self.cell_value, self.case_sensitive = \
                'blank', None, False
        if self.forceGetInputFromPort('split_offset'):
            self.split_offset = self.forceGetInputFromPort('split_offset')
        else:
            self.split_offset = (0, 0)
        #print "excelutils:548", type(self.split_offset), self.split_offset

        # switch to sensible default (???) if a value is filled in
        if self.cell_value and not self.cell_match:
            self.cell_match = 'contains'

        self.blocks = []  # see add_block()
        for sheet_name in self.xls.sheet_list:
            self.sheet = self.xls.book.sheet_by_name(sheet_name)
            # store list of any blank cols
            blank_cols = []
            if self.cell_match in ['blank', 'cols']:
                for col in range(self.sheet.ncols):
                    col_list = self.xls._parse_column(self.sheet, col,
                                                      date_as_tuple=True)
                    if col_list and col_list[0] in [None, ''] \
                    and check_if_equal(col_list):  # all blanks!
                        blank_cols.append(col)
                if not '0' in blank_cols:
                    blank_cols.insert(0, -1)  # will always split at first col
            # process splits & create blocks
            found_blank_rows = False
            for row in range(self.sheet.nrows):
                if self.cell_value and self.cell_match in ['contains', 'exact',
                                                           'starts']:
                    if not self.process_rows or row in self.process_rows:
                        # get list of row (value, type)
                        row_list = self.xls._parse_row_type(self.sheet, row,
                                                        date_as_tuple=True)
                        self.process_row(row, row_list)
                elif self.cell_match in ['blank', 'rows']:
                    if not self.process_rows or row in self.process_rows:
                        row_list = self.xls._parse_row(self.sheet, row,
                                                       date_as_tuple=True)
                        #print "excelutils 582", row, row_list[0]
                        if row == 0 or (row_list and row_list[0] in [None, '']\
                        and check_if_equal(row_list)):  # all blanks!
                            found_blank_rows = True
                            if row == 0:
                                row = -1
                            if blank_cols and self.cell_match in ['blank', ]:
                                for col in blank_cols:
                                    self.add_block(row + 1, col + 1)
                            else:
                                self.add_block(row + 1, 0)
                elif self.cell_match in ['cols', ]:
                    pass  # see below
                else:
                    self.raiseError(
                    'Cell match has not been specified! Please make a choice.')
            # blanks: no split on blank rows; just split on blank cols
            if not found_blank_rows and self.cell_match in ['blank', 'rows',
                                                            'cols']:
                for col in blank_cols:
                    self.add_block(0, col + 1)

        # set up output file
        new_file = self.create_excel_file()
        if not new_file:
            self.raiseError('Unable to create output file!')
            return
        # check for blocks
        if not self.blocks:
            self.raiseError('No suitable split matches found in input file!')
            return
        # set date format
        date_style = xlwt.XFStyle()
        date_style.num_format_str = DATE_FORMAT

        # create data in Excel file using block info
        workbook = xlwt.Workbook()
        for row_index, block in enumerate(self.blocks):
            worksheet = workbook.add_sheet("%s_%s" %
                                        (row_index + 1,
                                         block[0][0:SHEET_NAME_SIZE]))
            for r, row in enumerate(range(block[1][0], block[2][0])):
                sheet = self.xls.book.sheet_by_name(block[0])
                #print "slicing row:cols", row, ":", block[1][1], block[2][1]
                row_slice = sheet.row_slice(row, block[1][1], block[2][1])
                worksheet_row = worksheet.row(r)
                for col_index, col_cell in enumerate(row_slice):
                    value = self.xls.parse_cell_value(col_cell.ctype,
                                                      col_cell.value,
                                                      date_as_datetime=True)
                    #print "excelutils:619",r,col_index,":",col_cell.ctype,value
                    if col_cell.ctype == 3:  # date
                        style = xlwt.XFStyle()
                        style.num_format_str = DATE_FORMAT
                        worksheet_row.write(col_index, value, style)
                    else:
                        worksheet_row.write(col_index, value)

                if r > 500:
                    worksheet.flush_row_data
                    # Recommended that flush_row_data is called for every 1000
                    # or so rows of normal size written to an xlwt.Workbook.
            worksheet.flush_row_data
        workbook.save(new_file.name)

        if new_file:
            self.setResult('file_out', new_file)  # port


@RPyCSafeModule()
class ExcelChopper(ExcelBase):
    """Read Excel file and remove rows/columns according to parameters.

    Note that only values will be reproduced in the new file; all formatting
    (e.g. alignment, font style and colors) will be lost.

    Input ports:
        file_in:
            input Excel file
        file_name_out:
            an optional full directory path and filename to be written; if None
            then a temporary file will be created
        sheets:
            a list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed. Sheet numbering starts
            from 1.
        rows:
            values:
                a list of row numbers to be removed. If None, then all empty
                rows will be removed. Row numbering starts from 1.
            range:
                a Boolean indicating if the row numbers specify a range.

            If range is `False`, the row values are just numbers of individual
            rows. If range is `True`, the following notation applies:
                 *  N: the first N rows
                 *  N, M: all rows from N to M inclusive
                 *  N, M, P: every "Pth" row, between N to M inclusive
        columns:
            values:
                a list of column numbers to be removed. If None, then no
                columns will be removed. Column numbering starts from 1.
            range:
                a Boolean indicating if the column numbers specify a range.

            If range is `False`, the column values are just numbers of
            individual columns. If range is `True`, the following notation
            applies:
                 *  N: the first N columns
                 *  N, M: all columns from N to M inclusive
                 *  N, M, P: every "Pth" column, between N to M inclusive

    Output ports:
        file_out:
            output Excel file
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
                if row in self.process_rows:
                    pass  # do not add to output
                else:
                    row_list = self.xls._parse_row(sheet, row,
                                                   date_as_tuple=True)
                    if row_list[0] in [None, ''] \
                    and check_if_equal(row_list):
                        pass  # do not add blank row to output
                    else:
                        if len(self.process_cols) > 0:
                            for col in self.process_cols:  # reverse order
                                try:
                                    row_list.pop(col)  # remove from output
                                except:
                                    pass
                        else:
                            # check/remove cols that are blank throughout???
                            pass
                            """ This code will not suffice; as it does not
                            check that the WHOLE column is blank...
                            for col in range(len(row_list) - 1, 0, -1):
                                if row_list[col] in [None, '']:
                                    row_list.pop(col)  # no blanks in output
                            """
                        out_list.append(row_list)
            results[sheet_name] = out_list
        self.save_results(results)


@RPyCSafeModule()
class ExcelReplacer(ExcelBase):
    """Read Excel file and replace values according to specific parameters.

    Input ports:
        file_in:
            input Excel file
        file_name_out:
            an optional full directory path and filename to be write; if None
            then a temporary file will be created
        sheets:
            a list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed. Sheet numbering starts
            from 1.
        rows:
            values:
                a list of row numbers to be processed.  If None, then all rows
                will be processed. Row numbering starts from 1.
            range:
                a Boolean indicating if the row numbers specify a range.

            If range is `False`, the row values are just numbers of individual
            rows. If range is `True`, the following notation applies:
                 *  N: the first N rows
                 *  N, M: all rows from N to M inclusive
                 *  N, M, P: every "Pth" row, between N to M inclusive
        columns:
            values:
                a list of column numbers to be processed. If None, then all
                columns will be processed. Column numbering starts from 1.
            range:
                a Boolean indicating if the column numbers specify a range.

            If range is `False`, the column values are just numbers of
            individual columns. If range is `True`, the following notation
            applies:
                 *  N: the first N columns
                 *  N, M: all columns from N to M inclusive
                 *  N, M, P: every "Pth" column, between N to M inclusive
        cell_match:
            value:
                the current cell value that is to be matched (and replaced).
            partial: Boolean
                if True, then part of a cell's current value will be replaced.
        cell_replace: string
            the new cell value that is to be used instead of the current.
            Can be None; then the current cell value will be replaced by an
            empty string.

    Output ports:
        file_out:
            output Excel file
    """

    # TODO - extend code to allow for multiple current -> single replace; and
    #                                 multiple current -> multiple replace

    _input_ports = [
        ('cell_match', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:Boolean)',
            {"defaults": str(["", False]),
             "labels": str(["value", "partial"])}),
        ('cell_replace', '(edu.utah.sci.vistrails.basic:String)'),
    ]

    def __init__(self):
        ExcelBase.__init__(self)

    def compute(self):
        super(ExcelReplacer, self).compute()
        cell_current, partial = self.getInputFromPort('cell_match')
        cell_replace = self.forceGetInputFromPort('cell_replace', "")
        results = {}
        if not cell_current:
            self.raiseError('Invalid or missing cell_current port')
        # create output dict; one entry per selected sheet name
        for sheet_name in self.xls.sheet_list:
            sheet = self.xls.book.sheet_by_name(sheet_name)
            # allow all columns to be processed by default
            if not self.process_cols:
                self.process_cols = range(0, sheet.ncols)
            out_list = []
            for row in range(sheet.nrows):
                row_list = self.xls._parse_row(sheet, row,
                                               date_as_tuple=True)
                if not self.process_rows or row in self.process_rows:
                    for col in self.process_cols:
                        if partial:
                            try:
                                iter(row_list[col])  # test if partial possible
                                if cell_current in row_list[col]:
                                    row_list[col] = row_list[col].replace(
                                                                cell_current,
                                                                cell_replace)
                            except:
                                pass
                        else:
                            if row_list[col] == cell_current:
                                row_list[col] = cell_replace
                out_list.append(row_list)
            results[sheet_name] = out_list
        self.save_results(results)


@RPyCSafeModule()
class ExcelFiller(ExcelBase):
    """Read Excel file and fill in data according to specific parameters.

    Input ports:
        file_in:
            input Excel file
        file_name_out:
            an optional full directory path and filename to be write; if None
            then a temporary file will be created
        sheets:
            a list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed. Sheet numbering starts
            from 1.
        rows:
            values:
                a list of row numbers to be processed.  If None, then all rows
                will be processed. Row numbering starts from 1.
            range:
                a Boolean indicating if the row numbers specify a range.

            If range is `False`, the row values are just numbers of individual
            rows. If range is `True`, the following notation applies:
                 *  N: the first N rows
                 *  N, M: all rows from N to M inclusive
                 *  N, M, P: every "Pth" row, between N to M inclusive
        columns:
            values:
                a list of column numbers to be processed.  If None, then all
                columns will be processed. Column numbering starts from 1.
            range:
                a Boolean indicating if the column numbers specify a range.

            If range is `False`, the column values are just numbers of
            individual columns. If range is `True`, the following notation
            applies:
                 *  N: the first N columns
                 *  N, M: all columns from N to M inclusive
                 *  N, M, P: every "Pth" column, between N to M inclusive
        cell_replace: string
            the new cell value that is to be used instead of any empty cell.
        use_last_value: Boolean
            if no value is specified for `cell_replace`, and this is True,
            any empty cells will be replaced with the last non-empty value
            found when traversing the worksheet (starting from top-left) in the
            specified `direction`.
        direction:
            the order in which the sheet is processed; down the columns or
            along the rows

    Output ports:
        file_out:
            output Excel file
    """

    _input_ports = [
        ('cell_replace', '(edu.utah.sci.vistrails.basic:String)'),
        ('use_last_value', '(edu.utah.sci.vistrails.basic:Boolean)'),
        ('direction', '(za.co.csir.eo4vistrails:Excel Direction:tools|excel)'),
        ]

    def __init__(self):
        ExcelBase.__init__(self)

    def compute(self):
        super(ExcelFiller, self).compute()
        cell_replace = self.forceGetInputFromPort('cell_replace', "")
        use_last_value = self.forceGetInputFromPort('use_last_value', False)
        direction = self.forceGetInputFromPort('direction', 'rows')
        results = {}
        if not cell_replace and not use_last_value:
            self.raiseError('Invalid or missing cell_replace port')
        # create output dict; one entry per selected sheet name
        for sheet_name in self.xls.sheet_list:
            sheet = self.xls.book.sheet_by_name(sheet_name)
            # allow all columns to be processed by default
            if not self.process_cols:
                self.process_cols = range(0, sheet.ncols)
            out_list = []
            if direction == 'rows':
                # process along a row
                for row in range(sheet.nrows):
                    row_list = self.xls._parse_row(sheet, row,
                                                   date_as_tuple=True)
                    if not self.process_rows or row in self.process_rows:
                        current = None
                        for col in self.process_cols:
                            if not row_list[col]:  # blank
                                if not use_last_value or current:
                                    row_list[col] = cell_replace
                                if use_last_value and current:
                                    row_list[col] = current
                            current = row_list[col]
                    out_list.append(row_list)
            elif direction == 'cols':
                current = self.xls._parse_row(sheet, 0, date_as_tuple=True)
                # process down a column
                for row in range(sheet.nrows):
                    if not self.process_rows or row in self.process_rows:
                        row_list = self.xls._parse_row(sheet, row,
                                                       date_as_tuple=True)
                        for col in self.process_cols:
                            if not row_list[col]:  # blank
                                if not use_last_value or current[col]:
                                    row_list[col] = cell_replace
                                if use_last_value and current[col]:
                                    row_list[col] = current[col]
                                    current[col] = row_list[col]
                            else:
                                # update "current" with new, non-blank value
                                current[col] = row_list[col]
                    out_list.append(row_list)
            else:
                self.raiseError('Invalid direction specification.')

            results[sheet_name] = out_list
        self.save_results(results)


class ExcelDirectionComboBoxWidget(ComboBoxWidget):
    """Constants used to decide direction of processing of an Excel file"""
    _KEY_VALUES = {'Along Rows': 'rows', 'Down Columns': 'cols'}

ExcelDirectionComboBox = new_constant('Excel Direction',
                                      staticmethod(str),
                                      'rows',
                                      staticmethod(lambda x: type(x) == str),
                                      ExcelDirectionComboBoxWidget)


# not used as at 10/10/2012
class ExcelSplitComboBoxWidget(ComboBoxWidget):
    """Constants used to decide splits for processing of an Excel file"""
    _KEY_VALUES = {'Row & Column': 'both', 'Along a Row': 'row',
                   'Along a Column': 'col'}

ExcelSplitComboBox = new_constant('Excel Split',
                                  staticmethod(str),
                                  'both',
                                  staticmethod(lambda x: type(x) == str),
                                  ExcelSplitComboBoxWidget)


class ExcelMatchComboBoxWidget(ComboBoxWidget):
    """Constants used to decide what type of match to use in an Excel file"""
    _KEY_VALUES = {'Blank Rows & Columns': 'blank', 'Blank Rows': 'rows',
                   'Blank Columns': 'cols', 'Contains': 'contains',
                   'Exact Match': 'exact', 'Starts With': 'starts'}

ExcelMatchComboBox = new_constant('Excel Match',
                                      staticmethod(str),
                                      'blank',
                                      staticmethod(lambda x: type(x) == str),
                                      ExcelMatchComboBoxWidget)

###########################################################################
##
## Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the ability to run code transparently in
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
"""This module provides a means to read an Excel file and convert the data to
a Python data structure.
"""
# library
import datetime
import os
import os.path
import sys
# third-party
import xlrd


class read_excel(object):
    """Extract data from an Excel File either as a dict, or a list of values,
    or a list of (value, type) tuples.
    
    Uses the xlrd module (version 0.5.2 or later), supporting Excel versions:
    2004, 2002, XP, 2000, 97, 95, 5, 4, 3
    
    Data is extracted via iterators that can either return one row at a time
    (either as a dict or as a list) or one column at a time.
    
    The dict generator assumes that the worksheet is in tabular format,
    with the first "data" row containing the variable names and all subsequent
    rows containing values.
    
    Extracted data is represented fairly logically. By default dates are
    returned as strings in "yyyy/mm/dd" format or "yyyy/mm/dd hh:mm:ss", as
    appropriate. However, when specifying date_as_tuple=True, dates will be
    returned as a (Year, Month, Day, Hour, Min, Second) tuple, for usage with
    mxDateTime or DateTime. Numbers are returned as either `int` or `float`,
    whichever is needed to support the data. Text, booleans, and error codes
    are also returned as appropriate representations.

    Example of use:
    
    .. code-block:: python
        
        import readexcel as rx
        xls = rx.read_excel('testdata.xls')
        # all sheets
        for sheet_name in xls.book.sheet_names():
            print sheet_name
            for row in xls.iter_dict(sheet_name):
                print row
        # first sheet
        sheets = xls.set_sheet_list()
        sheet = sheets[0]
        it = xls.iter_tuples(sheet)
        for row in it:
            print row

    Original code:
    
        `<http://gizmojo.org/code/readexcel/>`_
    """

    def __init__(self, filename):
        """ Wraps an XLRD book """
        if not os.path.isfile(filename):
            raise ValueError("%s is not a valid filename" % filename)
        self.book = xlrd.open_workbook(filename)
        self.sheet_keys = {}
        self.sheet_list = []

    def _is_data_row(self, sheet, i):
        values = sheet.row_values(i)
        if isinstance(values[0], basestring) and values[0].startswith('#'):
            return False  # ignorable comment row
        for v in values:
            if bool(v):
                return True  # row full of (valid) False values?
        return False

    def _is_data_column(self, sheet, i):
        values = sheet.column_values(i)
        if isinstance(values[0], basestring) and values[0].startswith('#'):
            return False  # ignorable comment row
        for v in values:
            if bool(v):
                return True  # row full of (valid) False values?
        return False

    def set_sheet_list(self, sheets=[]):
        """Set the required list of sheet names.

        :param list sheets:
            the required sheets; either sheet names or sheet numbers.
            Sheet numbering starts from 1.
        """
        if sheets:
            #print "readexcel:85 sheets", sheets
            for index, name in enumerate(self.book.sheet_names()):
                if index + 1 in sheets or name in sheets:
                    self.sheet_list.append(name)
        else:
            self.sheet_list = self.book.sheet_names()

    def parse_cell_value(self, type, value, date_as_tuple=False,
                         date_as_datetime=False):
        # Data Type Codes:
        #  EMPTY 0
        #  TEXT 1 a Unicode string
        #  NUMBER 2 float
        #  DATE 3 float
        #  BOOLEAN 4 int; 1 means TRUE, 0 means FALSE
        #  ERROR 5
        #print "readexcel:133", type, value
        if type == 2:
            if value == int(value):
                value = int(value)
        elif type == 3:
            try:
                datetuple = xlrd.xldate_as_tuple(value, self.book.datemode)
            except xlrd.xldate.XLDateAmbiguous:
                raise Exception(
                    "Ambiguous date: Cannot process value '%s'" % value)
            if date_as_tuple:
                value = datetuple
            elif date_as_datetime:
                value = datetime.datetime(*datetuple)
            else:
                # time only, no date component
                if datetuple[0] == 0 and datetuple[1] == 0 and \
                   datetuple[2] == 0:
                    value = "%02d:%02d:%02d" % datetuple[3:]
                # date only, no time component
                elif datetuple[3] == 0 and datetuple[4] == 0 and \
                     datetuple[5] == 0:
                    value = "%04d/%02d/%02d" % datetuple[:3]
                else:  # full date
                    value = "%04d/%02d/%02d %02d:%02d:%02d" % datetuple
        elif type == 5:
            try:
                value = xlrd.error_text_from_code[value]
            except KeyError:
                value = value
        return value

    def _parse_column(self, sheet, col_index, date_as_tuple=False):
        """Sanitize incoming Excel data; return list of column values."""
        values = []
        if col_index < sheet.ncols:
            for type, value in zip(
                    sheet.col_types(col_index), sheet.col_values(col_index)):
                value = self.parse_cell_value(type, value, date_as_tuple)
                values.append(value)
        return values

    def _parse_row(self, sheet, row_index, date_as_tuple=False):
        """Sanitize incoming Excel data; return list of row values."""
        values = []
        if row_index < sheet.nrows:
            for type, value in zip(
                    sheet.row_types(row_index), sheet.row_values(row_index)):
                value = self.parse_cell_value(type, value, date_as_tuple)
                values.append(value)
        return values

    def _parse_row_type(self, sheet, row_index, date_as_tuple=False):
        """Sanitize incoming Excel data; return list of (value, type) tuples"""
        values = []
        #print "readexcel:184 sheet, row_index", sheet.name, row_index
        for type, value in zip(
                sheet.row_types(row_index), sheet.row_values(row_index)):
            try:
                value = self.parse_cell_value(type, value, date_as_tuple)
                values.append((value, type))
            except Exception, e:
                raise Exception('Error in sheet "%s" in row %s:\n%s' % \
                    (sheet.name, row_index, e))
        return values

    def iter_dict(self, sheet_name, date_as_tuple=False):
        """Iterator for a worksheet's rows as dictionaries """
        sheet = self.book.sheet_by_name(sheet_name)  # XLRDError
        # parse first row, set dict keys & first_row_index
        keys = []
        first_row_index = None
        for i in range(sheet.nrows):
            if self._is_data_row(sheet, i):
                headings = self._parse_row(sheet, i, False)
                for j, var in enumerate(headings):
                    # replace duplicate headings with "F#".
                    if not var or var in keys:
                        var = u'F%s' % (j)
                    keys.append(var.strip())
                first_row_index = i + 1
                break
        self.sheet_keys[sheet_name] = keys
        # generate a dict per data row
        if first_row_index is not None:
            for i in range(first_row_index, sheet.nrows):
                if self._is_data_row(sheet, i):
                    yield dict(map(None, keys,
                            self._parse_row(sheet, i, date_as_tuple)))

    def iter_list(self, sheet_name, date_as_tuple=False):
        """Iterator for a worksheet's rows as lists of values"""
        sheet = self.book.sheet_by_name(sheet_name)  # XLRDError
        for i in range(sheet.nrows):
            if self._is_data_row(sheet, i):
                yield self._parse_row(sheet, i, date_as_tuple)

    def iter_tuples(self, sheet_name, date_as_tuple=True):
        """Iterator for a worksheet's rows as lists of (value, type) tuples"""
        sheet = self.book.sheet_by_name(sheet_name)  # XLRDError
        for i in range(sheet.nrows):
            if self._is_data_row(sheet, i):
                yield self._parse_row_type(sheet, i, date_as_tuple)

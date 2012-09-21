"""
    http://gizmojo.org/code/readexcel/
"""

class readexcel(object):
    """ Simple OS-independent class for extracting data from an Excel File.

    Uses the xlrd module (version 0.5.2 or later), supporting Excel versions:
    2004, 2002, XP, 2000, 97, 95, 5, 4, 3

    Data is extracted via iterators that return one row at a time -- either
    as a dict or as a list. The dict generator assumes that the worksheet is
    in tabular format with the first "data" row containing the variable names
    and all subsequent rows containing values.

    Extracted data is represented fairly logically. By default dates are
    returned as strings in "yyyy/mm/dd" format or "yyyy/mm/dd hh:mm:ss", as
    appropriate. However, when specifying date_as_tuple=True, dates will be
    returned as a (Year, Month, Day, Hour, Min, Second) tuple, for usage with
    mxDateTime or DateTime. Numbers are returned as either INT or FLOAT,
    whichever is needed to support the data. Text, booleans, and error codes
    are also returned as appropriate representations. Quick Example:

        xls = readexcel('testdata.xls')
        for sname in xls.book.sheet_names():
            for row in xls.iter_dict(sname):
                print row
    """
    def __init__(self, filename):
        """ Wraps an XLRD book """
        if not os.path.isfile(filename):
            raise ValueError, "%s is not a valid filename" % filename
        self.book = xlrd.open_workbook(filename)
        self.sheet_keys = {}

    def is_data_row(self, sheet, i):
        values = sheet.row_values(i)
        if isinstance(values[0], basestring) and values[0].startswith('#'):
            return False # ignorable comment row
        for v in values:
            if bool(v):
                return True #+ row full of (valid) False values?
        return False

    def _parse_row(self, sheet, row_index, date_as_tuple):
        """ Sanitize incoming excel data """
        # Data Type Codes:
        #  EMPTY 0
        #  TEXT 1 a Unicode string
        #  NUMBER 2 float
        #  DATE 3 float
        #  BOOLEAN 4 int; 1 means TRUE, 0 means FALSE
        #  ERROR 5
        values = []
        for type, value in zip(
                sheet.row_types(row_index), sheet.row_values(row_index)):
            if type == 2:
                if value == int(value):
                    value = int(value)
            elif type == 3:
                datetuple = xlrd.xldate_as_tuple(value, self.book.datemode)
                if date_as_tuple:
                    value = datetuple
                else:
                    # time only no date component
                    if datetuple[0] == 0 and datetuple[1] == 0 and \
                       datetuple[2] == 0:
                        value = "%02d:%02d:%02d" % datetuple[3:]
                    # date only, no time
                    elif datetuple[3] == 0 and datetuple[4] == 0 and \
                         datetuple[5] == 0:
                        value = "%04d/%02d/%02d" % datetuple[:3]
                    else: # full date
                        value = "%04d/%02d/%02d %02d:%02d:%02d" % datetuple
            elif type == 5:
                value = xlrd.error_text_from_code[value]
            values.append(value)
        return values

    def iter_dict(self, sname, date_as_tuple=False):
        """ Iterator for the worksheet's rows as dicts """
        sheet = self.book.sheet_by_name(sname) # XLRDError
        # parse first row, set dict keys & first_row_index
        keys = []
        first_row_index = None
        for i in range(sheet.nrows):
            if self.is_data_row(sheet, i):
                headings = self._parse_row(sheet, i, False)
                for j, var in enumerate(headings):
                    # replace duplicate headings with "F#".
                    if not var or var in keys:
                        var = u'F%s' % (j)
                    keys.append(var.strip())
                first_row_index = i + 1
                break
        self.sheet_keys[sname] = keys
        # generate a dict per data row
        if first_row_index is not None:
            for i in range(first_row_index, sheet.nrows):
                if self.is_data_row(sheet, i):
                    yield dict(map(None, keys,
                            self._parse_row(sheet, i, date_as_tuple)))

    def iter_list(self, sname, date_as_tuple=False):
        """ Iterator for the worksheet's rows as lists """
        sheet = self.book.sheet_by_name(sname) # XLRDError
        for i in range(sheet.nrows):
            if self.is_data_row(sheet, i):
                yield self._parse_row(sheet, i, date_as_tuple)
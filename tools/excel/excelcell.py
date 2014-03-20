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
"""This module provides a means to visualise an Excel file, in a Vistrails
spreadsheet cell, as an HMTL table.
"""
# library
import os.path
import sys
from datetime import date, datetime, time
# third-party
import xlrd
from PyQt4 import QtCore, QtGui
# vistrails
from core.modules.vistrails_module import Module, ModuleError
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget
import shutil

ENCODING = "utf-8"  # will probably differ in some countries ???

# TODO - recode from "fyle.write('<html>')" using a Jinja template !!!

##############################################################################


class ExcelCell(SpreadsheetCell):
    """ ExcelCell is a custom module to view Excel files as HTML tables.
    
    Input ports:
    
        Location:
            the Location of the output display cell
        File:
            a File in .xls format
        Sheets:
            a List of sheet numbers, or names, that must be displayed.
            If None, then all sheets will be displayed.
        ColumnWidths:
            a List of values corresponding to column width in pixels. If there
            is only one number, it wil be used for all the columns; if two
            numbers, the first will be used for the first column, and the
            second for all other columns; if three numbers, the first will be
            used for the first column, the second for the second column, and
            the third for all other columns... and so on.
        References?
            If True (checked), the column and row numbers will be shown on the
            top and lefthand sides.
        Disabled?
            If True, then the output is not displayed.
    
    Output ports:
    
        HTML File:
            the HTML file displaying the Excel
    """

    def compute(self):
        """ compute() -> None
        Create HTML and dispatch the contents to the VisTrails spreadsheet
        """
        disabled = self.forceGetInputFromPort("Disabled?", False)
        if self.hasInputFromPort("File"):
            fileValue = self.getInputFromPort("File")
            fileHTML = self.interpreter.filePool.create_file(suffix='.html')
            fileReference = self.forceGetInputFromPort("References?", False)
            columnWidths = self.forceGetInputFromPort("ColumnWidths", [])
            try:
                fileSheets = self.getInputListFromPort("Sheets")
                if isinstance(fileSheets[0], (list, tuple)):
                    fileSheets = fileSheets[0]  # remove Vistrails "wrapper"
            except:
                fileSheets = []
        else:
            fileValue = None
        if not disabled:
            self.cellWidget = self.displayAndWait(ExcelCellWidget,
                                                  (fileValue,
                                                   fileHTML,
                                                   fileSheets,
                                                   fileReference,
                                                   columnWidths))
            self.setResult('HTML File', fileHTML)


class ExcelCellWidget(QCellWidget):
    """ExcelCellWidget has a QTextBrowser to display HTML files
    """

    def __init__(self, parent=None):
        """ ExcelCellWidget(parent: QWidget) -> ExcelCellWidget
        Create a rich text cell without a toolbar

        """
        QCellWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.browser = QtGui.QTextBrowser()
        self.layout().addWidget(self.browser)
        self.browser.setMouseTracking(True)
        self.browser.controlBarType = None
        self.fileSrc = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new changed in filename

        """
        self.fileSrc = None
        (fileExcel, fileHTML, fileSheets, fileReference, columnWidths) = \
                                                                    inputPorts
        if fileExcel:
            html_file = self.create_html(fileExcel, fileHTML, fileSheets,
                                         date_as_tuple=False, css=None,
                                         fileReference=fileReference,
                                         columnWidths=columnWidths)
            if html_file:
                try:
                    fi = open(html_file.name, "r")
                except IOError:
                    self.browser.setText("Cannot create/load the HTML file!")
                    return
                self.browser.setHtml(fi.read())
                fi.close()
                self.fileSrc = html_file.name
            else:
                self.browser.setText("HTML file could not be created!")
        else:
            self.browser.setText("No Excel file is specified!")

    def dumpToFile(self, filename):
        """ dumpToFile(filename) -> None
        It will generate a screenshot of the cell contents and dump to filename
        It will also create a copy of the original text file used with
        filename's base name and the original extension.
        """
        if self.fileSrc is not None:
            (_, s_ext) = os.path.splitext(self.fileSrc)
            (f_root, f_ext) = os.path.splitext(filename)
            ori_filename = f_root + s_ext
            shutil.copyfile(self.fileSrc, ori_filename)
        QCellWidget.dumpToFile(self, filename)

    def saveToPDF(self, filename):
        printer = QtGui.QPrinter()
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        self.browser.print_(printer)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error with traceback display."""
        import traceback
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ' - %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def create_html(self, file_in, file_out, sheets=None,
                         date_as_tuple=False, css=None,
                         fileReference=False, columnWidths=[]):
        """Return HTML in the output file from an Excel input file.

        Args:
            file_in: File object
                points to Excel file
            file_out: File object
                points to (temporary) HTML file
            sheets: List
                the sheet numbers or names to be processed; if None
                then all are processed.  Sheet numbering starts from 1.
        """
        if not file_in or not file_out:
            return None
        if not css:
            # ??? Table-level CSS does not work
            css = 'table, th, td { border: 1px solid black; } \
                   body {font-family: Arial, sans-serif; }'
            table_borders = ' border="1"'  # TEMPORARY WORK-AROUND
        # grid reference style
        ref_style = 'font-weight:bold; background-color:#808080; color:white;'
        try:
            book = xlrd.open_workbook(file_in.name, formatting_info=True)
        except:
            self.raiseError('Unable to open or access %s' % file_in.name)
            return None
        try:
            fyle = open(file_out.name, 'w')
        except:
            self.raiseError('Unable to open or access %s' % file_out.name)
            return None
        fyle.write('<html>')
        fyle.write('\n<head>')
        fyle.write('\n  <style type="text/css">%s\n</style>' % css)
        fyle.write('\n</head>')
        fyle.write('<body>')
        font = book.font_list
        alignment = {1: ' text-align: left;',
                     2: ' text-align: center;',
                     3: ' text-align: right;',
                    }
        # list of selected sheets
        sheet_list = []
        if sheets:
            for index, name in enumerate(book.sheet_names()):
                if index + 1 in sheets or name in sheets:
                    sheet_list.append(name)
            if not sheet_list:
                self.raiseError('Invalid list of sheets; please check file')
                return None
        else:
            sheet_list = book.sheet_names()
        # create table per selected sheet
        for name in sheet_list:
            # create style for column widths
            widths = []
            for col_n in range(0, book.sheet_by_name(name).ncols):
                if len(columnWidths) == 1:
                    columnWidths[0]  # all the same
                elif len(columnWidths) > 0:
                    try:
                        widths.append(columnWidths[col_n])
                    except:
                        widths.append(columnWidths[-1])  # default is last
                else:
                    pass
            # write data to file
            fyle.write('\n<h1>%s</h1>\n' % name)
            fyle.write('  <table%s>\n' % table_borders)
            if fileReference:  # show grid col labels
                fyle.write('    <tr><td style="%s">&#160;</td>      ' %
                           ref_style)
                for col_n in range(0, book.sheet_by_name(name).ncols):
                    fyle.write('<td style="%s" align="center">%s</td>' %
                               (ref_style, str(col_n + 1)))
                fyle.write('    </tr>\n      ')
            for row_n in range(0, book.sheet_by_name(name).nrows):
                fyle.write('    <tr>\n      ')
                if fileReference:  # show grid row labels
                    fyle.write('<td style="%s" align="center">%s</td>' %
                               (ref_style, str(row_n + 1)))
                for col_n in range(0, book.sheet_by_name(name).ncols):
                    style = ''
                    type = None
                    try:
                        value = book.sheet_by_name(name).cell(row_n, col_n).value
                        type = book.sheet_by_name(name).cell(row_n, col_n).ctype
                        xfx = book.sheet_by_name(name).cell_xf_index(row_n, col_n)
                        xf = book.xf_list[xfx]
                        cell_font = font[xf.font_index]
                        if cell_font.italic:
                            style += ' font-style: italic;'
                        if cell_font.weight > 400:
                            style += ' font-weight: bold;'  # 700
                        if cell_font.underline_type:
                            style += ' text-decoration: underline;'
                        if cell_font.struck_out:
                            style += ' text-decoration:line-through;'
                        # font color
                        font_color = book.colour_map[cell_font.colour_index]
                        if font_color:
                            style += ' color:rgb(%s,%s,%s);' % font_color
                        # cell color
                        bgx = xf.background.pattern_colour_index
                        cell_color = book.colour_map[bgx]
                        if cell_color:
                            style += ' background-color:rgb(%s,%s,%s);' % cell_color
                        # text align
                        align = xf.alignment.hor_align
                        if align:
                            style += alignment.get(align) or ''
                    except IndexError:
                        value = None
                    # check data types
                    # 0:EMPTY; 1:TEXT (a Unicode string); 2:NUMBER (float);
                    # 3:DATE (float); 4:BOOLEAN (1 TRUE, 0 FALSE); 5: ERROR
                    if type == 1:
                        value = value.encode(ENCODING, 'ignore')
                    elif type == 2:
                        if value == int(value):
                            value = int(value)
                        style += ' text-align:right;'
                    elif type == 3:
                        datetuple = xlrd.xldate_as_tuple(value, book.datemode)
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
                            else:  # full date
                                value = "%04d/%02d/%02d %02d:%02d:%02d" % \
                                        datetuple
                    elif type == 5:
                        value = xlrd.error_text_from_code[value]
                    else:
                        value = ''
                    # create cell with formatting
                    if len(widths) > 0:
                        fyle.write('<td width="%spx" style="%s">%s</td>' %
                                   (widths[col_n], style, value or '&#160;'))
                    else:
                        fyle.write('<td style="%s">%s</td>' %
                               (style, value or '&#160;'))
                fyle.write('    </tr>\n')
            fyle.write('  </table>\n')
        fyle.write('</body>\n')
        fyle.write('</html>\n')
        fyle.close()
        return fyle

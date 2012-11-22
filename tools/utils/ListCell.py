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
"""This module provides a means to visualise a Python list-of-lists, in a
Vistrails spreadsheet cell, as an HMTL table.
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

ENCODING = "utf-8"  # will differ in some countries; add as hidden port ???

##############################################################################


class ListCell(SpreadsheetCell):
    """
    ListCell is a custom module to view lists as HTML tables

    Input ports:
        Location:
            the Location of the output display cell
        List:
            a standard List
        LineNumbers?
            If True (checked), the line numbers will be shown on the lefthand
            side of the table.

    Output ports:
        HTML File:
            the HTML file displaying the List
    """
    def compute(self):
        """ compute() -> None
        Create HTML and dispatch the contents to the VisTrails spreadsheet
        """
        if self.hasInputFromPort("List"):
            list_in = self.getInputFromPort("List")
            fileHTML = self.interpreter.filePool.create_file(suffix='.html')
            fileReference = self.forceGetInputFromPort("References?", False)
            columnWidths = self.forceGetInputFromPort("ColumnWidths", [])
        else:
            fileValue = None
        self.cellWidget = self.displayAndWait(ListCellWidget, (list_in,
                                                                fileHTML,
                                                                fileReference,
                                                                columnWidths))
        self.setResult('HTML File', fileHTML)


class ListCellWidget(QCellWidget):
    """
    ListCellWidget has a QTextBrowser to display HTML files

    """
    def __init__(self, parent=None):
        """ ListCellWidget(parent: QWidget) -> ListCellWidget
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
        (list_in, fileHTML, fileReference, columnWidths) = inputPorts
        if list_in:
            html_file = self.create_html(list_in, fileHTML,
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
            self.browser.setText("No list is specified!")

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

    def create_html(self, list_in, file_out,
                         date_as_tuple=False, css=None,
                         fileReference=False, columnWidths=[]):
        """Return HTML in the output file from an Excel input file.

        Args:
            list_in: List object
                points to List
            file_out: File object
                points to (temporary) HTML file
        """
        if not list_in or not file_out:
            return None
        if not css:
            # ??? Table-level CSS does not work
            css = 'table, th, td { border: 1px solid black; } \
                   body {font-family: Arial, sans-serif; }'
            table_borders = ' border="1"'  # TEMPORARY WORK-AROUND
        # grid reference style
        ref_style = 'font-weight:bold; background-color:#808080; color:white;'
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
        alignment = {1: ' text-align: left;',
                     2: ' text-align: center;',
                     3: ' text-align: right;',
                    }

        # write data to file
        fyle.write('  <table%s>\n' % table_borders)

        for row_n, row in enumerate(list_in):
            fyle.write('    <tr>\n      ')
            if fileReference:  # show grid row labels
                fyle.write('<td style="%s" align="center">%s</td>' %
                           (ref_style, str(row_n + 1)))
            for col_n, value in enumerate(row):
                style = ""
                # check data types and change alignment???
                """
                # 0:EMPTY; 1:TEXT (a Unicode string); 2:NUMBER (float);
                # 3:DATE (float); 4:BOOLEAN (1 TRUE, 0 FALSE); 5: ERROR
                if type == 1:
                    value = value.encode(ENCODING, 'ignore')
                elif type == 2:
                    if value == int(value):
                        value = int(value)
                    style += alignment[1]
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
                """
                # create cell with formatting
                fyle.write('<td style="%s">%s</td>' % \
                           (style, value or '&#160;'))
            fyle.write('    </tr>\n')
        fyle.write('  </table>\n')
        fyle.write('</body>\n')
        fyle.write('</html>\n')
        fyle.close()
        return fyle

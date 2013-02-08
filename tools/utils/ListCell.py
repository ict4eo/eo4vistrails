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
"""
from core.bundles import py_import
from core import debug
try:
    pkg_dict = {'linux-ubuntu': 'python-xlrd',
                'linux-fedora': 'python-xlrd'}
    xlrd = py_import('xlrd', pkg_dict)
except Exception, e:
    debug.critical("Exception: %s" % e)
"""
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
    """ListCell is a custom module to view list-of-lists as an HTML table.

    Each outer list is a line in the table; each item in the nested list is a
    cell.

    Input ports:
        Heading:
            a heading to display above the table
        Location:
            the Location of the output display cell
        List:
            a standard List
        LineNumbers?
            If True (checked), the line numbers will be shown on the left-hand
            side of the table.
        Disabled?
            If True, then the output is not displayed.

    Output ports:
        HTML File:
            the HTML file displaying the List
    """
    def compute(self):
        """ compute() -> None
        Create HTML and dispatch the contents to the VisTrails spreadsheet
        """
        disabled = self.forceGetInputFromPort("Disabled?", False)
        if self.hasInputFromPort("List"):
            list_in = self.getInputFromPort("List")
            file_HTML = self.interpreter.filePool.create_file(suffix='.html')
            fileReference = self.forceGetInputFromPort("References?", False)
            tableHeading = self.forceGetInputFromPort("Heading", "")
            columnWidths = self.forceGetInputFromPort("ColumnWidths", [])
        else:
            fileValue = None
        if not disabled:
            self.cellWidget = self.displayAndWait(ListCellWidget,
                                                  (list_in, file_HTML,
                                                   fileReference, columnWidths,
                                                   tableHeading))
            self.setResult('HTML File', file_HTML)


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
        self.list_in, self.file_HTML, self.fileReference, self.columnWidths, \
            self.tableHeading = inputPorts
        if self.list_in:
            html_file = self.create_html()
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
                self.browser.setText("The HTML table could not be created!")
        else:
            self.browser.setText("No list is specified for display!")

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

    def is_sequence(self, arg):
        """Check that sequence is not, in fact, a string."""
        return (not hasattr(arg, "strip") and
                hasattr(arg, "__getitem__") or
                hasattr(arg, "__iter__"))

    def create_html(self, css=None):
        """Return output file, containing HTML table, from a list-of-lists.

        Args:
            css: string
                styling for the HTML (NOT WORKING)
        """
        if not self.list_in or not self.file_HTML:
            return None
        width = self.columnWidths or 20
        table_borders = ' border="1" width="%spx"' % width  # remove if css works
        if not css:
            # ??? Table-level CSS does not work
            css = """
                table, th, td { border: 1px solid black;}
                td {width: %spx}
                body {font-family: Arial, sans-serif; }""" % width

        # grid reference style
        ref_style = 'font-weight:bold; background-color:#808080; color:white;'
        try:
            fyle = open(self.file_HTML.name, 'w')
        except:
            self.raiseError('Unable to open or access "%s"' %
                            self.file_HTML.name)
            return None
        # settings
        alignment = {1: ' text-align: left;',
                     2: ' text-align: center;',
                     3: ' text-align: right;',
                    }
        # append data to output list
        output = []
        output.append('<html>')
        output.append('\n<head>')
        output.append('\n  <style type="text/css">%s\n</style>' % css)
        output.append('\n</head>')
        output.append('<body>')
        if self.tableHeading:
            output.append('<h1>%s</h1>' % self.tableHeading)
        output.append('  <table%s>\n' % table_borders)

        for row_n, row in enumerate(self.list_in):
            if row and not self.is_sequence(row):
                row = [row, ]
            output.append('    <tr>\n      ')
            if self.fileReference:  # show grid row labels
                output.append('<td style="%s" align="center">%s</td>' %
                           (ref_style, str(row_n + 1)))
            for col_n, value in enumerate(row):
                style = alignment[1]
                # change alignment for numbers
                try:
                    float(value)
                    style = alignment[3]
                except:
                    pass
                # create cell with formatting
                output.append('<td style="%s">%s</td>' %
                           (style, value or '&#160;'))
            output.append('    </tr>\n')
        output.append('  </table>\n')
        output.append('</body>\n')
        output.append('</html>\n')
        # write output list (as string) to file and return
        html = u'\n'.join(output)
        fyle.write(html.encode('utf-8'))
        fyle.close()
        return fyle

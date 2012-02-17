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
handle writing of specialised text data files, with or without header rows.
"""
# library
import csv
import os
import os.path
# vistrails
from core.modules.vistrails_module import Module, ModuleError
from core.modules import basic_modules
from core.modules.basic_modules import File, String, Boolean
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget

@RPyCSafeModule()
class TextDataWriter(ThreadSafeMixin, Module):
    """Data file writer utility for creating specialised text files.

    Input ports:
        filename:
            full path and name of output file; if not set, then a system
            generated file will be created
        data_output_type:
            pre-set data output type
            * csv - standard CSV (uses column_header_list)
            * odv - ocean data view (uses own columns)
        column_header_list:
            optional list of column headings
        data_values:
            list of lists contain the rows of data to write to file

    Output ports:
        created_file:
            a full pathname to the file created, if successful. On RPyC nodes,
            will refer to files on that remote filesystem.

    """

    _input_ports = [('filename', '(edu.utah.sci.vistrails.basic:String)'),
                    ('column_header_list', '(edu.utah.sci.vistrails.basic:List)'),
                    ('data_output_type', '(za.co.csir.eo4vistrails:Data Output Type:utils)'),
                    ('data_values', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('created_file', '(edu.utah.sci.vistrails.basic:String)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        filename = self.getInputFromPort('filename')
        data_output_type = self.getInputFromPort('data_output_type', 'csv')
        column_headers = []
        data_values = self.getInputFromPort('data_values')

        if data_output_type == 'csv':
            ext = '.csv'
        elif data_output_type == 'odv':
            ext = '.odv'
            column_headers = '"Cruise", "Station", "Type", "mon/day/yr", \
                "hh:mm", "Lon (°E)", "Lat (°N)", "Bot. Depth [m]".'
        elif data_output_type == 'dat':
            ext = '.dat'
        else:
            raise ModuleError(self, 'Create extension: Unknown Data Output Type')
        if not filename:
            filename = self.interpreter.filePool.create_file(suffix=ext)

        try:
            csvfile = csv.writer(open(filename, 'w'),
                                 delimiter=',',
                                 quotechar="'")
            if len(column_headers) > 0:
                csvfile.writerow(column_headers)
            if len(dvll) > 0:
                csvfile.writerows(data_values)
            self.setResult('created_file', filename)
        except Exception, e:
            raise ModuleError(self, 'Cannot create CSV: %s' % str(e))

        csvfile = None  # flush to disk


class DataWriterTypeComboBoxWidget(ComboBoxWidget):
    """Types of specialised data writing options."""
    _KEY_VALUES = {'ovd': 'Ocean View Data (OVD)',
                   'csv': 'Comma-separated View',
                   'dat': 'R data file'}

DataWriterTypeComboBox = basic_modules.new_constant('Data Output Type',
                                        staticmethod(str),
                                        '-',
                                        staticmethod(lambda x: type(x) == str),
                                        DataWriterTypeComboBoxWidget)

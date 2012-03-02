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
import os
import os.path
# vistrails
from core.modules.vistrails_module import Module, ModuleError
from core.modules import basic_modules
from core.modules.basic_modules import File, String, Boolean
# eo4vistrails
from packages.eo4vistrails.geoinf.datamodels.TemporalVectorLayer import \
    TemporalVectorLayer
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget


@RPyCSafeModule()
class TextDataWriter(ThreadSafeMixin, Module):
    """Utility for creating a text file from a temporal vector layer.

    Input ports:
        vector_layer:
            a temporal vector layer
        filename:
            full path and name of output file; if not set, then a system
            generated file will be created
        data_output_type:
            pre-set data output type
            * csv - standard CSV (uses column_header_list)
            * odv - ocean data view (uses its own columns; see
              http://odv.awi.de/
        column_header_list:
            optional list of column headings
        missing_value:
            optional value to be used to replace any missing or null values

    Output ports:
        created_file:
            On RPyC nodes, will refer to file(s) on that remote filesystem.

    """

    _input_ports = [('vector_layer',
                     '(za.co.csir.eo4vistrails:Temporal Vector Layer:data)'),
                    ('filename',
                     '(edu.utah.sci.vistrails.basic:String)'),
                    ('column_header_list',
                     '(edu.utah.sci.vistrails.basic:List)'),
                    ('missing_value',
                     '(edu.utah.sci.vistrails.basic:String)'),
                    ('data_output_type',
                     '(za.co.csir.eo4vistrails:Data Output Type:utils)')]
    _output_ports = [('created_file', '(edu.utah.sci.vistrails.basic:File)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        vector_layer = self.getInputFromPort('vector_layer')
        filename = self.forceGetInputFromPort('filename', None)
        data_output_type = self.forceGetInputFromPort('data_output_type', 'csv')
        column_headers = self.forceGetInputFromPort('column_header_list', [])
        missing_value = self.forceGetInputFromPort('missing_value', None)

        if not filename:
            _file = self.interpreter.filePool.create_file(suffix=".%s" % \
                                                          data_output_type)
            filename = _file.name
        if data_output_type == 'csv':
            file_out = vector_layer.to_csv(filename_out=filename,
                                           missing_value=missing_value)
        elif data_output_type == 'odv':
            file_out = vector_layer.to_odv(filename_out=filename,
                                           missing_value=missing_value)
        elif data_output_type == 'dat':
            file_out = vector_layer.to_csv(filename_out=filename,
                                           missing_value=missing_value)
        else:
            raise ModuleError(self, 'Unknown Data Output Type')

        self.setResult('created_file', file_out)


class DataWriterTypeComboBoxWidget(ComboBoxWidget):
    """Types of specialised data writing options."""
    _KEY_VALUES = {'Ocean Data View': 'odv',
                   'Comma-separated': 'csv',
                   'R data file': 'dat'}

DataWriterTypeComboBox = basic_modules.new_constant('Data Output Type',
                                        staticmethod(str),
                                        '-',
                                        staticmethod(lambda x: type(x) == str),
                                        DataWriterTypeComboBoxWidget)

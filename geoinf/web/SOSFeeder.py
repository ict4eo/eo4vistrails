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
handle data feeds to an OGC SOS (including InsertObservation & RegisterSensor)
"""
# library
import os
import os.path
from jinja2 import Environment, PackageLoader, FileSystemLoader
# third-party
import xlrd
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin
#names of ports as constants
import init


@RPyCSafeModule()
class SOSFeeder(ThreadSafeMixin, Module):
    """Accept a file, extract data from it, and POST it to a specified SOS.

    Input ports:
        OGC_URL:
            the network address of the SOS
        data_file:
            an Excel (.xls format) file; containing data to populate the SOS
        configuration:
            an optional configuration dictionary - this will override the
            default settings used to access data from the Excel file
        active:
            a boolean port; if True (default) then incoming data is POSTed
            directly to the SOS

    Output ports:
        PostData:
            an XML string; containing data POSTed to the SOS
    """

    """
    _input_ports = [
                ('OGC_URL', '(edu.utah.sci.vistrails.basic:String)'),
                ('data_file', '(edu.utah.sci.vistrails.basic:File)'),
                ('configuration', '(edu.utah.sci.vistrails.basic:Dictionary)'),
                ('active', '(edu.utah.sci.vistrails.basic:Boolean)')]
    _output_ports = [('PostData', '(edu.utah.sci.vistrails.basic:String)'),]
    """

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error with traceback display."""
        import traceback
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ' - %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def compute(self):
        self.URL = self.getInputFromPort(init.OGC_URL_PORT)
        self.file_in = self.getInputFromPort('data_file')
        _config = self.forceGetInputFromPort('configuration', None)
        self.active = self.forceGetInputFromPort('active', True)
        # template location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir),
                               trim_blocks=True)

        try:
            self.config = self.get_config(_config)
            # process the POST
            XML = self.create_data()
            #print "SOSfeed:102\n", XML
            if self.active:
                # TO DO ...
                pass
            # output POST data, if required
            if init.OGC_POST_DATA_PORT in self.outputPorts:
                self.setResult(init.OGC_POST_DATA_PORT, XML)

        except Exception, ex:
            self.raiseError(ex)

    def get_config(self, config=None):
        """Create the configuration needed to read data in from the file."""
        return None

    def create_data(self):
        """Create the XML for the POST to the SOS, using a Jinja template."""
        pass  # override in inherited classes


class RegisterSensor(SOSFeeder):
    """Extend SOS Feeder to register a sensor for a SOS."""

    def __init__(self):
        SOSFeeder.__init__(self)

    def create_data(self):
        """Create the XML for the POST to the SOS, using a Jinja template."""
        return None  # TO DO !!!


class InsertObservation(SOSFeeder):
    """Extend SOS Feeder to create observation data for a SOS."""

    def __init__(self):
        SOSFeeder.__init__(self)

    def load_from_excel(self):
        """Read data from Excel file, and store it in dictionaries

        Default location (row, col) tuples for data

        "components"
        ------------
        This dictionary has:
            row: start row where components are listed
            count: no of components (rows) available
            name, type, urn, units: column numbers for these entries

        "values"
        --------
        The 'start_end' tuple can have:
            (row1, ) - starting row; read values down to end of sheet
            (row1, row2) - starting row (1); read values down to second row (2)

        The 'columns' tuple values correspond to the equivalent component
        number in the "components' list.
        """
        # default locations for data
        pos = {
            'sensor': (1, 1),
            'procedure': (2, 1),
            'period': {'start': (4, 1), 'end': (4, 2), 'offset': (4, 3)},
            'foi': {'id': (6, 2), 'name': (6, 1), 'srs': (6, 3),
                    'latitude': (6, 4), 'longitude': (6, 5), },
            'separator': {'decimal': (8, 1), 'token': (8, 2), 'block': (8, 3)},
            'components': {'name': 1, 'type': 2, 'urn': 2, 'units': 4,
                           'row': 10, 'count': 4},
            'values': {'start_end': (16, ), 'columns': (1, 2, 3)}
        }
        if self.config:
            # override default data locations from self.config dictionary
            for item in ('sensor', 'procedure', 'period', 'foi', 'separator',
                         'components', 'values'):
                pos[item] = self.config.get(item) or pos[item]
        # open data file
        work_book = xlrd.open_workbook(self.file_in.name)
        sh = work_book.sheet_by_index(0)
        # meta data
        self.core = {
            'sensorID': sh.cell(*pos['sensor']).value,
            'procedureID': sh.cell(*pos['procedure']).value}
        self.period = {
            'start': sh.cell(*pos['period']['start']).value,
            'end': sh.cell(*pos['period']['end']).value,
            'offset': sh.cell(*pos['period']['offset']).value or 0}
        self.foi = {
            'name': sh.cell(*pos['foi']['name']).value,
            'id': sh.cell(*pos['foi']['id']).value,
            'srs': sh.cell(*pos['foi']['srs']).value,
            'latitude': sh.cell(*pos['foi']['latitude']).value,
            'longitude': sh.cell(*pos['foi']['longitude']).value}
        self.separator = {
            'decimal': sh.cell(*pos['separator']['decimal']).value,
            'token': sh.cell(*pos['separator']['token']).value,
            'block': sh.cell(*pos['separator']['block']).value}
        # set components
        self.components = []
        for rownum in range(pos['components']['row'],
                pos['components']['row'] + pos['components']['count'] + 1):
            self.components.append({
                'name': sh.cell(rownum, pos['components']['name']).value,
                'type': sh.cell(rownum, pos['components']['type']).value,
                'urn': sh.cell(rownum, pos['components']['urn']).value,
                'units': sh.cell(rownum, pos['components']['units']).value,
                })
        # read observation data
        self.values = []
        offset = self.period['offset']
        row_start = pos['values']['start_end'][0]
        if len(pos['values']['start_end']) == 2:
            row_end = pos['values']['start_end'][1]
        else:
            row_end = sh.nrows
        for row_num in range(row_start - 1, row_end):
            set = []
            for col in pos['values']['columns']:
                col_num = col - 1
                type = sh.cell(row_num, col_num).ctype
                val = sh.cell(row_num, col_num).value
                if type == 3:
                    date_tuple = xlrd.xldate_as_tuple(val, work_book.datemode)\
                            + (offset, )
                    value = "%04d-%02d-%02dT%02d:%02d:%02d+%02d" % date_tuple
                elif type == 2:
                    if val == int(val):
                        value = int(val)
                elif type == 5:
                    value = xlrd.error_text_from_code[val]
                else:
                    value = val
                set.append(value)
            self.values.append(set)


    def create_data(self):
        """Create the XML for the POST to the SOS, using a Jinja template."""
        template = self.env.get_template('InsertObservation.xml')
        self.period, self.values, self.separator = None, [], None
        self.core, self.components, self.foi = None, [], None
        """
        # test data
        self.core = {
            'sensorID': 'urn:ogc:object:feature:Sensor:Derwent-Station-2',
            'procedureID': 'urn:ogc:object:feature:Sensor:Derwent-Station-2'}
        self.period = {
            'start': '2008-04-03T04:44:15+11:00',
            'end': '2008-05-03T04:44:15+11:00'}
        self.foi = {
            'name': 'Hobart 2',
            'id': 'Hobart-2',
            'srs': 'urn:ogc:def:crs:EPSG::4326',
            'latitude': '-42.91',
            'longitude': '147.33'}
        self.separator = {
            'decimal': '.',
            'token': ':',
            'block': ';'}
        self.components = []
        self.components.append({
          'urn': 'http://www.opengis.net/def/uom/ISO-8601/0/Gregorian',
          'name': 'Time',
          'type': 'Time'})
        self.components.append({
          'urn': 'http://www.opengis.net/def/property/OGC/0/FeatureOfInterest',
          'name': 'feature',
          'type': 'Text'})
        self.components.append({
          'urn': 'urn:ogc:def:phenomenon:OGC:1.0.30:temperature',
          'name': 'temperature',
          'type': 'Quantity',
          'units': 'cel'})
        self.values = [
            ['1963-12-13T00:00:00+02', 22, 60],
            ['1963-12-14T00:00:00+02', 24, 65],
            ['1963-12-15T00:00:00+02', 25, 45],
            ['1963-12-16T00:00:00+02', 21, 50],
            ['1963-12-17T00:00:00+02', 23, 55],
            ['1963-12-18T00:00:00+02', 24, 60]]
        """
        # load data from file
        self.load_from_excel()
        data = template.render(period=self.period, values=self.values,
                               separator=self.separator, core=self.core,
                               components=self.components, foi=self.foi,)
        return data

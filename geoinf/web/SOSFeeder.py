# -*- coding: utf-8 -*-
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
"""This module forms part of the eo4vistrails capabilities. It is used to
handle data feeds to an OGC SOS (including InsertObservation & RegisterSensor)
"""
# library
import csv
import os
import os.path
from jinja2 import Environment, PackageLoader, FileSystemLoader
import cgi
# third-party
import xlrd
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.geoinf.datamodels.WebRequest import WebRequest
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.tools.utils.listutils import uniqify
#names of ports as constants
import init


SRS_DEFAULT = 'urn:ogc:def:crs:EPSG::4326'


@RPyCSafeModule()
class SOSFeeder(ThreadSafeMixin, Module):
    """An abstract VisTrails class for creating SOS data feeders.

    This base class contains common methods and properties.

    The compute() method initialises data for ports that are common to all
    classes; but should be extended (via super) to perform processing specific
    to the inherited class; e.g. extract observation data from the file, and
    POST this to a Sensor Observation Service (SOS).

    Input ports:
        OGC_URL:
            the network address of the SOS
        active:
            Boolean port; if True (default is False) then outgoing data is
            POSTed directly to the specified SOS address (OGC_URL)

    Output ports:
        PostData:
            a list of XML strings; each containing data POSTed to the SOS
    """

    _input_ports = [
        ('OGC_URL', '(edu.utah.sci.vistrails.basic:String)'),
        ('active', '(edu.utah.sci.vistrails.basic:Boolean)'), ]
    _output_ports = [
        ('PostData', '(edu.utah.sci.vistrails.basic:List)'), ]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)
        self.webRequest = WebRequest()

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error with traceback display."""
        import traceback
        #print "sosfeed 89", msg
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ' - %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def unicode_csv_reader(self, utf8_data, dialect=csv.excel, **kwargs):
        """Read and encode data from CSV as 'utf-8'.

        NOTE:
            Data from Excel is read as unicode; this is used to maintain
            interoperability between excel data and csv data!

        Source:
            http://stackoverflow.com/questions/904041/\
            reading-a-utf8-csv-file-with-python
        """
        csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
        for row in csv_reader:
            yield [unicode(cell, 'utf-8') for cell in row]

    def make_list(self, lst=None):
        """"Return a list from any given single element."""
        if not lst:
            return []
        if hasattr(lst, '__iter__'):
            return list(lst)
        else:
            return [lst]

    def extract_pairs(self, string):
        """Return [(x1,y1), (x2,y2), ...] from "x1 y1, x2 y2. ..." string."""
        if string:
            coord_list = string.replace('"', '').strip(' ').split(',')
            coords = [(cl.strip(' ').split(' ')[0],
                       cl.strip(' ').split(' ')[1]) \
                       for cl in coord_list]
            return coords
        return []

    def set_sheet_list(self, sheets=[]):
        """Sets the list of Excel sheet names for the SOSFeeder.

        Args:
            sheets: a list
                the required sheets; either sheet names or sheet numbers.
                Sheet numbering starts from 1. If None, get all sheets.
        """
        self.sheet_list = []
        if sheets:
            for index, name in enumerate(self.workbook.sheet_names()):
                if index + 1 in sheets or name in sheets:
                    self.sheet_list.append(name)
        else:
            self.sheet_list = self.workbook.sheet_names()

    def compute(self):  # inherit and extend in child class
        # optional port
        self.test_mode = self.forceGetInputFromPort('TEST_MODE', False)
        # port data
        self.url = self.forceGetInputFromPort(init.OGC_URL_PORT, None)
        self.file_in = self.forceGetInputFromPort('data_file', None)
        #_config = self.forceGetInputFromPort('configuration', None)
        self.active = self.forceGetInputFromPort('active', False)
        # validate port values
        if self.active and not self.url:
            self.raiseError('SOS URL must be specified if feed is Active')
        # template location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, 'templates')
        #print "sosfeed:145", current_dir, template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir),
                               trim_blocks=True)


class InsertObservation(SOSFeeder):
    """Accept an Excel file, extract observation data from it, and POST it to a
    Sensor Observation Service (SOS), as per specified parameters.

    Input ports:
        OGC_URL:
            the network address of the SOS
        file_in:
            input Excel file
        sheets:
            a list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed. Sheet numbering starts
            from 1.
        active:
            a Boolean port; if True (default is False) then the outgoing data
            is POSTed directly to the SOS
        procedure:
            The physical sensor or analysis process that has recorded or
            carried out the observations.

            value:
                the name of the procedure, which is set for all observations
            row:
                the row in which the name of the procedure appears - rows are
                numbered from 1 onwards.
            column:
                the column in which the name of the procedure appears - columns
                are numbered from 1 onwards.
        feature:
            The feature-of-interest(s) (FOI) for which the observations were
            carried out; typically this corresponds to a monitoring station /
            sampling point (but can be, for example, a geographical area).

            name:
                the name of the single feature; set for all observations
            row:
                the row in which the name of the features appear- rows are
                numbered from 1 onwards.
            column:
                the column in which the name of the features appear- columns
                are numbered from 1 onwards.
            If both row and column are filled in, the name of the feature is
            taken from that specific cell.
        feature_details:
            An (optional) expanded set of information for each feature;
            including SRS, latitude and longitude.

            A list-of-lists, containing the details for a number of features-
            of-interest. Each feature is associated with a corresponding
            sensor, with each list item in the form:
                ID, "name", "co-ordinates", SRS
            `co-ordinates` can be a single pair of space-separated
            lat/long values, or a comma-delimited list of such values. SRS is
            optional; if not supplied, the default ('urn:ogc:def:crs:EPSG::4326')
            will be used.

            The co-ordinate list must be wrapped in "" - e.g.
                ID_1, name_1, "45.12 23.25, 44.13 22.15", SRS_1
        property:
            The ID(s) for the property(ies) measured or calculated as part of
            the observation; for example, the water flowrate at river guage.
            Multiple properties can be inserted as part of an observation.

            ID:
                single unique property ID, which is set for all observations
            row:
                the row in which the unique property IDs appear- rows are
                numbered from 1 onwards.
            column:
                the column in which the unique property IDs appear- columns
                are numbered from 1 onwards.
            If both row and column are filled in, the property ID is taken
            from that specific cell.
        property_details:
            A list-of-lists, containing the details for each property;
            including its descriptive name, the URN (Uniform Resource Name) -
            as used by a standards body such OGC or NASA (SWEET) - and units of
            measure (in standard SI notation). Each list item has the form:
                "name", "URN", "units", "type"
            where type is optional and defaults to "Quantity" if omitted.
        date:
            The date(s) on which the property which was measured or calculated.
            This should be in the format YYYY-MM-DD; or YYYY-MM-DD HH:SS if
            there is a specific time associated.

            value:
                a single date, which is the same for all observations
            row:
                the row in which the dates appear - rows are numbered from 1
                onwards.
            column:
                the column in which the dates appear - columns are numbered
                from 1 onwards.
            offset:
                the difference (in hours) between UTC and the timezone in which
                the properties were measured or calculated
        observations:
            These are the actual recorded observation values (numeric or non-
            numeric) made for the features and properties, at the specified
            dates.

            row:
                the row in which the first observation appears- rows are
                numbered from 1 onwards.
            column:
                the column in which the first observation  appears- columns
                are numbered from 1 onwards.
        separators:
            The characters used to separate observations in the SOS XML file
            (only change these if absolutely required).

            decimal:
                a single character used to demarcate a decimal fraction (this
                defaults to ".")
            token:
                a single character used to separate items in a single
                observation (this defaults to ",")
            block:
                a single character used to separate sets of observations (this
                defaults to ";")

    Output ports:
        PostData:
            a list of XML strings; each containing data for a single POST
        Results:
            a list; each item containing the result of a single POST
    """
    _input_ports = [
        ('file_in', '(edu.utah.sci.vistrails.basic:File)'),
        ('sheets', '(edu.utah.sci.vistrails.basic:List)'),
        ('procedure', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:Integer,edu.utah.sci.vistrails.basic:Integer)',
            {"defaults": str(["", 0, 0]),
             "labels": str(["name", "row", "column"])}),
        ('feature', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:Integer,edu.utah.sci.vistrails.basic:Integer)',
            {"defaults": str(["", 0, 0]),
             "labels": str(["name", "row", "column"])}),
        ('feature_details', '(edu.utah.sci.vistrails.basic:List)'),
        ('property', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:Integer,edu.utah.sci.vistrails.basic:Integer)',
            {"defaults": str(["", 0, 0]),
             "labels": str(["ID", "row", "column"])}),
        ('property_details', '(edu.utah.sci.vistrails.basic:List)'),
        ('date', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:Integer,edu.utah.sci.vistrails.basic:Integer,\
edu.utah.sci.vistrails.basic:Integer)',
            {"defaults": str(["", 0, 0, 0]),
             "labels": str(["value", "row", "column", "offset"])}),
        ('observations', '(edu.utah.sci.vistrails.basic:Integer,\
edu.utah.sci.vistrails.basic:Integer)',
            {"defaults": str([1, 1]),
             "labels": str(["row", "column"])}),
        ('separators', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:String,edu.utah.sci.vistrails.basic:String)',
            {"defaults": str([".", ",", ";"]),
             "labels": str(["decimal", "token", "block"])}),
    ]

    def __init__(self):
        SOSFeeder.__init__(self)

    def load_from_excel(self, sheet_name=None, reset=True):
        """Read data from a named Excel worksheet, and store in dictionaries

        Args:
            sheet_name: string
                name of worksheet in `self.workbook` Excel file
            reset: Boolean
                whether all storage dictionaris are reset to null

        Uses:
            self.configuration = {
                'sensor': {'value': xxx, 'rowcol': (row, col)},
                'procedure': {'value': xxx, 'rowcol': (row, col)},
                'period': {'value': date_x, 'rowcol': (row, col),
                           'offset': hours},
                'foi': {'value': xxx, 'rowcol': (row, col)},
                'separator': {'decimal': char, 'token': char, 'block': char},
                'properties': {'value': xxx, 'rowcol': (row, col)},
                'values': {'rowcol': (row, col)},
                }
            self.property_lookup: dictionary
                details for each property, in the format:
                    {"ID_1": ["name_1", "URN_value1", "units_abc"],
                     "ID_2": ["name_2", "URN_value2", "units_pqr"],}
            self.feature_lookup: dictionary
                details for each feature, in the format:
                    {"ID_1": {"name": "name_1", "srs": "SRS_1",
                              "coords": [(a,b), (c,d) ...]},
                     "ID_2": {"name": "name_2", "srs": "SRS_2",
                              "coords": [(p,q), (r,s) ...]},}
        """

        def cell_value(sheet, row_num, col_num):
            """Return the correct type of value from a valid Excel cell."""
            row_num = max(row_num, 0)
            col_num = max(col_num, 0)
            value = None
            if row_num < sh.nrows and col_num < sh.ncols:
                ctype = sheet.cell(row_num, col_num).ctype
                val = sheet.cell(row_num, col_num).value
                if ctype == 3:
                    date_tuple = xlrd.xldate_as_tuple(val,
                                                      self.workbook.datemode)\
                                                      + (offset, )
                    value = "%04d-%02d-%02dT%02d:%02d:%02d+%02d" % date_tuple
                elif ctype == 2:
                    if val == int(val):
                        value = int(val)
                    else:
                        try:
                            value = float(val)
                        except:
                            value = val
                elif ctype == 5:
                    value = xlrd.error_text_from_code[val]
                else:
                    value = val
            return value

        def add_property(name, source_type=None, row=None, col=None):
            """If property is found in lookup, add to properties attribute."""
            prop = self.property_lookup.get(name.strip(' '))
            if not prop:
                self.raiseError('Unable to locate property "%s" in the lookup' % \
                                name)
            #print "sosfeed 407\n'%s'-'%s'" % (name.strip(' '), prop)
            if len(prop) >= 3:
                self.properties.append({
                    'name': name,
                    'type': prop[0] or 'Quantity',
                    'urn': prop[1],
                    'units': prop[2],
                    'row': row,
                    'col': col,
                    'source': source_type})
                if not self.unique_property_names.get(name):
                    self.unique_property_names[name] = name
                    self.unique_properties.append({
                        'name': name,
                        'type': prop[0] or 'Quantity',
                        'urn': prop[1],
                        'units': prop[2]})
            else:
                self.raiseError('Invalid details for property "%s" in the lookup',\
                                name)

        def add_foi(foi_ID, row=None, col=None):
            """If FOI is found in lookup, add to the FOI's dictionary."""
            try:
                ID = unicode(foi_ID)  # convert Excel int to unicode
            except:
                ID = foi_ID
            foi_ID_entry = self.feature_lookup.get(ID)
            #print "sosfeed:435", foi_ID_entry, ID, type(ID)
            if foi_ID_entry:
                # convert coords "list of tuples with unicode strings"
                coords = []
                coords_list = foi_ID_entry.get('coords')
                if coords_list:
                    try:
                        for coord in coords_list:
                            coords.append(float(coord[0]))
                            coords.append(float(coord[1]))
                    except:
                        coords = coords_list
                self.fois[ID] = {
                    'id': ID,
                    'name': foi_ID_entry.get('name') or ID,
                    'srs': foi_ID_entry.get('srs') or SRS_DEFAULT,
                    'coords': coords,
                    'col': col,
                    'row': row}

        def add_date(_date, row=None, col=None):
            """Add to date list."""
            self.unique_dates.append(_date)
            self.dates.append({
                'date': _date,
                'row': row,
                'col': col
                })

        def get_foi_ID(row=None, col=None):
            # fixed FOI value
            if len(self.fois) == 1:
                foi = self.fois[self.fois.iterkeys().next()]  # first entry
                if foi.get('col') is None and foi.get('row') is None:
                    return foi.get('id')
            for key, foi in self.fois.iteritems():
                if foi.get('col') == col or foi.get('row') == row:
                    #print "sosfeed:475", foi.get('col'), col, foi.get('id')
                    return foi.get('id')
            return None

        def get_property_name(row=None, col=None):
            # fixed property value
            if len(self.properties) == 1:
                if self.properties[0]['col'] is None and \
                   self.properties[0]['row'] is None:
                    return self.properties[0].get('name')
            for property in self.properties:
                #print "sosfeed:486", row,col,property['col'],property['row']
                if property['col'] == col or property['row'] == row:
                    return property.get('name')
            return None

        def get_vdate(row=None, col=None):
            # constant date
            if len(self.dates) == 1:
                if self.dates[0]['col'] is None and self.dates[0]['row'] is None:
                    return self.dates[0]
            for date in self.dates:
                if date['col'] == col or date['row'] == row:
                    return date

        # initialize
        if reset:
            self.period, self.values, self.separator = None, [], None
            self.core, self.properties, self.foi = None, [], None
        sh = self.workbook.sheet_by_name(sheet_name)
        # input data checks & links
        if self.configuration:
            config = self.configuration
        else:
            self.raiseError('Internal Error: Configuration not set.')
        if config['values']['rowcol'][0] - 1 > sh.nrows:
            self.raiseError('Observation rows outside sheet limits!')
        if config['values']['rowcol'][1] - 1 > sh.ncols:
            self.raiseError('Observation columns outside sheet limits!')
        self.data_row = config['values']['rowcol'][0] - 1
        self.data_col = config['values']['rowcol'][1] - 1
        # meta data
        self.core = {
            'sensorID': config['sensor']['value'] or \
                        cell_value(sh,
                                   config['sensor']['rowcol'][0] - 1,
                                   config['sensor']['rowcol'][1] - 1),
            'procedureID': config['procedure']['value'] or \
                           cell_value(sh,
                                      config['procedure']['rowcol'][0] - 1,
                                      config['procedure']['rowcol'][1] - 1)}
        self.separator = config['separator']
        # features
        self.fois = {}
        if config['foi']['value']:
            foi_ID = config['foi']['value']
            add_foi(foi_ID)
        elif config['foi']['rowcol'][0] and config['foi']['rowcol'][1]:
            foi_ID = cell_value(sh, config['foi']['rowcol'][0] - 1,
                                  config['foi']['rowcol'][1] - 1)
            add_foi(foi_ID)
        elif config['foi']['rowcol'][0] and not config['foi']['rowcol'][1]:
            row_num = config['foi']['rowcol'][0]
            for col_num in range(self.data_col, sh.ncols):
                foi_ID = cell_value(sh, row_num - 1, col_num)
                add_foi(foi_ID, row=None, col=col_num)
        elif config['foi']['rowcol'][1] and not config['foi']['rowcol'][0]:
            col_num = config['foi']['rowcol'][1]
            for row_num in range(self.data_row, sh.nrows):
                foi_ID = cell_value(sh, row_num, col_num - 1)
                add_foi(foi_ID, row=row_num, col=None)
        else:
            self.raiseError('Feature settings not configured properly!')
        # properties
        self.properties = []
        self.unique_properties = []
        self.unique_property_names = {}
        if config['properties']['value']:
            name = config['properties']['value']
            add_property(name, source_type='constant')
        elif config['properties']['rowcol'][0] \
        and config['properties']['rowcol'][1]:
            name = cell_value(sh, config['properties']['rowcol'][0] - 1,
                                  config['properties']['rowcol'][1] - 1)
            add_property(name, source_type='constant')
        elif config['properties']['rowcol'][0] \
        and not config['properties']['rowcol'][1]:
            row_num = config['properties']['rowcol'][0]
            for col_num in range(self.data_col, sh.ncols):
                name = cell_value(sh, row_num - 1, col_num)
                add_property(name, source_type='row', row=None, col=col_num)
        elif config['properties']['rowcol'][1] \
        and not config['properties']['rowcol'][0]:
            col_num = config['properties']['rowcol'][1]
            for row_num in range(self.data_row, sh.nrows):
                name = cell_value(sh, row_num, col_num - 1)
                add_property(name, source_type='col', row=row_num, col=None)
        else:
            self.raiseError('Property settings not configured properly!')
        # add time (date?) as "always present"
        self.unique_properties.insert(0, {
            'name': "Time",
            'type': "Time",
            'urn': "urn:ogc:data:time:iso8601"})
        # dates
        self.unique_dates = []
        self.dates = []
        if config['period']['value']:
            value = config['period']['value']
            add_date(value)
        elif config['period']['rowcol'][0] and config['period']['rowcol'][1]:
            value = cell_value(sh, config['period']['rowcol'][0] - 1,
                                  config['period']['rowcol'][1] - 1)
            add_date(value)
        elif config['period']['rowcol'][0] \
        and not config['period']['rowcol'][1]:
            row_num = config['period']['rowcol'][0]
            for col_num in range(self.data_col, sh.ncols):
                value = cell_value(sh, row_num - 1, col_num)
                add_date(value, row=row_num, col=None)
        elif config['period']['rowcol'][1] \
        and not config['period']['rowcol'][0]:
            col_num = config['period']['rowcol'][1]
            for row_num in range(self.data_row, sh.nrows):
                value = cell_value(sh, row_num, col_num - 1)
                add_date(value, row=None, col=col_num)
        else:
            self.raiseError('Date settings not configured properly!')
        self.unique_dates = uniqify(self.unique_dates)
        self.period = {
            'start': self.unique_dates[0],
            'end': self.unique_dates[len(self.unique_dates) - 1],
            'offset': config['period']['offset'] or 0}

        # observation data values
        offset = config['period']['offset']
        try:
            offset = int(offset)
        except:
            offset = 0
        self.values = {}
        for row_num in range(self.data_row, sh.nrows):
            for col_num in range(self.data_col, sh.ncols):
                # keys
                foi = get_foi_ID(row_num, col_num)
                vdate = get_vdate(row_num, col_num)
                property = get_property_name(row_num, col_num)
                #print "sosfeed:626 FDP", foi, vdate['date'], property
                if foi and vdate and property:
                    value = cell_value(sh, row_num, col_num)
                    if value:
                        # data
                        self.values[(foi, vdate.get('date'), property)] = value

    def create_XML(self, sheet_name=None, data={}):
        """Create the XML for an InsertObservation POST using a Jinja template
        """
        template = self.env.get_template('InsertObservation.xml')
        """        """
        if self.test_mode:
            data['core'] = {
                'sensorID': 'urn:ogc:object:feature:Sensor:TestFooBar1',
                'procedureID': 'urn:ogc:object:feature:Sensor:TestFooBar1'}
            data['period'] = {
                'start': '1963-11-13T00:00:00+2:00',
                'end': '1963-11-13T00:00:00+2:00'}
            data['foi'] = {
                'name': 'Test FooBar 1',
                'id': 'TestFooBar1',
                'srs': SRS_DEFAULT,
                'coords': [('-42.91', '147.33')]}
            data['separator'] = {
                'decimal': '.',
                'token': ',',
                'block': ';'}
            data['properties'] = []
            data['properties'].append({
              'urn': 'http://www.opengis.net/def/uom/ISO-8601/0/Gregorian',
              'name': 'Time',
              'type': 'Time'})
            data['properties'].append({
              'name': 'temperature',
              'urn': 'urn:ogc:def:phenomenon:OGC:1.0.30:temperature',
              'name': 'temperature',
              'type': 'Quantity',
              'units': 'celcius'})
            data['properties'].append({
              'name': 'temperature',
              'urn': 'urn:ogc:def:phenomenon:OGC:1.0.30:humidity',
              'name': 'humidity',
              'type': 'Quantity',
              'units': 'percentage'})
            data['values'] = [
                ['1963-11-13T00:00:00+02', 22, 60],
                ['1963-11-14T00:00:00+02', 24, 65],
                ['1963-11-15T00:00:00+02', 25, 45],
                ['1963-11-16T00:00:00+02', 21, 50],
                ['1963-11-17T00:00:00+02', 23, 55],
                ['1963-11-18T00:00:00+02', 24, 60]]

        data = template.render(period=data.get('period'),
                               values=data.get('values'),
                               separator=data.get('separator'),
                               core=data.get('core'),
                               components=data.get('properties'),
                               foi=data.get('foi'),)
        return data  # XML

    def create_results(self):
        """Create list of XML POST datasets for each feature of interest.
        """
        results = []
        for sheet_name in self.sheet_list:
            #print "\nsosfeed:688 sheet", sheet_name
            # load data from worksheet into dictionaries
            self.load_from_excel(sheet_name)
            for key, foi in self.fois.iteritems():
                data = {}
                data['values'] = []
                data['core'] = self.core
                data['period'] = self.period
                data['foi'] = foi
                data['separator'] = self.separator
                data['properties'] = self.unique_properties

                token = data['separator']['token']
                for _date in self.unique_dates:
                    value_set = [_date, ]
                    for prop in self.unique_properties:
                        key = (foi.get('id'), _date, prop.get('name'))
                        val = self.values.get(key)
                        #print "sosfeed:709", foi, _date, prop.get('name'), val
                        value_set.append(val)
                    data['values'].append(value_set)

                XML = self.create_XML(sheet_name=sheet_name, data=data)
                if XML:
                    results.append(XML)
                    #print "\nsosfeed:719\n", XML
            return results

    def compute(self):
        super(InsertObservation, self).compute()
        # open data file
        try:
            self.workbook = xlrd.open_workbook(self.file_in.name)
        except:
            self.raiseError("A valid Excel file has not been specified")
        # get data sheets
        self.sheets = self.make_list(self.forceGetInputListFromPort('sheets'))
        self.set_sheet_list(self.sheets)
        if not self.sheet_list:
            self.raiseError("Unable to extract sheets from Excel file")
        # get port values
        if self.forceGetInputFromPort('procedure'):
            _proc, _proc_row, _proc_col = self.forceGetInputFromPort('procedure')
        else:
            _proc, _proc_row, _proc_col = None, None, None
        if self.forceGetInputFromPort('feature'):
            _FOI, _FOI_row, _FOI_col = self.forceGetInputFromPort('feature')
        else:
            _FOI, _FOI_row, _FOI_col = None, None, None
        _feature = self.forceGetInputFromPort('feature_details', None)
        if self.forceGetInputFromPort('property'):
            _prop, _prop_row, _prop_col = self.forceGetInputFromPort('property')
        else:
            _prop, _prop_row, _prop_col = None, None, None
        _property = self.forceGetInputFromPort('property_details', None)
        if self.forceGetInputFromPort('date'):
            _date, _date_row, _date_col, _date_offset = \
                                            self.forceGetInputFromPort('date')
        else:
            _date, _date_row, _date_col, _date_offset = None, None, None, 0
        if self.forceGetInputFromPort('observations'):
            _obs_row, _obs_col = self.forceGetInputFromPort('observations')
        else:
            _obs_row, _obs_col = None, None
        if self.forceGetInputFromPort('separators'):
            _sep_decimal, _sep_token, sep_block = \
                                    self.forceGetInputFromPort('separators')
        else:
            _sep_decimal, _sep_token, _sep_block = ".", ",", ";"

        # validate port values
        if not _proc and not _proc_row and not _proc_col:
            self.raiseError('Either name, row or column must be specified for %s'\
                            % 'procedure')
        if not _FOI and not _FOI_row and not _FOI_col:
            self.raiseError('Either ID, row or column must be specified for %s'\
                            % 'feature')
        if not _prop and not _prop_row and not _prop_col:
            self.raiseError('Either name, row or column must be specified for %s'\
                            % 'property')
        if not _obs_row and not _obs_col:
            self.raiseError('Observation row and column must be specified.')
        if not _date and not _date_row and not _date_col:
            self.raiseError('Either name, row or column must be specified for %s'\
                            % 'date')
        if not _property:
            self.raiseError('The property details must be specified')
        if not _feature:
            self.raiseError('The feature details must be specified')

        # get property lookup details as dictionary
        self.property_lookup = {}
        if _property:
            for item in _property:
                if item:
                    if len(item) >= 3:
                        _dict = dict(zip(xrange(len(item)), item))
                        self.property_lookup['name'] = \
                            cgi.escape(_dict.get(0) or "")
                        self.property_lookup['type'] = \
                            cgi.escape(_dict.get(1) or 'Quantity')
                        self.property_lookup['urn'] = \
                            cgi.escape(_dict.get(2) or "")
                        self.property_lookup['units'] = \
                            cgi.escape(_dict.get(3) or "")
                    else:
                        self.raiseError("Insufficient property values on each line'")

        # get FOI lookup details as dictionary
        self.feature_lookup = {}
        if _feature:
            for item in _feature:
                #print "sosfeed:784 item", len(item), item, bool(item)
                if item:
                    if len(item) >= 3:
                        _dict = dict(zip(xrange(len(item)), item))
                        self.feature_lookup[cgi.escape(_dict.get(0) or "")] = {
                            'name': cgi.escape(_dict.get(1)or ""),
                            'coords': self.extract_pairs(_dict.get(2)),
                            'srs': _dict.get(3) or SRS_DEFAULT}
                    else:
                        self.raiseError("Insufficient FOI values in each and/or every list.")

        # create configuration dictionary
        self.configuration = {
            'sensor': {'value': _FOI, 'rowcol': (_FOI_row, _FOI_col)},
            'procedure': {'value': _proc, 'rowcol': (_proc_row, _proc_col)},
            'period': {'value': _date, 'rowcol': (_date_row, _date_col),
                       'offset': _date_offset},
            'foi': {'value': _FOI, 'rowcol': (_FOI_row, _FOI_col)},
            'separator': {'decimal': _sep_decimal, 'token': _sep_token,
                          'block': _sep_block},
            'properties': {'value': _prop, 'rowcol': (_prop_row, _prop_col)},
            'values': {'rowcol': (_obs_row, _obs_col)},
        }

        # process configuration and generate output
        try:
            results = self.create_results()
            # output POST data, if port is linked to another module
            if init.OGC_POST_DATA_PORT in self.outputPorts:
                self.setResult(init.OGC_POST_DATA_PORT, results)
            if self.active:
                self.webRequest.url = self.url
                dataset = []
                for result in results:
                    self.webRequest.data = result
                    data = self.webRequest.runRequest()
                    dataset.append(data)
                # output results of POSTs, if port is linked to another module
                if init.DATA_PORT in self.outputPorts:
                    self.setResult(init.DATA_PORT, dataset)
        except Exception, ex:
            self.raiseError(ex)


class RegisterSensor(SOSFeeder):
    """Register a sensor for a Sensor Observation Service (SOS) via a POST of
    the supplied parameters.

    Each sensor will be associated with each feature-of-interest supplied, so
    multiple POST operations may be created.

    Input ports:
        OGC_URL:
            the network address of the SOS
        active:
            a Boolean port; if True (default is False) then the outgoing data
            is POSTed directly to the SOS
        offering:
            The set of related sensors that form part of an offering

            ID:
                the ID of the offering
            name:
                the name of the offering
        sensor_details:
            A single physical sensor, computation, simulation, or process
            that has created the observation(s).

            ID:
                the unique identifier for the sensor
            name:
                the name of the sensor
            SRS:
                the coordinate reference system - the default is
                urn:ogc:def:crs:EPSG::4326
            latitude:
                the latitude of the sensor (default units are decimal_degrees)
            longitude:
                the longitude of the sensor (default units are decimal_degrees)
            altitude:
                the altitude of the sensor (default units are metres [m])
            Note that only ID and name are required.
        sensor:
            A list-of-lists, containing the details for a number of sensors,
            with each list item containing data for one sensor in the form:
                "ID", "name", longitude, latitude, altitude, "SRS"

            These items are as described above under `sensor_details`. SRS is
            optional; if not supplied, the default will be used.
        coordinates:
            A list-of-lists, containing the details for each coordinate, with
            each nested list with each list in the form:
                "type", "units"

            Coordinates are used to define the units associated with a sensor
            location; including longitude, latitude and altitude.  This is an
            optional port; if no input is supplied the defaults will be used:
            longitude and latitude in "decimal_degrees" and altitude in "metres".
        feature:
            A list-of-lists, containing the details for a number of features-
            of-interest. Each feature is associated with a corresponding
            sensor, with each list item in the form:
                ID, "name", "co-ordinates", SRS
            `co-ordinates` can be a single pair of space-separated
            lat/long values, or a comma-delimited list of such values. SRS is
            optional; if not supplied, the default will be used (see above).

            The co-ordinate list must be wrapped in "" - e.g.
                ID_1, name_1, "45.12 23.25, 44.13 22.15", SRS_1
        property:
            A list-of-lists, containing the details for each property;
            including its descriptive name, the URN (Uniform Resource Name) -
            as used by a standards body such OGC or NASA (SWEET) - and units of
            measure (in standard SI notation). Each list item has the form:
                "name", "URN", "units", "type"
            where type is optional and defaults to "Quantity" if omitted.

    Output ports:
        PostData:
            a list of XML strings; each containing data for a single POST
        Results:
            a list; each item containing the result of a single POST
    """
    _input_ports = [
        ('sensor_details', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:String,edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:Float,edu.utah.sci.vistrails.basic:Float,\
edu.utah.sci.vistrails.basic:Float)',
            {"defaults": str(["", "", SRS_DEFAULT, "", "", ""]),
             "labels": str(["ID", "name", "srs", "longitude", "latitude", "altitude"])}),
        ('sensor', '(edu.utah.sci.vistrails.basic:List)'),
        ('offering', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:String)',
            {"defaults": str(["", ""]), "labels": str(["ID", "name"])}),
        ('coordinates', '(edu.utah.sci.vistrails.basic:List)'),
        ('feature', '(edu.utah.sci.vistrails.basic:List)'),
        ('property', '(edu.utah.sci.vistrails.basic:List)'),
    ]

    def __init__(self):
        SOSFeeder.__init__(self)

    def create_results(self):
        """Create list of XML POST datasets for each sensor.
        """
        data = {}
        data['offering'] = self.offering
        data['properties'] = self.property
        results = []
        for sensor in self.sensors:
            data['sensor'] = sensor
            for foi in self.foi:
                data['foi'] = foi
                XML = self.create_XML(sheet_name=None, data=data)
                if XML:
                    results.append(XML)
                    #print "\nSOSfeed:1003\n", XML
        return results

    def create_XML(self, sheet_name=None, data={}):
        """Create the XML for a RegisterSensor POST using a Jinja template
        """
        template = self.env.get_template('RegisterSensor.xml')
        # test data
        if self.test_mode:
            data['offering'] = {
                'ID': 'TEST',
                'name': 'Test Sensor Offering'}
            data['sensor'] = {
                'ID': 'urn:ogc:object:feature:Sensor:TestFooBar1',
                'name': 'Foo Bar 1',
                'srs': SRS_DEFAULT,
                'latitude': '30.3',
                'longitude': '29.1',
                'altitude': '0'}
            data['coords'] = []
            data['coords'].append({
                'type': 'longitude',
                'uom': 'degree'})
            data['coords'].append({
                'type': 'latitude',
                'uom': 'degree'})
            data['coords'].append({
                'type': 'altitude',
                'uom': 'm'})
            data['foi'] = {
                'name': 'Test FooBar 1',
                'id': 'TestFooBar1',
                'srs': SRS_DEFAULT,
                'coords': [(-42.91, 147.33)]}
            data['properties'] = []
            data['properties'].append({
              'name': 'temperature',
              'urn': 'urn:ogc:def:phenomenon:OGC:1.0.30:temperature',
              'type': 'Quantity',
              'units': 'celcius'})
            data['properties'].append({
              'name': 'humidity',
              'urn': 'urn:ogc:def:phenomenon:OGC:1.0.30:humidity',
              'type': 'Quantity',
              'units': 'percentage'})

        data = template.render(sensor=data.get('sensor'),
                               offering=data.get('offering'),
                               foi=data.get('foi'),
                               components=data.get('properties'),
                               coords=data.get('coords'),)
        return data  # XML

    def compute(self):
        super(RegisterSensor, self).compute()
        # check other port values
        _sensor = self.forceGetInputFromPort('sensor', None)
        if self.forceGetInputFromPort('offering'):
            _offering_ID, _offering_name = \
                self.forceGetInputFromPort('offering')
        else:
            _offering_ID, _offering_name = None, None

        if self.forceGetInputFromPort('sensor_details'):
            _sensor_ID, _sensor_name, _sensor_srs, _sensor_lat, _sensor_lon, _sensor_alt = \
                self.forceGetInputFromPort('sensor_details')
        else:
            _sensor_ID, _sensor_name, _sensor_srs, _sensor_lat, _sensor_lon, _sensor_alt = \
                None, None, None, None, None, None
        _coords = self.forceGetInputFromPort('coordinates', None)
        _FOI = self.forceGetInputFromPort('feature', None)
        _property = self.forceGetInputFromPort('property', None)

        # validate port values
        if not _sensor and not (_sensor_ID and _sensor_name):
            self.raiseError('Either sensor or sensor details must be specified')
        if not _property:
            self.raiseError('Property details are required!')

        # offering core metadata
        self.offering = {}
        self.offering['ID'] = cgi.escape(_offering_ID)
        self.offering['name'] = cgi.escape(_offering_name)

        # sensor(s) core metadata
        self.sensors = []
        # single sensor
        if  _sensor_ID:
            sensor = {}
            sensor['ID'] = cgi.escape(_sensor_ID)
            sensor['name'] = cgi.escape(_sensor_name)
            srs = _sensor_srs or SRS_DEFAULT
            sensor['srs'] = srs
            sensor['latitude'] = _sensor_lat
            sensor['longitude'] = _sensor_lon
            sensor['altitude'] = _sensor_alt
            self.sensors.append(sensor)
        # multiple sensors
        if _sensor:
            for item in _sensor:
                if item:
                    if len(item) >= 2:
                        _dict = dict(zip(xrange(len(item)), item))
                        self.sensors.append({
                            'ID': cgi.escape(_dict.get(0) or ""),
                            'name': cgi.escape(_dict.get(1) or ""),                            'latitude': _dict.get(2),
                            'longitude': _dict.get(3),
                            'altitude': _dict.get(4),
                            'srs': _dict.get(5) or SRS_DEFAULT})
                    else:
                        self.raiseError("Sensor does not contain sufficient data in each and/or every list.")

        # get sensor coords details as list of dictionaries
        self.coords = []
        if _coords:
            for item in _coords:
                #print "sosfeed:1090 item", item
                if item:
                    if len(item) >= 2:
                        _dict = dict(zip(xrange(len(item)), item))
                        if _dict.get(0) in ['longitude', 'latitude', 'altitude']:
                            self.coords.append({'type': _dict.get(0),
                                                'uom': _dict.get(1)})
                        else:
                            self.raiseError("Sensor co-ordinate types must be 'longitude', 'latitude' or 'altitude'")
                    else:
                        self.raiseError("Insufficient coordinates values in each and/or every list.")
        else:
            self.coords.append({'type': 'longitude', 'uom': 'degree'})
            self.coords.append({'type': 'latitude', 'uom': 'degree'})
            self.coords.append({'type': 'altitude', 'uom': 'm'})

        # get FOI lookup details as list of dictionaries
        self.foi = []
        if _FOI:
            for item in _FOI:
                #print "sosfeed:1115 item", len(item), item, bool(item)
                if item:
                    if len(item) >= 3:
                        _dict = dict(zip(xrange(len(item)), item))
                        self.foi.append({
                            'id':  cgi.escape(_dict.get(0) or ""),
                            'name': cgi.escape(_dict.get(1)or ""),
                            'coords': self.extract_pairs(_dict.get(2)),
                            'srs': _dict.get(3) or SRS_DEFAULT})
                    else:
                        self.raiseError("Insufficient FOI values in each and/or every list.")

        # get property lookup details as list of dictionaries
        self.property = []
        if _property:
            for item in _property:
                if item:
                    if len(item) >= 3:
                        _dict = dict(zip(xrange(len(item)), item))
                        self.property.append({
                            'name': cgi.escape(_dict.get(0) or ""),
                            'type': cgi.escape(_dict.get(1) or 'Quantity'),
                            'urn': cgi.escape(_dict.get(2) or ""),
                            'units': cgi.escape(_dict.get(3) or "")})
                    else:
                        self.raiseError("Insufficient property values on each line'")

        # process configuration and generate output
        try:
            results = self.create_results()
            # output POST data, if port is linked to another module
            if init.OGC_POST_DATA_PORT in self.outputPorts:
                self.setResult(init.OGC_POST_DATA_PORT, results)
            if self.active:
                self.webRequest.url = self.url
                dataset = []
                for result in results:
                    self.webRequest.data = result
                    data = self.webRequest.runRequest()
                    dataset.append(data)
                # output results of POSTs, if port is linked to another module
                if init.DATA_PORT in self.outputPorts:
                    self.setResult(init.DATA_PORT, dataset)
        except Exception, ex:
            self.raiseError(ex.message)

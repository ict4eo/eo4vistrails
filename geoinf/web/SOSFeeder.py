
"""This module forms part of the eo4vistrails capabilities. It is used to
handle data feeds to an OGC SOS (including InsertObservation & RegisterSensor)
"""
# library
import csv
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
        file_in:
            input Excel file
        sheets:
            a list of worksheet numbers, or names, that must be processed.
            If None, then all sheets will be processed. Sheet numbering starts
            from 1.
        active:
            Boolean port; if True (default is False) then outgoing data is
            POSTed directly to the specified SOS address (OGC_URL)

    Output ports:
        PostData:
            a list of XML strings; each containing data POSTed to the SOS
    """

    _input_ports = [
        ('OGC_URL', '(edu.utah.sci.vistrails.basic:String)'),
        ('file_in', '(edu.utah.sci.vistrails.basic:File)'),
        ('sheets', '(edu.utah.sci.vistrails.basic:List)'),
        ('active', '(edu.utah.sci.vistrails.basic:Boolean)'), ]
    _output_ports = [
        ('PostData', '(edu.utah.sci.vistrails.basic:List)'), ]

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

    def make_list(self, lst=None):
        """"Return a list from any given single element."""
        if not lst:
            return []
        if hasattr(lst, '__iter__'):
            return list(lst)
        else:
            return [lst]

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
        # port data
        self.URL = self.forceGetInputFromPort(init.OGC_URL_PORT, '')
        self.file_in = self.getInputFromPort('data_file')
        #_config = self.forceGetInputFromPort('configuration', None)
        self.active = self.forceGetInputFromPort('active', False)
        # validate port values
        if self.active and not self.URL:
            self.raiseError('SOS URL must be specified if feed is Active')
        # open data file
        try:
            self.workbook = xlrd.open_workbook(self.file_in.name)
        except:
            self.raiseError("%s is not a valid Excel file" % self.file_in.name)
        # get data sheets
        self.sheets = self.make_list(self.forceGetInputListFromPort('sheets'))
        self.set_sheet_list(self.sheets)
        if not self.sheet_list:
            self.raiseError("Unable to extract sheets from Excel file")

        # template location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, 'templates')
        #print "SOSFeeder:75", current_dir, template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir),
                               trim_blocks=True)

    def create_data(self):
        """Create the XML for the POST to the SOS, using a Jinja template."""
        pass  # override in inherited classes


class RegisterSensor(SOSFeeder):
    """TODO - Extend SOS Feeder to register a sensor for a SOS."""

    def __init__(self):
        SOSFeeder.__init__(self)

    def create_data(self, sheet_name=None):
        """Create the XML for the POST to the SOS, using a Jinja template."""
        return None  # TO DO !!!

    def compute(self):
        super(RegisterSensor, self).compute()
        # check other port values

        try:
            results = []
            for sheet_name in self.sheet_list:
                XML = self.create_data(sheet_name)
                results.append(XML)
                #print "SOSfeed:600\n", XML
                if self.active:
                    # TO DO ...post XML data
                    pass
            # output POST data, if port is linked to another module
            if init.OGC_POST_DATA_PORT in self.outputPorts:
                self.setResult(init.OGC_POST_DATA_PORT, results)
        except Exception, ex:
            self.raiseError(ex)


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
            a Boolean port; if True (default) then outgoing data is POSTed
            directly to the SOS
        procedure:
            The physical sensor or process that has carried out the observation

            name:
                the name of the procedure, which is set for all observations
            row:
                the row in which the name of the procedure appears - rows are
                numbered from 1 onwards.
            column:
                the column in which the name of the procedure appears - columns
                are numbered from 1 onwards.
        feature:
            The feature-of-interest (FOI) for which the observation was carried
            out; typically this corresponds to a geographical area or a
            monitoring station / sampling point.

            name:
                the name of the feature, which is set for all observations
            row:
                the row in which the name of the feature appears- rows are
                numbered from 1 onwards.
            column:
                the column in which the name of the feature appears- columns
                are numbered from 1 onwards.
        feature_details:
            An (optional) expanded set of information for each feature;
            including SRS, latitude and longitude.

            filename:
                the name of the CSV file containing the details for each
                feature, in the form:
                    name, SRS_value, "co-ordinates"
                where `co-ordinates` can be a single pair of space-separated
                lat/long values, or a comma-delimited list of such values.
                The co-ordinates must be wrapped in "" - e.g.
                    name_1, SRS_1, "45 12, 44 13, 43 14"
            dictionary:
               each dictionary entry is keyed on the feature ID, with a
               nested dictionary of feature details, in the format:
                    {"ID_1": {"name": "name_1", "srs": "SRS_1",
                              "coords": [(a,b), (c,d) ...]},
                     "ID_2": {"name": "name_2", "srs": "SRS_2",
                              "coords": [(p,q), (r,s) ...]},}
        property:
            The property ID which was measured or calculated as part of the
            observation; for example, the water flowrate at river guage.
            Multiple properties can be inserted as part of an observation.

            ID:
                the unique property ID, which is set for all observations
            row:
                the row in which the unique property ID appears- rows are
                numbered from 1 onwards.
            column:
                the column in which the unique property ID appears- columns
                are numbered from 1 onwards.
        property_details:
            An (optional) expanded set of information for each property;
            including its descriptiv name, the URN - as used by standards
            bodies, such OGC or NASA (SWEET), and units of measure (in
            standard SI notation).

            filename:
                the name of the CSV file containing the details for each
                property, in the form:
                    "id", "name", "URN_value", "units"
            dictionary:
                each dictionary entry is keyed on the property ID, with a
                list containing the details for that property, in the format:
                    {"ID_1": ["name_1", "URN_value1", "units_abc"],
                     "ID_2": ["name_2", "URN_value2", "units_pqr"],}
                these entries will be added to, and overwrite, and entries read
                in from the file

            A dictionary of commonly used properties, for measurements made in
            the environmental domain, is supplied with this program; this will
            only be used if information is not available from the above sources
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
            numeric) made for the properties at the specified dates.

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
            an XML string; containing data POSTed to the SOS
    """
    _input_ports = [
        ('procedure', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:Integer,edu.utah.sci.vistrails.basic:Integer)',
            {"defaults": str(["", 0, 0]),
             "labels": str(["name", "row", "column"])}),
        ('feature', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:Integer,edu.utah.sci.vistrails.basic:Integer)',
            {"defaults": str(["", 0, 0]),
             "labels": str(["name", "row", "column"])}),
        ('feature_details', '(edu.utah.sci.vistrails.basic:File,\
edu.utah.sci.vistrails.basic:Dictionary)',
            {"defaults": str(["", {}]),
             "labels": str(["file", "list"])}),
        ('property', '(edu.utah.sci.vistrails.basic:String,\
edu.utah.sci.vistrails.basic:Integer,edu.utah.sci.vistrails.basic:Integer)',
            {"defaults": str(["", 0, 0]),
             "labels": str(["ID", "row", "column"])}),
        ('property_details', '(edu.utah.sci.vistrails.basic:File,\
edu.utah.sci.vistrails.basic:Dictionary)',
            {"defaults": str(["", {}]),
             "labels": str(["file", "dictionary"])}),
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

    def load_from_excel(self, sheet_name=None):
        """Read data from a named Excel worksheet, and store in dictionaries

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
                details for a property ID, in the format:
                    {"ID_1": ["name_1", "URN_value1", "units_abc"],
                     "ID_2": ["name_2", "URN_value2", "units_pqr"],}
            self.feature_lookup: dictionary
                details for a feature, in the format:
                    {"ID_1": {"name": "name_1", "srs": "SRS_1",
                              "coords": [(a,b), (c,d) ...]},
                     "ID_2": {"name": "name_2", "srs": "SRS_2",
                              "coords": [(p,q), (r,s) ...]},}
        """

        def cell_value(sh, row_num, col_num):
            """Return the correct value from an Excel cell."""
            row_num = max(row_num, 0)
            col_num = max(col_num, 0)
            ctype = sh.cell(row_num, col_num).ctype
            val = sh.cell(row_num, col_num).value
            #print "sosfeed:359", row_num, col_num, val, ctype
            if ctype == 3:
                date_tuple = xlrd.xldate_as_tuple(val, self.workbook.datemode)\
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

        def add_property(name, type=None):
            """If property is found in lookup, add to properties attribute."""
            prop = self.property_lookup.get(name)
            #print "sosFeeder:389", name, type, prop
            if prop and len(prop) >= 3:
                self.properties.append({
                    'name': name,
                    'type': prop[0],
                    'urn': prop[1],
                    'units': prop[2],
                    })

        if self.configuration:
            config = self.configuration
        else:
            self.raiseError('Internal Error: Configuration not set.')
        sh = self.workbook.sheet_by_name(sheet_name)
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
        self.period = {
            'start': None,  # TODO ! calculate this from max date
            'end': None,  # TODO ! calculate this from min date
            'offset': config['period']['offset'] or 0}
        foi_ID = config['foi']['value'] or \
                 cell_value(sh, config['procedure']['rowcol'][0] - 1,
                                config['procedure']['rowcol'][1] - 1)
        foi_ID_entry = self.feature_lookup.get(foi_ID)
        if foi_ID_entry:
            self.foi = {
                'id': foi_ID,
                'name': foi_ID_entry.get('name') or foi_ID,
                'srs': foi_ID_entry.get('srs') or SRS_DEFAULT,
                'coords': foi_ID_entry.get('coords')}
        self.separator = config['separator']
        self.properties = []
        if config['properties']['value']:
            name = config['properties']['value']
            add_property(name, type='constant')
        elif config['properties']['rowcol'][0]:
            row_num = config['properties']['rowcol'][0]
            for col_num in range(0, sh.ncols):
                name = cell_value(sh, row_num - 1, col_num)
                add_property(name, type='row')
        elif config['properties']['rowcol'][1]:
            col_num = config['properties']['rowcol'][1]
            for row_num in range(0, sh.nrows):
                name = cell_value(sh, row_num, col_num - 1)
                add_property(name, type='col')

        # observation data values
        self.values = []
        offset = config['period']['offset']
        try:
            offset = int(offset)
        except:
            offset = 0
        if config['values']['rowcol'][0] - 1 > sh.nrows:
            self.raiseError('Observation rows outside sheet limits!')
        if config['values']['rowcol'][1] - 1 > sh.ncols:
            self.raiseError('Observation columns outside sheet limits!')

        for row_num in range(config['values']['rowcol'][0] - 1, sh.nrows):
            set = []
            for col_num in range(config['values']['rowcol'][1] - 1, sh.ncols):
                value = cell_value(sh, row_num, col_num)
                set.append(value)
            self.values.append(set)

    def create_data(self, sheet_name=None):
        """Create the XML for the POST to the SOS, using a Jinja template.
        """
        template = self.env.get_template('InsertObservation.xml')
        self.period, self.values, self.separator = None, [], None
        self.core, self.properties, self.foi = None, [], None
        # load data from file
        self.load_from_excel(sheet_name)
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
        self.properties = []
        self.properties.append({
          'urn': 'http://www.opengis.net/def/uom/ISO-8601/0/Gregorian',
          'name': 'Time',
          'type': 'Time'})
        self.properties.append({
          'urn': 'http://www.opengis.net/def/property/OGC/0/FeatureOfInterest',
          'name': 'feature',
          'type': 'Text'})
        self.properties.append({
          'name': 'temperature',
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
        data = template.render(period=self.period, values=self.values,
                               separator=self.separator, core=self.core,
                               properties=self.properties, foi=self.foi,)
        return data  # XML

    def compute(self):
        super(InsertObservation, self).compute()
        # get port values
        if self.forceGetInputFromPort('procedure'):
            _proc, _proc_row, _proc_col = self.forceGetInputFromPort('procedure')
        else:
            _proc, _proc_row, _proc_col = None, None, None
        if self.forceGetInputFromPort('feature'):
            _FOI, _FOI_row, _FOI_col = self.forceGetInputFromPort('feature')
        else:
            _FOI, _FOI_row, _FOI_col = None, None, None
        if self.forceGetInputFromPort('feature_details'):
            _FOI_file, _FOI_dict = self.forceGetInputFromPort('feature_details')
        else:
            _FOI_file, _FOI_dict = None, None
        if self.forceGetInputFromPort('property'):
            _prop, _prop_row, _prop_col = self.forceGetInputFromPort('property')
        else:
            _prop, _prop_row, _prop_col = None, None, None
        if self.forceGetInputFromPort('property_details'):
            _prop_file, _prop_dict = self.forceGetInputFromPort('property_details')
        else:
            _prop_file, _prop_dict = None, None
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
        if not _prop_file and not _prop_dict:
            self.raiseError('Either file or dictionary must be specified for %s'\
                            % 'property details')
        if not _FOI_file and not _FOI_dict:
            self.raiseError('Either file or dictionary must be specified for %s'\
                            % 'feature details')

        # get property lookup details as dictionary
        self.property_lookup = {}
        #print "sosfeeder:574", _prop_file, type(_prop_file), _prop_file.name
        if _prop_file and _prop_file.name:
            try:
                reader = csv.reader(open(_prop_file.name), delimiter=',',
                                    quotechar='"')
                self.property_lookup = {row[0]: row[1:] for row in reader}
            except IOError:
                self.raiseError('Properties file "%s" does not exist' % \
                                _prop_file.name)
        if _prop_dict:
            self.property_lookup.update(_prop_dict)

        # get FOI lookup details as list
        self.feature_lookup = {}
        if _FOI_file and _FOI_file.name:
            try:
                reader = csv.reader(open(_FOI_file.name), delimiter=',',
                                    quotechar='"')
                for row in reader:
                    coord_list = row[3].split(',')
                    coords = [(cl.strip(' ').split(' ')[0],
                               cl.strip(' ').split(' ')[1]) for cl in coord_list]
                    self.feature_lookup = {row[0]: {'name': row[1],
                                                    'srs': row[2],
                                                    'coords': coords}}
            except IOError:
                self.raiseError('Feature file "%s" does not exist' % \
                                _FOI_file.name)
            except IndexError:
                self.raiseError('Feature file "%s" is not configured properly' % \
                                _FOI_file.name)
        if _FOI_dict:
            self.feature_lookup.update(_FOI_dict)

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

        # process the data to create the POST
        try:
            results = []
            for sheet_name in self.sheet_list:
                XML = self.create_data(sheet_name)
                results.append(XML)
                #print "SOSfeeder:600\n", XML
                if self.active:
                    # TO DO ...post XML data
                    pass
            # output POST data, if port is linked to another module
            if init.OGC_POST_DATA_PORT in self.outputPorts:
                self.setResult(init.OGC_POST_DATA_PORT, results)
        except Exception, ex:
            self.raiseError(ex)

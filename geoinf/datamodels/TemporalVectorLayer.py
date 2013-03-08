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
"""This module provides a data structure for creating and storing vector data,
as well as associated attribute data (typically time-series data), based on the
format defined by QGIS, from different input data types.
"""
# library
import csv
from datetime import datetime, tzinfo, timedelta
# third party
import qgis.core
from PyQt4.QtCore import QFileInfo
try:
    from osgeo import ogr
except:
    import ogr
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.tools.utils.Parser import Parser
from packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.tools.utils.datetimeutils import parse_datetime,\
                                                      get_date_and_time
from packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
# local
from QgsLayer import QgsVectorLayer
from DataRequest import DataRequest


# strings that may be used by GML to indicate missing data
GML_NO_DATA_LIST = ["noData", "None", "Null", "NULL"]
# strings that may be used by GML to indicate certain types of data
GML_TIME_NAMES = ['time', 'esecs']
GML_DEPTH_NAMES = ['depth', 'z-position']
GML_LAT_NAMES = ['latitude', 'y-position']
GML_LON_NAMES = ['longitude', 'x-position']


#TODO: find out why geometry data is not extracted into CSV, R etc files ???


class TemporalVectorLayer(QgsVectorLayer):
    """Create an extended vector layer, based on a QGIS vector layer.

    Associated data is stored, and can be referenced, in a local file.

    For example, in the case of a SOS, the data fetched from the server
    will be stored in an O&M schema-based XML file, with the filename
    *self.results_file*

    Methods are provided to extract data from the GML file and return file(s)
    containing data in various formats; e.g. "flat files" such as CSV, ODV,
    or as plain GML (containing only location data)
    """

    def __init__(self, uri=None, layername=None, driver=None):
        QgsVectorLayer.__init__(self, uri, layername, driver)
        #print "TVL:79 - in layer creation",
        self.SUPPORTED_DRIVERS += ['OM', 'HDF']  # add new supported types
        self.time_series = {}
        self.results_file = None

    def compute(self):
        """Execute the module to create the output"""
        fileObj = None
        try:
            thefile = self.forceGetInputFromPort('file', None)
            dataReq = self.forceGetInputFromPort('dataRequest', None)
            #print "TVL:91 file,name", thefile, thefile.name

            try:
                isFILE = (thefile != None) and (thefile.name != '')
            except AttributeError:
                isFILE = (thefile.name != '')
            isQGISSuported = isinstance(dataReq, DataRequest) and \
                            dataReq.get_driver() in self.SUPPORTED_DRIVERS

            if isFILE:
                # self.results_file may have already been set directly
                if not self.results_file:
                    self.thefilepath = thefile.name
                    self.results_file = self.thefilepath
                else:
                    self.thefilepath = self.results_file
                #print "TVL:107", self.thefilepath
                #print "TVL:108", self.results_file
                self.thefilename = QFileInfo(self.thefilepath).fileName()
                qgis.core.QgsVectorLayer.__init__(
                    self,
                    self.thefilepath,
                    self.thefilename,
                    "ogr")
            elif isQGISSuported:
                qgis.core.QgsVectorLayer.__init__(
                    self,
                    dataReq.get_uri(),
                    dataReq.get_layername(),
                    dataReq.get_driver())
            else:
                if dataReq:
                    self.raiseError('Vector layer driver %s not supported' %
                                    str(dataReq.get_driver()))
                else:
                    pass
                    self.raiseError('No valid data request')

            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))

    def extract_field_data(self, doc, fields):
        """Return a list of field dictionaries from GML field element.
        
        :param str doc: a GML document (or section thereof)
        :param list field: a list of fields
        
        :rtype: a list with a field dictionary for each field, including:
            
            *   id
            *   name
            *   definition
            *   units
        """
        field_list = []
        if fields:
            for index, field in enumerate(fields):
                field_set = {}
                name = doc.elem_attr_value(field, 'name')
                units = None
                if len(field) > 0:  # no.of nodes
                    child = field[0]  # any of: Time/Quantity/Text/Category
                    defn = doc.elem_attr_value(child, 'definition')
                    field_set['id'] = index
                    field_set['definition'] = defn
                    field_set['name'] = name or defn
                    # units
                    uom = doc.elem_tag(child, 'uom')
                    field_set['units'] = doc.elem_attr_value(uom, 'code') or ''
                field_list.append(field_set)
        return field_list

    def extract_fields(self, thefile):
        """Parse a SOS GML file and extract the field data."""
        doc = Parser(file=thefile, namespace="http://www.opengis.net/swe/1.0.1")
        om_result = doc.tag('member/Observation/result', doc.get_ns('om'))
        fields = doc.elem_tags(
            om_result,
            'DataArray/elementType/DataRecord/field')
        return self.extract_field_data(doc, fields)

    def extract_procedure(self, doc=None, thefile=None):
        """Return the procedure from either a GML file or Observation element.
        
        .. warning:: This method has not been used or tested.
        """
        if thefile:
            doc = Parser(file=thefile, namespace="http://www.opengis.net/swe/1.0.1")
            om_result = doc.elem_tag('member/Observation/procedure')
        elif doc:
            om_result = doc.elem_tag('procedure')
        else:
            om_result = None
        if om_result:
            return doc.elem_attr_value(om_result, 'href', doc.get_ns('xlink'))
        return None

    def extract_bounds(self, thefile):
        """Parse a SOS GML file and extract the bounding box as a tuple."""
        doc = Parser(file=thefile, namespace="http://www.opengis.net/gml")
        try:
            bnd_up = doc.tag_value('boundedBy/Envelope/upperCorner').split()
            bnd_lo = doc.tag_value('boundedBy/Envelope/lowerCorner').split()
            return (bnd_up + bnd_up)
        except:
            return ()

    def extract_swe_values_GML(self, thefile, line=True):
        """Parse SOS output and extract locations from swe:values as GML data.
        
        :param str doc: a GML document (or section thereof)
        :param boolean line selection:if False, then points are returned
        
        :rtype:
            a string, with lat/lon data wrapped as elements in a GML line
        """
        doc = Parser(file=thefile, namespace="http://www.opengis.net/swe/1.0.1")
        GML = ''
        om_members = doc.tags('member', doc.get_ns('om'))
        for om_member in om_members:
            om_obs = doc.elem_tag(om_member,
                                  'Observation',
                                  doc.get_ns('om'))
            # process results...
            om_obs_result = doc.elem_tag(om_member,
                                       'Observation/result',
                                       doc.get_ns('om'))
            if om_obs_result:
                # meta data - field information
                fields = doc.elem_tags(
                    om_obs_result,
                    'DataArray/elementType/DataRecord/field')
                fields = self.extract_field_data(doc, fields)
                # locate lat/lon fields
                lat, lon = -1, -1
                for key, field in enumerate(fields):
                    if True in [field['name'].lower().__contains__(x) \
                                for x in GML_LAT_NAMES]:
                        lat = key
                    if True in [field['name'].lower().__contains__(x) \
                                for x in GML_LON_NAMES]:
                        lon = key
                # extract lat/lon data
                if lat > -1 and lon > -1:
                    textblock = doc.elem_tag(
                        om_obs_result,
                        'DataArray/encoding/TextBlock')
                    block = doc.elem_attr_value(textblock, 'blockSeparator')
                    token = doc.elem_attr_value(textblock, 'tokenSeparator')
                    values = doc.elem_tag_value(om_obs_result, 'DataArray/values')
                    if values:
                        val_set = values.split(block)
                        for val in val_set:
                            items = val.split(token)
                            try:
                                if line:
                                    GML = GML + '%s %s ' % (items[lat], items[lon])
                                else:
                                    GML = GML + '<gml:Point><gml:pos>%s %s</gml:pos></gml:Point>\n' % (items[lat], items[lon])
                            except:
                                pass
                        if GML:
                            if line:
                                return '<gml:LineString><gml:posList>%s\
                                        </gml:posList></gml:LineString>' % GML
        return GML

    def extract_time_series(self, thefile):
        """Parse a SOS GML file and extract time series and other meta data.
        
        :param str thefile:
            a GML document (or section thereof)
        
        :rtype: a list, with a dictionary for each member consisting of:
        
        *   fields
        *   observation
        *   sampling point
        *   feature
        *   data
        """
        doc = Parser(file=thefile, namespace="http://www.opengis.net/swe/1.0.1")
        results = []
        om_members = doc.tags('member', doc.get_ns('om'))
        for om_member in om_members:
            om_obs = doc.elem_tag(om_member,
                                  'Observation',
                                  doc.get_ns('om'))
            # look for an observation id
            observation = {}
            id = doc.elem_attr_value(om_obs, 'href', doc.get_ns('xlink'))
            if not id:
                id = doc.elem_attr_value(om_obs, 'id', doc.get_ns('gml'))
            observation['id'] = id
            # get procedure id/name
            om_proc = doc.elem_tag(om_member,
                                   'Observation/procedure',
                                   doc.get_ns('om'))
            observation['procedure'] = doc.elem_attr_value(om_proc, 'href',
                                                           doc.get_ns('xlink'))
            # process results...
            om_obs_result = doc.elem_tag(om_member,
                                       'Observation/result',
                                       doc.get_ns('om'))
            if om_obs_result is not None:
                result = {}
                # meta data - feature information
                feature = {}
                om_feature = doc.elem_tag(om_member,
                                        'Observation/featureOfInterest',
                                        doc.get_ns('om'))
                # look for a feature id
                id = doc.elem_attr_value(om_feature, 'href',
                                         doc.get_ns('xlink'))
                if not id:
                    id = doc.elem_attr_value(om_feature, 'id',
                                             doc.get_ns('gml'))
                feature['id'] = id
                feature['name'] = None  # attempt to find a name ...TODO???

                # get feature geometry
                om_point = doc.elem_tag_nested(om_feature,
                                               'Point',
                                               doc.get_ns('gml'))
                om_poly = doc.elem_tag_nested(om_feature,
                                               'Polygon',
                                               doc.get_ns('gml'))
                #print "TVL:320", om_point, om_poly
                geom_wkt = None
                if om_point:
                    geom_value = doc.elem_tag_value(om_point[0],
                                                    'pos',
                                                    doc.get_ns('gml'))
                    if not geom_value:
                        geom_value = doc.elem_tag_value(om_point[0],
                                                        'coordinates',
                                                        doc.get_ns('gml'))
                    # convert to WKT (Well Known Text) format
                    if geom_value:
                        points = geom_value.split(',')
                        #print "TVL:333 points", points
                        point = ogr.Geometry(ogr.wkbPoint)
                        if len(points) == 2:
                            point.AddPoint(float(points[0]), float(points[1]))
                            geom_wkt = point.ExportToWkt()
                elif om_poly:
                    for tag in om_poly:
                        geom_value = doc.elem_tag_value(tag,
                                                    'pos',
                                                    doc.get_ns('gml'))
                        if not geom_value:
                            geom_value = doc.elem_tag_value(tag,
                                                        'coordinates',
                                                        doc.get_ns('gml'))
                        if geom_value:
                            break
                    # convert to WKT (Well Known Text) format
                    if geom_value:
                        points = geom_value.split(' ')
                        poly = ogr.Geometry(ogr.wkbPoly)
                        for p in points:
                            lat_lon = p.split(',')
                            if len(lat_lon) == 2:
                                poly.AddPoint(float(lat_lon[0]), float(lat_lon[1]))
                        geom_wkt = poly.ExportToWkt()
                else:
                    pass  # could NOT detect feature geometry type ??? TODO
                feature['geometry'] = geom_wkt

                # look for a sample point id
                #   sa:SamplingPoint as a nested child ...
                sampling_point = {}
                om_sampling_point = doc.elem_tag_nested(om_feature,
                                                      'SamplingPoint',
                                                      doc.get_ns('sa'))
                #print "TVL:365", om_sampling_point
                if om_sampling_point and len(om_sampling_point) == 1:
                    id = doc.elem_attr_value(om_feature, 'xlink:href')
                    if not id:
                        id = doc.elem_attr_value(om_sampling_point[0],
                                                 'id',
                                                 doc.get_ns('gml'))
                sampling_point['id'] = id
                # meta data - field information
                fields = doc.elem_tags(
                    om_obs_result,
                    'DataArray/elementType/DataRecord/field')
                result['fields'] = self.extract_field_data(doc, fields)
                # data
                textblock = doc.elem_tag(
                    om_obs_result,
                    'DataArray/encoding/TextBlock')
                block = doc.elem_attr_value(textblock, 'blockSeparator')
                token = doc.elem_attr_value(textblock, 'tokenSeparator')
                value_list = []
                values = doc.elem_tag_value(om_obs_result, 'DataArray/values')
                if values:
                    val_set = values.split(block)
                    for val in val_set:
                        vals = []
                        items = val.split(token)
                        for item in items:
                            try:
                                vals.append(float(item))
                            except:
                                vals.append(item)
                        value_list.append(vals)
                # store results
                result['observation'] = observation
                result['sampling_point'] = sampling_point
                result['feature'] = feature
                result['data'] = value_list
                #print "TVL:405 extract_time_series", result
                results.append(result)
        return results

    def to_gml(self, filename_out, header=True,
               delimiter=',', quotechar=None, missing_value=None):
        """Transform GML to create a GML representation of all spatial data.
        
        :param str filename_out: name of the file to which the data must be written
        :param boolean header: if header row required (defaults to TRUE)
        :param str(1) delimiter: character between each field (defaults to ,)
        :param str(1) quotechar: character; if None then the CSV file writer has the
            QUOTE_MINIMAL flag
        :param str missing_value: a place-holder to be subsituted for missing data
        """
        HEADER = """<om:ObservationCollection
                    xmlns:om="http://www.opengis.net/om/1.0"
                    xmlns:swe="http://www.opengis.net/swe/1.0.1"
                    xmlns:gml="http://www.opengis.net/gml"
                    xmlns:xlink="http://www.w3.org/1999/xlink"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://www.opengis.net/om/1.0
                        http://schemas.opengis.net/om/1.0.0/om.xsd">"""
        FOOTER = '</om:ObservationCollection>\n'
        GML_file = self.results_file
        if not GML_file:
            self.raiseError('No GML file specified from which to extract data')
        results = self.extract_swe_values_GML(GML_file)
        #point_results = self.extract_swe_values_GML(GML_file, False)
        #print "TVL:399:gml", point_results
        if results:
            file_out = open(filename_out, "w")
            file_out.write(HEADER)
            file_out.write(results)
            file_out.write(FOOTER)
            file_out.close()
            return file_out
        else:
            return None

    def to_csv(self, filename_out, header=True,
               delimiter=',', quotechar=None, missing_value=None):
        """Transform GML to create a CSV representation of the time-series data.
        
        :param str filename_out: name of the file to which the data must be written
        :param boolean header: if header row required (defaults to TRUE)
        :param str delimiter: character between each field (defaults to ,)
        :param str quotechar: character; if None then the CSV file writer has the
            QUOTE_MINIMAL flag
        :param str missing_value: a place-holder to be subsituted for missing data
        
        :rtype:  A list of fully-qualified filenames, containing CSV data.
            Each 'member' node in the GML file will cause a new CSV file to have
            been created.
        
            The data columns in each CSV file are:
            *  Observation ID
            *  Feature ID
            *  Sample Point ID
            *  Geometry
            *  One or more columns with the phenomena/property data; typically
                with a field name, followed by a time value.  Units (if
                available in the meta data) are shown in square brackets []
                after the field name.
        """
        GML_file = self.results_file
        if not GML_file:
            self.raiseError('No GML file specified from which to extract data')
        results = self.extract_time_series(GML_file)  # get data & metadata
        #print "TVL:441", results[0], results[1]
        if results and results[0]['fields']:
            quoting = csv.QUOTE_NONNUMERIC
            file_out = open(filename_out, "w")
            if quotechar:
                csv_writer = csv.writer(file_out,
                                    delimiter=delimiter,
                                    quotechar=quotechar,
                                    quoting=quoting)
            else:
                csv_writer = csv.writer(file_out,
                                        delimiter=delimiter,
                                        quoting=quoting)

            if header:
                common = ['Observation', 'Feature', 'Sample Point', 'Geometry']
                #only take field names from FIRST member
                for field in results[0]['fields']:
                    _field = field['name']
                    if field['units']:
                        _field += ' [' + field['units'] + ']'
                    else:
                        _field += ' []'
                    common.append(_field)
                csv_writer.writerow(common)

            for result in results:
                # write to file
                for index, datum in enumerate(result['data']):
                    if missing_value:
                        for key, item in enumerate(datum):
                            #print "TVL:500", type(item), item
                            if not item or item in GML_NO_DATA_LIST:
                                datum[key] = missing_value
                    datum.insert(0, result['feature']['geometry'])
                    datum.insert(0, result['sampling_point']['id'])
                    datum.insert(0, result['feature']['id'])
                    datum.insert(0, result['observation']['id'])
                    csv_writer.writerow(datum)

            file_out.close()
            return file_out
        else:
            return None

    def to_odv(self, filename_out, missing_value=-1e10):
        """Transform GML to create a ODV representation of the time-series data.
        
        :param str filename_out: name of the file to which the data must be written
        :param str missing_value: a place-holder to be subsituted for missing data
        
        :rtype: file
            An ODV generic spreadsheet (text) file. See: `<http://odv.awi.de/>`_
            
            The data columns required by each ODV file are:
                "Cruise", "Station", "Type", "mon/day/yr", "hh:mm",
                "Lon (°E)", "Lat (°N)", "Bot. Depth [m]", followed by columns
                for data variables, up to 60 characters, long which should
                include unit specifications enclosed in brackets [ ].
            
            These correspond to the following fields from the GML:
             *  Cruise > Procedure ID
             *  Type > "*"  (ODV will choose approproiate type upon import)
             *  Station > Sample Point ID
             *  mon/day/yr > Date (day)
             *  hh:mm:ss > Date (time)
             *  Lat (°N) > latitude
             *  Lon (°E) > longitude
             *  Depth > "0"  (depth is unknown)
             *  Data Variables> one or more columns with the phenomena/property
                data; typically with a field name, followed by a time value.
                Units (if available in the meta data) are shown in square
                brackets [] after the field name.
        """
        GML_file = self.results_file
        if not GML_file:
            self.raiseError('No GML file specified from which to extract data')
        results = self.extract_time_series(GML_file)  # get data & metadata
        #print "TVL:545", results[0]
        if results and results[0]['fields']:
            file_out = open(filename_out, "w")
            csv_writer = csv.writer(file_out,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_NONNUMERIC)
            header = ["Cruise", "Station", "Type", "mon/day/yr", "hh:mm:ss",
                      "Lon (°E)", "Lat (°N)", "Bot. Depth [m]"]

            key_fields = [-1, -1, -1, -1]  # correspond to: date/time, lat, lon, depth
            #only take field names from FIRST member
            for field in results[0]['fields']:
                _field = field['name']
                key = field['id']
                # extract and record key fields used for OVD
                if True in [_field.lower().__contains__(x) for x in GML_TIME_NAMES]:
                    key_fields[0] = key
                elif True in [_field.lower().__contains__(x) for x in GML_LAT_NAMES]:
                    key_fields[1] = key
                elif True in [_field.lower().__contains__(x) for x in GML_LON_NAMES]:
                    key_fields[2] = key
                elif True in [_field.lower().__contains__(x) for x in GML_DEPTH_NAMES]:
                    key_fields[3] = key
                # ordinary (measured) variable fields
                else:
                    if field['units']:
                        _field += ' [' + field['units'] + ']'
                    else:
                        _field += ' []'
                    header.append(_field)
            reverse_key_fields = sorted(key_fields, reverse=True)
            csv_writer.writerow(header)

            #print "TVL:586", results[0]['fields'], key_fields
            for index, result in enumerate(results):
                for datum in result['data']:
                    if missing_value:
                        for item in datum:
                            try:
                                if not item or item in GML_NO_DATA_LIST:
                                    item.replace(GML_NO_DATA_LIST, missing_value)
                            except TypeError:
                                pass  # ignore non-strings
                    # extract key field values from datum
                    #print "TVL:596 datum", datum
                    time = day = lat = lon = None
                    depth = 0
                    for key, value in enumerate(datum):
                        if key in key_fields:
                            if key_fields[key] == 0:  # time
                                date_time = get_date_and_time(datum[key],
                                                              date_format="%m/%d/%Y")
                                day, time = date_time[0], date_time[1]
                            # NOTE !!! no formatting is performed on lat/lon fields...
                            if key_fields[key] == 1:  # lat
                                lat = datum[key]
                            if key_fields[key] == 2:  # lon
                                lon = datum[key]
                            if key_fields[key] == 3:  # depth
                                depth = datum[key]
                    # remove key field values from datum array, in REVERSE position
                    for kf in reverse_key_fields:
                        datum.pop(kf)
                    # add in key field values at the start of the datum array
                    datum.insert(0, depth)
                    datum.insert(0, lat)
                    datum.insert(0, lon)
                    datum.insert(0, time)
                    datum.insert(0, day)
                    datum.insert(0, "*")
                    datum.insert(0, result['sampling_point']['id'])
                    datum.insert(0, result['observation']['procedure'])
                    #datum.insert(0, result['observation']['id'])
                    csv_writer.writerow(datum)
            return file_out

    def to_numpy(self):
        """Transform GML to create a numpy array of the time-series data.
        
        .. todo:: Not yet implemented!
        """
        GML_file = self.results_file
        if not GML_file:
            self.raiseError('No GML file specified from which to extract data')
        results = self.extract_time_series(GML_file)  # get data & metadata

        # TO DO !!!
        self.raiseError('Code to convert layer to numpy is not implemented!')

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
"""This module is used to add data transformations for Spatial Layers to
eo4vistrails.
"""
# global
import csv as csv
# third-party
from PyQt4 import QtCore, QtGui
try:
    from osgeo import ogr
except:
    import ogr
# vistrails
from core.modules.vistrails_module import \
    Module, new_module, NotCacheable, ModuleError, ModuleErrors
# eo4vistrails
from packages.eo4vistrails.tools.utils.Parser import Parser
# local
from Transformer import Transform

GML_NO_DATA = "noData"  # string used by GML to indicate missing data
CSV_NO_DATA = "9999"  # string used by CSV to indicate missing data


class SpatialTemporalTransform(Transform):
    """Transform GML data associated with a Spatial Temporal Layer.

    Parse the GML (XML format) file created by a OGC web service (for example,
    a SOS) and create a CSV representation of the time-series data.

    The data columns in each CSV file are:
     *  Observation ID
     *  Feature ID
     *  Sample Point ID
     *  Geometry
     *  One or more columns with the phenomena/property data; typically with
        a field name, followed by a time value.  Units (where available in
        the meta data) are shown in brackets after the field name.

    Requires:
     *  the filename containing the GML data

    Returns:
     *  A list of fully-qualified filenames, containing CSV data.
        Each 'member' node in the GML file will cause a new CSV file to have
        been created.
    """

    _input_ports = [('QgsMapLayer', '(za.co.csir.eo4vistrails:QgsMapLayer:data)'), ]
    # need a port that has an array of output choices ?
    _output_ports = [('CSV_list', '(edu.utah.sci.vistrails.basic:List)')]
    # ('output file', '(edu.utah.sci.vistrails.basic:File)')

    def __init__(self):
        Transform.__init__(self)

    def compute(self):
        # get layer from input port
        layer = self.getInputFromPort('QgsMapLayer')
        # get other parameters (from input ports?) e.g. CSV options
        # TODO ???
        try:
            # get GML file associated with layer
            gml_file = layer.results_file
            if 'CSV_list' in self.outputPorts:
                # call get_csv to process GML
                filename_list = self.get_csv(gml_file, missing_value=CSV_NO_DATA)
                # attach result (list of filenames) to the output port
                self.setResult("CSV_list", filename_list)
        except Exception, e:
            self.setResult("CSV_list", None)
            self.raiseError('Cannot process output specifications: %s' % str(e))


    def get_csv(self, SOS_XML_file, delimiter=',', header=True,
                quotechar='"', missing_value=None):
        """Create one or more CSV files, containing time series data.

        Requires:
         *  a GML (XML-based) file
         *  a delimiter character (between each field)
         *  a boolean header value (ON/off)
         *  a quote character; if None then the CSV file writer has the
            QUOTE_MINIMAL flag
         *  a string to be used in place of any missing data

        Returns:
         *  a tuple of filenames.
        """
        if not SOS_XML_file:
            self.raiseError('No GML file specified from which to extract CSV data')
        results = self.extract_time_series(SOS_XML_file)  # get data a& metadata
        filenames = []
        for index, result in enumerate(results):
            file_out = self.interpreter.filePool.create_file(suffix=".csv")
            # delete next 2 lines if using VT "temp" file
            #if index > 0:
            #    file_out = file_out + '_' + str(index)
            #f_out = open(file_out.name, "w")
            if quotechar:
                quoting = csv.QUOTE_NONNUMERIC
            else:
                quoting = csv.QUOTE_MINIMAL
            csv_writer = csv.writer(open(file_out.name, "w"),
                                    delimiter=delimiter,
                                    quotechar=quotechar,
                                    quoting=quoting)
            if header:
                common = ['Observation', 'Feature', 'Sample Point', 'Geometry']
                for field in result['fields']:
                    _field = field['name']
                    if field['units']:
                        _field += ' (' + field['units'] + ')'
                    common.append(_field)
                csv_writer.writerow(common)
            # write to file
            for datum in result['data']:
                if missing_value:
                    for item in datum:
                        if GML_NO_DATA in item:
                            item.replace(GML_NO_DATA, missing_value)
                datum.insert(0, result['feature']['geometry'])
                datum.insert(0, result['sampling_point']['id'])
                datum.insert(0, result['feature']['id'])
                datum.insert(0, result['observation']['id'])
                csv_writer.writerow(datum)
            # track filename used
            filenames.append(file_out.name)
        #print "TLT:154", filenames
        return filenames

    def get_fields(self, thefile):
        """Parse a SOS GML file and extract the field data."""
        doc = Parser(file=thefile, namespace="http://www.opengis.net/swe/1.0.1")
        om_result = doc.tag('member/Observation/result', doc.get_ns('om'))
        fields = doc.elem_tags(
            om_result,
            'DataArray/elementType/DataRecord/field')
        return self.extract_field_data(doc, fields)

    def get_bounds(self, thefile):
        """Parse a SOS GML file and extract bounding box as a tuple."""
        doc = Parser(file=thefile, namespace="http://www.opengis.net/gml")
        try:
            bnd_up = doc.tag_value('boundedBy/Envelope/upperCorner').split()
            bnd_lo = doc.tag_value('boundedBy/Envelope/lowerCorner').split()
            return (bnd_up + bnd_up)
        except:
            return []

    def extract_field_data(self, doc, fields):
        """Return a data dictionary from a SOS XML field element."""
        field_list = []
        if fields:
            for index, field in enumerate(fields):
                field_set = {}
                name = doc.elem_attr_value(field, 'name')
                units = None
                if len(field) > 0:  # no.of nodes
                    child = field[0]  # any of: Time/Quantity/Text/Category
                    defn = doc.elem_attr_value(child, 'definition')
                    field_set['definition'] = defn
                    field_set['name'] = name or defn
                    # units
                    uom = doc.elem_tag(child, 'uom')
                    field_set['units'] = doc.elem_attr_value(uom, 'code') or ''
                field_list.append(field_set)
        return field_list

    def extract_time_series(self, thefile):
        """Parse a SOS GML file and extract time series and other meta data."""
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
            # process results...
            om_obs_result = doc.elem_tag(om_member,
                                       'Observation/result',
                                       doc.get_ns('om'))
            if om_obs_result:
                result = {}
                # 'meta' data - feature information
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
                feature['name'] = None  # attempt to find a name ...???
                # get feature geomtry
                om_point = doc.elem_tag_nested(om_feature,
                                               'Point',
                                               doc.get_ns('gml'))
                if om_point:
                    geom_wkt = None
                    geom_value = doc.elem_tag_value(om_point[0],
                                                    'pos',
                                                    doc.get_ns('gml'))
                    if not geom_value:
                        geom_value = doc.elem_tag_value(om_point,
                                                        'coordinates',
                                                        doc.get_ns('gml'))
                    # convert to WKT (well known text format)
                    if geom_value:
                        points = geom_value.split(' ')
                        point = ogr.Geometry(ogr.wkbPoint)
                        point.AddPoint(float(points[0]), float(points[1]))
                        geom_wkt = point.ExportToWkt()  # WKT format
                    feature['geometry'] = geom_wkt
                else:
                    feature['geometry'] = None
                # look for a sample point id
                #   sa:SamplingPoint as a nested child ...
                sampling_point = {}
                om_sampling_point = doc.elem_tag_nested(om_feature,
                                                      'SamplingPoint',
                                                      doc.get_ns('sa'))
                #print "TLT:125", om_sampling_point
                if om_sampling_point and len(om_sampling_point) == 1:
                    id = doc.elem_attr_value(om_feature, 'xlink:href')
                    if not id:
                        id = doc.elem_attr_value(om_sampling_point[0],
                                                 'id',
                                                 doc.get_ns('gml'))
                sampling_point['id'] = id
                # 'meta' data - field information
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
                        value_list.append(val.split(token))
                # store results
                result['observation'] = observation
                result['sampling_point'] = sampling_point
                result['feature'] = feature
                result['data'] = value_list
                #print "extract_time_series:133", result
                results.append(result)
        return results

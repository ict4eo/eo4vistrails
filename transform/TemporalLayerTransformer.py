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
from packages.eo4vistrails.utils.Parser import Parser
# local
import Transformer

CSV_OUT = "/tmp/sos.csv"  # need to use VisTrails temp file


class SpatialTemporalTransformModule(Transformer, Module):
    """Transform GML data associated with a Spatial Temporal Layer"""

    _input_ports  = [('QgsMapLayer', '(za.co.csir.eo4vistrails:QgsMapLayer:data)'), ]
    # need a port that has an array of output choices ?
    _output_ports = [('raster layer', '(za.co.csir.eo4vistrails:Raster Layer:data)'),
                     ('filenames', '()')]
    # ('output file', '(edu.utah.sci.vistrails.basic:File)')

    def __init__(self):
        Transformer.__init__(self)
        Module.__init__(self)

    def compute(self):
        pass
        # get layer from input port
        layer = self.getInputFromPort('QgsMapLayer')
        # get other params (from input port?) e.g. CSV options
        # ???
        # get file associated with layer
        gml_file = layer.results_file
        # call get_csv
        # filenames = self.get_csv(gml_file)
        # attach result (list of filenames) to output port
        # self.setResult("raster filename", filenames)

    def get_csv(SOS_XML_file, delimiter=',', header=True, missing_value=None,
                quotechar='"'):
        """Create one or more CSV files, containing time series data.

        Return a tuple of filenames.
        """
        results = extract_time_series(SOS_XML_file)  # get data and metadata
        filenames = []
        for index, result in enumerate(results):
            file_out = CSV_OUT
            # delete next 2 lines if using VT "temp" file
            if index > 0:
                file_out = file_out + '_' + str(index)
            f_out = open(file_out, "w")
            if quotechar:
                quoting = csv.QUOTE_NONNUMERIC
            else:
                quoting = csv.QUOTE_MINIMAL
            csv_writer = csv.writer(open(file_out, "w"),
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
            for index, datum in enumerate(result['data']):
                datum.insert(0, result['feature']['geometry'])
                datum.insert(0, result['sampling_point']['id'])
                datum.insert(0, result['feature']['id'])
                datum.insert(0, result['observation']['id'])
                csv_writer.writerow(datum)
            # track filename used
            filenames.append(file_out)
        return filenames

    def get_fields(thefile):
        """Parse a SOS GML file and extract the field data."""
        doc = Parser(file=thefile, namespace="http://www.opengis.net/swe/1.0.1")
        om_result = doc.tag('member/Observation/result', doc.get_ns('om'))
        fields = doc.elem_tags(
            om_result,
            'DataArray/elementType/DataRecord/field')
        return extract_field_data(doc, fields)

    def get_bounds(thefile):
        """Parse a SOS GML file and extract bounding box as a tuple."""
        doc = Parser(file=thefile, namespace="http://www.opengis.net/gml")
        try:
            bnd_up = doc.tag_value('boundedBy/Envelope/upperCorner').split()
            bnd_lo = doc.tag_value('boundedBy/Envelope/lowerCorner').split()
            return (bnd_up + bnd_up)
        except:
            return []

    def extract_field_data(doc, fields):
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

    def extract_time_series(thefile):
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
                print "125", om_sampling_point
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
                result['fields'] = extract_field_data(doc, fields)
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

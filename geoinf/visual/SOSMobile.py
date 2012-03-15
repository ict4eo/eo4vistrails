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
"""This package provides GIS capabilities for eo4vistrails.
This module provides a means for displaying converting temporal vector data,
derived from a mobile SOS, to add-in GML from location data embedded in the
observation results.
"""
# library
import sys
import os
import os.path
# third party
from qgis.core import *
from qgis.gui import *
# vistrails
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
import core.system
# eo4vistrails
import packages.eo4vistrails.geoinf.visual
from packages.eo4vistrails.geoinf.datamodels.TemporalVectorLayer import \
    TemporalVectorLayer
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin


@RPyCSafeModule()
class SOSMobile(ThreadSafeMixin, Module):
    """Utility for creating an enhanced data file from a temporal vector layer.

    Input Ports:
        temporal_vector_layer:
            a temporal_vector_layer (derived from a SOS GetObservation)
        style:
            `point` or `line` (default is `point`)

    Notes:

    This module extracts location data (if any) from the swe:values in the GML
    file associated with the temporal vector layer and creates a new element
    in the GML - either a multi-point or a line, depending on  user selection.
    This new element in inserted as a child element of the featureOfInterest.

    It should be noted that GDAL/OGR (used by QGIS to import GML) seems to
    only extract one set of GML data for each featureOfInterest; specifically
    the last GML element loaded.  So, in this case, displaying the new
    temporal vector layer in QGISCanvas will only show the new multi-point (or
    line) element and not the original GML linked to the featureOfInterest.
    """

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        vector_layer = self.getInputFromPort('temporal_vector_layer')
        style = self.forceGetInputFromPort('mobile_format', 'point')
        #print "SOSMobile:83", vector_layer.results_file #vector_layer.__dict__
        GML_tree = self.inject_results_gml(filename=vector_layer.results_file,
                                           style=style)
        if GML_tree:
            fileObj = self.interpreter.filePool.create_file(suffix=".gml")
            GML_tree.write(fileObj.name)
            temporalVectorLayer = TemporalVectorLayer(fileObj.name,
                                                      fileObj.name, "ogr")
            temporalVectorLayer.results_file = fileObj.name
            self.setResult('temporal_vector_layer', temporalVectorLayer)
        else:
            self.setResult('temporal_vector_layer', None)

    def inject_results_gml(self, filename=None, data=None, style='point'):
        """Extract locations from SOS swe:results, and adds to XML as GML data.

        Args
            data:
                a string containing a SOS XML observation result
                (om:ObservationCollection)
            filename:
                the name of a file containing SOS XML observation results
                (om:ObservationCollection)
            style: `point` or `line`

        Returns
            ElementTree:
                XML (om:ObservationCollection) with GML-encoded locations,
                extracted from swe:results as `point` or `line` values,
                appended at the end of the swe:DataArray tag.
        """

        import xml.etree.ElementTree as ET

        try:
            register_namespace = ET.register_namespace  # only ElementTree 1.3
        except AttributeError:

            def register_namespace(prefix, uri):
                ET._namespace_map[uri] = prefix

        # add other names as needed
        GML_LAT_NAMES = ['latitude', 'y-position']
        GML_LON_NAMES = ['longitude', 'x-position']
        SWE = "{http://www.opengis.net/swe/1.0.1}"
        OM = "{http://www.opengis.net/om/1.0}"

        # namespaces - otherwise ElementTree uses ns* everywhere
        register_namespace("html", "http://www.w3.org/1999/xhtml")
        register_namespace("sos", "http://www.opengis.net/sos/1.0")
        register_namespace("om", "http://www.opengis.net/om/1.0")
        register_namespace("swe", "http://www.opengis.net/swe/1.0.1")
        register_namespace("gml", "http://www.opengis.net/gml")
        register_namespace("xlink", "http://www.w3.org/1999/xlink")
        register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

        lat, lon = -1, -1
        block = token = None, None
        if style == 'line':
            line = True
        else:
            line = False

        # root element
        if filename or data:
            if data:
                tree = ET.fromstring(data)
            elif filename:
                try:
                    full_tree = ET.parse(filename)
                    tree = full_tree.getroot()
                except IOError, e:
                    tree = None
                    raise ModuleError(self, 'Unable to process %s' % filename)
        if not tree:
            return None

        # add other namespaces back in to the root element
        # clunky?  yes - see http://bytes.com/topic/python/answers/565988-\
        #                    elementtree-namespace-declaration-each-element
        tree.set("xmlns:sos", "http://www.opengis.net/sos/1.0")
        tree.set("xmlns:gml", "http://www.opengis.net/gml")
        tree.set("xmlns:swe", "http://www.opengis.net/swe/1.0.1")
        tree.set("xmlns:xlink", "http://www.w3.org/1999/xlink")

        leaves = tree.getiterator()
        for key, leaf in enumerate(leaves):
            try:
                if leaf.tag == '%sfeatureOfInterest' % OM:
                    current_foi = leaf

                if leaf.tag == '%sDataArray' % SWE:

                    _fields = leaf.findall("%selementType/%sDataRecord/%sfield" % \
                                           (SWE, SWE, SWE))
                    if _fields:
                        for key, _field in enumerate(_fields):
                            _name = _field.attrib.get("name")  # name="y-position"
                            if True in [_name.lower().__contains__(x) \
                                        for x in GML_LAT_NAMES]:
                                lat = key
                            if True in [_name.lower().__contains__(x) \
                                        for x in GML_LON_NAMES]:
                                lon = key
                        #print "SOSMobile:187 _fields", lat, lon

                    textblock = leaf.findall("%sencoding/%sTextBlock" % (SWE, SWE))
                    if textblock:
                        block = textblock[0].attrib.get('blockSeparator')
                        token = textblock[0].attrib.get('tokenSeparator')
                        #print "SOSMobile:192 textblock", block, token

                    _values = leaf.findall("%svalues" % (SWE,))
                    GML = ""
                    if not line:
                        multipoint = ET.SubElement(leaf, "gml:MultiPoint")
                        multipoint.set("srsName", "EPSG:4326")  # TOD - get srs from Feature?
                    if _values and _values[0].text and lat > -1 and lon > -1:
                        #print "SOSMobile:200 ... processing values"
                        val_set = _values[0].text.split(block)
                        for val in val_set:
                            try:
                                items = val.split(token)
                                if  not line:
                                    # NB: namespaces defined in the root element
                                    pointmember = ET.SubElement(multipoint,
                                                                "gml:pointMember")
                                    point = ET.SubElement(pointmember, "gml:Point")
                                    pos = ET.SubElement(point, "gml:pos")
                                    pos.text = '%s %s' % (items[lon], items[lat])
                                else:
                                    GML = GML + '%s %s ' % (items[lon], items[lat])
                            except:
                                pass
                        if line and GML:
                            line = ET.SubElement(leaf, "gml:LineString")
                            pos = ET.SubElement(line, "gml:posList")
                            pos.text = GML

            except AttributeError:
                pass
                #print "SOSMobile:224 ", leaf.__dict__

        return ET.ElementTree(tree)  # as string: return ET.tostring(tree)

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
"""This module forms part of EO4VisTrails capabilities - it is used to
handle XML file processing.
"""

#all namespaces used by geospatial XML file
NAMESPACES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rss": "http://purl.org/rss/1.0/",
    "taxo": "http://purl.org/rss/1.0/modules/taxonomy/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "syn": "http://purl.org/rss/1.0/modules/syndication/",
    "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "csw": "http://www.opengis.net/cat/csw/2.0.2",
    "dct": "http://purl.org/dc/terms/",
    "gco": "http://www.isotc211.org/2005/gco",
    "gmd": "http://www.isotc211.org/2005/gmd",
    "gts": "http://www.isotc211.org/2005/gts",
    "srv": "http://www.isotc211.org/2005/srv",
    "fgdc": "http://www.fgdc.gov",
    "dif": "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/",
    "gml": "http://www.opengis.net/gml",
    "ogc": "http://www.opengis.net/ogc",
    "ows": "http://www.opengis.net/ows",
    "ows": "http://www.opengis.net/ows/1.1",
    "ows": "http://www.opengis.net/ows/2.0",
    "wms": "http://www.opengis.net/wms",
    "wmc": "http://www.opengis.net/context",
    "wfs": "http://www.opengis.net/wfs",
    "sos": "http://www.opengis.net/sos/1.0",
    "rim": "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "xs2": "http://www.w3.org/XML/Schema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xlink": "http://www.w3.org/1999/xlink",
    "om": "http://www.opengis.net/om/1.0",
    "swe": "http://www.opengis.net/swe/1.0.1",
    "sa": "http://www.opengis.net/sampling/1.0"}

#ows
KEY_NAMESPACE = 'http://www.opengis.net/ows/1.1'


def patch_well_known_namespaces(etree_module):
    """Monkey patches the etree module to add some well-known namespaces."""
    etree_module._namespace_map.update({
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#":  "rdf",
            "http://purl.org/rss/1.0/":                     "rss",
            "http://purl.org/rss/1.0/modules/taxonomy/":    "taxo",
            "http://purl.org/dc/elements/1.1/":             "dc",
            "http://purl.org/rss/1.0/modules/syndication/": "syn",
            "http://www.w3.org/2003/01/geo/wgs84_pos#":     "geo",
            "http://www.opengis.net/cat/csw/2.0.2":         "csw",
            "http://purl.org/dc/terms/":                    "dct",
            "http://www.isotc211.org/2005/gco":             "gco",
            "http://www.isotc211.org/2005/gmd":             "gmd",
            "http://www.isotc211.org/2005/gts":             "gts",
            "http://www.isotc211.org/2005/srv":             "srv",
            "http://www.fgdc.gov":                          "fgdc",
            "http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/":   "dif",
            "http://www.opengis.net/gml":                   "gml",
            "http://www.opengis.net/ogc":                   "ogc",
            "http://www.opengis.net/ows":                   "ows",
            "http://www.opengis.net/ows/1.1":               "ows",
            "http://www.opengis.net/ows/2.0":               "ows",
            "http://www.opengis.net/wms":                   "wms",
            "http://www.opengis.net/context":               "wmc",
            "http://www.opengis.net/wfs":                   "wfs",
            "http://www.opengis.net/sos/1.0":               "sos",
            "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0":  "rim",
            "http://www.w3.org/2001/XMLSchema":             "xs",
            "http://www.w3.org/XML/Schema":                 "xs2",
            "http://www.w3.org/2001/XMLSchema-instance":    "xsi",
            "http://www.w3.org/1999/xlink":                 "xlink",
            "http://www.opengis.net/om/1.0":                "om",
            "http://www.opengis.net/swe/1.0.1":             "swe",
            "http://www.opengis.net/sampling/1.0":          "sa"})

try:
    # Python < 2.5 with ElementTree installed
    import elementtree.ElementTree as etree
    patch_well_known_namespaces(etree)
except ImportError:
    try:
        # Python 2.5 with ElementTree included
        import xml.etree.ElementTree as etree
        patch_well_known_namespaces(etree)
    except ImportError:
        try:
            from lxml import etree
        except ImportError:
            raise RuntimeError(
                'You need either ElementTree or lxml to use Parser!')


class Parser(object):
    """This module provides utility methods to parse an XML datastream.
    """

    def __init__(self, file=None, url=None, data=None, namespace=KEY_NAMESPACE):
        self.url = url
        self.file = file
        self.data = data
        self.namespace = namespace or KEY_NAMESPACE
        self.xml = None
        if self.file:
            f = open(self.file)
            self.xml = etree.fromstring(f.read())
        elif self.data:
            self.xml = etree.fromstring(data)
        elif self.url:
            pass
            #TO DO: add capability to open XML from a URL -
            #       see lib/owslib/ows.py - def openURL()

    def tag(self, item, namespace=None):
        """Return a tag as an element object, based on XML document."""
        if not namespace:
            namespace = self.namespace
        try:
            foo = self.nspath(item, namespace)
            return self.xml.find(foo)
        except:
            return None

    def tags(self, item, namespace=None):
        """Return a set of tags as element objects, based on XML document."""
        if not namespace:
            namespace = self.namespace
        try:
            foo = self.nspath(item, namespace)
            return self.xml.findall(foo)
        except:
            return None

    def tag_value(self, item, namespace=None):
        """Return the text value of a tag, based on XML document."""
        if not namespace:
            namespace = self.namespace
        try:
            foo = self.nspath(item, namespace)
            val = self.xml.find(foo)
            return self.testXMLValue(val)
        except:
            return None

    def elem_tag(self, element, item, namespace=None):
        """Return a tag as an element object, for a given element."""
        if not namespace:
            namespace = self.namespace
        try:
            foo = self.nspath(item, namespace)
            return element.find(foo)
        except:
            return None

    def elem_tag_nested(self, element, item, namespace=None):
        """Return all child tags as an array of element objects,
        i.e. those nested somewhere inside a given parent element."""
        if not namespace:
            namespace = self.namespace
        try:
            foo = self.nspath(item, namespace)
            return element.getiterator(foo)
        except:
            return None

    def elem_tag_value(self, element, item, namespace=None):
        """Return the text value of a tag, for a given element."""
        if not namespace:
            namespace = self.namespace
        try:
            foo = self.nspath(item, namespace)
            val = element.find(foo)
            return self.testXMLValue(val)
        except:
            return None

    def elem_attr_value(self, element, attribute, namespace=None):
        """Return an attribute value for an element.
        
        *NOTE:* elementtree considers an element to "not exist" if it does not
        contain tag data; even though it may have attributes, so this test:
        
            if element:
        
        is insufficient to check that an element does/does not exist in the
        source document.
        """
        if not namespace:
            namespace = self.namespace
        result = None
        try:
            element.__dict__  # causes exception if element does not exist
            try:
                result = element.attrib[self.nspath(attribute, namespace)]
            except:
                result = element.attrib[attribute]
        except:
            pass  # element does not exist
        return result

    def elem_attr_values(self, element, namespace=None):
        """Return a dictionary of all attribute values for an element."""
        #TODO
        result = {}
        return result

    def elem_tags(self, element, item, namespace=None):
        """Return a set of tags as element objects, for a given element."""
        if not namespace:
            namespace = self.namespace
        try:
            foo = self.nspath(item, namespace)
            return element.findall(foo)
        except:
            return None

    def get_ns(self, key):
        """Return the full namespace from an abbrevation."""
        return NAMESPACES[key]

    def nspath(self, path, namespace=None):
        """Prefix the given path with the given namespace identifier.

        Parameters:
         *  path: ElementTree API Compatible path expression
         *  ns: the XML namespace URI.
        """
        if path is None:
            return None
        if not namespace:
            namespace = self.namespace
        components = []
        if '/' in path:
            for component in path.split('/'):
                if component != '*':
                    component = '{%s}%s' % (namespace, component)
                components.append(component)
            return '/'.join(components)
        else:
            return '{%s}%s' % (namespace, path)

    def elem_find(self, element, nss=()):
        """Wraps etree.find to search MULTIPLE namespaces

        Parameters:
         *  element: name of element
         *  nss:  a tuple of possible XML namespace URIs
        """
        if name is None:
            return None
        if not nss:
            nss = (self.namespace, '')

        for namespace in nss:
            if namespace:
                path = '{%s}%s' % (namespace, element)
            else:
                path = element
            val = element.find(path)
            if val:
                return val
        return none

    def testXMLValue(self, val, attrib=False):
        """Test that the XML value exists

        Parameters:
         *  val: the value to be tested

        Returns:
         *  exists: returns val.text
         *  not exists: returns None
        """
        if val is not None:
            if attrib == True:
                return val
            else:
                return val.text
        else:
            return None

    def xmlvalid(self, xml, xsd):
        """Test whether an XML document is valid against an XSD Schema

        Parameters:
         *  xml: XML content
         *  xsd: pointer to XML Schema (local file path or URL)
        """
        xsd1 = etree.parse(xsd)
        xsd2 = etree.XMLSchema(xsd1)
        doc = etree.parse(StringIO(xml))
        return xsd2.validate(doc)

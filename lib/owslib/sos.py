# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2008, Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@hotmail.com>
#
# Contact email: tomkralidis@hotmail.com
# =============================================================================
#
# Authors : Derek Hohls <dhohls@csir.co.za>
#
# Contact email: dhohls@csir.co.za
# =============================================================================


"""
API for Sensor Observation Service (SOS) methods and metadata.

Currently supports only version 1.0.0 of the SOS protocol.
"""

import cgi
from urllib import urlencode
from urllib2 import urlopen
from urllib2 import HTTPPasswordMgrWithDefaultRealm
from urllib2 import HTTPBasicAuthHandler
from urllib2 import ProxyHandler
from urllib2 import build_opener
from urllib2 import install_opener
from urllib2 import URLError
from etree import etree

import owslib.ows as ows
from owslib import util
import filter

GML_NAMESPACE = 'http://www.opengis.net/gml'
SOS_NAMESPACE = 'http://www.opengis.net/sos/1.0'
XLINK_NAMESPACE = 'http://www.w3.org/1999/xlink'


class ServiceException(Exception):
    pass


class CapabilitiesError(Exception):
    pass


class SensorObservationService(object):
    """Abstraction for OGC Sensor Observation Service (SOS).

    Implements ISensorObservationService.
    """

    def __getitem__(self, name):
        ''' check contents dict to allow dict like access to service layers'''
        if name in self.__getattribute__('contents').keys():
            return self.__getattribute__('contents')[name]
        else:
            raise KeyError("No content named %s" % name)

    def __init__(self, url, version='1.0.0', xml=None,
                username=None, password=None, timeout=None, ignore_proxy=False):
        """Initialize."""
        self.url = url
        self.username = username
        self.password = password
        self.timeout = timeout
        self.ignore_proxy = ignore_proxy
        self.version = version
        self._capabilities = None

        self._open = urlopen
        if self.ignore_proxy:
            #print "sos:76 - ignoring proxy..."
            proxy_support = ProxyHandler({})  # disables proxy
            opener = build_opener(proxy_support)
            install_opener(opener)
            self._open = opener.open

        if self.username and self.password:
            # Provide login information in order to use the SOS server
            # Create an OpenerDirector with support for Basic HTTP
            # Authentication...
            passman = HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, self.url, self.username, self.password)
            auth_handler = HTTPBasicAuthHandler(passman)
            opener = build_opener(auth_handler)
            self._open = opener.open
            reader = SOSCapabilitiesReader(
                self.version, url=self.url, un=self.username, pw=self.password,
                to=self.timeout, px=self.ignore_proxy)
            self._capabilities = reader.readString(self.url)
        else:
            reader = SOSCapabilitiesReader(self.version, to=self.timeout,
                                           px=self.ignore_proxy)
            if xml:
                #read from stored xml
                self._capabilities = reader.readString(xml)
            else:
                #read from non-password protected server
                self._capabilities = reader.read(self.url, timeout=self.timeout)

        #build metadata objects
        self._buildMetadata()

    def _getcapproperty(self):
        if not self._capabilities:
            reader = SOSCapabilitiesReader(
                self.version, url=self.url, un=self.username, pw=self.password)
            self._capabilities = ServiceMetadata(reader.read(self.url))
        return self._capabilities

    capabilities = property(_getcapproperty, None)

    def _buildMetadata(self):
        ''' set up capabilities metadata objects '''

        # ServiceIdentification
        val = self._capabilities.find('{http://www.opengis.net/ows/1.1}ServiceIdentification')
        self.identification = ows.ServiceIdentification(val)

        # ServiceProvider
        val = self._capabilities.find('{http://www.opengis.net/ows/1.1}ServiceProvider')
        self.provider = ows.ServiceProvider(val)

        # ServiceOperations metadata
        self.operations = []
        for elem in self._capabilities.findall('{http://www.opengis.net/ows/1.1}OperationsMetadata/{http://www.opengis.net/ows/1.1}Operation'):
            self.operations.append(ows.OperationsMetadata(elem))

        # FilterCapabilities
        val = self._capabilities.find('{http://www.opengis.net/sos/1.0}Filter_Capabilities')
        if val is not None:
            self.filters = filter.FilterCapabilities(val)
        else:
            val = self._capabilities.find('{http://www.opengis.net/sos/1.0}FilterCapabilities')
            if val:
                self.filters = filter.FilterCapabilities(val)
            else:
                self.filters = None

        #serviceContents metadata: our assumption is that services use a top-level
        #layer as a metadata organizer, nothing more.

        #caps = self._capabilities.find('Capability')
        #for elem in caps.findall('Layer'):
        #    cm=ContentMetadata(elem)
        #    self.contents[cm.id]=cm
        #    for subelem in elem.findall('Layer'):
        #        subcm=ContentMetadata(subelem, cm)
        #        self.contents[subcm.id]=subcm

        # Contents
        self.contents = []
        elem_set = self._capabilities.find('{http://www.opengis.net/sos/1.0}Contents/{http://www.opengis.net/sos/1.0}ObservationOfferingList')
        if elem_set is not None:
            for elem in elem_set:
                if elem is not None:
                    #print  "owslib.sos.py:161", type(elem), "\n", elem
                    meta = ContentsMetadata(elem)
                    # attempt to find defaults at ObservationOfferingList level
                    if not meta.response_format:
                        meta.response_format = self.get_sos_element_values(
                            elem_set, 'responseFormat')
                    if not meta.result_model:
                        meta.result_model = self.get_sos_element_values(
                            elem_set, 'resultModel')
                    if not meta.response_mode:
                        meta.response_mode = self.get_sos_element_values(
                            elem_set, 'responseMode')
                    self.contents.append(meta)
        """
        print "**owslib.sos.py:175 elem_set**", elem_set
        print "\n**contents**\n", self.contents
        for c in self.contents:
            items = c.__dict__
            print "\n**content item**\n"
            for i in items:
                print i, items[i]
        """

        #exceptions
        self.exceptions = ['text/xml']

    def get_sos_element_values(self, elem, ele_name):
        result = []
        vals = elem.findall(util.nspath(ele_name, SOS_NAMESPACE))
        if vals is not None:
            for v in vals:
                result.append(util.testXMLValue(v))
        return result

    def items(self):
        '''supports dict-like items() access'''
        items = []
        for item in self.contents:
            items.append((item, self.contents[item]))
        return items

    def getcapabilities(self):
        """Request and return capabilities document from the SOS as a
        file-like object.
        NOTE: this is effectively redundant now"""

        reader = SOSCapabilitiesReader(
            self.version, url=self.url, un=self.username, pw=self.password,
            to=self.timeout)
        u = self._open(reader.capabilities_url(self.url), timeout=self.timeout)
       # check for service exceptions, and return
        if u.info().gettype() == 'application/vnd.ogc.se_xml':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            raise ServiceException(
                str(se_tree.find('ExceptionReport').text).strip())
        return u

    def getmap(self, layers=None, styles=None, srs=None, bbox=None,
               format=None, size=None, time=None, transparent=False,
               bgcolor='#FFFFFF',
               exceptions='application/vnd.ogc.se_xml',
               method='Get'):
        """Request and return an image from the SOS as a file-like object.

        Parameters
        ----------
        layers : list
            List of content layer names.
        styles : list
            Optional list of named styles, must be the same length as the
            layers list.
        srs : string
            A spatial reference system identifier.
        bbox : tuple
            (left, bottom, right, top) in srs units.
        format : string
            Output image format such as 'image/jpeg'.
        size : tuple
            (width, height) in pixels.
        transparent : bool
            Optional. Transparent background if True.
        bgcolor : string
            Optional. Image background color.
        method : string
            Optional. HTTP DCP method name: Get or Post.

        Example
        -------
            >>> img = wms.getmap(layers=['global_mosaic'],
            ...                  styles=['visual'],
            ...                  srs='EPSG:4326',
            ...                  bbox=(-112,36,-106,41),
            ...                  format='image/jpeg',
            ...                  size=(300,250),
            ...                  transparent=True,
            ...                  )
            >>> out = open('example.jpg', 'wb')
            >>> out.write(img.read())
            >>> out.close()

        """
        base_url = self.getOperationByName('GetMap').methods[method]['url']
        request = {'version': self.version, 'request': 'GetMap'}

        # check layers and styles
        assert len(layers) > 0
        request['layers'] = ','.join(layers)
        if styles:
            assert len(styles) == len(layers)
            request['styles'] = ','.join(styles)
        else:
            request['styles'] = ''

        # size
        request['width'] = str(size[0])
        request['height'] = str(size[1])

        request['srs'] = str(srs)
        request['bbox'] = ','.join([str(x) for x in bbox])
        request['format'] = str(format)
        request['transparent'] = str(transparent).upper()
        request['bgcolor'] = '0x' + bgcolor[1:7]
        request['exceptions'] = str(exceptions)

        if time is not None:
            request['time'] = str(time)

        data = urlencode(request)
        if method == 'Post':
            u = self._open(base_url, data=data)
        else:
            u = self._open(base_url + data)

        # check for service exceptions, and return
        if u.info()['Content-Type'] == 'application/vnd.ogc.se_xml':
            se_xml = u.read()
            se_tree = etree.fromstring(se_xml)
            raise ServiceException(
                str(se_tree.find('ExceptionReport').text).strip())
        return u

    def getfeatureinfo(self):
        raise NotImplementedError

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError("No operation named %s" % name)

    def getContentByName(self, name):
        """Return a named content item."""
        for item in self.contents:
            if item.name == name:
                return item
        raise KeyError("No content named %s" % name)

    def getOperationByName(self, name):
        """Return a named content item."""
        for item in self.operations:
            if item.name == name:
                return item
        raise KeyError("No operation named %s" % name)


# NB NOT "content" singular!!!
class ContentsMetadata:
    """Initialize an SOS Contents metadata construct"""

    def __init__(self, elem, namespace=ows.DEFAULT_OWS_NAMESPACE):
        self.elem = elem
        # id & name $& description
        self.id = elem.attrib[util.nspath('id', GML_NAMESPACE)]  # '{http://www.opengis.net/gml}id']
        val = elem.find(util.nspath('name', GML_NAMESPACE))  # gml
        self.name = util.testXMLValue(val)
        val = elem.find(util.nspath('description', GML_NAMESPACE))  # gml
        self.description = util.testXMLValue(val)
        # time
        self.time = None
        time_ = elem.find(util.nspath('time', SOS_NAMESPACE))  # sos
        if time_ is not None:
            time_period = time_.find(util.nspath('TimePeriod', GML_NAMESPACE))
            if time_period:
                val = time_period.find(util.nspath('beginPosition', GML_NAMESPACE))
                begin = util.testXMLValue(val)
                val = time_period.find(util.nspath('endPosition', GML_NAMESPACE))
                end = util.testXMLValue(val)
                self.time = (begin, end)
        # bbox
        self.bounding_box = None
        bound = elem.find(util.nspath('boundedBy', GML_NAMESPACE))
        if bound is not None:
            env = bound.find(util.nspath('Envelope', GML_NAMESPACE))
            if env is not None:
                try:  # sometimes the SRS attribute is (wrongly) not provided
                    srs = env.attrib['srsName']
                except KeyError:
                    srs = None
                val = env.find(util.nspath('lowerCorner', GML_NAMESPACE))
                lower = util.testXMLValue(val)
                val = env.find(util.nspath('upperCorner', GML_NAMESPACE))
                upper = util.testXMLValue(val)
                if upper is not None and lower is not None:
                    self.bounding_box = (
                        float(lower.split(' ')[0]),  # minx
                        float(lower.split(' ')[1]),  # miny
                        float(upper.split(' ')[0]),  # maxx
                        float(upper.split(' ')[1]),  # maxy
                        srs,)
        # other metadata...
        self.response_format = self.get_sos_element_values('responseFormat')
        self.result_model = self.get_sos_element_values('resultModel')
        self.response_mode = self.get_sos_element_values('responseMode')

        self.procedure = []
        procs = elem.findall(util.nspath('procedure', SOS_NAMESPACE))
        if procs is not None:
            for proc in procs:
                self.procedure.append(proc.attrib[util.nspath('href', XLINK_NAMESPACE)])

        self.observed_property = []
        ops = elem.findall(util.nspath('observedProperty', SOS_NAMESPACE))
        if ops is not None:
            for op in ops:
                self.observed_property.append(op.attrib[util.nspath('href', XLINK_NAMESPACE)])

        self.feature_of_interest = []
        fois = elem.findall(util.nspath('featureOfInterest', SOS_NAMESPACE))
        if fois is not None:
            for foi in fois:
                self.feature_of_interest.append(foi.attrib[util.nspath('href', XLINK_NAMESPACE)])

    # default namespace for elem_find is OWS common
    OWS_NAMESPACE = 'http://www.opengis.net/ows/1.1'

    def elem_find(elem, nss=(OWS_NAMESPACE, '')):
        """Wraps etree.find to search multiple namespaces

        Parameters
        ----------
        - elem: name of element
        - nss:  a tuple of possible XML namespace URIs.

        """
        if nss is None or name is None:
            return None

        for namespace in nss:
            if namespace:
                path = '{%s}%s' % (namespace, elem)
            else:
                path = elem
            val = elem.find(path)
            if val:
                return val
        return none

    def get_sos_element_values(self, ele_name):
        result = []
        vals = self.elem.findall(util.nspath(ele_name, SOS_NAMESPACE))
        if vals is not None:
            for v in vals:
                result.append(util.testXMLValue(v))
        return result


class ContentMetadata:
    """
    Abstraction for SOS layer metadata.

    Implements IContentMetadata.
    """

    def __init__(self, elem, parent=None):
        self.parent = parent
        if elem.tag != 'Layer':
            raise ValueError('%s should be a Layer' % (elem,))
        for key in ('Name', 'Title', 'Attribution'):
            val = elem.find(key)
            if val is not None:
                setattr(self, key.lower(), val.text.strip())
            else:
                setattr(self, key.lower(), None)
                self.id = self.name  # conform to new interface
        # bboxes
        b = elem.find('BoundingBox')
        self.boundingBox = None
        if b is not None:
            try:  # sometimes the SRS attribute is (wrongly) not provided
                srs = b.attrib['SRS']
            except KeyError:
                srs = None
            self.boundingBox = (
                    float(b.attrib['minx']),
                    float(b.attrib['miny']),
                    float(b.attrib['maxx']),
                    float(b.attrib['maxy']),
                    srs,)
        elif self.parent:
            if hasattr(self.parent, 'boundingBox'):
                self.boundingBox = self.parent.boundingBox

        b = elem.find('LatLonBoundingBox')
        if b is not None:
            self.boundingBoxWGS84 = (
                float(b.attrib['minx']),
                float(b.attrib['miny']),
                float(b.attrib['maxx']),
                float(b.attrib['maxy']),)
        elif self.parent:
            self.boundingBoxWGS84 = self.parent.boundingBoxWGS84
        else:
            self.boundingBoxWGS84 = None
        # crs options
        self.crsOptions = []
        if elem.find('SRS') is not None:
            ## some servers found in the wild use a single SRS
            ## tag containing a whitespace separated list of SRIDs
            ## instead of several SRS tags. hence the inner loop
            for srslist in map(lambda x: x.text, elem.findall('SRS')):
                if srslist:
                    for srs in srslist.split():
                        self.crsOptions.append(srs)
        elif self.parent:
            self.crsOptions = self.parent.crsOptions
        else:
            # raise ValueError('%s no SRS available!?' % (elem,))
            # Comment by D Lowe.
            #   Do not raise ValueError as it is possible that a layer is
            #   purely a parent layer and does not have SRS specified.
            #   Instead set crsOptions to None
            self.crsOptions = None
        # styles
        self.styles = {}
        for s in elem.findall('Style'):
            name = s.find('Name')
            title = s.find('Title')
            if name is None or title is None:
                raise ValueError('%s missing name or title' % (s,))
            style = {'title': title.text}
            # legend url
            legend = s.find('LegendURL/OnlineResource')
            if legend is not None:
                style['legend'] = legend.attrib['{http://www.w3.org/1999/xlink}href']
            self.styles[name.text] = style

        # keywords
        self.keywords = [f.text for f in elem.findall('KeywordList/Keyword')]

        # timepositions - times for which data is available.
        self.timepositions = None
        for extent in elem.findall('Extent'):
            if extent.attrib.get("name").lower() == 'time':
                self.timepositions = extent.text.split(',')
                break

        self.layers = []
        for child in elem.findall('Layer'):
            self.layers.append(ContentMetadata(child, self))

    def __str__(self):
        return 'Layer Name: %s Title: %s' % (self.name, self.title)


class SOSCapabilitiesReader:
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='1.0.0', url=None, un=None, pw=None, to=None,
                 px=False):
        """Initialize

        Parameters:
         *  url:  URL
         *  un: username
         *  pw: password
         *  to: timeout (j seconds)
         *  px: ignore_proxy
        """
        self.version = version
        self._infoset = None
        self.url = url
        self.username = un
        self.password = pw
        self.timeout = to
        self.ignore_proxy = px

        self._open = urlopen
        if self.ignore_proxy:
            #print "sos:552 - ignoring proxy..."
            proxy_support = ProxyHandler({})  # disables proxy
            opener = build_opener(proxy_support)
            install_opener(opener)
            self._open = opener.open

        if self.username and self.password:
            # Provide login information in order to use the SOS server
            # Create an OpenerDirector with support for Basic HTTP
            # Authentication...
            passman = HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, self.url, self.username, self.password)
            auth_handler = HTTPBasicAuthHandler(passman)
            opener = build_opener(auth_handler)
            self._open = opener.open

    def capabilities_url(self, service_url):
        """Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if 'service' not in params:
            qs.append(('service', 'SOS'))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, service_url, timeout):
        """Get and parse a SOS capabilities document, returning an
        elementtree instance

        service_url is the base url, to which is appended the service,
        version, and request parameters
        """
        request = self.capabilities_url(service_url)
        u = self._open(request, timeout=self.timeout)
        return etree.fromstring(u.read())

    def readString(self, st):
        """Parse a SOS capabilities document, returning an elementtree instance

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError("String must be of type string, not %s" % type(st))
        return etree.fromstring(st)


class SOSError(Exception):
    """Base class for SOS module errors
    """

    def __init__(self, version, language, code, locator, text):
        """Initialize an SOS Error"""
        self = ows.OWSExceptionReport(
            "1.0.0", "en-US", "InvalidParameterValue", "request", "foo")

    def toxml(self):
        """Serialize into SOS Exception Report XML
        """
        return self.toxml()

###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
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
"""This module provides a base OGC (Open Geospatial Consortium) service class.
"""

from PyQt4 import QtCore, QtGui
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from packages.eo4vistrails.geoinf.datamodels.Raster import RasterModel
from OgcConfigurationWidget import OgcConfigurationWidget
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
import init


class OGC(NotCacheable):
    """
    Provide basic connection service to an OGC (Open Geospatial Consortium)
    web service.
    Configuration allows the base URL for the service to be set and called.
    Choosing the appropriate combination of specific service type and other
    parameters, will cause the input port to be set with a specific POST call,
    once the configuration interface is closed.
    Running the module will set the (string) values of the URL and data (if any)
    for access via the output ports.

    """
    def __init__(self):
        pass

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))

    def compute(self):
        """Execute the module to create the output"""
        try:
            post_request = self.getInputFromPort(init.OGC_POST_REQUEST_PORT)
            #print "OgcService:62 POST Request from port :::", init.OGC_POST_REQUEST_PORT, type(request), request, len(request)
        except:
            post_request = None

        try:
            get_request = self.getInputFromPort(init.OGC_GET_REQUEST_PORT)
            #print "OgcService:68 GET Request from port :::", init.OGC_GET_REQUEST_PORT, type(request), request, len(request)
        except:
            get_request = None

        try:
            url = self.getInputFromPort(init.URL_PORT)
            #print "OgcService:73 URL from port :::", init.OGC_URL_PORT, type(url), url, len(url)
        except:
            url = None

        if get_request:
            print "OgcService:79 URL", get_request
            self.setResult(init.URL_PORT, get_request)
            self.setResult(init.DATA_PORT, '')

        if post_request and url:
            self.setResult(init.URL_PORT, url)
            self.setResult(init.DATA_PORT, post_request)

'''
    # NOW MOVED TO /util/WebRequest.py

    def compute(self):
        """Execute the module to create the output"""
        try:
            post_request = self.getInputFromPort(init.OGC_POST_REQUEST_PORT)
            #print "Request from port :::", init.OGC_POST_REQUEST_PORT, type(request), request, len(request)
        except:
            post_request = None

        try:
            get_request = self.getInputFromPort(init.OGC_GET_REQUEST_PORT)
            #print "Request from port :::", init.OGC_GET_REQUEST_PORT, type(request), request, len(request)
        except:
            get_request = None

        try:
            url = self.getInputFromPort(init.OGC_URL_PORT)
            #print "URL from port :::", init.OGC_URL_PORT, type(url), url, len(url)
        except:
            url = None

        try:
            out = None
            if post_request:
                out = self.runRequest(url, post_request, 'POST')
            if get_request:
                out = self.runRequest(url, get_request,'GET')
            self.setResult(init.OGC_RESULT_PORT, out)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))

    def runRequest(self, url, request, type='GET'):
        """Execute an HTTP POST request for a given URL"""
        import urllib
        import urllib2
        import os
        from urllib2 import URLError
        result = None
        print "OgcService:95\n", url, request, type
        if request:
            if type == 'GET':
                print "OgcService:98\n", request
                req = urllib2.Request(request)
            elif type == 'POST':
                print "OgcService:99\n", url, request, headers
                user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
                headers = {'User-Agent': user_agent}
                req = urllib2.Request(url, request, headers)
            else:
                raise ModuleError(
                    self,
                    'Unknown OgcService request type' + ': %s' % str(type)
                )
            #assuming this works inside a proxy ... otherwise:
            #os.environ["http_proxy"] = "http://myproxy.com:3128"
            try:
                urllib2.urlopen(req)
                response = urllib2.urlopen(req)
                result = response.read()
            except URLError, e:
                if hasattr(e, 'reason'):
                    self.raiseError('Failed to reach the server. Reason', e.reason)
                elif hasattr(e, 'code'):
                    self.raiseError('The server couldn\'t fulfill the request. Error code', e.code)
            except Exception, e:
                self.raiseError('Exception', e)
        else:
            pass  # ignore and do nothing ...
        return result
'''

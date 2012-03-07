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
"""This module forms part of the eo4vistrails capabilities - it is used to
handle web request (e.g. for WFS, WCS or SOS) processing inside vistrails.
"""
# library
import os
import socket
import urllib
import urllib2
# third-party
# vistrails
from core.modules.vistrails_module import ModuleError
# eo4vistrails
# local
from DataRequest import DataRequest


class WebRequest(DataRequest):
    """This module will process a web-based request.

    * With only the 'urls' port set, the module will execute a GET request.
    * With the 'data' port set as well, the module will execute a POST request.
    """

    def __init__(self, url=None, data=None, runTheRequest=False, timeout=180):
        DataRequest.__init__(self)
        self.url = url
        self.data = data
        self.runTheRequest = runTheRequest
        self.timeout = timeout
        socket.setdefaulttimeout(timeout)  # timeout for ALL urllib2 requests

    def get_uri(self):
        """Overwrite method in DataRequest"""
        return self.url

    def get_layername(self):
        """Overwrite method in DataRequest"""
        if not self._layername:
            import random
            random.seed()
            self._layername = 'web_layer' + str(random.randint(0, 10000))
        return self._layername

    def compute(self):
        """Overwrite method in DataRequest to execute the module
        and create the output"""
        # access data from DataRequest input ports
        DataRequest.compute(self)
        # separate URL
        try:
            self.url = self.getInputFromPort('urls')
        except:
            pass
        # separate data
        try:
            self.data = self.getInputFromPort('data')
        except:
            pass
        # request (combined data and URL)
        try:
            request = self.getInputFromPort('request')
            if request:
                self.url = request.url
                self.data = request.data
            #print "WebRequest:93\n url:%s\n data: %s" % (self.url,self.data)
        except:
            pass
        # execute request IF required
        try:
            self.runTheRequest = self.getInputFromPort('runRequest')
        except:
            self.runTheRequest = False
        try:
            if self.runTheRequest:
                out = self.runRequest()
                self.setResult('out', out)
            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))

    def runRequest(self):
        """Execute an HTTP POST request for a given URL and data"""
        result = None
        #print "\nWebRequest:106\n", self.url, self.requestType(), self.data
        if self.url:
            request_type = self.requestType()
            if request_type == 'GET':
                req = urllib2.Request(self.url)
            elif request_type == 'POST':
                user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
                headers = {'User-Agent': user_agent,
                           'Content-Type': 'application/xml'}
                req = urllib2.Request(self.url, self.data, headers)
            else:
                raise ModuleError(
                    self,
                    'Unknown web request type: %s (should be GET or POST)' %\
                        str(request_type))

            response = None
            try:
                response = urllib2.urlopen(req)
            except:
                try:
                    #print "WebRequest:130 - ignoring proxy..."
                    proxy_support = urllib2.ProxyHandler({})  # disables proxy
                    opener = urllib2.build_opener(proxy_support)
                    urllib2.install_opener(opener)
                    response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                    if hasattr(e, 'reason'):
                        self.raiseError(
                            'Failed to reach the server. Reason', e.reason)
                    elif hasattr(e, 'code'):
                        self.raiseError(
                            'The server couldn\'t fulfill the request. Error code',
                            e.code)
                except Exception, e:
                    self.raiseError('Exception', e)
            if response:
                result = response.read()
        else:
            pass  # ignore and do nothing ...
        return result

    def requestType(self):
        """Determine the request type - return GET or POST"""
        request_type = 'GET'
        if self.data:
            request_type = 'POST'
        return request_type

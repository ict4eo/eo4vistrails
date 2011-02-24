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
"""
Created on Wed Feb 23 14:08:10 2011

@author: dhohls

Module forms part of the eo4vistrails capabilities, used to handle web request
(e.g. for WFS, WCS or SOS) processing inside vistrails.

"""
#History
#Derek Hohls, 25 Feb 2011, Version 0.1.3

from core.modules.vistrails_module import Module, NotCacheable

class WebRequest(NotCacheable, Module):
    """This module will process a web-based request.

    With only the 'url' port set, the module will execute a GET request.

    With the 'data' port set as well, the module will execute a POST request.
    """

    def __init__(self):
        Module.__init__(self)
        self.url = None
        self.data = None
        self.runTheRequest = False

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))

    def compute(self):
        """Execute the module to create the output"""
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
            self.url = request.url
            self.data = request.data
            #print "\nWebRequest:78\n url:%s\n data: %s" % (self.url, self.data)
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
        import urllib
        import urllib2
        import os
        from urllib2 import URLError
        result = None
        if self.url:
            request_type = self.requestType()
            if request_type == 'GET':
                req = urllib2.Request(self.url)
            elif request_type == 'POST':
                user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
                headers = {'User-Agent': user_agent}
                req = urllib2.Request(self.url, self.data, headers)
            else:
                raise ModuleError(
                    self,
                    'Unknown web request type: %s (should be GET or POST)' % str(request_type)
                )
            #assumes this works inside a proxy ... otherwise, try:
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

    def requestType(self):
        request_type = 'GET'
        if self.data:
            request_type = 'POST'
        return request_type

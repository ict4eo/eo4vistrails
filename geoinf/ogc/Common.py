############################################################################
###
### Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
###
### eo4vistrails extends VisTrails, providing GIS/Earth Observation
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
"""This module provides a small api for fetching the service and dealing with
OGC (Open Geospatial Consortium) Web Service Metadata which is common to the
various services (via owslib).

Requirements:
    owslib 0.3.4

NOTE:
    As at 2010-11-09, you will need to patch version 0.3.4b for owslib sos.py:
        `self.filters=filter.Filter_Capabilities(val)`
    should be:
        `self.filters=filter.FilterCapabilities(val)`

"""

import xml.etree.cElementTree as etree
import traceback
from urllib2 import URLError
try:
    from owslib import wfs as wfs
    from owslib import wcs as wcs
    from owslib import sos as sos
except:
    import owslib.wfs as wfs
    import owslib.sos as sos
    import owslib.wcs as wcs


class OgcService():
    """TODO:  - add docstring / summary description

    Parameters
    ----------
        service_url: string
            URL for OGC service
        service_type: string
            'wfs', 'sos', 'wcs'
        service_version: string
            currently only version 1.0 for OGC services (but see Notes)
        timeout: integer
            in seconds - some lines/servers experiences slow speeds and/or the
            XML being returned is in a large document, taking time to construct
            (see inline comments about usage in different services)
        capabilities:
            a full capabilities document - if provided, no call will be made
            by owslib to the service_url, and this will be used instead

    Notes
    -----
      Namespace issues pervade wfs in owslib e.g.
      * cannot handle when geoserver shortcuts a namespace with an abbreviation
      * wfs will never load a 1.1.0 instance, but it should be loaded as wfs200
    """

    def __init__(self, service_url, service_type, service_version, timeout=180,
                 capabilities=None):
        self.INVALID_OGC_TYPE_MESSAGE = \
            "Please provide an OGC Service Type: 'wfs', 'sos', or 'wcs'"
        #print "common:83:\nservice_url, service_type, service_version\n", \
            #service_url, '#', service_type, '#', service_version
        self.timeout = timeout  # seconds
        self.capabilities = capabilities  # full capabilities document
        self.service = None
        if service_url:
            service_url = str(service_url)
            # check for service and request key-value pairs;
            # if not there, add (some services don't have a capabilities reflector),
            STRICT_OGC_CAPABILITIES = \
                "Service=%s&Request=GetCapabilities" % service_type
            service_url_check = service_url.split("?")
            if len(service_url_check) == 1:
                service_url = service_url + "?" + STRICT_OGC_CAPABILITIES
            else:
                # various of the capabilities may be present - remove and replace
                service_url = service_url_check[0] + "?" + STRICT_OGC_CAPABILITIES
        # set common attributes
        self.service_id_key_set = [
            {'service_type':'Service'},
            {'service_version':'Version'},
            {'service_title':'Title'},
            {'service_abstract':'Abstract'},
            {'service_keywords':'Keywords'},
            {'service_fees':'Fees'},
            {'service_accessconstraints':'Access Constraints'},
        ]
        self.provider_key_set = [
            {'provider_name':'Provider Name'},
            {'provider_url':'Provider URL'},
            {'provider_contact_name':'Contact Name'},
            {'provider_contact_position':'Contact Position'},
            {'provider_contact_role':'Contact Role'},
            {'provider_contact_organization':'Contact Organization'},
            {'provider_contact_address':'Contact Address'},
            {'provider_contact_city':'Contact City'},
            {'provider_contact_region':'Contact Region'},
            {'provider_contact_postcode':'Contact Postal Code'},
            {'provider_contact_country':'Contact Country'},
            {'provider_contact_phone':'Contact Phone'},
            {'provider_contact_fax':'Contact Fax'},
            {'provider_contact_site':'Contact Site'},
            {'provider_contact_email':'Contact Email'},
            {'provider_contact_hours':'Contact Hours'},
            {'provider_contact_instructions':'Contact Instructions'},
        ]
        # set service-specific attributes
        self.service_valid = False
        self.service_valid_error = ''
        if service_url:
            if service_type != "":
                try:
                    if service_type.lower() == "sos":
                        # NB as of 2011-09-27, only owslib sos module
                        # has been upgraded to handle timeout
                        try:
                            self.service = sos.SensorObservationService(
                                service_url, service_version,
                                timeout=self.timeout,
                                xml=self.capabilities)
                        except URLError:
                            self.service = sos.SensorObservationService(
                                service_url, service_version,
                                timeout=self.timeout, ignore_proxy=True,
                                xml=self.capabilities)
                        self.service_valid = True
                    elif service_type.lower() == "wfs":
                        self.service = wfs.WebFeatureService(
                            service_url, service_version,
                            xml=self.capabilities)
                        self.service_valid = True
                    elif service_type.lower() == "wcs":
                        self.service = wcs.WebCoverageService(
                            service_url, service_version,
                            xml=self.capabilities)
                        self.service_valid = True
                    else:
                        self.service_valid = False
                        raise ValueError(self.INVALID_OGC_TYPE_MESSAGE)
                except Exception, e:
                    traceback.print_exc()  # e.g. HTTP Error 404: Not Found
                    self.service_valid = False
                    self.service_valid_error = str(e)
            else:
                raise ValueError(self.INVALID_OGC_TYPE_MESSAGE)
        self.service_url = service_url
        self.ini_service_type = service_type.lower()
        self.ini_service_version = service_version

        if self.service_valid:
            # NOTE: '_capabilities' may change in future versions of owslib!  See:
            #   http://www.mail-archive.com/community@lists.gispython.org/msg00840.html
            #   http://lists.gispython.org/pipermail/community/2008-January/001502.html
            elem = self.service._capabilities  # etree element
            # extract XML containing "raw" GetCapabilities data
            self.capabilities = etree.tostring(elem, encoding='utf-8')
            #print "Common:180", self.capabilities
            # store metadata
            # this looks bizzare, but it is true...
            if service_type.lower() == "wfs" and service_version == "1.0.0":
                self.setServiceIdentification(
                    self.service.__dict__['provider'].__dict__)
                self.setProviderIdentification(
                    self.service.__dict__['provider'].__dict__)
            elif service_type.lower() == "wcs" or service_type.lower() == "sos":
                self.setServiceIdentification(
                    self.service.__dict__['identification'].__dict__)
                self.setProviderIdentification(
                    self.service.__dict__['provider'].__dict__)
                self.setOperations(
                    self.service.__dict__['operations'])
            else:
                raise ValueError(self.INVALID_OGC_TYPE_MESSAGE)

    def setOperations(self, service_list):
        """service identification metadata is structured differently
        for the different services - parse appropriately"""

        self.service_operations = []
        if self.ini_service_type == "sos":
            for service in service_list:
                if 'name' in service.__dict__:
                    self.service_operations.append(service.__dict__['name'])
        else:
            raise NotImplementedError(
                "OGC Service version %s not supported for Operations." % \
                self.ini_service_version)

    def setServiceIdentification(self, service_dict):
        """service identification metadata is structured differently
        for the different services - parse appropriately"""

        if self.ini_service_type == "sos":
            if 'service' in service_dict:
                self.service_type = service_dict['service']  # we know this, but rebuild anyway
            if 'version' in service_dict:
                self.service_version = service_dict['version']  # we know this, but rebuild anyway
            if 'title' in service_dict:
                self.service_title = service_dict['title']
            if 'abstract' in service_dict:
                self.service_abstract = service_dict['abstract']
            if 'keywords' in service_dict:
                self.service_keywords = service_dict['keywords']
            if 'fees' in service_dict:
                self.service_fees = service_dict['fees']
            if 'accessconstraints' in service_dict:
                self.service_accessconstraints = service_dict['accessconstraints']

        elif self.ini_service_type == "wfs":
            if self.ini_service_version == '1.0.0':
                # got to dive into the elements of _root key of service_dict
                # (in this case the provider_dict)to get anything useful.
                for elem in service_dict['_root'].__dict__['_children']:
                    if 'tag' in elem.__dict__ and 'text' in elem.__dict__:
                        # we have a kvp, so process
                        tg = elem.__dict__['tag']
                        tx = elem.__dict__['text']
                        try:  # check for {http://www.opengis.net/wfs} prefix
                            tg = tg.split('}')[1].lower()
                        except:
                            pass
                        if tg == "name":
                            self.service_type = tx
                        if tg == "title":
                            self.service_title = tx
                        if tg == "abstract":
                            self.service_abstract = tx
                        if tg == "keywords":
                            self.service_keywords = tx
                        if tg == "fees":
                            self.service_fees = tx
                        if tg == "accessconstraints":
                            self.service_accessconstraints = tx
                self.service_version = '1.0.0'  # will not find this dynamically
            elif self.ini_service_version == '1.1.0':
                pass
            else:
                raise NotImplementedError(
                    "OGC Service version %s not supported for ServiceIdentification." % \
                    self.ini_service_version)

        elif self.ini_service_type == "wcs":
            if 'service' in service_dict:
                self.service_type = service_dict['service']
            if 'version' in service_dict:
                self.service_version = service_dict['version']
            if 'title' in service_dict:
                self.service_title = service_dict['title']
            if 'abstract' in service_dict:
                self.service_abstract = service_dict['abstract']
            if 'keywords' in service_dict:
                self.service_keywords = service_dict['keywords']
            if 'fees' in service_dict:
                self.service_fees = service_dict['fees']
            if 'accessconstraints' in service_dict:
                self.service_accessconstraints = service_dict['accessconstraints']

        else:
            raise ValueError(self.INVALID_OGC_TYPE_MESSAGE)

    def setProviderIdentification(self, provider_dict):
        """provider metadata is structured differently
        for the different services - parse appropriately"""
        if self.ini_service_type == "sos":
            if 'name' in provider_dict:
                self.provider_name = provider_dict['name']
            if 'url' in provider_dict:
                self.provider_url = provider_dict['url']
            if 'contact' in provider_dict:
                if 'name' in provider_dict['contact'].__dict__:
                    self.provider_contact_name = provider_dict['contact'].__dict__['name']
                if 'position' in provider_dict['contact'].__dict__:
                    self.provider_contact_position = provider_dict['contact'].__dict__['position']
                if 'role' in provider_dict['contact'].__dict__:
                    self.provider_contact_role = provider_dict['contact'].__dict__['role']
                if 'organization' in provider_dict['contact'].__dict__:
                    self.provider_contact_organization = provider_dict['contact'].__dict__['organization']
                if 'address' in provider_dict['contact'].__dict__:
                    self.provider_contact_address = provider_dict['contact'].__dict__['address']
                if 'city' in provider_dict['contact'].__dict__:
                    self.provider_contact_city = provider_dict['contact'].__dict__['city']
                if 'region' in provider_dict['contact'].__dict__:
                    self.provider_contact_region = provider_dict['contact'].__dict__['region']
                if 'postcode' in provider_dict['contact'].__dict__:
                    self.provider_contact_postcode = provider_dict['contact'].__dict__['postcode']
                if 'country' in provider_dict['contact'].__dict__:
                    self.provider_contact_country = provider_dict['contact'].__dict__['country']
                if 'phone' in provider_dict['contact'].__dict__:
                    self.provider_contact_phone = provider_dict['contact'].__dict__['phone']
                if 'fax' in provider_dict['contact'].__dict__:
                    self.provider_contact_fax = provider_dict['contact'].__dict__['fax']
                if 'site' in provider_dict['contact'].__dict__:
                    self.provider_contact_site = provider_dict['contact'].__dict__['site']
                if 'email' in provider_dict['contact'].__dict__:
                    self.provider_contact_email = provider_dict['contact'].__dict__['email']
                if 'hours' in provider_dict['contact'].__dict__:
                    self.provider_contact_hours = provider_dict['contact'].__dict__['hours']
                if 'instructions' in provider_dict['contact'].__dict__:
                    self.provider_contact_instructions = provider_dict['contact'].__dict__['instructions']

        elif self.ini_service_type == "wfs":
            """There is NO provider data available for wfs service"""
            pass

        elif self.ini_service_type == "wcs":
            """Provider data  for wcs service - see self.provider_key_set in _init_"""
            if 'name' in provider_dict:
                self.provider_name = provider_dict['name']
            if 'url' in provider_dict:
                self.provider_url = provider_dict['url']
            if 'contact' in provider_dict:
                if 'name' in provider_dict['contact'].__dict__:
                    self.provider_contact_name = provider_dict['contact'].__dict__['name']
                if 'position' in provider_dict['contact'].__dict__:
                    self.provider_contact_position = provider_dict['contact'].__dict__['position']
                if 'role' in provider_dict['contact'].__dict__:
                    self.provider_contact_role = provider_dict['contact'].__dict__['role']
                if 'organization' in provider_dict['contact'].__dict__:
                    self.provider_contact_organization = provider_dict['contact'].__dict__['organization']
                if 'address' in provider_dict['contact'].__dict__:
                    self.provider_contact_address = provider_dict['contact'].__dict__['address']
                if 'city' in provider_dict['contact'].__dict__:
                    self.provider_contact_city = provider_dict['contact'].__dict__['city']
                if 'region' in provider_dict['contact'].__dict__:
                    self.provider_contact_region = provider_dict['contact'].__dict__['region']
                if 'postcode' in provider_dict['contact'].__dict__:
                    self.provider_contact_postcode = provider_dict['contact'].__dict__['postcode']
                if 'country' in provider_dict['contact'].__dict__:
                    self.provider_contact_country = provider_dict['contact'].__dict__['country']
                if 'phone' in provider_dict['contact'].__dict__:
                    self.provider_contact_phone = provider_dict['contact'].__dict__['phone']
                if 'fax' in provider_dict['contact'].__dict__:
                    self.provider_contact_fax = provider_dict['contact'].__dict__['fax']
                if 'site' in provider_dict['contact'].__dict__:
                    self.provider_contact_site = provider_dict['contact'].__dict__['site']
                if 'email' in provider_dict['contact'].__dict__:
                    self.provider_contact_email = provider_dict['contact'].__dict__['email']
                if 'hours' in provider_dict['contact'].__dict__:
                    self.provider_contact_hours = provider_dict['contact'].__dict__['hours']
                if 'instructions' in provider_dict['contact'].__dict__:
                    self.provider_contact_instructions = provider_dict['contact'].__dict__['instructions']

        else:
            raise ValueError(self.INVALID_OGC_TYPE_MESSAGE)

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
OGC Web Service Metadata common to the various services (via owslib).

Requirements:
    owslib 0.3.2 or higher

NOTE: As at 2010-11-09, you will need to patch version 0.3.4b for owslib sos.py:
        self.filters=filter.Filter_Capabilities(val)
    should be:
        self.filters=filter.FilterCapabilities(val)
"""

try:
        from owslib import wfs as wfs


        from owslib import wcs as wcs


        from owslib import sos as sos

except:


        import owslib.wfs as wfs

        import owslib.sos as sos

        import owslib.wcs as wcs




class OgcService():
    #########
    ## namespace issues pervade wfs in owslib e.g.
    ## cannot handle when geoserver shorcuts a namespace with an abbreviation
    ## also wfs will never load a 1.1.0 instance, but it should be loaded as wfs200
    #########

    INVALID_OGC_TYPE_MESSAGE = \
        "Please provide an OGC Service Type: 'wfs', 'sos', or 'wcs'"

    def __init__(self, service_url, service_type, service_version):
        #print service_url
        service_url = str(service_url)
        # check for service and request kvp's -
        # if not there, add 'em (some services don't have a capabilities reflector),
        STRICT_OGC_CAPABILITIES = \
        "Service=%s&Request=GetCapabilities"%  service_type
        service_url_check = service_url.split("?")
        if len(service_url_check) == 1:
            service_url = service_url + "?" + STRICT_OGC_CAPABILITIES
        else:  # various of the capabilities may be present - clobber them and replace
            service_url = service_url_check[0] + "?" + STRICT_OGC_CAPABILITIES

        if service_type != "":
            try:
                if service_type.lower() == "sos":
                    self.service = sos.SensorObservationService(service_url, service_version)
                    self.service_valid = True
                elif service_type.lower() == "wfs":
                    self.service = wfs.WebFeatureService(service_url, service_version)
                    self.service_valid = True
                elif service_type.lower() == "wcs":
                    self.service = wfs.WebCoverageService(service_url, service_version)
                    self.service_valid = True
                else:
                    self.service_valid = False
                    raise ValueError, INVALID_OGC_TYPE_MESSAGE
            except: # e.g. urllib2.HTTPError: HTTP Error 404: Not Found
                self.service_valid = False
        else:
            raise ValueError, INVALID_OGC_TYPE_MESSAGE
        self.service_url = service_url
        self.ini_service_type = service_type.lower()
        self.provider_keys = []  # set per service type
        self.service_id_keys = []  # set per service type
        self.ini_service_version = service_version
        if self.service_valid:
            # store metadata
            # this looks bizzare, but it is true...
            if service_type.lower() == "wfs" and service_version =="1.0.0":
                self.setServiceIdentification(
                    self.service.__dict__['provider'].__dict__)
                self.setProviderIdentification(
                    self.service.__dict__['provider'].__dict__)
            elif service_type.lower() == "wcs" or service_type.lower() == "sos":
                self.setServiceIdentification(
                    self.service.__dict__['identification'].__dict__)
                self.setProviderIdentification(
                    self.service.__dict__['provider'].__dict__)
            else:
                raise ValueError, INVALID_OGC_TYPE_MESSAGE

    def setServiceIdentification(self, service_dict):
        """service identification metadata is structured differently
        for the different services - parse appropriately"""
        self.service_id_keys = [
            'service_type','service_version','service_title',
            'service_abstract','service_keywords','service_fees',
            'service_accessconstraints']

        if self.ini_service_type == "sos":

            if service_dict.has_key('service'):
                self.service_type = service_dict['service'] # we actually know this, but rebuild anyway
            if service_dict.has_key('version'):
                self.service_version = service_dict['version']# we actually know this, but rebuild anyway
            if service_dict.has_key('title'):
                self.service_title = service_dict['title']
            if service_dict.has_key('abstract'):
                self.service_abstract = service_dict['abstract']
            if service_dict.has_key('keywords'):
                self.service_keywords = service_dict['keywords']
            if service_dict.has_key('fees'):
                self.service_fees = service_dict['fees']
            if service_dict.has_key('accessconstraints'):
                self.service_accessconstraints = service_dict['accessconstraints']

        elif self.ini_service_type == "wfs":
            if self.ini_service_version == '1.0.0':
                # got to dive into the elements of _root key of service_dict
                # (in this case the provider_dict)to get anything useful.
                for elem in service_dict['_root'].__dict__['_children']:
                    if elem.__dict__.has_key('tag') and elem.__dict__.has_key('text'):# we have a kvp, so process
                        tg = elem.__dict__['tag']
                        tx = elem.__dict__['text']
                        try:# check for {http://www.opengis.net/wfs} prefix
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
                self.service_version =  '1.0.0' # will not find this dynamically
            elif self.ini_service_version == '1.1.0':
                pass
            else:
                raise NotImplementedError,  "OGC Service version %s not supported." % self.ini_service_version

        elif self.ini_service_type == "wcs":
            """TO DO: add service data for wcs service"""
            pass

        else:
            raise ValueError, INVALID_OGC_TYPE_MESSAGE

    def setProviderIdentification(self, provider_dict):
        """provider metadata is structured differently
        for the different services - parse appropriately"""
        if self.ini_service_type == "sos":
            self.provider_keys = [
                'provider_url','provider_contact_fax',
                'provider_contact_name','provider_contact_country',
                'provider_contact_phone','provider_contact_region',
                'provider_contact_city','provider_name',
                'provider_contact_address','provider_contact_postcode',
                'provider_contact_email','provider_contact_role',
                'provider_contact_position','provider_contact_site',
                'provider_contact_organization',
                'provider_contact_instructions','provider_contact_hours']
            if provider_dict.has_key('name'):
                self.provider_name = provider_dict['name']
            if provider_dict.has_key('url'):
                self.provider_url = provider_dict['url']
            if provider_dict.has_key('contact'):
                if provider_dict['contact'].__dict__.has_key('name'):
                    self.provider_contact_name = provider_dict['contact'].__dict__['name']
                if provider_dict['contact'].__dict__.has_key('position'):
                    self.provider_contact_position = provider_dict['contact'].__dict__['position']
                if provider_dict['contact'].__dict__.has_key('role'):
                    self.provider_contact_role =  provider_dict['contact'].__dict__['role']
                if provider_dict['contact'].__dict__.has_key('organization'):
                    self.provider_contact_organization = provider_dict['contact'].__dict__['organization']
                if provider_dict['contact'].__dict__.has_key('address'):
                    self.provider_contact_address =  provider_dict['contact'].__dict__['address']
                if provider_dict['contact'].__dict__.has_key('city'):
                    self.provider_contact_city = provider_dict['contact'].__dict__['city']
                if provider_dict['contact'].__dict__.has_key('region'):
                    self.provider_contact_region = provider_dict['contact'].__dict__['region']
                if provider_dict['contact'].__dict__.has_key('postcode'):
                    self.provider_contact_postcode = provider_dict['contact'].__dict__['postcode']
                if provider_dict['contact'].__dict__.has_key('country'):
                    self.provider_contact_country = provider_dict['contact'].__dict__['country']
                if provider_dict['contact'].__dict__.has_key('phone'):
                    self.provider_contact_phone = provider_dict['contact'].__dict__['phone']
                if provider_dict['contact'].__dict__.has_key('fax'):
                    self.provider_contact_fax = provider_dict['contact'].__dict__['fax']
                if provider_dict['contact'].__dict__.has_key('site'):
                    self.provider_contact_site = provider_dict['contact'].__dict__['site']
                if provider_dict['contact'].__dict__.has_key('email'):
                    self.provider_contact_email = provider_dict['contact'].__dict__['email']
                if provider_dict['contact'].__dict__.has_key('hours'):
                    self.provider_contact_hours = provider_dict['contact'].__dict__['hours']
                if provider_dict['contact'].__dict__.has_key('instructions'):
                    self.provider_contact_instructions = provider_dict['contact'].__dict__['instructions']

        elif self.ini_service_type == "wfs":
            """There is NO provider data available for wfs service"""
            pass

        elif self.ini_service_type == "wcs":
            """TO DO: check if provider data is available for wcs service"""
            pass

        else:
            raise ValueError, INVALID_OGC_TYPE_MESSAGE

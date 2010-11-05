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
#"""This module provides a small api for fetching the service and dealing with 
#OGC Web Service Metadata common to the various services (via owslib).
#"""
#
#from owslib import wfs,  wcs,  sos
#
#class OgcService():
#    #########
#    ##namespace issues pervade wfs in owslib e.g. cannot handle when geoserver shorcuts a namespace with an abbreviation
#    ##also wfs will never load a 1.1.0 instance, but it should be loaded as a wfs200
#    #########
#    def __init__(self,  service_url, service_type,  service_version):
#        
#        if service_type != "":
#            #if service_type.lower() == "sos":
#            #    self.service = sos.SensorObservationService(service_url,  service_version)
#            if service_type.lower() == "wfs":
#                self.service = wfs.WebFeatureService(service_url,  service_version)
#            if service_type.lower() == "wcs":
#                self.service = wfs.WebCoverageService(service_url,  service_version)
#        else:
#            raise ValueError,  "Please provide an OGC Service Type e.g. 'wfs', 'sos','wcs'"
#        self.service_url = service_url
#        self.ini_service_type = service_type.lower()
#        self.setServiceIdentification(self.service.__dict__['identification'].__dict__)
#        self.setProviderIdentification(self.service.__dict__['provider'].__dict__)
#    
#    def setServiceIdentification(self,  service_dict):
#        ''' service identification metadata is structured differently for the different services - parse appropriately'''
#        if self.ini_service_type == "sos":
#            if service_dict.has_key('service'):
#                self.service_type = service_dict['service'] #we actually know this, but rebuild anyway
#            if service_dict.has_key('version'):            
#                self.service_version = service_dict['version']
#            if service_dict.has_key('title'):            
#                self.service_title = service_dict['title']
#            if service_dict.has_key('abstract'):            
#                self.service_abstract = service_dict['abstract']
#            if service_dict.has_key('keywords'):            
#                self.service_keywords = service_dict['keywords']       
#            if service_dict.has_key('fees'):            
#                self.service_fees = service_dict['fees']       
#            if service_dict.has_key('accessconstraints'):            
#                self.service_accessconstraints = service_dict['accessconstraints']    
#        
#        elif self.ini_service_type == "wfs":
#            pass
#        
#        elif self.ini_service_type == "wcs":
#            pass        
#        
#        else:
#            pass
#            
#    def setProviderIdentification(self,  provider_dict):
#        '''provider metadata is structured differently for the different services - parse appropriately'''
#        if self.ini_service_type == "sos":
#            if provider_dict.has_key('name'):
#                self.provider_name = provider_dict['name']
#            if provider_dict.has_key('url'):            
#                self.provider_url = provider_dict['url']
#            if provider_dict.has_key('contact'): 
#                if provider_dict['contact'].__dict__.has_key('name'):
#                    self.provider_contact_name = provider_dict['contact'].__dict__['name']
#                if provider_dict['contact'].__dict__.has_key('position'):            
#                    self.provider_contact_position = provider_dict['contact'].__dict__['position']
#                if provider_dict['contact'].__dict__.has_key('role'):            
#                    self.provider_contact_role =  provider_dict['contact'].__dict__['role']
#                if provider_dict['contact'].__dict__.has_key('organization'):            
#                    self.provider_contact_organization = provider_dict['contact'].__dict__['organization']
#                if provider_dict['contact'].__dict__.has_key('address'):            
#                    self.provider_contact_address =  provider_dict['contact'].__dict__['address']
#                if provider_dict['contact'].__dict__.has_key('city'):            
#                    self.provider_contact_city = provider_dict['contact'].__dict__['city']
#                if provider_dict['contact'].__dict__.has_key('region'):           
#                    self.provider_contact_region = provider_dict['contact'].__dict__['region']
#                if provider_dict['contact'].__dict__.has_key('postcode'):           
#                    self.provider_contact_postcode = provider_dict['contact'].__dict__['postcode']
#                if provider_dict['contact'].__dict__.has_key('country'):            
#                    self.provider_contact_country = provider_dict['contact'].__dict__['country']
#                if provider_dict['contact'].__dict__.has_key('phone'):           
#                    self.provider_contact_phone = provider_dict['contact'].__dict__['phone']
#                if provider_dict['contact'].__dict__.has_key('fax'):            
#                    self.provider_contact_fax = provider_dict['contact'].__dict__['fax']
#                if provider_dict['contact'].__dict__.has_key('site'):            
#                    self.provider_contact_site = provider_dict['contact'].__dict__['site']
#                if provider_dict['contact'].__dict__.has_key('email'):            
#                    self.provider_contact_email = provider_dict['contact'].__dict__['email']
#                if provider_dict['contact'].__dict__.has_key('hours'):            
#                    self.provider_contact_hours = provider_dict['contact'].__dict__['hours']
#                if provider_dict['contact'].__dict__.has_key('instructions'):
#                    self.provider_contact_instructions = provider_dict['contact'].__dict__['instructions']        
#        
#        elif self.ini_service_type == "wfs":
#            #got to dive into the elements of _root key to get anything useful
#            for elem in provider_dict['_root'].__dict__['_children']:
#                if elem.__dict__.has_key('tag') and elem.__dict__.has_key('text'):#we have a kvp, so process
#                    tg = elem.__dict__['tag']
#                    tx = elem.__dict__['text']
#                    try:#check for {http://www.opengis.net/wfs} prefix
#                        tg = tg.split('}')[1].lower()
#                    except:
#                        pass
#                    if tg == "name":pass
#                    if tg == "title":pass
#                    if tg == "abstract":pass
#                    if tg == "keywords":pass
#                    if tg == "onlineresource":pass
#                    if tg == "fees":pass
#                    if tg == "accessconstraints":pass
#        
#        
#        
#        elif self.ini_service_type == "wcs":
#            pass       
#            
#        else:
#            pass
                         

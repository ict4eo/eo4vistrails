###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation 
## ingestion, pre-processing, transformation, analytic and visualisation 
## capabilities . Included is the abilty to run code transparently in 
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
"""This module provides a small api for fetching the service and dealing with 
OGC Web Service Metadata common to the various services (via owslib).
"""

from owslib import wfs,  wcs,  sos

class OgcService():
    
    def __init__(self,  service_url, service_type,  service_version):
        
        if service_type != "":
            if service_type.lower() == "sos":
                self.service = sos.SensorObservationService(service_url,  service_version)
            if service_type.lower() == "wfs":
                self.service = wfs.WebFeatureService(service_url,  service_version)
            if service_type.lower() == "wcs":
                self.service = wfs.WebCoverageService(service_url,  service_version)
        self._service_url = service_url
        self.setServiceIdentification(self.service.__dict__['identification'].__dict__)
        self.setProviderIdentification(self.service.__dict__['provider'].__dict__)
    
    def setServiceIdentification(self,  service_dict):
        self.service_type = service_dict['service']
        self.service_version = service_dict['version']
        self.service_title = service_dict['title']
        self.service_fees = service_dict['fees']
        self.service_keywords = service_dict['keywords']       
        
        
    def setProviderIdentification(self,  provider_dict):
        self.provider_url = provider_dict['url']
        #self.service_type = service_type
        #self.service_version=version       

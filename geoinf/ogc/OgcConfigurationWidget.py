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
"""This module provides general ogc selection widgetry for configuring geoinf.ogc modules.
This refers primarily to GetCapabilities requests
"""

from SpatialTemporalConfigurationWidget import SpatialTemporalConfigurationWidget
from owslib import wfs,  sos,  wcs


class OgcCommonWidget(QtGui.QtWidget):
    
    def __init__(self,  url, service_id_dict, provider_id_dict,  parent=None):
        QtGui.QtWidget.__init__(self, parent)
        
        self_service_url = url
        self.setServiceIdentification(service_id_dict)
        self.setProviderIdentification(provider_id_dict)
    
    def setServiceIdentification(self,  service_dict):
        self.service_type = service_dict['service']
        self.service_version = service_dict['version']
        self.service_title = service_dict['title']
        self.service_title = service_dict['fees']
        self.service_title = service_dict['keywords']       
        
        
        
    def setProviderIdentification(self,  provider_dict):
        pass
        #self.service_type = service_type
        #self.service_version=version       
        
class OgcConfigurationWidget(SpatialTemporalConfigurationWidget):
    def __init__(self, metadata_dict,  parent=None):
        SpatialTemporalConfigurationWidget.__init__(self, parent)

        self.ogc_common_widget = OgcCommonWidget(ogc_service_type)

        self.tabs.addTab(self.ogc_common_widget, "")
        


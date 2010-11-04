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

class OgcCommonWidget(QtGui.QtWidget):
    
    def __init__(self,  parent=None):
        QtGui.QtWidget.__init__(self, parent)

class OgcConfigurationWidget(SpatialTemporalConfigurationWidget):
    def __init__(self,  parent=None):
        SpatialTemporalConfigurationWidget.__init__(self, parent)

        self.ogc_common_widget = OgcCommonWidget()

        self.tabs.addTab(self.ogc_common_widget, "")
        


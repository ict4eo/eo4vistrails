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

@author: tvanzyl

"""
#History

from core.modules.vistrails_module import Module, ModuleError
import qgis.core
from PyQt4.QtCore import QFileInfo

#export set PYTHONPATH=/usr/lib/python2.6
qgis.core.QgsApplication.setPrefixPath("/usr", True) 
qgis.core.QgsApplication.initQgis() 

class QgsMapLayer(Module):
    """This module will create a QGIS layer from a file
    """
    def __init__(self):
        Module.__init__(self)
        
    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))
 
class QgsVectorLayer(QgsMapLayer):
    
     def compute(self):
        """Execute the module to create the output"""
        try:
            thefile = self.getInputFromPort('file').get_name()
            fileInfo = QFileInfo(thefile)   
            self.value = qgis.core.QgsVectorLayer(thefile, fileInfo.fileName(), "ogr")
            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))
            
class QgsRasterLayer(QgsMapLayer):
     def compute(self):
        """Execute the module to create the output"""
        try:
            thefile = self.getInputFromPort('file')
            fileInfo = QFileInfo(thefile) 
            qgis.core.QgsRasterLayer.__init__(thefile, fileInfo.fileName(), "ogr")                
            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))

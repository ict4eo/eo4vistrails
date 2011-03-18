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
import osgeo.ogr
from PyQt4.QtCore import QFileInfo
from packages.eo4vistrails.utils.WebRequest import WebRequest, PostGISRequest

#export set PYTHONPATH=/usr/lib/python2.6
qgis.core.QgsApplication.setPrefixPath("/usr", True)
qgis.core.QgsApplication.initQgis()


class QgsMapLayer(Module):
    """This module will create a QGIS layer from a file
    """
    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))
 
class QgsVectorLayer(QgsMapLayer, qgis.core.QgsVectorLayer):
    
    def __init__(self, uri=None, layername=None, driver=None):
        QgsMapLayer.__init__(self)
        if uri and layername and driver:
            qgis.core.QgsVectorLayer.__init__(self, uri, layername, driver)
    
    def compute(self):
        """Execute the module to create the output"""
        try:     
            thefile = self.forceGetInputFromPort('file', None)
            thedataRequest = self.forceGetInputFromPort('dataRequest', None)

            isOGR = (thefile != None) and (thefile.name != '')
            isWFS = isinstance(thedataRequest, WebRequest)
            isPOSTGRES  = isinstance(thedataRequest, PostGISRequest)

            if isOGR:            
                thefilepath = thefile.name
                thefilename = QFileInfo(thefilepath).fileName()
                qgis.core.QgsVectorLayer.__init__(self, thefilepath, thefilename, "ogr")
            elif isPOSTGRES:
                uri = qgis.core.QgsDataSourceURI()
                uri.setConnection('146.64.28.204', '5432', 'experiments', 'ict4eo', 'ict4eo')
                uri.setDataSource('', '(select * from ba_modis_giglio limit 10000)', 'the_geom', '', 'gid')
                qgis.core.QgsVectorLayer.__init__(self, uri.uri(), 'postgis layer', "postgres")
            elif isWFS:
                #Note this is case sensative -> "WFS"
                qgis.core.QgsVectorLayer.__init__(self, thedataRequest.url, 'wfs layer', "WFS")
            
            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))
            
class QgsRasterLayer(QgsMapLayer, qgis.core.QgsRasterLayer):
    def compute(self):
        """Execute the module to create the output"""
        try:
            thefile = self.getInputFromPort('file').name
            fileInfo = QFileInfo(thefile)   
            qgis.core.QgsRasterLayer.__init__(self, thefile, fileInfo.fileName())
            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))

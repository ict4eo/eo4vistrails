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
"""This package provides GIS capabilities for eo4vistrails.
This module provides a data structure for storing raster and vector data
in the format defined by QGIS.
"""
# library
# third party
import qgis.core
from PyQt4.QtCore import QFileInfo
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
# local


from packages.eo4vistrails.utils.DataRequest import DataRequest

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
    
    def mapLayerFactory(self, uri=None, layername=None, driver=None):
        if uri and layername and driver:
            if driver in QgsVectorLayer.SUPPORTED_DRIVERS:
                return QgsVectorLayer(uri, layername, driver)
            elif driver in QgsRasterLayer.SUPPORTED_DRIVERS:
                return QgsRasterLayer(uri, layername, driver)
            else:
                self.raiseError('Map Layer Driver %s not supported' % str(driver))
        else:
            self.raiseError('All Map Layer Properties must be set')

class QgsVectorLayer(QgsMapLayer, qgis.core.QgsVectorLayer):
    """TO DO: Add doc string
    """
    SUPPORTED_DRIVERS = ['WFS','ogr', 'postgres']    
    
    def __init__(self, uri=None, layername=None, driver=None):
        QgsMapLayer.__init__(self)
        if uri and layername and driver:
            qgis.core.QgsVectorLayer.__init__(self, uri, layername, driver)

    def compute(self):
        """Execute the module to create the output"""
        try:
            thefile = self.forceGetInputFromPort('file', None)
            dataReq = self.forceGetInputFromPort('dataRequest', None)

            isFILE = (thefile != None) and (thefile.name != '')
            #Note this is case sensitive -> "WFS"
            isQGISSuported = isinstance(dataReq, DataRequest) and dataReq.get_driver() in self.SUPPORTED_DRIVERS

            if isFILE:
                thefilepath = thefile.name
                thefilename = QFileInfo(thefilepath).fileName()
                qgis.core.QgsVectorLayer.__init__(
                    self, thefilepath, thefilename, "ogr")
            elif isQGISSuported:
                qgis.core.QgsVectorLayer.__init__(
                    self,
                    dataReq.get_uri(),
                    dataReq.get_layername(),
                    dataReq.get_driver())
            else:
                self.raiseError('vector Layer Driver %s not supported' % str(dataReq.get_driver()))

            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))


class QgsRasterLayer(QgsMapLayer, qgis.core.QgsRasterLayer):
    """TO DO: Add doc string
    """
    SUPPORTED_DRIVERS = ['WCS', 'gdl']
    
    def __init__(self, uri=None, layername=None, driver=None):
        QgsMapLayer.__init__(self)
        if uri and layername:
            qgis.core.QgsRasterLayer.__init__(self, uri, layername)

    def compute(self):
        """Execute the module to create the output"""
        try:
            thefile = self.forceGetInputFromPort('file', None)
            dataReq = self.forceGetInputFromPort('dataRequest', None)

            isFILE = (thefile != None) and (thefile.name != '')
            isQGISSuported = isinstance(dataReq, DataRequest) and dataReq.get_driver() in self.SUPPORTED_DRIVERS

            if isFILE:
                thefilepath = thefile.name
                thefilename = QFileInfo(thefilepath).fileName()
                qgis.core.QgsRasterLayer.__init__(
                    self, thefilepath, thefilename)
            elif isQGISSuported:
                qgis.core.QgsRasterLayer.__init__(
                    self,
                    dataReq.get_uri(),
                    dataReq.get_layername())
            else:
                self.raiseError('Raster Layer Driver %s not supported' % str(dataReq.get_driver()))

            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))

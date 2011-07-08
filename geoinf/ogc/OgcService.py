###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the ability to run code transparently in
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
"""This module provides a base OGC (Open Geospatial Consortium) service class.
"""

# library
import init
import random
# third-party
from PyQt4 import QtCore, QtGui
# vistrails
from core.modules.vistrails_module import \
    Module, new_module, NotCacheable, ModuleError
# eo4vistrails
from packages.eo4vistrails.geoinf.datamodels.Feature import FeatureModel
from packages.eo4vistrails.geoinf.datamodels.Raster import RasterModel
from packages.eo4vistrails.geoinf.datamodels.QgsLayer import \
    QgsVectorLayer, QgsRasterLayer
from packages.eo4vistrails.geoinf.ogc.OgcConfigurationWidget import \
    OgcConfigurationWidget
from packages.eo4vistrails.utils.WebRequest import WebRequest


class OGC(NotCacheable):
    """
    Provide basic connection service to an OGC (Open Geospatial Consortium)
    web service.

    Configuration allows the base URL for the service to be set and called.
    Choosing the appropriate combination of specific service type and other
    parameters, will cause the input port to be set with a specific POST call,
    once the configuration interface is closed.

    Running the module will set the (string) values of the URL, data (if any),
    and the resulting QGIS layer, for access via the output ports.
    """

    def __init__(self):
        self.post_data = None
        self.get_request = None
        self.url = None
        self.layername = None
        self.webRequest = WebRequest()

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))

    def compute(self):
        """Execute the module to create the output"""
        # get input
        try:
            self.post_data = self.getInputFromPort(init.OGC_POST_DATA_PORT)
        except:
            self.post_data = None
        try:
            self.get_request = self.getInputFromPort(init.OGC_GET_REQUEST_PORT)
        except:
            self.get_request = None
        try:
            self.url = self.getInputFromPort(init.OGC_URL_PORT)
        except:
            self.url = None
        #print "OgcService:86\n url: %s\n get_req: %s\n post_data: %s" %\
        #    (self.url, self.get_request, self.post_data)

        # assign to webRequest
        if self.get_request:
            self.webRequest.url = self.get_request
            self.webRequest.data = None
        if self.post_data and self.url:
            self.webRequest.url = self.url
            self.webRequest.data = self.post_data

        # request port
        if init.WEB_REQUEST_PORT in self.outputPorts:
            self.setResult(init.WEB_REQUEST_PORT, self.webRequest)
        if init.URL_PORT in self.outputPorts:
            self.setResult(init.URL_PORT, self.webRequest.url)

        # data port (data could be text or a 'raw' image)
        if init.DATA_PORT in self.outputPorts:
            self.webRequest.runRequest()  # create the data stream
            if self.webRequest.data:
                self.setResult(init.DATA_PORT, self.webRequest.data)

        # layer port
        if self.url:
            random.seed()
            # conditional execution: only set layername if upstream connection
            if init.OGC_LAYERNAME_PORT in self.inputPorts:
                self.layername = \
                    self.getInputFromPort(init.OGC_LAYERNAME_PORT) or \
                    self.webRequest.get_layername() or \
                    'ogc_layer' + str(random.randint(0, 10000))
            # conditional execution: only setResult if downstream connection
            if init.VECTOR_PORT in self.outputPorts:
                qgsVectorLayer = QgsVectorLayer(
                    self.url, self.layername, self.webRequest.get_driver())
                #print "qgsVectorLayer", qgsVectorLayer
                self.setResult(init.VECTOR_PORT, qgsVectorLayer)
            if init.RASTER_PORT in self.outputPorts:
                qgsRasterLayer = QgsRasterLayer(
                    self.url, self.layername, self.webRequest.get_driver())
                #print "qgsRasterLayer", qgsRasterLayer
                self.setResult(init.RASTER_PORT, qgsRasterLayer)

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
"""This module provides a data structure for creating and storing vector data,
as well as associated attribute data (typically time-series data), based on the
format defined by QGIS, from different input data types.
"""
# library
# third party
import qgis.core
from PyQt4.QtCore import QFileInfo
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.utils.Parser import Parser
from packages.eo4vistrails.utils.DataRequest import DataRequest
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
# local
from QgsLayer import QgsVectorLayer


class TemporalVectorLayer(QgsVectorLayer, qgis.core.QgsVectorLayer):
    # TO DO - OMIT qgis.core.QgsVectorLayer
    """Create an extended vector layer, based on QGIS vector layer.

    Associated data is stored, and can be referenced, in a local file.

    For example, in the case of a SOS, the data fetched from the server
    will be stored in an O&M schema-based XML file (self.results_file)
    """

    def __init__(self, uri=None, layername=None, driver=None):
        QgsVectorLayer.__init__(self)
        if uri and layername and driver:
            qgis.core.QgsVectorLayer.__init__(self, uri, layername, driver)
        self.SUPPORTED_DRIVERS += ['OM', 'HDF']  # add new supported types
        self.time_series = {}

    def compute(self):
        """Execute the module to create the output"""
        fileObj = None
        try:
            thefile = self.forceGetInputFromPort('file', None)
            dataReq = self.forceGetInputFromPort('dataRequest', None)

            try:
                isFILE = (thefile != None) and (thefile.name != '')
            except AttributeError:
                isFILE = (thefile.name != '')
            isQGISSuported = isinstance(dataReq, DataRequest) and \
                            dataReq.get_driver() in self.SUPPORTED_DRIVERS

            if isFILE:
                self.thefilepath = thefile.name
                self.thefilename = QFileInfo(self.thefilepath).fileName()
                qgis.core.QgsVectorLayer.__init__(
                    self,
                    self.thefilepath,
                    self.thefilename,
                    "ogr")
                #print "TVL:84", self.thefilepath
                self.results_file = self.thefilepath
            elif isQGISSuported:
                qgis.core.QgsVectorLayer.__init__(
                    self,
                    dataReq.get_uri(),
                    dataReq.get_layername(),
                    dataReq.get_driver())
            else:
                if dataReq:
                    self.raiseError('Vector Layer Driver %s not supported' %
                                    str(dataReq.get_driver()))
                else:
                    pass
                    self.raiseError('No valid data request')

            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))

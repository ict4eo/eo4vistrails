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
as well as attribute data, based the format defined by QGIS, from different
input data types.
"""
# library
# third party
import qgis.core
from PyQt4.QtCore import QFileInfo
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.utils.DataRequest import DataRequest
from packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
# local
from QgsLayer import QgsVectorLayer

'''
class TemporalLayer(ThreadSafeMixin, Module):
    """Create a map layer from a data input stream.

    Data is assumed to be a format suitable for conversion to a vector layer;
    for example, HDF or O&M formats.
    """

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))

    def mapLayerFactory(self, uri=None, layername=None, driver=None):
        """Create a QGIS vector map layer based on driver."""
        if uri and layername and driver:
            if driver in TemporalVectorLayer.SUPPORTED_DRIVERS:
                return TemporalVectorLayer(uri, layername, driver)
            else:
                self.raiseError('Map Layer Driver %s not supported' %\
                                str(driver))
        else:
            self.raiseError('All Map Layer Properties must be set')
'''

class TemporalVectorLayer(QgsVectorLayer, qgis.core.QgsVectorLayer):
    """Create an extended vector layer, based on QGIS vector layer
    """

    def __init__(self, uri=None, layername=None, driver=None):
        QgsVectorLayer.__init__(self)
        if uri and layername and driver:
            print "TVL:82", uri, layername, driver
            qgis.core.QgsVectorLayer.__init__(self, uri, layername, driver)
        self.SUPPORTED_DRIVERS += ['OM', 'HDF']  # add new supported types
        print "TVL:84", uri, layername, driver

    def compute(self):
        """Execute the module to create the output"""
        print "TVL:89"
        try:
            print "TVL:90"
            thefile = self.forceGetInputFromPort('file', None)
            dataReq = self.forceGetInputFromPort('dataRequest', None)

            try:
                isFILE = (thefile != None) and (thefile.name != '')
            except AttributeError:
                isFILE = (thefile.name != '')

            #Note this is case sensitive -> "WFS"
            isQGISSuported = isinstance(dataReq, DataRequest) and \
                            dataReq.get_driver() in self.SUPPORTED_DRIVERS

            print "TVL:100", uri, layername, driver, isQGISSuported
            if isFILE:
                thefilepath = thefile.name
                thefilename = QFileInfo(thefilepath).fileName()
                qgis.core.QgsVectorLayer.__init__(
                    self,
                    thefilepath,
                    thefilename,
                    "ogr")
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

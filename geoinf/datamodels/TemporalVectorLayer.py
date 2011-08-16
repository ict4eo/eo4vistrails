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
                thefilepath = thefile.name
                thefilename = QFileInfo(thefilepath).fileName()
                qgis.core.QgsVectorLayer.__init__(
                    self,
                    thefilepath,
                    thefilename,
                    "ogr")
                print "TVL:108", thefilepath
                self.extract_time_series(thefilepath)
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

    def extract_time_series(self, thefile):
        """Parse SOS GML file and extract time series data."""
        parse = Parser(file=thefile, namespace="http://www.opengis.net/om/1.0")
        print "TVL:132 - NS", parse.namespace, '\n        - XML', parse.xml
        # if get
        print "TVL:134 - ObservationCollection", parse.tag_value('ObservationCollection')
        print "TVL:135 - ObservationCollection", \
            parse.tag_value(
                'boundedBy/Envelope/lowerCorner',
                namespace=parse.get_ns('gml')) #path is split via '/'
        om_result = parse.elem_tag(
            'member/Observation/result',
            namespace=parse.get_ns('om'))
        print "TVL:139 - om:result", om_result
        print "TVL:139 - swe:values", \
            parse.elem_tag_value(
                om_result,
                'DataArray/values',
                namespace=parse.get_ns('swe'))

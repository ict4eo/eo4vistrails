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
"""This module provides a data structure for storing raster and vector data
in the formats defined by QGIS.
"""
# library
# third party
import qgis.core
from PyQt4.QtCore import QFileInfo
# vistrails
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
# eo4vistrails
from packages.eo4vistrails.utils.DataRequest import DataRequest
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget
# local
from core.modules import basic_modules
from threading import Thread, currentThread, RLock


class EPSGComboBoxWidget(ComboBoxWidget):
    """TODO: Add docstring
    """
    default = ('4326', 4326)

    def getKeyValues(self):
        return {'3867': 3786, '4326': 4326}

EPSGCode = basic_modules.new_constant('EPSG Code',
                                      staticmethod(eval),
                                      4326,
                                      staticmethod(lambda x: type(x) == int),
                                      EPSGComboBoxWidget)


#global globalQgsLock
#globalQgsLock = RLock()

class QgsMapLayer(Module, NotCacheable):
    """
    This module will create a QGIS layer from a file

    Notes:
        It is not threadsafe and has race conditions on the qgis drivers
    """

    #_input_ports = [('EPSG Code', '(za.co.csir.eo4vistrails:EPSG Code:data)')]

    def __init__(self):
        #ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error with traceback display."""
        import traceback
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ' - %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def temp_q(self):
        """test to check if temp file created."""
        return self.interpreter.filePool.create_file(suffix=".csv")

    def mapLayerFactory(self, uri=None, layername=None, driver=None):
        """Create a QGIS map layer based on driver."""
        if uri and layername and driver:
            if driver in QgsVectorLayer.SUPPORTED_DRIVERS:
                return QgsVectorLayer(uri, layername, driver)
            elif driver in QgsRasterLayer.SUPPORTED_DRIVERS:
                return QgsRasterLayer(uri, layername, driver)
            else:
                self.raiseError('Map Layer Driver %s not supported' %\
                                str(driver))
        else:
            self.raiseError('All Map Layer Properties must be set')


class QgsVectorLayer(QgsMapLayer, qgis.core.QgsVectorLayer):
    """Create a QGIS vector layer.
    """

    def __init__(self, uri=None, layername=None, driver=None):
        QgsMapLayer.__init__(self)
        if uri and layername and driver:
            qgis.core.QgsVectorLayer.__init__(self, uri, layername, driver)
        self.SUPPORTED_DRIVERS = ['WFS', 'ogr', 'postgres']

    def temp(self):
        """test to check if temp file created."""
        return self.temp_q()

    def compute(self):
        """Execute the module to create the output"""
        #global globalQgsLock

        try:
            thefile = self.forceGetInputFromPort('file', None)
            dataReq = self.forceGetInputFromPort('dataRequest', None)
            theProj = self.forceGetInputFromPort('EPSG Code', None)
            self.layer_file = thefile

            try:
                isFILE = (thefile != None) and (thefile.name != '')
            except AttributeError:
                isFILE = (thefile.name != '')

            #Note this is case sensitive -> "WFS"
            isQGISSuported = isinstance(dataReq, DataRequest) and \
                            dataReq.get_driver() in self.SUPPORTED_DRIVERS

            if isFILE:
                thefilepath = thefile.name
                thefilename = QFileInfo(thefilepath).fileName()

                #globalQgsLock.acquire()
                qgis.core.QgsVectorLayer.__init__(
                    self,
                    thefilepath,
                    thefilename,
                    "ogr")
                #globalQgsLock.release()

                if theProj:
                    self.setCrs(qgis.core.QgsCoordinateReferenceSystem(theProj))
            elif isQGISSuported:

                #globalQgsLock.acquire()
                qgis.core.QgsVectorLayer.__init__(
                    self,
                    dataReq.get_uri(),
                    dataReq.get_layername(),
                    dataReq.get_driver())
                #globalQgsLock.release()

                if theProj:
                    self.setCrs(qgis.core.QgsCoordinateReferenceSystem(theProj))
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


@RPyCSafeModule()
class QgsRasterLayer(QgsMapLayer, qgis.core.QgsRasterLayer):
    """Create a QGIS raster layer.
    """

    def __init__(self, uri=None, layername=None, driver=None):
        QgsMapLayer.__init__(self)
        if uri and layername:
            qgis.core.QgsRasterLayer.__init__(self, uri, layername)
        self.SUPPORTED_DRIVERS = ['WCS', 'gdl']
        self.ownNotSupported = True

    def compute(self):
        """Execute the module to create the output"""
        global globalQgsLock

        try:
            thefile = self.forceGetInputFromPort('file', None)
            dataReq = self.forceGetInputFromPort('dataRequest', None)
            theProj = self.forceGetInputFromPort('EPSG Code', None)

            #print "Qgslayer:188-thefile", thefile
            #print "Qgslayer:189-thefile name", thefile.name
            #print "Qgslayer:190-projection", theProj

            if thefile:
                isFILE = (thefile.name != '')
            isQGISSuported = isinstance(dataReq, DataRequest) and \
                            dataReq.get_driver() in self.SUPPORTED_DRIVERS

            if isFILE:
                thefilepath = thefile.name
                thefilename = QFileInfo(thefilepath).fileName()

                #globalQgsLock.acquire()
                qgis.core.QgsRasterLayer.__init__(
                    self,
                    thefilepath,
                    thefilename)
                #globalQgsLock.release()

                if theProj:
                    self.setCrs(qgis.core.QgsCoordinateReferenceSystem(theProj))

            elif isQGISSuported:

                #globalQgsLock.acquire()
                qgis.core.QgsRasterLayer.__init__(
                    self,
                    dataReq.get_uri(),
                    dataReq.get_layername())
                #globalQgsLock.release()

                if theProj:
                    self.setCrs(qgis.core.QgsCoordinateReferenceSystem(theProj))

            else:
                if dataReq:
                    self.raiseError('Raster Layer Driver %s not supported' %
                                str(dataReq.get_driver()))
                else:
                    self.raiseError('Raster Layer is not specified.')

            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))

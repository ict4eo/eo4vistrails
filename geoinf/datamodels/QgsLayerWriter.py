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
"""This module provides a means for saving raster and vector data to file,
in the format defined by QGIS.
"""
# library
# third party
import qgis.core
from PyQt4.QtCore import QFileInfo
from qgis.core import QgsVectorFileWriter, QgsCoordinateReferenceSystem
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
# local

#export set PYTHONPATH=/usr/lib/python2.6
qgis.core.QgsApplication.setPrefixPath("/usr", True)
qgis.core.QgsApplication.initQgis()


class QgsLayerWriter(Module):
    """This module will create a shape file from a QGIS vector layer
    """

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))

    def compute(self):
        """Execute the module to create the output
        """
        try:
            thefile = self.forceGetInputFromPort('file', None)
            thelayer = self.forceGetInputFromPort('value', None)
            isFILE = (thefile != None) and (thefile.name != '')
            if isFILE:
                thefilepath = thefile.name
                #thefilename = QFileInfo(thefilepath).fileName()
                # TODO - upgrade the input port to specify the file type out
                self.write_vector_layer(thelayer, thefilepath, 'SHP')
            else:
                self.raiseError('Invalid output file')

            self.setResult('value', self)
        except Exception, e:
            self.raiseError('Cannot set output port: %s' % str(e))

    def write_vector_layer(self, layer, filename, filetype='SHP',
                           encoding=None):
        """Write a QGIS vector layer to disk
        """
        SUPPORTED = ('SHP',)  # QGIS 1.6 only handles shapefile (SHP) outputs
        if not layer:
            self.raiseError('Missing layer file')
        elif not layer.isValid():
            self.raiseError('Invalid layer file')
        else:
            if not encoding:
                encoding = 'CP1250'
            if filetype in SUPPORTED:
                if filetype == 'SHP':
                    crsDest = QgsCoordinateReferenceSystem(layer.srs())
                    error = QgsVectorFileWriter.writeAsShapefile(
                        layer, filename, encoding, crsDest, False)
                    #print "QgsLayer:89", error,  filename, encoding, crsDest
                # TODO IN FUTURE
                # add support for other vector types
            else:
                if filetype:
                    self.raiseError('Vector layer type "%s" not supported' % \
                                    str(filetype))
                else:
                    self.raiseError('Vector layer type not specified')

            """# COMPLEX VECTOR LAYER WRITING
            # define fields for feature attributes
            # ??? rather retrieve all features for an existing layer ???
            fields = { 0 : QgsField("first", QVariant.Int),
                       1 : QgsField("second", QVariant.String) }

            # create an instance of vector file writer to create the shapefile.
            # Arguments:
            # 1. path to new shapefile (will fail if exists already)
            # 2. encoding of the attributes
            # 3. field map
            # 4. geometry type - from WKBTYPE enum
            # 5. layer's spatial ref(instance of QgsSpatialRefSys) - opt
            writer = QgsVectorFileWriter(filename, encoding, fields,
                                         layer.wkbType(), None)

            if writer.hasError() != QgsVectorFileWriter.NoError:
              print "Error when creating shapefile: ", writer.hasError()

            # add layer features
            writer.addFeature(fet)

            # delete the writer to flush features to disk (optional)
            del writer
            """

    def write_raster_layer(self, layer, filename, filetype=None,
                           encoding=None):
        """.. todo:: Write a QGIS raster layer to disk
        """
        pass

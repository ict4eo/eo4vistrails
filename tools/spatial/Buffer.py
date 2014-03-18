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
"""This module provides a buffering process operation for a vector layer for
EO4VisTrails.
"""
# library
import os
import os.path
# third-party
from qgis.analysis import QgsGeometryAnalyzer
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from vistrails.packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from vistrails.packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin


@RPyCSafeModule()
class Buffer(ThreadSafeMixin, Module):
    """Accept a vector layer and buffer it according to specified parameters.
    
    Input ports:
    
        list_in:
            a QGIS MapLayer
        buffer:
            the distance for buffering
        dissolve:
            whether or not to merge the buffer with the source features (False)
    
    Output ports:
        
        shapefile:
            the buffered output as a shapefile
    """

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error with traceback display."""
        import traceback
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ' - %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def compute(self):
        layer = self.getInputFromPort('layer')
        dissolve = self.forceGetInputFromPort('dissolve', False)
        distance = self.forceGetInputFromPort('distance', 0.0)
        output_file = self.interpreter.filePool.create_file(suffix='.shp')

        try:
            if 'shapefile' in self.outputPorts:
                #layer, shapefileName, bufferDistance, onlySelectedFeatures,
                # dissolve, bufferDistanceField = -1, p = 0)
                myshape = QgsGeometryAnalyzer.buffer(layer, output_file,
                                                    distance, False,
                                                    dissolve, -1, 0)
            else:
                myshape = None
            self.setResult('shapefile', myshape)

        except Exception, ex:
            self.raiseError(ex)

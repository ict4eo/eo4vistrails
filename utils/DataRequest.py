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
"""This module forms part of the eo4vistrails capabilities - it is used to
handle data and PostGIS requests for processing inside vistrails.
"""

# library
# third party
from qgis.core import QgsDataSourceURI
# vistrails
# eo4vistrails
from core.modules.vistrails_module import Module, NotCacheable, ModuleError
# local


class DataRequest(NotCacheable, Module):
    """TO DO: Add doc string"""
    def __init__(self, uri = None, layername = None, driver = None):
        Module.__init__(self)
        self._uri = uri
        self._layername = layername
        self._driver = driver

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))

    def get_uri(self):
        return self._uri

    def get_layername(self):
        return self._layername

    def get_driver(self):
        return self._driver

    def compute(self):
        self._uri = self.forceGetInputFromPort('uri',None)
        self._layername = self.forceGetInputFromPort('layername',None)
        self._driver = self.forceGetInputFromPort('driver',None)

    _input_ports = [('uri', '(edu.utah.sci.vistrails.basic:String)'),
                    ('layername', '(edu.utah.sci.vistrails.basic:String)'),
                    ('driver', '(edu.utah.sci.vistrails.basic:String)')]


class PostGISRequest(DataRequest, QgsDataSourceURI):
    """TO DO: Add doc string"""
    def __init__(self):
        import random
        random.seed()
        DataRequest.__init__(self)
        QgsDataSourceURI.__init__(self)
        self._driver = 'postgres'
        self._layername = 'postgislayer' + str(random.randint(0,10000))

    def get_uri(self):
        return self.uri()

    def compute(self):
        self.setResult('value', self)
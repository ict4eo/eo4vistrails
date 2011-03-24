# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 10:08:59 2011

@author: tvzyl
"""
from core.modules.vistrails_module import Module, NotCacheable, ModuleError
from qgis.core import QgsDataSourceURI

class DataRequest(NotCacheable, Module):
    
    def __init__(self, uri = None, layername = None, driver = None):
        Module.__init__(self)
        self._layername = layername
        self._driver = driver
        self._uri = uri

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error."""
        import traceback
        traceback.print_exc()
        raise ModuleError(self, msg + ': %s' % str(error))
        
    def get_layername(self):
        return self._layername
        
    def get_driver(self):
        return self._driver
        
    def get_uri(self):
        return self._uri

class PostGISRequest(DataRequest, QgsDataSourceURI):
    
    def __init__(self):
        import random
        random.seed()
        DataRequest.__init__(self)
        QgsDataSourceURI.__init__(self)
        self._driver = 'postgres'
        self._layername = 'postgreslayer' + str(random.randint(0,10000))
    
    def get_uri(self):
        return self.uri()
    
    def compute(self):        
        self.setResult('value', self)
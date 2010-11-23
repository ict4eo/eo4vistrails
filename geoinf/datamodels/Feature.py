###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation 
## ingestion, pre-processing, transformation, analytic and visualisation 
## capabilities . Included is the abilty to run code transparently in 
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
"""This module provides an generic OGC Simple Features data model via OGR. 
All eo4vistrails modules dealing with feature data must extend this class.
"""
import core.modules.module_registry
import core.system
from core.modules.vistrails_module import Module, ModuleError
from core.modules.basic_modules import File
import gui.application
try:
    from osgeo import ogr
except:
    import ogr

import os
import os.path

class _OgrMemModel():
    """
    Used as both a storage mechanism for MemFeatureModel instances
    and as a general OGR constructor, i.e. whether you want an 
    in-memory OGR data provider or not, data will always be passed 
    into OGR control via instances of _OgrMemModel
    """
    def __init__(self):
        self.driver = ogr.GetDriverByName('Memory')
        self.datasource = self.driver.CreateDataSource("working_ds")
    
    def loadContentFromFile(self,  sourceDS,  getStatement=""):
        """Loads content off filesystem, e.g. from a shapefile
        Expects datasets with one layer, so some arcane formats are out...
        sourceDS is a path to a file.
        {
        shapefiles;
        csv files;
        gml files;
        }
        """
        if os.path.exists(sourceDS):
            conn = ogr.Open(sourceDS)
            lyr = conn.GetLayer(0)
            self.datasource.CopyLayer(lyr)
        
            conn.ReleaseResultSet(lyr)
            conn = None 
        else:
            raise ValueError,  "Path to OGR dataset does not exist"
        
    def loadContentFromDB(self,  connstr,  getStatement):
        """Loads content off PostGIS or SpatialLite database, specified by 
        connection string and layer defined by a Select statement"""
        conn = ogr.Open(connstr)
        lyr = conn.ExecuteSQL(getStatement)
        self.datasource.CopyLayer(lyr)
        
        conn.ReleaseResultSet(lyr)
        conn = None
    
    def loadContentFromURI(self,  uri,  getStatement=""):
        """Loads content off web service, feed etc, like a WFS, GeoRSS"""
        pass
        
    def dumpToFile(self,  datasetType = "shp"):    
        pass
        
    def __del__(self):
        """connection resetting, memory deallocation"""
        self.datasource.ReleaseResultLayer(0)
        self.datasource = None
        
class MemFeatureModel(Module):
    """
    Retains a copy of an OGR dataset in memory
    """
    def __init__(self):
        Module.__init__(self)
    
    def compute(self):
        self.feature_model = _OgrMemModel()
        

class FileFeatureModel(File):
    """
    Persists a FeatureModel to disk at a user specified location;
    Likely outputs via OGR would be :
    {shapefile, a spatialite database, a GML file,GeoJSON}
    """
    def __init__(self):
        File.__init__(self)
        
    @staticmethod
    def translate_to_python(x):
        result = File()
        result.name = x
        result.setResult("value", result)
        return result

    def compute(self):
        n = self.get_name()
        if (self.hasInputFromPort("create_file") and
            self.getInputFromPort("create_file")):
            core.system.touch(n)
        if not os.path.isfile(n):
            raise ModuleError(self, 'File "%s" does not exist' % n)
        self.set_results(n)
        self.setResult("local_filename", n)
        self.setResult("self", self)

    @staticmethod
    def get_widget_class():
        return FileChooserWidget

class FeatureModel(Module):
    """This is a common representation of Vector/Feature 
    data, sourced from numerous places {postgis, shapefiles, wfs's, gml,...}
    Representation is provided by the GDAL/OGR (OGR) library.
    Classes that implement this module are expected to generate the 
    internal OGR objects. Optionally, they may expose ports that 
    serialise the OGR objects, but is more likely to take place 
    via external serialisers. Should there be an in-memory and 
    a cacheable version of this?
    """
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        """Overriden by subclasses - typically where the 
        conversion to an OGR Dataset takes place"""
        pass

def initialize(*args, **keywords):
    """sets everything up"""
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(FeatureModel)
    #input ports
    
    #reg.add_input_port(FeatureModel, "service_version", (core.modules.basic_modules.String, 'Web Map Service version - default 1.1.1'))   
    #output ports
    reg.add_output_port(
        FeatureModel,
        "OGRDataset",
        (ogr.Dataset, 'Feature data in OGR Dataset')
    )

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
"""This module provides an generic Coverage/Raster data model via GDAL. 
All eo4vistrails modules dealing with raster data must extend this class.
"""

import os
import os.path
import urllib
import hashlib
import core.modules.module_registry
import core.system
from core.modules.vistrails_module import Module, ModuleError
from core.modules.basic_modules import File
import gui.application
try:
    from osgeo import gdal
except:
    import gdal

class _GdalMemModel():
    """
    Used as both a storage mechanism for MemRasterModel instances
    and as a general GDAL constructor, i.e. whether you want an
    in-memory GDAL data provider or not, data will always be passed
    into GDAL control via instances of _GdalMemModel
    """
    def __init__(self):
        self.driver = gdal.GetDriverByName('MEM')
        #self.datasource = self.driver.CreateDataSource("working_ds")

    def loadContentFromFile(self, sourceDS, getStatement=""):
        """Loads content off filesystem, e.g. from a geotiff
        Expects datasets with one layer, so some arcane formats are out...
        sourceDS is a path to a file.
        {
        geotiff
        }
        """
        if os.path.exists(sourceDS):
            self.datasource = self.driver.CreateCopy("working_ds", gdal.Open(sourceDS))
        else:
            raise ValueError, "Path to GDAL dataset does not exist"


    def loadContentFromURI(self, uri, getStatement=""):
        """Loads content off web service, feed etc, like a WCS
        
        uri: string of the service endpoint
        getStatement: a string of the xml of the request parameters
        
        These two variables allow creation of get/post requests and also allow us 
        to make GDAL sensibly deal with the inputs.
        
        For WCS, we expect a WCS GetCoverage request to be incoming.
        GDAL, our ratser swiss army knife, expects to access a wcs from a 
        config file on the filesystem, that looks like:
        <WCS_GDAL>
            <ServiceURL>http://ict4eo.meraka.csir.co.za/geoserver/wcs?</ServiceURL>
            <CoverageName>nurc:Img_Sample</CoverageName>
        </WCS_GDAL>
        
        and is called something like ict4eowcs.wcs
        
        GDAL needs RW access to this file, for it then rights the capabilities 
        to it for later reference

        """
        #first, get a temporary file location that is writeable
        temp_filepath = core.system.default_dot_vistrails() + "/eo4vistrails/gdal/"
        if not os.path.exists(temp_filepath):
            os.mkdir(temp_filepath)
            sourceDS = temp_filepath + hashlib.sha1(urllib.quote_plus(uri+getStatement)).hexdigest() + ".wcs"
        #write wcs params to it
        rw = open(sourceDS, 'w')
        gs_list = getStatement.split("&")
        for gs_listitem in gs_list:
            gskvp = gs_listitem.split("=")
            if gskvp[0].lower() == "coverage": coverage = gskvp[1]
            #ideally would handle cases beyond setting up a basic config - this is essentially a GetCapabilities checker - but it needs to handle the GetCoverage properly, since that is what it will receive...
        str = "<WCS_GDAL><ServiceURL>%s</ServiceURL><CoverageName>%s</CoverageName></WCS_GDAL>" % (uri,  coverage)
        rw.close()
        if os.path.exists(sourceDS):
            self.datasource = self.driver.CreateCopy("working_ds", gdal.Open(sourceDS))
        else:
            raise ValueError, "Path to GDAL dataset does not exist"       
       

        
        def _guessOutputType(type_string):
            print type_string
            if type_string.split(';')[0].lower() == "text/xml":
                #is gml, O&M etc
                return ".xml"
            if type_string.split(';')[0].lower() == "gml2":
                return ".gml"
        
        def _viaCache():
            temp_filepath = core.system.default_dot_vistrails() + "/eo4vistrails/gdal/"
            if not os.path.exists(temp_filepath):
                os.mkdir(temp_filepath)
            temp_filename = temp_filepath + hashlib.sha1(urllib.quote_plus(uri+getStatement)).hexdigest() + outputtype
            #core.system.touch(temp_filename)
            postdata = urllib.urlencode({'request': getStatement})
            print postdata
            u = urllib.urlretrieve(url = uri,  filename = temp_filename,  data = postdata,)
            self.loadContentFromFile(temp_filename)
            
        def _viaStream():
            pass
            
        outputtype = _guessOutputType(fmt)
        #implement first a non-streaming version of this method, 
        #i.e. fetches from uri, caches, reads from cache
        
        _viaCache()
        
    def dumpToFile(self,  filesource,  datasetType = "GTiff"):
        try:
            driver = gdal.GetDriverByName(datasetType)
            if datasetType == "CSV":
                ds = driver.CreateDataSource( filesource,  options=["GEOMETRY=AS_XY"])
                ds.CopyLayer(self.datasource.GetLayer(0),  self.datasource.GetLayer(0).GetName(),  options=["GEOMETRY=AS_XY"])
            else:
                ds = driver.CreateDataSource( filesource)
                ds.CopyLayer(self.datasource.GetLayer(0),  self.datasource.GetLayer(0).GetName())
            filename = ds.GetName()
            ds = None
        except:
            return (False,  "")
        return (True,  filename)

    def __del__(self):
        """connection resetting, memory deallocation"""
        try:
            self.datasource.ReleaseResultLayer(0)
        except:
            pass
        try:
            self.datasource = None
        except:
            pass




class RasterModel(Module):
    """TO DO - add docstring"""
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        pass

def initialize(*args, **keywords):
    """sets everything up"""
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(RasterModel)
    #input ports
   
    #reg.add_input_port(FeatureModel, "service_version", (core.modules.basic_modules.String, 'Web Map Service version - default 1.1.1'))   
    #output ports
    reg.add_output_port(
        RasterModel,
        "GDALDataset",
        (gdal.Dataset, 'Raster data as GDAL')
    )

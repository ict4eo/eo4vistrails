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
"""
Created on Tue Dec 14 09:38:10 2010

@author: tvzyl

Module forms part of the rpyc vistrails capabilties, used to add multicore
parallel and distributed processing to vistrails.

This Module is the called by higher level inits to ensure that regsitration with 
vsitrails takes place

"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

def initialize(*args, **keywords):
    from core.modules.module_registry import get_module_registry
    from core.modules import basic_modules
    
    import QgsLayer
    
    from Feature import FeatureModel,  FileFeatureModel,  MemFeatureModel
    from Raster import RasterModel
    from GeoStrings import GMLString,  GeoJSONString,  GeoString
    from packages.eo4vistrails.utils.WebRequest import WebRequest
    from core.modules.basic_modules import String
    
    """
    sets everything up called from the top level initialize
    """
    reg = get_module_registry()
    mynamespace = "geoinf"

    #Add QgsMapLayer
    reg.add_module(QgsLayer.QgsMapLayer,
                   namespace=mynamespace)
    reg.add_input_port(QgsLayer.QgsMapLayer, 'file',
                       basic_modules.File)
    reg.add_output_port(QgsLayer.QgsMapLayer, "value", 
                        QgsLayer.QgsMapLayer)

    #Add QgsVectorLayer
    reg.add_module(QgsLayer.QgsVectorLayer,
                   namespace=mynamespace)
                   
    #Add QgsRasterLayer
    reg.add_module(QgsLayer.QgsRasterLayer,
                   namespace=mynamespace)
                   
    reg.add_module(GeoString)
    reg.add_module(GMLString)
    reg.add_module(GeoJSONString)
    #input ports
    reg.add_module(FeatureModel) #abstract

    reg.add_module(MemFeatureModel)
    reg.add_input_port(MemFeatureModel,  "source_file", String )
    #reg.add_input_port(MemFeatureModel,  "output_type", core.modules.basic_modules.String )
    reg.add_input_port(MemFeatureModel,  "dbconn", String )
    reg.add_input_port(MemFeatureModel,  "sql", String )
    reg.add_input_port(MemFeatureModel, "webrequest",  WebRequest)
    #reg.add_input_port(MemFeatureModel,  "uri", core.modules.basic_modules.String )
    #reg.add_input_port(MemFeatureModel,  "uri_data", core.modules.basic_modules.String)
    reg.add_input_port(MemFeatureModel,  "gstring", GeoString )
    reg.add_output_port(MemFeatureModel, "feature_dataset", MemFeatureModel)


    reg.add_module(FileFeatureModel)
    reg.add_input_port(FileFeatureModel,  "source_file", String )
    reg.add_input_port(FileFeatureModel,  "source_feature_dataset", MemFeatureModel )
    reg.add_input_port(FileFeatureModel, "webrequest",  WebRequest)
    reg.add_input_port(FileFeatureModel,  "output_type", String )

    reg.add_module(RasterModel) #abstract


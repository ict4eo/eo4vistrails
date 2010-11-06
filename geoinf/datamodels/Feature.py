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
from core.modules.vistrails_module import Module, ModuleError
import gui.application
try:
    from osgeo import ogr
except:
    import ogr

class FeatureModel(Module):
    
    def __init__(self):
        Module.__init__(self)
        
    
    def compute(self):
        pass
    
def initialize(*args, **keywords):
    '''sets everything up'''
    
    # We'll first create a local alias for the module_registry so that
    # we can refer to it in a shorter way.
    reg = core.modules.module_registry.get_module_registry()
    
    reg.add_module(FeatureModel)
    #input ports
   
    #reg.add_input_port(FeatureModel, "service_version", (core.modules.basic_modules.String, 'Web Map Service version - default 1.1.1'))   
    #output ports
    reg.add_output_port(FeatureModel, "OGRDataset", (ogr.Dataset, 'Feature data in OGR Dataset'))


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
"""This module forms part of the rpyc vistrails capabilties.  It adds multicore
parallel and distributed processing to VisTrails.
"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

def initialize(*args, **keywords):
    """This method is called by higher-level ones,
    to ensure that registration with VisTrails takes place."""
    from core.modules.module_registry import get_module_registry
    from core.modules.python_source_configure import PythonSourceConfigurationWidget
    from core.modules import basic_modules

    import RPyC, RPyCHelper, RPyCTest

    """
    sets everything up called from the top level initialize
    """
    reg = get_module_registry()
    mynamespace = "rpyc"

    #Add RPyCNode
    reg.add_module(RPyCHelper.RpyCNodie,
                   name="RpyC Nodie",
                   namespace=mynamespace,
                   abstract=True)
    #Add RPyCNode
    reg.add_module(RPyCHelper.RPyCNode,
                   name="RpyC Node",
                   namespace=mynamespace)

    #Dummy Module Mixed into all RPYCSafeModules
    reg.add_module(RPyC.RPyCModule,
                   namespace=mynamespace,
                   abstract=True)

    #Add RPyCCode
    reg.add_module(RPyCHelper.RPyCCode,
                   name = "RPyC Code",
                   configureWidgetType=PythonSourceConfigurationWidget,
                   namespace=mynamespace)
    reg.add_input_port(RPyCHelper.RPyCCode, 'source',
                       basic_modules.String)
    reg.add_output_port(RPyCHelper.RPyCCode, 'self',
                        basic_modules.Module)
    reg.add_module(RPyCHelper.RPyC_C_Code,
                   name = "RPyC C Code",
                   configureWidgetType=PythonSourceConfigurationWidget,
                   namespace=mynamespace)

    #Add RPyCTestModule
    reg.add_module(RPyCTest.RPyCTestModule,
                   name="RpyC Test Module",
                   namespace="utils|tests")                   

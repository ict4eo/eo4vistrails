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
    from core.modules.python_source_configure import PythonSourceConfigurationWidget
    from core.modules import basic_modules
   
    import RPyC, RPyCHelper
    
    """
    sets everything up called from the top level initialize
    """
    reg = get_module_registry()
    mynamespace = "rpyc"
    
    #Add RPyCNode
    reg.add_module(RPyC.RPyCNode,
                   namespace=mynamespace)
    reg.add_input_port(RPyC.RPyCNode, 'ip',
                       basic_modules.String)
    reg.add_input_port(RPyC.RPyCNode, 'port',
                       basic_modules.Integer)
    reg.add_output_port(RPyC.RPyCNode, "value", 
                        RPyC.RPyCNode)

    #Add RPyCSession
    reg.add_module(RPyC.RPyCSession,
                   namespace=mynamespace)
    reg.add_input_port(RPyC.RPyCSession, 'rpycnode',
                       (RPyC.RPyCNode, 'an rpyc node'))
    reg.add_output_port(RPyC.RPyCSession, "value",
                        RPyC.RPyCSession)
    
    #Dummy Module Mixed into all RPYCSafeModules
    reg.add_module(RPyC.RPyCModule, 
                   namespace=mynamespace)
    reg.add_input_port(RPyC.RPyCModule, 'rpycsession',
                      (RPyC.RPyCSession, 'A valid RPYC Session, if not given will execute locally'))
    
    #Add RPyCCode
    reg.add_module(RPyCHelper.RPyCCode,
                   configureWidgetType=PythonSourceConfigurationWidget,
                   namespace=mynamespace)
    reg.add_input_port(RPyCHelper.RPyCCode, 'source',
                       basic_modules.String)
    reg.add_output_port(RPyCHelper.RPyCCode, 'self',
                        basic_modules.Module)

    #Add RPyCDiscover
    reg.add_module(RPyCHelper.RPyCDiscover,
                   namespace=mynamespace)
    reg.add_output_port(RPyCHelper.RPyCDiscover, 'rpycslaves',
                       (RPyC.RPyCNode, 'IP Address and Port of RPyC Node'))
    reg.add_output_port(RPyCHelper.RPyCDiscover, 'self',
                        basic_modules.Module)

    #Add RPyCTestModule
    reg.add_module(RPyCHelper.RPyCTestModule,
                   namespace=mynamespace)
    reg.add_input_port(RPyCHelper.RPyCTestModule, 'input',
                       basic_modules.String)

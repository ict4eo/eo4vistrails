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
"""This module acts as dummy placeholder for actual rpyc capabilties.
RPyC package adds multicore parallel and distributed processing to VisTrails.
"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0


def initialize(*args, **keywords):
    """This method is called by higher-level ones,
    to ensure that registration with VisTrails takes place."""
    from core.modules.module_registry import get_module_registry
    import core.requirements
    from core.modules.python_source_configure import \
        PythonSourceConfigurationWidget
    from core.modules import basic_modules

    import RPyC
    reg = get_module_registry()
    rpyc_namespace = "rpyc"

    manager = core.packagemanager.get_package_manager()
    if manager.has_package('za.co.csir.rpyc4vistrails'):
        #Dummy Module Mixed into all RPYCSafeModules
        #reg.add_module(RPyC.RPyCModule,
        #               namespace=rpyc_namespace,
        #               abstract=True)
        pass
    else:
        #Generic Module
        reg.add_module(RPyC.RPyCModule,
                       namespace=rpyc_namespace,
                       abstract=True)

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
    from core.vistrail.port import PortEndPoint
    import PySAL

    from packages.NumSciPy.Array import NDArray

    reg = get_module_registry()
    mynamespace = "pysal"

    #Add PySAL
    reg.add_module(PySAL.W,
                   namespace=mynamespace)
    reg.add_input_port(PySAL.W, 'neighbors',
                       basic_modules.Dictionary)
    reg.add_input_port(PySAL.W, 'weights',
                       basic_modules.Dictionary)
    reg.add_output_port(PySAL.W, "value",
                        (PySAL.W, 'value'))

    import Networkx
    mynamespace = "networkx"

     #Add Networkx
    reg.add_module(Networkx.Graph,
                   namespace=mynamespace)
    reg.add_input_port(Networkx.Graph, 'neighbors',
                       NDArray)
    reg.add_output_port(Networkx.Graph, "value",
                        (Networkx.Graph, 'value'))

    reg.add_module(Networkx.connected_components,
                   namespace=mynamespace)
    reg.add_input_port(Networkx.connected_components, 'graph',
                       Networkx.Graph)
    reg.add_output_port(Networkx.connected_components, "value",
                        (basic_modules.List, 'value'))

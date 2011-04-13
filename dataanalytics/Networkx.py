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
"""This module forms part of the rpyc eo4vistrails capabilties;
used to add multicore parallel and distributed processing to vistrails.

This module holds a rpycnode type that can be passed around between modules.
"""

import networkx as nx
from core.modules.vistrails_module import Module

from packages.eo4vistrails.rpyc.RPyC import RPyCModule, RPyCSafeModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin


class NetworkxModule(ThreadSafeMixin):
    def __init__(self):
        ThreadSafeMixin.__init__(self)

@RPyCSafeModule()
class Graph(NetworkxModule, RPyCModule, nx.Graph):
    """ Represents a network Graph  """

    _input_ports  = [('neighbors', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('value', '(za.co.csir.eo4vistrails:Graph:networkx)')]

    def __init__(self):
        RPyCModule.__init__(self)
        NetworkxModule.__init__(self)
        nx.Graph.__init__(self)

    def compute(self):
        neighbors = self.getInputFromPort('neighbors')
        self.add_edges_from(neighbors)
        #self.add_edges_from(ndArray.get_array())
        self.setResult("value", self)

@RPyCSafeModule()
class connected_components(NetworkxModule, RPyCModule):
    """ Container class for the pysal.W class """

    _input_ports  = [('graph', '(za.co.csir.eo4vistrails:Graph:networkx)')]
    _output_ports = [('value', '(edu.utah.sci.vistrails.basic:List)')]

    def __init__(self):
        RPyCModule.__init__(self)
        NetworkxModule.__init__(self)

    def compute(self):
        self._graph = self.getInputFromPort('graph')
        self.setResult("value", nx.connected_components(self._graph))

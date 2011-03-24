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


class NetworkxModule(object):
    pass


class Graph(NetworkxModule, Module, nx.Graph):
    """ Container class for the pysal.W class """
    def __init__(self):
        Module.__init__(self)
        nx.Graph.__init__(self)

    def compute(self):
        self.add_edges_from(self.forceGetInputFromPort('neighbors'))
        self.setResult("value", self)


class connected_components(NetworkxModule, Module):
    """ Container class for the pysal.W class """
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        self._graph = self.forceGetInputFromPort('graph')
        self.setResult("value", nx.connected_components(self._graph))

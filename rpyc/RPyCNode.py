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

This Module hold a rpycnode type that can be past around between modules

"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

from core.modules.vistrails_module import Module

class RPyCNodeModule(object):
    pass

class RPyCNode(Module, RPyCNodeModule):
    """ Container class for the numpy.ndarray class """
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        self.ip = self.forceGetInputFromPort('ip')
        self.port = self.forceGetInputFromPort('port', 18812)
        self.setResult("value", self)
        
    def get_ip(self):
        return self.ip
    
    def set_ip(self, ip):
        self.ip = ip
    
    def get_port(self):
        return self.port
    
    def set_port(self, port):
        self.port = port
    
class RPyCModule(Module):
    pass
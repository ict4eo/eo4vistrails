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

This Module holds code to help test the rpyc functioning in vistrails

"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

from core.modules.vistrails_module import NotCacheable
from multiprocessing import current_process
from time import ctime, sleep
from RPyC import RPyCSafeModule
from RPyCNode import RPyCModule

@RPyCSafeModule([])
class RPyCTestModule(NotCacheable, RPyCModule):
    """This Test Module is to check that ThreadSafe is working and also provides
    a template for others to use ThreadSafe"""
    
    def compute(self):
        print self.__class__.__bases__
        print "Hello ", self.getInputFromPort("input")
        print self.getInputConnector("input")
        print ctime()," ", current_process(), " Started RPyCSafe Module, Waiting 2 Seconds"
        sleep(2)
        print ctime()," ", current_process(), " Stoped RPyCSafe Module"


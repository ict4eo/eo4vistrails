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
# -*- coding: utf-8 -*-
"""TODO  Add documentation to this module.
"""
#Created on Thu Aug 25 09:46:42 2011 @author: tvzyl

from core.modules.vistrails_module import Module, NotCacheable
from time import time

class Timer(NotCacheable, Module):
    """ Container class for the random class """

    _input_ports = [('start flow', '(edu.utah.sci.vistrails.basic:Module)')]

    _output_ports = [('total time', '(edu.utah.sci.vistrails.basic:Float)')                     ]

    def __init__(self):
        Module.__init__(self)
        self.start_time = 0

    def update(self):
        self.start_time  = time()
        Module.update(self)

    def compute(self):
        end_time = time()
        self.setResult("total time", end_time - self.start_time)


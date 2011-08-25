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
"""
Created on Thu Aug 25 09:46:42 2011

@author: tvzyl
"""

"""TODO  Add documentation to this module.
"""

from core.modules.vistrails_module import Module, ModuleError

import random

class Command(Module):
    """ Container class for the random class """
    
    _input_ports = [('command', '(edu.utah.sci.vistrails.basic:String)'),
                    ('input file path', '(edu.utah.sci.vistrails.basic:String)'),
                    ('output file path', '(edu.utah.sci.vistrails.basic:String)')
                   ]

    _output_ports = [('output file path', '(edu.utah.sci.vistrails.basic:String)')
                    ]
                    
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        command = self.getInputFromPort('command')
        i_name = self.forceGetInputFromPort('input file path', None)
        o_name = self.forceGetInputFromPort('output file path', None)
        
        from subprocess import call
        call(command%{"i": i_name, "o": o_name},shell=True)

        self.setResult('output file path', o_name )
             

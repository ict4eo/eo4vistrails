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
"""This module holds a rpycnode type that can be passed around between modules.
"""
#History
#Created by Terence van Zyl

from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule, RPyCModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from packages.eo4vistrails.utils.synhigh import SyntaxSourceConfigurationWidget

from core.modules.vistrails_module import ModuleError, NotCacheable, Module
from core.modules.basic_modules import File


from subprocess import call
from tempfile import mkstemp
from os import fdopen, remove
import urllib

@RPyCSafeModule()
class OctaveScript(ThreadSafeMixin, RPyCModule):
    """
       Executes a PovRay Script and returns a link to a temp file which is the output
    """
    _input_ports = [('+W', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('+H', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('+A', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('+L', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('source', '(edu.utah.sci.vistrails.basic:String)')
                   ]

    _output_ports = [('+O', '(edu.utah.sci.vistrails.basic:File)'),
                     ('self', '(edu.utah.sci.vistrails.basic:Module)')
                    ]

    def __init__(self):
        Module.__init__(self)
        ThreadSafeMixin.__init__(self)

    def compute(self):
        """Will need to fetch a PostGisSession object on its input port
        Overrides supers method"""
        W = self.getInputFromPort('+W')
        H = self.getInputFromPort('+H')
        A = self.getInputFromPort('+A')
        L = self.getInputFromPort('+L').name
        
        povray_script = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        
        #Get a temp file to write the script into
        povFileDescript, povFileName = mkstemp(suffix='.pov',text=True)
        #Write the script to the file
        povFile = fdopen(povFileDescript, 'w')
        povFile.write(povray_script)
        povFile.close()

        #Get a temp file to write the output into
        povFileDescript, O = mkstemp(suffix='.png')
        
        #Execute the command
        args = ["povray", "+I%s"%povFileName, "+W%s"%W, "+H%s"%H, "+A%s"%A, "+L%s"%L,"+O%s"%O, "-D"]
        a = call(args)
        remove(povFileName)
        
        if a == 0:
            f = File()
            f.set_results(O)
            self.setResult('+O', f)
        else:
            raise ModuleError, (OctaveScript, "Could not execute PovRay Script")

class OctaveSourceConfigurationWidget(SyntaxSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SyntaxSourceConfigurationWidget.__init__(self, module, controller, 
                                                 "Octave", parent)

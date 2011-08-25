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

class PovRayConfig(Module):
    """
       Executes a PovRay Script and returns a link to a temp file which is the output
    """
    _input_ports = [('+W', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('+H', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('+A', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('+AM', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('+R', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('+J', '(edu.utah.sci.vistrails.basic:Float)'),
                    ('+L', '(edu.utah.sci.vistrails.basic:Directory)'),
                    ('+F', '(edu.utah.sci.vistrails.basic:String)')
                   ]

    _output_ports = [('PovRay Args string', '(edu.utah.sci.vistrails.basic:String)'),
                     ('self', '(edu.utah.sci.vistrails.basic:Module)')
                    ]

    formatExtLookup = {'C':'.tga','N':'.png','P':'.ppm','S':'.bmp','T':'.tga'}

    def __init__(self):
        Module.__init__(self)

    def compute(self):
        """Will need to fetch a PostGisSession object on its input port
        Overrides supers method"""
        W = self.getInputFromPort('+W')
        H = self.getInputFromPort('+H')
        A = self.getInputFromPort('+A')
        AM = self.getInputFromPort('+AM')
        R = self.getInputFromPort('+R')
        J = self.getInputFromPort('+J')
        L = self.getInputFromPort('+L').name
        F = self.forceGetInputFromPort('+F','N')
        
        #Execute the command
        args = "+W%s +H%s +A%s +L%s +F%s +AM%s +R%s +J%s"%(W, H, A, L, F, AM, R, J)
        print args
        
        self.setResult('PovRay Args string', args)


@RPyCSafeModule()
class PovRayScript(ThreadSafeMixin, RPyCModule):
    """
       Executes a PovRay Script and returns a link to a temp file which is the output
    """
    _input_ports = [('PovRay Args string', '(edu.utah.sci.vistrails.basic:String)'),
                    ('source', '(edu.utah.sci.vistrails.basic:String)'),
                    ('Output Directory', '(edu.utah.sci.vistrails.basic:Directory)')
                   ]

    _output_ports = [('+O', '(edu.utah.sci.vistrails.basic:File)'),
                     ('%s', '(edu.utah.sci.vistrails.basic:String)'),
                     ('self', '(edu.utah.sci.vistrails.basic:Module)')
                    ]

    formatExtLookup = {'C':'.tga','N':'.png','P':'.ppm','S':'.bmp','T':'.tga'}

    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)

    def compute(self):
        """Will need to fetch a PostGisSession object on its input port
        Overrides supers method"""
        args = self.forceGetInputFromPort('PovRay Args string','')
        directory = self.forceGetInputFromPort('Directory', None)
        
        povray_script = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        
        #Get a temp file to write the script into
        povFileName = self.interpreter.filePool.create_file(suffix='.pov')
        #Write the script to the file
        povFile = open(povFileName.name, 'a+')
        povFile.write(povray_script)
        povFile.close()

        #Get a temp file to write the script into
        iniFileName = self.interpreter.filePool.create_file(suffix='.ini')
        #Write the script to the file
        iniFile = open(iniFileName.name, 'w+')
        for inputPort in self.inputPorts:
            portFound = False
            for _inputPort in self._input_ports:
                if inputPort == _inputPort[0]:
                    portFound = True          
            if not portFound:
                val = self.forceGetInputFromPort(inputPort, None)
                if val:
                    iniFile.write('Declare=%s=%s\n'%(inputPort,val))
        iniFile.close()

        #Get a temp file to write the output into
        start = args.find('+F')
        if start >= 0:
            #move to the end of the +F
            start = start + 2
            end = args.find(' ', start)
            if end < start:
                F  = args[start:]
            else:
                F = args[start:end]
        else:
            #no format given use defaults
            F = 'N'
        
        if directory:
            povFileDescript, O = mkstemp(suffix=self.formatExtLookup[F], dir=directory)
        else:
            povFileDescript, O = mkstemp(suffix=self.formatExtLookup[F])
        
        #Execute the command
        args = "povray %s +I%s %s +O%s -D"%(iniFileName.name, povFileName.name, args, O)
        print args
        a = call(args, shell=True)
        
        #check if the file exists that should indicate sucsess
        if a == 0:            
            f = File()
            f.set_results(O)
            self.setResult('+O', f)
        else:
            raise ModuleError, (PovRayScript, "Could not execute PovRay Script")

class PovRaySourceConfigurationWidget(SyntaxSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        
        SyntaxSourceConfigurationWidget.__init__(self, module, controller, "PovRay", 
                                                 parent=parent, has_outputs=False)

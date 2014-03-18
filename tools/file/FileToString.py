# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
############################################################################
###
### Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
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
"""This module forms part of the eo4vistrails capabilities. It is used to
handle writing of a string to a file.
"""
# library
import os
import os.path
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from vistrails.packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from vistrails.packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin


@RPyCSafeModule()
class FileToString(ThreadSafeMixin, Module):
    """Accept a filer and reads it to a string.
    
    Input ports:
    
        file:
            the output file created from the string
    
    Output ports:
    
         string: string
            a standard VisTrails (Python) string
    """

    _output_ports = [('string', '(edu.utah.sci.vistrails.basic:String)'),]
    _input_ports = [('file', '(edu.utah.sci.vistrails.basic:File)'),]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error with traceback display."""
        import traceback
        traceback.print_exc()
        if error:
            raise ModuleError(self, msg + ' - %s' % str(error))
        else:
            raise ModuleError(self, msg)

    def compute(self):
        try:
            _file = self.forceGetInputFromPort('file', None)
            _filename = _file.name
            
            out_string = None
            with open(_filename, 'r') as text_file:
                out_string = text_file.read()
            
            self.setResult('string', out_string)
            
        except Exception, ex:
            self.raiseError(ex)

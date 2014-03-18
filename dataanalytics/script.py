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
"""This module ???
"""
# library
from tempfile import mkstemp
from os import fdopen
# third-party
# vistrails
# eo4vistrails
from vistrails.packages.eo4vistrails.rpyc.RPyC import RPyCModule
from vistrails.packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin


class Script(ThreadSafeMixin, RPyCModule):
    """
       Executes a script
       Writes output to output files and reads input from input files
    """
    _input_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)

    def write_script_to_file(self, script, preScript=None, postScript=None,
                             suffix='.e4v'):
        #Get a temp file to write the script into
        self.scriptFileDescript, self.scriptFileName = mkstemp(suffix=suffix,
                                                               text=True)
        #Write the script to the file
        scriptFile = fdopen(self.scriptFileDescript, 'w')
        if preScript:
            scriptFile.write(preScript)
            scriptFile.write("\n")
        scriptFile.write(script)
        if postScript:
            scriptFile.write("\n")
            scriptFile.write(postScript)
        scriptFile.close()

    def compute(self):
        pass

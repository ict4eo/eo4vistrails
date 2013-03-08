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
"""This module forms part of the eo4vistrails capabilities. It is used to
handle directory related queries.
"""
# library
import os
import os.path
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin


@RPyCSafeModule()
class ListDirContent(ThreadSafeMixin, Module):
    """A utility for walking a directory to discover files with specified
    extensions.
    
    Input ports:
    
        directory path:
            place in which files are to be discovered
        file_extensions:
            a list of types of files to be discovered
    
    Output ports:
    
        csv_list:
            A list of full filenames. On RPyC nodes, will refer to files on
            that remote filesystem.
    """

    _input_ports = [('directorypath', '(edu.utah.sci.vistrails.basic:String)'),
                    ('file_extensions', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('file_list', '(edu.utah.sci.vistrails.basic:List)')]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def compute(self):
        filename_list = []
        dp = self.getInputFromPort('directorypath')
        fel = self.getInputFromPort('file_extensions')

        def _index(directory):
            #stack = [directory]
            files = []
            #while stack:
                #directory = stack.pop()
            for filename in os.listdir(directory):
                fullname = os.path.join(directory, filename)
                files.append(fullname)
                    #if os.path.isdir(fullname) and not os.path.islink(fullname):
                    #    stack.append(fullname)
            return files

        for fname in _index(dp):
            try:
                if fname.split(".")[-1] in fel:
                    filename_list.append(fname)
            except:
                #likely a directory, ignore
                pass

        self.setResult('file_list', filename_list)

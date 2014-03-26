# -*- coding: utf-8 -*-
############################################################################
##
## Copyright (C) 2012 CSIR Meraka Institute. All rights reserved.
##
## This full package extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the abilty to run code transparently in
## OpenNebula cloud environments. There are various software
## dependencies, but all are FOSS.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""This module forms part of the eo4vistrails capabilities. It is used to
handle writing of a string to a file.
"""
# library
import codecs
import os
import os.path
# vistrails
from core.modules.vistrails_module import Module, ModuleError
# eo4vistrails
from vistrails.packages.eo4vistrails.rpyc.RPyC import RPyCSafeModule
from vistrails.packages.eo4vistrails.tools.utils.ThreadSafe import ThreadSafeMixin


@RPyCSafeModule()
class StringToFile(ThreadSafeMixin, Module):
    """Accept a string and write it to a UTF-8 encoded text file.
    
    Input ports:
    
        string: string
            a standard VisTrails (Python) string
        filename: string
            the name of the output file being created
        chars: integer
            an optional filter (defaults to "0") that slices the first N chars
            from the string (if negative, slices the last N chars)
        overwrite: boolean
            if not True (default), then existing file will not be overwritten
        append: boolean
            if True (default), then existing file will be appended to
            (if overwrite is True, this setting will be ignored)
    
    Output ports:
    
        file:
            the output file created from the string
            
    Notes:
        
        If string is None, then no output will be written; otherwise an 
        error will be raised.
    """

    _input_ports = [('string', '(edu.utah.sci.vistrails.basic:String)'),
                    ('filename', '(edu.utah.sci.vistrails.basic:String)'),
                    ('chars', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('overwrite', '(edu.utah.sci.vistrails.basic:Boolean)'),
                    ('append', '(edu.utah.sci.vistrails.basic:Boolean)')]
    _output_ports = [('file', '(edu.utah.sci.vistrails.basic:File)'),]

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)

    def raiseError(self, msg, error=''):
        """Raise a VisTrails error with traceback display."""
        import traceback
        traceback.print_exc()
        if error:
            try:
                raise ModuleError(self, str(msg) + ': %s' % error)
            except:
                print msg, error
                raise ModuleError(self, 'Unable to show error: please check console!')
        else:
            raise ModuleError(self, str(msg))

    def compute(self):
        _string = self.forceGetInputFromPort('string', None)
        _filename = self.getInputFromPort('filename')
        _chars = self.forceGetInputFromPort('chars', 0)
        _overwrite = self.forceGetInputFromPort('overwrite', True)
        _append = self.forceGetInputFromPort('append', True)

        if _chars and _string and abs(_chars) < len(_string):
            if _chars > 0:
                # items from the beginning through chars-1
                _string = _string[:_chars]
            else:
                # last chars in the string (default is all if 0 chars)
                _string = _string[_chars:]

        try:
            if not _overwrite and os.path.isfile(_filename) and not _append:
                self.raiseError('File already exists')
            if _append and not _overwrite and os.path.isfile(_filename):
                text_file = codecs.open(_filename, 'a', 'utf-8')
            else:
                text_file = codecs.open(_filename, 'w', 'utf-8')
            try:
                if _string:
                    text_file.write(_string)
            except TypeError, e:
                self.raiseError("Unable to write to file", e)
            text_file.close()

        except Exception, ex:
            self.raiseError(ex)

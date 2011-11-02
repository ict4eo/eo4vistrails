# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 12:00:49 2011

@author: tvzyl
"""
from packages.eo4vistrails.rpyc.RPyC import RPyCModule
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin

from tempfile import mkstemp
from os import fdopen

class Script(ThreadSafeMixin, RPyCModule):
    """
       Executes a Octave Script 
       Writes output to output files and reads input from inout files
    """
    _input_ports = [('source', '(edu.utah.sci.vistrails.basic:String)')]

    def __init__(self):
        RPyCModule.__init__(self)
        ThreadSafeMixin.__init__(self)

    def write_script_to_file(self, script, preScript=None, postScript=None, suffix='.e4v'):
        #Get a temp file to write the script into
        self.scriptFileDescript, self.scriptFileName = mkstemp(suffix=suffix, text=True)
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
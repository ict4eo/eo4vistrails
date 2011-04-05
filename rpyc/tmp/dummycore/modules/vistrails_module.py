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

Complete dummy insatnce of vistrails module

"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

class IncompleteImplementation(Exception):
    def __str__(self):
        return "Module has incomplete implementation"

class MissingModule(Exception):
    pass

class ModuleBreakpoint(Exception):
    def __init__(self, module):
        self.module = module
        self.msg = "Hit breakpoint"

    def __str__(self):
        retstr = "Encoutered breakpoint at Module %s:\n" % (self.module)
        for k in self.module.__dict__.keys():
            retstr += "\t%s = %s\n" % (k, self.module.__dict__[k])

        inputs = self.examine_inputs()
        retstr += "\nModule has inputs:\n"
        
        for i in inputs.keys():
            retstr += "\t%s = %s\n" % (i, inputs[i])

        return retstr

    def examine_inputs(self):
        in_ports = self.module.__dict__["inputPorts"]
        inputs = {}
        for p in in_ports:
            inputs[p] = self.module.getInputListFromPort(p)

        return inputs
        
class ModuleError(Exception):
    """Exception representing a VisTrails module runtime error. This
exception is recognized by the interpreter and allows meaningful error
reporting to the user and to the logging mechanism."""
    
    def __init__(self, module, errormsg):
        """ModuleError should be passed the module that signaled the
error and the error message as a string."""
        Exception.__init__(self, errormsg)
        self.module = module
        self.msg = errormsg

class ModuleErrors(Exception):
    """Exception representing a list of VisTrails module runtime errors.
    This exception is recognized by the interpreter and allows meaningful
    error reporting to the user and to the logging mechanism."""
    def __init__(self, module_errors):
        """ModuleErrors should be passed a list of ModuleError objects"""
        Exception.__init__(self, str(tuple(me.msg for me in module_errors)))
        self.module_errors = module_errors

class _InvalidOutput(object):
    """ Specify an invalid result
    """
    pass

InvalidOutput = _InvalidOutput

class Module(object):
    def __init__(self): pass
    def clear(self): pass
    def is_cacheable(self): pass
    def updateUpstreamPort(self, port): pass
    def updateUpstream(self): pass
    def update(self): pass
    def checkInputPort(self, name): pass
    def compute(self): pass
    def setResult(self, port, value): pass
    def get_output(self, port): pass
    def getInputConnector(self, inputPort): pass
    def getInputFromPort(self, inputPort): pass
    def hasInputFromPort(self, inputPort): pass
    def __str__(self): pass
    def annotate(self, d): pass
    def forceGetInputFromPort(self, inputPort, defaultValue=None): pass
    def set_input_port(self, inputPort, conn, is_method=False): pass
    def getInputListFromPort(self, inputPort): pass
    def forceGetInputListFromPort(self, inputPort): pass
    def enableOutputPort(self, outputPort): pass
    def removeInputConnector(self, inputPort, connector): pass
    def create_instance_of_type(self, ident, name, ns=''): pass
    @classmethod
    def provide_input_port_documentation(cls, port_name): pass
    @classmethod
    def provide_output_port_documentation(cls, port_name): pass

################################################################################

class NotCacheable(object):
    def is_cacheable(self):
        return False

################################################################################

class ModuleConnector(object):
    def __init__(self, obj, port, spec=None):
        self.obj = obj
        self.port = port

    def clear(self):
        """clear() -> None. Removes references, prepares for deletion."""
        self.obj = None
        self.port = None
    
    def __call__(self):
        return self.obj.get_output(self.port)
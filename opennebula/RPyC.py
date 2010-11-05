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
#"""This full package extends VisTrails, providing GIS/Earth Observation 
#ingestion, pre-processing, transformation, analytic and visualisation 
#capabilities . Included is the abilty to run code transparently in 
#OpenNebula cloud environments.
#"""

import core.modules.module_registry
import core.cache.hasher
from core.modules import module_configure
from core.modules.module_registry import get_module_registry
from core.modules import port_configure
from core.modules import vistrails_module
from core.modules.vistrails_module import Module, new_module, NotCacheable, ModuleError
from core.modules.python_source_configure import PythonSourceConfigurationWidget
from core.modules.tuple_configuration import TupleConfigurationWidget, \
    UntupleConfigurationWidget
from core.modules.constant_configuration import StandardConstantWidget, \
    PathChooserWidget, FileChooserWidget, DirectoryChooserWidget, ColorWidget, \
    ColorChooserButton, BooleanWidget
from core.system import vistrails_version
from core.utils import InstanceObject
from core.modules.paramexplore import make_interpolator, \
     QFloatLineEdit, QIntegerLineEdit, FloatLinearInterpolator, \
     IntegerLinearInterpolator
from PyQt4 import QtGui

import core.system
from itertools import izip
import os
import os.path
try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new
import zipfile
import urllib
import sys

class OneAbstract(NotCacheable, Module):
    def __init__(self):
        Module.__init__(self)
    
    def runcmd(self, operation):
        import paramiko   
        client = paramiko.SSHClient()
        client.load_system_host_keys()  
        self.username = self.getInputFromPort("username")
        self.password = self.getInputFromPort("password")
        self.server = self.getInputFromPort("server")
        client.connect(self.server,username=self.username,password=self.password)        
        i,o,e = client.exec_command(operation)
        self.setResult("stdout", o.readlines())
        self.setResult("stderr", e.readlines())

    def compute(self):
        return

class OneCmd(OneAbstract):
    # This constructor is strictly unnecessary. However, some modules
    # might want to initialize per-object data. When implementing your
    # own constructor, remember that it must not take any extra
    # parameters.
    def __init__(self):
        OneAbstract.__init__(self)
        
    def compute(self):
        operation = self.getInputFromPort("operation")
        self.runcmd(operation)

class OneVM_List(OneAbstract):
    def __init__(self):
        OneAbstract.__init__(self)
    
    def compute(self):
        self.runcmd("source .one-env; onevm list")
        for i in t:
            if i.find('missr')>=0:
                int(i[0:i.find('missr')])
        
        

###############################################################################
# RPyC
#
# A VisTrails name, globals, locals, fromlist, level))
# Module.  For this class to be executable, it must define a method
# compute(self) that will perform the appropriate computations and set
# the results.
#
# Extra helper methods can be defined, as usual. In this case, we're
# using a helper method op(self, v1, v2) that performs the right
# operations.
class RPyCDiscover(NotCacheable, Module):
    """RPyCDiscover is a Module that allow onbe to discover RPyC
    servers
    """
    # This constructor is strictly unnecessary. However, some modules
    # might want to initialize per-object data. When implementing your
    # own constructor, remember that it must not take any extra
    # parameters.
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        import rpyc
        self.setResult("RPyCSlaves", rpyc.discover("slave"))


class RPyC(NotCacheable, Module):
    """RPyC is a Module that executes an arbitrary piece of
    Python code remotely.

    TODO: If you want a PythonSource execution to fail, call
    fail(error_message).

    TODO: If you want a PythonSource execution to be cached, call
    cache_this().
    """

    # This constructor is strictly unnecessary. However, some modules
    # might want to initialize per-object data. When implementing your
    # own constructor, remember that it must not take any extra
    # parameters.
    def __init__(self):
        Module.__init__(self)


    def run_code(self, code_str,
                 use_input=False,
                 use_output=False):
        """run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution."""
        import core.packagemanager
        import rpyc
        def fail(msg):
            raise ModuleError(self, msg)
        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True
        
        conn = rpyc.classic.connect(self.getInputFromPort('rPyCServer'))

        if use_input:
            inputDict = dict([(k, self.getInputFromPort(k))
                              for k in self.inputPorts])
            conn.namespace.update(inputDict)
            
        if use_output:
            outputDict = dict([(k, None)
                               for k in self.outputPorts])
            conn.namespace.update(outputDict)

        _m = core.packagemanager.get_package_manager()
        reg = get_module_registry()
        conn.namespace.update({'fail': fail,
                        'package_manager': _m,
                        'cache_this': cache_this,
                        'registry': reg,
                        'self': self})
        del conn.namespace['source']

        conn.modules.sys.stdout = sys.stdout
        
        conn.execute(code_str)
        #exec code_str in locals_, locals_
        
        if use_output:
            for k in outputDict.iterkeys():
                if conn.namespace[k] != None:
                    self.setResult(k, conn.namespace[k])

    def compute(self):
        s = core.modules.basic_modules.urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        self.run_code(s, use_input=True, use_output=True)



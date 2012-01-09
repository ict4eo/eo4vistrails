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
"""This module holds some helper classes to make working with rpyc easier.
It also has the rpyc remote code that is used for ???.
"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0

# library
# third-party
import rpyc
from RPyC import RPyCSafeMixin, RPyCModule
# vistrails
from core.modules import basic_modules
from core.modules.vistrails_module import ModuleError, NotCacheable
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
# eo4vistrails
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget
from packages.eo4vistrails.utils.ModuleHelperMixin import ModuleHelperMixin
# local


class RPyCCode(NotCacheable, RPyCSafeMixin, ThreadSafeMixin, RPyCModule,
               ModuleHelperMixin):
    """
    This module that executes an arbitrary piece of Python code remotely.
    TODO: This code is not threadsafe. Terence needs to fix it
    """
    #TODO: If you want a PythonSource execution to fail, call fail(error_message).
    #TODO: If you want a PythonSource execution to be cached, call cache_this().

    def __init__(self):
        self._requiredVisPackages = ["packages.eo4vistrails", "packages.spreadsheet"]
        ThreadSafeMixin.__init__(self)
        RPyCModule.__init__(self)
        self.preCodeString = None
        self.postCodeString = None

    def run_code_common(self, locals_, execute, code_str, use_input, use_output,
                        pre_code_string, post_code_string):
        """TODO: Add docstring.
        """
        import core.packagemanager

        def fail(msg):
            raise ModuleError(self, msg)

        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True

        if use_input:
            inputDict = None
            self.setInputResults(locals_, inputDict)

        outputDict = None
        if use_output:
            outputDict = dict([(k, None) for k in self.outputPorts])
            del outputDict['self']
            locals_.update(outputDict)

        _m = core.packagemanager.get_package_manager()
        from core.modules.module_registry import get_module_registry
        reg = get_module_registry()
        locals_.update({'fail': fail,
                        'package_manager': _m,
                        'cache_this': cache_this,
                        'registry': reg,
                        'self': self})

        if pre_code_string:
            execute(pre_code_string)
        execute(code_str)
        if post_code_string:
            execute(post_code_string)

        if use_output:
            self.setOutputResults(locals_, outputDict)

    def setInputResults(self, locals_, inputDict):
        """TODO: Add docstring.
        """
        from packages.NumSciPy.Array import NDArray

        inputDict = dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])
        del inputDict['source']
        if 'rpycnode' in inputDict:
            del inputDict['rpycnode']

        #check that if any are NDArrays we get the numpy array out
        for k in inputDict.iterkeys():
            if isinstance(inputDict[k], NDArray):
                inputDict[k] = inputDict[k].get_array()
        locals_.update(inputDict)

    def setOutputResults(self, locals_, outputDict):
        """TODO: Add docstring.
        """
        from packages.NumSciPy.Array import NDArray

        for k in outputDict.iterkeys():
            try:
                if k in locals_ and locals_[k] != None:
                    if isinstance(self.getPortType(k), NDArray):
                        outArray = NDArray()
                        outArray.set_array(locals_[k])
                        self.setResult(k, outArray)
                    else:
                        self.setResult(k, locals_[k])
            except AttributeError:
                self.setResult(k, locals_[k])

    def run_code_orig(self, code_str, use_input, use_output, pre_code_string, post_code_string):
        """Runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution."""

        locals_ = locals()

        def execute(s):
            exec s in locals_

        print "Starting executing in main thread"
        self.run_code_common(locals_, execute, code_str, use_input, use_output,
                             pre_code_string, post_code_string)
        print "Finished executing in main thread"

    def run_code(self, code_str, conn, use_input, use_output, pre_code_string,
                 post_code_string):
        """
        Runs a piece of code as a VisTrails module.

        Use_input and use_output control whether to use the input port
        and output port dictionary as local variables inside the execution.
        """
        #import sys
        #conn.modules.sys.stdout = sys.stdout

        print "Starting executing in other thread"
        self.run_code_common(conn.namespace, conn.execute, code_str, use_input,
                             use_output, pre_code_string, post_code_string)
        print "Finished executing in other thread"

    def compute(self):
        """
        Vistrails Module Compute, Entry Point Refer, to Vistrails Docs
        """
        self.sharedPorts = {}
        isRemote, self.conn, v = self.getConnection()

#        if self.hasInputFromPort('rpycnode'):
#            (isRemote, self.conn) = self.inputPorts['rpycnode'][0].obj.getSharedConnection()

        from core.modules import basic_modules
        s = basic_modules.urllib.unquote(str(self.forceGetInputFromPort('source', '')))

        if s == '':
            return

        if self.conn:
            self.run_code(s, self.conn, True, True, self.preCodeString, self.postCodeString)
        else:
            self.run_code_orig(s, True, True, self.preCodeString, self.postCodeString)


class RPyC_C_Code(RPyCCode):
    """TODO: Add docstring.
    """

    def run_code_orig(self, code_str, use_input=False, use_output=False):
        """Runs a piece of code as a VisTrails module.

        Use_input and use_output control whether to use the input port
        and output port dictionary as local variables inside the execution."""
        import core.packagemanager

        def fail(msg):
            raise ModuleError(self, msg)

        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True

        locals_ = locals()
        if use_input:
            inputDict = dict([(k, self.getInputFromPort(k))
                              for k in self.inputPorts])
            locals_.update(inputDict)
        if use_output:
            outputDict = dict([(k, None)
                               for k in self.outputPorts])
            locals_.update(outputDict)
        _m = core.packagemanager.get_package_manager()
        from core.modules.module_registry import get_module_registry
        reg = get_module_registry()
        locals_.update({'fail': fail,
                        'package_manager': _m,
                        'cache_this': cache_this,
                        'registry': reg,
                        'self': self})

        print "Starting executing in main thread"

        from scipy.weave import inline
        from scipy.weave.converters import blitz
        try:
            del inputDict['source']
        except:
            pass
        try:
            del inputDict['rpycnode']
        except:
            pass
        try:
            del outputDict['self']
        except:
            pass

        keys = inputDict.keys() + outputDict.keys()

        err = inline(code_str, keys, type_converters=blitz, compiler='gcc')
        print err
        #exec code_str in locals_, locals_
        if use_output:
            for k in outputDict.iterkeys():
                if locals_[k] != None:
                    self.setResult(k, locals_[k])
        print "Finished executing in main thread"

    def run_code(self, code_str, conn, use_input=False, use_output=False):
        """
        Runs a piece of code as a VisTrails module.

        Use_input and use_output control whether to use the input port
        and output port dictionary as local variables inside the execution.
        """
        if code_str == '':
            return

        def fail(msg):
            raise ModuleError(self, msg)

        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True

        #TODO: changed to demo that this is in the cloud!!!!
        #import sys
        #conn.modules.sys.stdout = sys.stdout

        if use_input:
            inputDict = dict([(k, self.getInputFromPort(k)) for k in self.inputPorts])
            conn.namespace.update(inputDict)

        if use_output:
            outputDict = dict([(k, self.get_output(k)) for k in self.outputPorts])
            conn.namespace.update(outputDict)

        from core import packagemanager
        _m = packagemanager.get_package_manager()
        from core.modules.module_registry import get_module_registry
        reg = get_module_registry()
        conn.namespace.update({'fail': fail,
                               'package_manager': _m,
                               'cache_this': cache_this,
                               'registry': reg,
                               'self': self})

        #del conn.namespace['source']

        try:
            del inputDict['source']
        except:
            pass
        try:
            del inputDict['rpycnode']
        except:
            pass
        try:
            del outputDict['self']
        except:
            pass

        conn.execute("from scipy.weave import inline")
        conn.execute("from scipy.weave.converters import blitz")

        conn.namespace["code_str"] = code_str

        keys = inputDict.keys() + outputDict.keys()
        conn.namespace["keys"] = keys

        err = conn.eval("inline(code_str, keys, type_converters=blitz, compiler='gcc')")
        #err = inline(code_str, keys, type_converters=blitz, compiler = 'gcc')
        print err
        #conn.execute(code_str)

        if use_output:
            for k in outputDict.iterkeys():
                try:
                    if conn.namespace[k] != None:
                        self.setResult(k, conn.namespace[k])
                except AttributeError:
                    self.setResult(k, conn.namespace[k])


class RPyCNodeWidget(ComboBoxWidget):
    """TODO: Add docstring
    """

    discoveredSlaves = None
    default = ('main', 0)

    def getKeyValues(self):
        if not self.discoveredSlaves:
            self.discoveredSlaves = {
                'Own Process': ('own', 0), 'Main Process': ('main', 0)}
            try:
                discoveredSlavesTuple = list(rpyc.discover("slave"))
                for slaveTuple in discoveredSlavesTuple:
                    self.discoveredSlaves["%s:%s" % slaveTuple] = slaveTuple
            except rpyc.utils.factory.DiscoveryError:
                pass
        return self.discoveredSlaves


class RpyCNodie(basic_modules.Constant):
    """TODO: Add docstring
    """

#Add ComboBox
RPyCNode = basic_modules.new_constant('RpyCNode',
                                       staticmethod(eval),
                                       ('main', 0),
                                       staticmethod(lambda x: type(x) == tuple),
                                       RPyCNodeWidget,
                                       base_class=RpyCNodie)

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

from core.modules.vistrails_module import ModuleError, NotCacheable
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
from RPyC import RPyCModule, refreshPackage
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget
from core.modules import basic_modules
import rpyc


def getRemoteConnection(ip, port):
    from rpyc.core.service import SlaveService
    connection = rpyc.connect(ip, port, SlaveService,
                        {'allow_all_attrs': True,
                         'instantiate_custom_exceptions': True,
                         'import_custom_exceptions': True})

    print "Got a Remote Node"
    #Make sure all the right stuff is in place espcially dummy core and packages
    #on the remote node, no need for this if local as the machine is already set up
    print "Checking requirements on node..."

    #make sure all packages are in the path
    if not "./tmp" in connection.modules.sys.path:
        connection.modules.sys.path.append('./tmp')

    #Check version info
    force = False
    try:
        core_system = connection.modules["core.system"]
        import core.system
        if core_system.vistrails_version() != core.system.vistrails_version():
            force = True
            print "Different Versions....", core_system.vistrails_version(), "and", core.system.vistrails_version()
        else:
            print "Vistrails Ok..."
    except ImportError:
        print "Core System Not Loaded"
        connection.modules.sys.path_importer_cache['./tmp'] = None

    print "Uploading requirements to node...."
    import packages.eo4vistrails.rpyc.tmp    
    rpyc.classic.upload_package(connection, packages.eo4vistrails.rpyc.tmp, "./tmp")
    #import init_for_library
    #rpyc.classic.upload_module(connection, init_for_library, "./tmp")
    refreshPackage(connection, "api", force=force)
    refreshPackage(connection, "core", force=force)
    refreshPackage(connection, "db", force=force)
    refreshPackage(connection, "gui", force=force)
    refreshPackage(connection, "index", force=force)
    refreshPackage(connection, "tests", force=force)
    print "Finished uploading vistrails requirements to node...."

    return connection


def getSubConnection():
    from rpyc.core.service import SlaveService
    from rpyc.utils import factory
    connection = factory.connect_subproc(["python", "-u",
                                         "/usr/local/bin/rpyc_classic.py",
                                         #rpyc.classic.SERVER_FILE,
                                         "-q", "-m", "stdio"],
                                         SlaveService,
                                         {'allow_all_attrs': True,
                                          'instantiate_custom_exceptions': True,
                                          'import_custom_exceptions': True})

    #connection = rpyc.classic.connect_subproc()
    #make sure all packages are in the path
    print "Got a subProc"
    import core.system
    #import sys
    #connection.modules.sys.path.extend(sys.path)
    connection.modules.sys.path.append(core.system.vistrails_root_directory())
    #connection.modules.sys.path.append(core.system.packages_directory())

    return connection


class RPyCCode(ThreadSafeMixin, RPyCModule):
    """
    This module that executes an arbitrary piece of Python code remotely.
    """
    #TODO: If you want a PythonSource execution to fail, call fail(error_message).
    #TODO: If you want a PythonSource execution to be cached, call cache_this().

    '''
    This constructor is strictly unnecessary. However, some modules
    might want to initialize per-object data. When implementing your
    own constructor, remember that it must not take any extra parameters.
    '''

    def __init__(self):
        ThreadSafeMixin.__init__(self)
        RPyCModule.__init__(self)

    def clear(self):
        print "clear"
        RPyCModule.clear(self)
        if self.conn:
            try:
                self.conn.proc.terminate()
            except:
                pass
            try:
                self.conn.proc.wait()
            except:
                pass
            try:
                self.conn.close()
            except:
                pass

    def run_code_orig(self, code_str, use_input=False, use_output=False):
        """run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution."""
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
        del locals_['source']
        print "Starting executing in main thread"
        exec code_str in locals_, locals_
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
        import sys
        conn.modules.sys.stdout = sys.stdout

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

        del conn.namespace['source']

        conn.execute(code_str)

        if use_output:
            for k in outputDict.iterkeys():
                try:
                    if conn.namespace[k] != None:
                        self.setResult(k, conn.namespace[k])
                except AttributeError:
                    self.setResult(k, conn.namespace[k])

    def compute(self):
        """
        Vistrails Module Compute, Entry Point Refer, to Vistrails Docs
        """
        self.conn = None
        if self.hasInputFromPort('rpycnode'):
            v = self.getInputFromPort('rpycnode')
            print v

            (isRemote, self.conn) = self.inputPorts['rpycnode'][0].obj.getSharedConnection()

        from core.modules import basic_modules
        s = basic_modules.urllib.unquote(
            str(self.forceGetInputFromPort('source', '')))

        if self.conn:
            self.run_code(s, self.conn, use_input=True, use_output=True)
        else:
            self.run_code_orig(s, use_input=True, use_output=True)


class RPyC_C_Code(RPyCCode):
    """TODO: Add doc.
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
        import sys
        conn.modules.sys.stdout = sys.stdout

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

        err = conn.eval("inline(code_str, keys, type_converters=blitz, compiler = 'gcc')")
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
                    self.discoveredSlaves[slaveTuple[0]] = slaveTuple
            except rpyc.utils.factory.DiscoveryError:
                pass
        return self.discoveredSlaves


class RpyCNodie(basic_modules.Constant):
    """TODO: Add docstring
    """

    def _getConnection(self, allowNone):
        v = self.get_output('value')
        print v
        connection = None
        if str(v[0]) == 'None' or str(v[0]) == '' and not allowNone:
            isRemote = False
            connection = None

        elif str(v[0]) == 'main'  and not allowNone:
            isRemote = False
            connection = None

        elif str(v[0]) == 'own' or allowNone:
            isRemote = False
            connection = getSubConnection()

        else:
            isRemote = True
            connection = getRemoteConnection(v[0], v[1])

        return (isRemote, connection)

    def getSharedConnection(self, allowNone=False):
        try:
            if not self.conn:
                (self.isRemote, self.conn) = self._getConnection(allowNone)
        except:
            (self.isRemote, self.conn) = self._getConnection(allowNone)
        return (self.isRemote, self.conn)

#Add ComboBox
RPyCNode = basic_modules.new_constant('RpyCNode',
                                       staticmethod(eval),
                                       ('main', 0),
                                       staticmethod(lambda x: type(x) == tuple),
                                       RPyCNodeWidget,
                                       base_class=RpyCNodie)

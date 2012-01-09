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
"""This module is the core; holding annotations and mixins.
"""
#History
#Terence van Zyl, 15 Dec 2010, Version 1.0


import rpyc  # Node must have rpyc installed so not a problem
#used to make a copy of the returned value
#import copy
#node has dummy versions of these so not a problem
from core.modules.vistrails_module import Module,  ModuleError, ModuleConnector

import socket
from thread import interrupt_main

from packages.eo4vistrails.utils.ModuleHelperMixin import ModuleHelperMixin
import Shared

from rpyc import SocketStream, VoidService, BaseNetref
from rpyc.utils.factory import connect_stream, connect
from multiprocessing import Process
from rpyc import SlaveService
from multiprocessing import sharedctypes
#local imports to reduce dependncies on nodes that don't do arrays
import numpy
from packages.NumSciPy.Array import NDArray


def getRemoteConnection(ip, port):
    connection = rpyc.connect(ip, port, SlaveService,
                        {'allow_all_attrs': True,
                         'instantiate_custom_exceptions': True,
                         'import_custom_exceptions': True})
    if connection:
        print "Got a Remote Node ip:%s port:%s" % (ip, port)
    else:
        raise ModuleError("no connection found ip:%s port:%s" % (ip, port))
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
    #added to make sure we have everything on the first load.
    refreshPackage(connection, "packages", force=force)
    print "Finished uploading vistrails requirements to node...."

    return connection


def getSubConnection(args={}):
    connection = connect_multiprocess(SlaveService, remote_service=SlaveService, args=args)

    #connection = rpyc.classic.connect_subproc()
    #make sure all packages are in the path
    print "Got a subProc"
    import core.system
    #import sys
    #connection.modules.sys.path.extend(sys.path)
    connection.modules.sys.path.append(core.system.vistrails_root_directory())
    #connection.modules.sys.path.append(core.system.packages_directory())
    return connection


# This is a temp solution until we have our changes merged into the RPYC
# core repo
def connect_multiprocess(service=VoidService, config={},
                         remote_service=VoidService, remote_config={}, args={}):
    """starts an rpyc server on a new thread, bound to an arbitrary port,
    and connects to it over a socket.

    :param service: the local service to expose (defaults to Void)
    :param config: configuration dict
    :param server_service: the remote service to expose (of the server; defaults to Void)
    :param server_config: remote configuration dict (of the server)
    :param args: namespace dict of local vars (if these are shared memory then changes will be bi-directional)
    """
    listener = socket.socket()
    listener.bind(("localhost", 0))
    listener.listen(1)

    def server(listener, args):
        client = listener.accept()[0]
        listener.close()
        conn = connect_stream(SocketStream(client), service=remote_service,
                              config=remote_config)
        try:
            for k in args:
                conn._local_root.exposed_namespace[k] = args[k]
            conn.serve_all()
        except KeyboardInterrupt:
            interrupt_main()
    proc = Process(target=server, args=(listener, args))
    proc.start()
    host, port = listener.getsockname()
    conn = connect(host, port, service=service, config=config)
    conn.proc = proc
    return conn


def refreshModule(connection, moduleName):
    module = __import__(moduleName, fromlist=['packages'])

    print "Uploading module %s..." % moduleName
    rpyc.classic.upload_module(connection, module, "./tmp/" +\
                                moduleName.replace(".", "/"))
    print "Refreshing Module %s..." % moduleName
    try:
        rmodule = connection.modules[moduleName]
        connection.modules.__builtin__.reload(rmodule)
        #print "Refreshed Module %s..."%refreshmodule
    except ImportError:
        print "Module %s not refreshed..." % moduleName


def refreshPackage(connection, packageName, checkVersion=False, force=False):
    reFresh = force
    package = __import__(packageName, fromlist=['packages'])

    try:
        rpackage = connection.modules[packageName]
    except ImportError, er:
        print packageName, er
        reFresh = True
    try:
        if (not reFresh) and checkVersion and (rpackage.version != package.version):
            print packageName, "Versions Differ %s vs %s" % (rpackage.version, package.version)
            reFresh = True
    except AttributeError:
        print packageName, "Has no versions forcing refresh"
        reFresh = True

    if reFresh:
        print "Uploading package %s..." % packageName
        rpyc.classic.upload_package(connection, package, "./tmp/" +\
                                    packageName.replace(".", "/"))
        print "Refreshing Modules for  %s..." % packageName
        refreshmodules = [(mod if mod.startswith(packageName) else None) \
            for mod in connection.modules.sys.modules.keys()]
        for refreshmodule in refreshmodules:
            if refreshmodule:
                try:
                    rpackage = connection.modules[refreshmodule]
                    connection.modules.__builtin__.reload(rpackage)
                    #print "Refreshed Module %s..."%refreshmodule
                except ImportError:
                    pass
                    #print "Module %s not refreshed..."%refreshmodule
    else:
        print "Skipping %s..." % packageName


class RPyCModule(Module):
    """
    This forms the basis for ensuring that rpyc-based modules have the correct
    input ports.
    """
    _input_ports = [('rpycnode', '(za.co.csir.eo4vistrails:RpyC Node:rpyc)')]


class RPyCSafeModule(object):
    """
    RPyCSafeModule executes the compute method on a RPyC node.

    This annotation mixes in the code needed to ensure both threadsafe execution
    and rpyc safe execution.
    """

    def __init__(self, requiredVisPackages=[]):
        #Always need packages.eo4vistrails in requiredvispackages
        self._requiredVisPackages = requiredVisPackages

    def __call__(self, clazz):
        if not "packages.eo4vistrails" in self._requiredVisPackages:
            #THIS NEEDS TO HAPPEN ONLY ONCE
            #ELSE YOU LOOSE ALLL MODULE LEVEL VARIABLES
            self._requiredVisPackages.append("packages.eo4vistrails")
            self._requiredVisPackages.append("packages.eo4vistrails.dataanalytics")
            self._requiredVisPackages.append("packages.eo4vistrails.datacube")
            self._requiredVisPackages.append("packages.eo4vistrails.geoinf")
            self._requiredVisPackages.append("packages.eo4vistrails.lib")
            self._requiredVisPackages.append("packages.eo4vistrails.rpyc")
            self._requiredVisPackages.append("packages.eo4vistrails.transform")
            self._requiredVisPackages.append("packages.eo4vistrails.utils")
            pass
        if not "packages.spreadsheet" in self._requiredVisPackages:
            self._requiredVisPackages.append("packages.spreadsheet")
        clazz._requiredVisPackages = self._requiredVisPackages

        if RPyCModule not in clazz.__bases__:
            try:
                clazz._input_ports = clazz._input_ports + RPyCModule._input_ports
            except AttributeError:
                clazz._input_ports = RPyCModule._input_ports
                pass

        if RPyCSafeMixin not in clazz.__bases__:
            new__bases__ = (RPyCSafeMixin,) + clazz.__bases__
            new__dict__ = clazz.__dict__.copy()
            new__dict__['_original_compute'] = new__dict__['compute']

            del(new__dict__['compute'])  # = RPyCSafeMixin.compute

        return type(clazz.__name__, new__bases__, new__dict__)


class DummyConnector(ModuleConnector):
    """TODO: Add docstring.
    """

    def __init__(self, obj, port, oid, netref_ip, netref_port):
        ModuleConnector.__init__(self, obj, port)
        self.oid = oid
        self.netref_ip = netref_ip
        self.netref_port = netref_port

    def clear(self):
        try:
            if self.conn:
                try:
                    self.conn.close()
                    print "closed"
                except:
                    pass
                try:
                    self.conn.proc.join()
                    print "joined"
                except:
                    pass
                self.conn = None
        except:
            pass
        print "clearing Connector"
        ModuleConnector.clear(self)

    def __call__(self):
        _locals = locals()
        print "in the closure Remote:%s" % Shared.isRemoteRPyCNode
        print "Shared.cachedResults", Shared.cachedResults.valuerefs()
        if _locals.has_key("___shm_%s" % self.oid):
            print "got shared mem %s" % self.oid
            return _locals["___shm_%s" % self.oid]
        elif Shared.cachedResults.has_key(self.oid):
            print "got cached result from same process for oid:%s" % self.oid
            return Shared.cachedResults[self.oid]
        elif isinstance(self.obj.get_output(self.port), BaseNetref) and self.netref_ip != "" and self.netref_port != "":
            print "setting up connection (%s, %s) for oid: %s" % (self.netref_ip, self.netref_port, self.oid)
            self.conn = rpyc.connect(self.netref_ip, self.netref_port, SlaveService,
                            {'allow_all_attrs': True,
                             'instantiate_custom_exceptions': True,
                             'import_custom_exceptions': True})
            self.conn.execute('import packages.eo4vistrails.rpyc.Shared as Shared')
            print "Remote Shared.cachedResults", self.conn.namespace['Shared'].cachedResults.valuerefs()
            return self.conn.namespace['Shared'].cachedResults[self.oid]
        else:
            print "using fallback connector"
            return ModuleConnector.__call__(self)


class DummyArray(object):
    pass


class RPyCSafeMixin(ModuleHelperMixin):
    """
    This module provides a developer with dummy versions
    of each of the methods that a module would normally supply.

    An instance of a RPyC module created in VisTrails will have the proper
    vistrails module mixed in by the annotation. On a RPyC node
    the dummy verion is used to instantiate a shadow of the original
    module. The shadow's methods are linked back to the original module.
    """

    def clear(self):
        try:
            if self.conn:
                try:
                    self.conn.close()
                    print "closed"
                except:
                    pass
                try:
                    self.conn.proc.join()
                    print "joined"
                except:
                    pass
                self.conn = None
        except:
            pass
        print "clearing"
        Module.clear(self)

    def getConnection(self):
        connection = None
        isRemote = False
        rpycnode = ('', '')
        if self.hasInputFromPort('rpycnode'):
            rpycnode = self.getInputFromPort('rpycnode')

            if str(rpycnode[0]) == 'None' or str(rpycnode[0]) == '':
                self.preCompute()

            elif str(rpycnode[0]) == 'main':
                self.preCompute()

            elif str(rpycnode[0]) == 'own':
                #setup shared memory
                #TODO: what happens if we want to have multi inputs on a shared
                #memory port?
                #Maybe I have handled it already I'm not sure, need to test
                print "Setting Up Shared Memory"
                self.preCompute()
                args = {}
                args.update(self.sharedPorts)
                for port in self.inputPorts:
                    values = self.forceGetInputListFromPort(port)
                    for value in values:
                        if Shared.cachedSharedResults.has_key(id(value)):
                            args.update({'___shm_%s' % id(value): value})
                connection = getSubConnection(args)
            else:
                isRemote = True
                connection = getRemoteConnection(rpycnode[0], rpycnode[1])
                #Upload any vistrails packages that may be required
                for packageName in self._requiredVisPackages:
                    if packageName.endswith(".py"):
                        #TODO: this doesn't work for some reason
                        refreshModule(connection, packageName[:-3])
                    else:
                        refreshPackage(connection, packageName, checkVersion=True, force=False)
                print "Finished uploading module requirements to node...."
        else:
            self.preCompute()
        return (isRemote, connection, rpycnode)

    def compute(self):
        #Get RPyC Node in good standing
        #input from rpycmodule

        isRemote = False
        rpycnode = ('', '')

        if Shared.isRemoteRPyCNode:
            self.conn = None
        else:
            self.sharedPorts = {}
            isRemote, self.conn, rpycnode = self.getConnection()

        if not self.conn:
            #run as per normal
            print "run as per normal", self
            self._original_compute()
        else:
            #redirect StdIO back here so we can see what is going on

            #make sure we have the rpycnode info available
            self.conn.rpycnode = rpycnode

            #Just sum setup stuff to make sure vistrails is safe
            self.conn.execute('import init_for_library')
            #Make sure it knows its a remote node
            self.conn.execute('import packages.eo4vistrails.rpyc.Shared as Shared')
            self.conn.execute('from packages.eo4vistrails.rpyc.RPyC import DummyConnector')

            self.conn.execute('Shared.isRemoteRPyCNode=True')
            #print "Entry remote Shared.cachedResults:", self.conn.namespace['Shared'].cachedResults.valuerefs()

            #Instantiate Shadow Object
            print 'from %s import %s' % (self.__module__, self.__class__.__name__)
            #print '%s' % self.conn.modules.sys.path
            self.conn.execute('from %s import %s' % (self.__module__, self.__class__.__name__))
            self.conn.execute('shadow = %s()' % (self.__class__.__name__))
            shadow = self.conn.eval('shadow')

            #Hook Up Shadow Objects Methods and Attributes
            #attributes
            for attribute in Module.__dict__:
                if not str(attribute) in ('setResult', 'getInputFromPort', 'forceGetInputFromPort', 'getInputListFromPort', 'forceGetInputListFromPort', 'compute', '__dict__', '__module__', '__doc__', '__str__', '__weakref__', '__init__'):
                    shadow.__setattr__(str(attribute), self.__getattribute__(str(attribute)))

            self.conn.execute('shadow.inputPorts = {}')
            shadow.inputPorts = self.inputPorts
            shadow.outputPorts = self.outputPorts
            shadow.is_method = self.is_method
            shadow.upToDate = self.upToDate
            shadow.logging = self.logging
            shadow._latest_method_order = self._latest_method_order
            shadow.moduleInfo = self.moduleInfo
            shadow.is_breakpoint = self.is_breakpoint
            shadow.is_fold_operator = self.is_fold_operator
            shadow.is_fold_module = self.is_fold_module
            shadow.computed = self.computed
            shadow.signature = self.signature

            self.conn.execute('import core.interpreter.default')
            shadow.interpreter = self.conn.eval('core.interpreter.default.get_default_interpreter()')

            self.conn.execute('shadow.sharedPorts = {}')

            #set up the sharedports on the client
            for port in shadow.inputPorts:
                for i in xrange(len(shadow.inputPorts[port])):
                    connector = shadow.inputPorts[port][i]
                    if isinstance(connector(), BaseNetref):
                        netref_ip = connector().____conn__().rpycnode[0]
                        netref_port = connector().____conn__().rpycnode[1]
                    else:
                        netref_ip = ""
                        netref_port = ""
                    if self.conn.namespace.has_key('___shm_%s' % id(connector())) \
                    or isinstance(connector(), BaseNetref):
                        print "ip: %s, port: %s" % (netref_ip, netref_port)
                        print "Setting up Dummy Connector for %s" % port
                        shadow.inputPorts[port][i] = self.conn.namespace['DummyConnector'](connector.obj, connector.port, id(connector()), netref_ip, netref_port)

            #set up the sharedports on the client
            for port in self.sharedPorts:
                shadow.sharedPorts[port] = self.conn.namespace[port]

            print "Executing in the shadow class"
            #Call the Shadow Objects Compute and pre compute
            if isRemote:
                shadow.preCompute()
            shadow.compute()
            #copy all the data to the local node
            for port in self.outputPorts:
                if port not in ['self']:
                    self._obtainLocalCopy(port, isRemote)

            #disconnect the remote node
            if not isRemote and self.conn:
                self.conn.close()
                print "closed"
                self.conn.proc.join()
                print "joined"
                self.conn = None

            #print "Exit remote Shared.cachedResults:", self.conn.namespace['Shared'].cachedResults.valuerefs()

    def preCompute(self):
        """
        Abstract method here you should call allocateSharedArrayMemory()
        to set up any shared memory that will be used for output ports.

        """
        pass

    def allocateSharedMemoryArray(self, port, data_ctype, shape):
        """
        Allocated Shared Array memory to be used as an output port

        :param port: the port to perfomr the operation on
        :param data_ctype: the data type as a ctype
        :param shape: shape of elements in array

        """
        if not isinstance(shape, tuple):
            shape = (shape,)
        size = 1
        for i in shape:
            size *= i

        a = sharedctypes.RawArray(data_ctype, size)
        dt = numpy.dtype(a._type_)
        d = DummyArray()
        d.__array_interface__ = {
            'data': (a._wrapper.get_address(), False),
            'typestr': dt.str,
            'descr': [('', dt.str)],
            'shape': shape,
            'strides': None,
            'version': 3}
        self.sharedPorts[port] = (numpy.asarray(d), a)

    def setResult(self, port, value, asNDArray=False):
        """
        Overide the set result of the base class
        if not a numpy array uses the origional

        :param port: the port to perfomr the operation on
        :param value: the actual value to set the port
        :param asNDArray: True ensures a NDArray is set if array type

        """
        try:
            if self.sharedPorts.has_key(port):
                print "#We set a shared memory case"
                shmem_np = self.sharedPorts[port][0]
                if isinstance(value, NDArray):
                    shmem_np[:] = value.get_array()
                    value.set_array(shmem_np)
                elif isinstance(value, numpy.ndarray):
                    shmem_np[:] = value
                    if asNDArray:
                        value = NDArray()
                        value.set_array(shmem_np)
                    else:
                        value = shmem_np
                elif value is None:
                    #no need to do the copy they giving us the original shared mem back this the quickest
                    if asNDArray:
                        value = NDArray()
                        value.set_array(shmem_np)
                    else:
                        value = shmem_np
                else:
                    print "Not a valid  array as input"
        except (AttributeError, RuntimeError):
            pass
        Module.setResult(self, port, value)

    def _obtainLocalCopy(self, port, isRemote):
        """
        Get a local copy of a remote connections result, may be the case it is
        shared memory and should be handled differently,
        also in the case of a remote node a local copy is
        handled somewhat different

        :param port: the port to perform the operation on
        :param isRemote: was this done on a remote connection

        """
        if self.sharedPorts.has_key(port):
            print "#We obtained a shared memory case for port %s" % (port)
            if isinstance(self.outputPorts[port], NDArray):
                self.outputPorts[port] = NDArray()
                self.outputPorts[port].set_array(self.sharedPorts[port][0])
            else:
                self.outputPorts[port] = self.sharedPorts[port][0]
            Shared.cachedSharedResults[id(self.outputPorts[port])] = self.outputPorts[port]
        elif not isRemote:
            print "#We obtained a non-remote memory case for port %s" % (port)
            #make arrays into a shared mamory case to pass to next process
            #costs us nothing since we doing a copy already
            if isinstance(self.outputPorts[port], NDArray):
                np_array = self.outputPorts[port].get_array()
                self.allocateSharedMemoryArray(port, numpy.ctypeslib._typecodes[np_array.dtype.str], np_array.shape)
                self.sharedPorts[port][0][:] = rpyc.classic.obtain(np_array)
                print "#We created a NDArray shared memory case"
                self.outputPorts[port] = NDArray()
                self.outputPorts[port].set_array(self.sharedPorts[port][0])
                Shared.cachedSharedResults[id(self.outputPorts[port])] = self.outputPorts[port]
            elif isinstance(self.outputPorts[port], numpy.ndarray):
                np_array = self.outputPorts[port]
                self.allocateSharedMemoryArray(port, numpy.ctypeslib._typecodes[np_array.dtype.str], np_array.shape)
                self.sharedPorts[port][0][:] = rpyc.classic.obtain(np_array)
                print "#We created a ndarray shared memory case"
                self.outputPorts[port] = self.sharedPorts[port][0]
                Shared.cachedSharedResults[id(self.outputPorts[port])] = self.outputPorts[port]
            else:
                self.outputPorts[port] = rpyc.classic.obtain(self.outputPorts[port])
        try:
            Shared.cachedResults[id(self.outputPorts[port])] = self.outputPorts[port]
            if isRemote:
                print "#making sure the Remote cache is set up for port %s, oid %s" % (port, id(self.outputPorts[port]))
                self.conn.namespace['Shared'].cachedResults[id(self.outputPorts[port])] = self.outputPorts[port]
        except TypeError:
            print "Cache is not set up for port %s, oid %s" % (port, id(self.outputPorts[port]))

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
debug = False

import rpyc  # Node must have rpyc installed so not a problem
import gc

#used to make a copy of the returned value
#import copy
#node has dummy versions of these so not a problem
from core.modules import basic_modules
from core.modules.vistrails_module import Module, ModuleError, ModuleConnector, NotCacheable

import socket
from thread import interrupt_main

from packages.eo4vistrails.utils.ModuleHelperMixin import ModuleHelperMixin
from packages.eo4vistrails.utils.DropDownListWidget import ComboBoxWidget
import Shared

import multiprocessing

from rpyc import SocketStream, VoidService, BaseNetref
from rpyc.utils.factory import connect_stream, connect
from rpyc import SlaveService
#from multiprocessing import sharedctypes, Process
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
    except ImportError as ie:
        print "Core System Not Loaded", ie
        connection.modules.sys.path_importer_cache['./tmp'] = None

    print "Uploading requirements to node...."
    import packages.eo4vistrails.rpyc.tmp
    rpyc.classic.upload_package(connection, packages.eo4vistrails.rpyc.tmp, "./tmp")
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
    if connection:
        print "Got a subProc"
    else:
        raise ModuleError("No sub connection made")

    #make sure all packages are in the path
    import core.system
    connection.modules.sys.path.append(core.system.vistrails_root_directory())
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
                if debug: print "added to sub process %s->%s"%(k, conn._local_root.exposed_namespace[k])
            conn.serve_all()
        except KeyboardInterrupt:
            interrupt_main()
    proc = multiprocessing.Process(target=server, args=(listener, args))
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
        if (not reFresh) and checkVersion:
            #print packageName, "Versions %s vs %s"%(rpackage.version, package.version)
            if (rpackage.version != package.version):            
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
                except ImportError:
                    pass
    else:
        pass
        #print "Skipping %s..." % packageName


class RPyCModule(Module):
    """
    This forms the basis for ensuring that rpyc-based modules have the correct
    input ports.
    """
    _input_ports = [('rpycnode', '(za.co.csir.eo4vistrails:RpyC Node:rpyc)', {"optional": False})]


class RPyCMultiProcessModule(RPyCModule):
    _input_ports = [('rpycnode', '(za.co.csir.eo4vistrails:RpyC Node:rpyc)', {"optional": False}),
                    ('worker pool size', '(core.modules.vistrails_module.Integer)', {"optional": True})]

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
        if not "packages.vtk" in self._requiredVisPackages:
            self._requiredVisPackages.append("packages.vtk")
        if not "packages.NumSciPy" in self._requiredVisPackages:
            self._requiredVisPackages.append("packages.NumSciPy")
        
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
    
    def __init__(self, obj, port, shmemobj, oid, netref_ip, netref_port):
        ModuleConnector.__init__(self, obj, port)
        self.oid = oid
        self.netref_ip = netref_ip
        self.netref_port  = netref_port
        self.shmemobj = shmemobj
        self.predecessorModuleOutput = None
    
    def clear(self):
        if debug: print "clearing DummyConnector"        
        self.oid = None
        self.netref_ip = None
        self.netref_port  = None
        self.shmemobj = None
        self.predecessorModuleOutput = None
        ModuleConnector.clear(self)
        gc.collect()

    def __del__(self):
        if debug: print self, "deleted"
        self.clear()

    def __call__(self):
        import os
        if debug: print "Process: %s in the closure isRPyC: %s with oid: %s"%(os.getpid(), Shared.isRemoteRPyCNode, self.oid)
        #if debug: print "Shared.cachedResults", Shared.cachedResults.valuerefs()        
        if self.predecessorModuleOutput is None:
            conn = None
            try:
                if not self.shmemobj is None:
                    if debug: print "got shared mem %s"%self.oid
                    self.predecessorModuleOutput = self.shmemobj
                elif Shared.cachedResults.has_key(self.oid) and not isinstance(Shared.cachedResults[self.oid], BaseNetref):
                    if debug: print "got non netref cached result from other thread for oid: %s"%self.oid
                    self.predecessorModuleOutput =  Shared.cachedResults[self.oid]
                elif isinstance(self.obj.get_output(self.port), BaseNetref):
                    if self.netref_ip != "":
                        if debug: print "setting up connection (%s, %s) for oid: %s"%(self.netref_ip, self.netref_port, self.oid)
                        conn = rpyc.connect(self.netref_ip, self.netref_port, SlaveService,
                                        {'allow_all_attrs': True,
                                         'instantiate_custom_exceptions': True,
                                         'import_custom_exceptions': True})
                        conn.execute('import packages.eo4vistrails.rpyc.Shared as Shared')
                        #print "remote Shared.cachedResults", conn.namespace['Shared'].cachedResults.valuerefs()
                        self.predecessorModuleOutput = rpyc.classic.obtain(conn.namespace['Shared'].cachedResults[self.oid])
                        Shared.cachedResults[self.oid] = self.predecessorModuleOutput
                    else:
                        if debug: print "got inverse remote proc copy of object: %s"%self.oid                        
                        self.predecessorModuleOutput = rpyc.classic.obtain(self.obj.get_output(self.port))
                        Shared.cachedResults[self.oid] = self.predecessorModuleOutput
                else:
                    if debug: print "using fallback connector: no exceptions"
                    self.predecessorModuleOutput = ModuleConnector.__call__(self)
            except TypeError:
                print "using fallback connector: exception case, fix code!!!!", self.obj
                self.predecessorModuleOutput = ModuleConnector.__call__(self)
            finally:
                if conn is not None:
                    conn.close()
                    conn = None
        return self.predecessorModuleOutput


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
    ownNotSupported = False
    multiWorkerSupported = False
    shadow = None
    conn = None

    def clear(self):
        try:
            if debug: print self, "clearing RPyCMixin"
            Module.clear(self)
            self.sharedMemOutputPorts = {}
            if self.shadow:
                if debug: print self, "clearing shadow"
                self.shadow.clear()
                self.conn.execute('shadow = None')
                self.shadow = None
        finally:
            if self.conn:
                if debug: print self, "closing connection"
                try:
                    self.conn.close()
                    if debug: print self, "closed"
                except:
                    pass
                try:
                    self.conn.proc.join()
                    if debug: print self, "joined"
                except:
                    pass
                self.conn = None
            gc.collect()

    def __del__(self):
        if debug: print self, "deleted"
        self.clear()
        
    def _getConnection(self, rpycnode):        
        connection = None
        isRemote = False
        
        if str(rpycnode[0]) == 'own':
            #setup shared memory
            #TODO: what happens if we want to have multi inputs on a shared
            #memory port?
            #Maybe I have handled it already I'm not sure, need to test                
            self.preCompute()
            args = {}
            args.update( self.sharedMemOutputPorts )
            for port in self.inputPorts:
                values = self.forceGetInputListFromPort(port)
                for value in values:
                    if not isinstance(value ,BaseNetref):                  
                        if debug: print "Added shared input param: %s value: %s"%('___shm_%s'%id(value), value)
                        args.update({'___shm_%s'%id(value):value})
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
            if debug: print "Finished uploading module requirements to node...."
        
        return (isRemote, connection)

    def compute(self):
        self.hasWorkerPool = False
        rpycnodes = [(None,None)]
        try:
            if self.hasInputFromPort('rpycnode'):
                rpycnodes = self.getInputFromPort('rpycnode')
                if not isinstance(rpycnodes, list):
                    rpycnodes = self.getInputListFromPort('rpycnode')
                if len(rpycnodes) > 1:
                    self.hasWorkerPool = True
    
            for index, rpycnode in zip(range(len(rpycnodes)), rpycnodes):
                #Get RPyC Node in good standing
                #input from rpycmodule        
                self.isRemote = False
        
                if Shared.isRemoteRPyCNode:
                    self.conn = None
                    
                elif rpycnode[0] is None or rpycnode[0] in ['main', ''] or self.ownNotSupported:
                    self.workerNodeID = None
                    self.conn = None
                    self.preCompute()
                    
                else:
                    self.sharedMemOutputPorts = {}
                    self.isRemote, self.conn = self._getConnection(rpycnode)
                    
                if not self.conn:
                    #run as per normal
                    if debug: print "run as per normal", self
                    if not Shared.isRemoteRPyCNode:
                        self._setupDummyInputs(self, locals())
                    self._original_compute()
                else:
                    #make sure we have the rpycnode info available
                    self.conn.rpycnode = rpycnode
                    
                    #Just sum setup stuff to make sure vistrails is safe
                    self.conn.execute('import init_for_library')
                    #Make sure it knows its a remote node
                    self.conn.execute('import packages.eo4vistrails.rpyc.Shared as Shared')
                    self.conn.execute('from packages.eo4vistrails.rpyc.RPyC import DummyConnector')
        
                    self.conn.execute('Shared.isRemoteRPyCNode=True')
                    #print self.conn.namespace['Shared'].cachedResults.valuerefs()
                    
                    #Instantiate Shadow Object
                    if debug: print 'from %s import %s' % (self.__module__, self.__class__.__name__)
                    self.conn.execute('from %s import %s' % (self.__module__, self.__class__.__name__))
                    self.conn.execute('shadow = %s()' % (self.__class__.__name__))
                    self.shadow = self.conn.eval('shadow')
                    #Set the worker nodes ID so he know who he is in the pool
                    self.shadow.workerNodeID = index
                    
                    #Hook Up Shadow Objects Methods and Attributes
                    for attribute in Module.__dict__:
                        if not str(attribute) in ('clear', 'setResult', 'getInputFromPort', 'forceGetInputFromPort', 'getInputListFromPort', 'forceGetInputListFromPort', 'compute', '__dict__', '__module__', '__doc__', '__str__', '__weakref__', '__init__'):
                            self.shadow.__setattr__(str(attribute), self.__getattribute__(str(attribute)))
        
                    #This ensures we still have a local copy of each port as they are used in the 
                    #update upstream workflow pipe, and we don't want to be breaking
                    #the local pipe, espacially when we replace all connectors with dummys            
                    self.conn.execute('shadow.inputPorts = {}')
                    for port in self.inputPorts:
                        self.shadow.inputPorts[port] =  self.conn.eval('[]')
                        for connector in self.inputPorts[port]:
                            self.shadow.inputPorts[port].append(connector)
                    
                    self.shadow.outputPorts = self.outputPorts
                    self.shadow.is_method = self.is_method
                    self.shadow.upToDate = self.upToDate
                    self.shadow.logging = self.logging
                    self.shadow._latest_method_order = self._latest_method_order
                    self.shadow.moduleInfo = self.moduleInfo
                    self.shadow.is_breakpoint = self.is_breakpoint
                    self.shadow.is_fold_operator = self.is_fold_operator
                    self.shadow.is_fold_module = self.is_fold_module
                    self.shadow.computed = self.computed
                    self.shadow.signature = self.signature
                    
                    self.conn.execute('import core.interpreter.default')
                    self.shadow.interpreter = self.conn.eval('core.interpreter.default.get_default_interpreter()')
                    
                    #set up the sharedMemOutputPorts on the client
                    self._setupDummyInputs(self.shadow,  self.conn.namespace)
                    
                    self.conn.execute('shadow.sharedMemOutputPorts = {}')                
                    #set up the sharedMemOutputPorts on the client
                    for port in self.sharedMemOutputPorts:
                        self.shadow.sharedMemOutputPorts[port] = self.conn.namespace[port]
                    
                    import os        
                    #Call the Shadow Objects Compute and pre compute
                    if self.isRemote:
                        if debug: print "Process: %s Executing in the pre-compute shadow class"%os.getpid()
                        self.shadow.preCompute()
                        if debug: print "Process: %s Completed Executing pre-compute in the shadow class"%os.getpid()
                    if debug: print "Process: %s Executing in the shadow class"%os.getpid()
                    self.shadow.compute()
                    if debug: print "Process: %s Completed Executing in the shadow class"%os.getpid()
                    #Handle Shared memory etc at local node
                    keepConn = False
                    for port in self.outputPorts:
                        keepConn = keepConn or self._obtainLocalCopy(port, self.isRemote)
                    
                    if debug: print "Having to keep connection: %s"%keepConn
                    
                    #Disconnect the remote node
                    if not self.isRemote and not keepConn:
                        self.conn.close()
                        if debug: print "closed"
                        self.conn.proc.join()
                        if debug: print "joined"
                        self.conn = None
                        self.shadow = None
                
                #If multiworker is no explicitly supported then we should only 
                #execute opn the first node
                if not self.multiWorkerSupported:
                    return
                    
        except:
            if self.conn:
                self.conn.close()
                if debug: print "closed"
                if not self.isRemote:
                    self.conn.proc.join()
                    if debug: print "joined"
                self.conn = None
                self.shadow = None
            gc.collect()
            raise
            

    def _setupDummyInputs(self, module, namespace):
        #set up the sharedMemOutputPorts on the client
        for port in module.inputPorts:
            for i in xrange(len(module.inputPorts[port])):                    
                connector = module.inputPorts[port][i]
                netref_ip = ""
                netref_port = ""
                if isinstance(connector(), BaseNetref):
                    netref_ip = connector().____conn__().rpycnode[0]
                    netref_port = connector().____conn__().rpycnode[1]
                oid = id(connector())
                shmemobj = None
                if namespace.has_key('___shm_%s'%oid):
                    shmemobj = namespace['___shm_%s'%oid]            
                if debug: print "Setting up Dummy Connector for %s with oid %s"%(port, oid)
                if debug: print "has type:", type(connector.obj)
                if debug: print "ip: %s, port: %s"%(netref_ip, netref_port)
                if debug: print "shared mem object: %s"%(shmemobj,)
                if debug: print ""                    
                if namespace.has_key('DummyConnector'):
                    module.inputPorts[port][i] = namespace['DummyConnector'](connector.obj, connector.port, shmemobj, oid, netref_ip, netref_port)
                else:
                    module.inputPorts[port][i] = DummyConnector(connector.obj, connector.port, shmemobj, oid, netref_ip, netref_port)

    def preCompute(self):
        """
        Abstract method here you should call allocateSharedArrayMemory()
        to set up any shared memory that will be used for output ports.

        """
        pass

    def allocateSharedMemoryArray(self, port, data_ctype, shape):
        """
        Allocated Shared Array memory to be used as an output port

        :param port: the port to perform the operation on
        :param data_ctype: the data type as a ctype
        :param shape: shape of elements in array

        """
        if not isinstance(shape, tuple):
            shape = (shape,)
        size = 1
        for i in shape:
            size *= i

        a = multiprocessing.sharedctypes.RawArray(data_ctype, size)
        dt = numpy.dtype(a._type_)
        d = DummyArray()
        d.__array_interface__ = {
            'data': (a._wrapper.get_address(), False),
            'typestr': dt.str,
            'descr': [('', dt.str)],
            'shape': shape,
            'strides': None,
            'version': 3}
        self.sharedMemOutputPorts[port] = (numpy.asarray(d), a)

    def setResult(self, port, value, asNDArray=False):
        """
        Overide the set result of the base class
        if not a numpy array uses the origional

        :param port: the port to perform the operation on
        :param value: the actual value to set the port
        :param asNDArray: True ensures a NDArray is set if array type

        """
        try:
            if self.sharedMemOutputPorts.has_key(port):
                if debug: print "#We set a shared memory case"
                shmem_np = self.sharedMemOutputPorts[port][0]
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
                    #no need to do the copy they giving us the original shared 
                    #mem back this is the quickest
                    if asNDArray:
                        value = NDArray()
                        value.set_array(shmem_np)
                    else:
                        value = shmem_np
                else:
                    if debug: print "Not a valid  array as input"
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
        import os
        keepConn = False
        if debug: print "running _obtainLocalCopy from process: %s for port %s"%(os.getpid(), port)
        if self.sharedMemOutputPorts.has_key(port):
            if debug: print "#We obtained a shared memory case for port %s" % (port)
            if isinstance(self.outputPorts[port], NDArray):
                self.outputPorts[port] = NDArray()
                self.outputPorts[port].set_array(self.sharedMemOutputPorts[port][0])
            else:
                self.outputPorts[port] = self.sharedMemOutputPorts[port][0]
            #try:
            #    Shared.cachedResults[id(self.outputPorts[port])] = self.outputPorts[port]
            #except TypeError:
            #    print "Cache is not set up for port %s, oid %s"%(port, id(self.outputPorts[port]))
        elif not isRemote:
            if debug: print "#We obtained a own-proc case for port %s"%(port)
            #make arrays into a shared mamory case to pass to next process
            #costs us nothing since we doing a copy already
            if isinstance(self.outputPorts[port], NDArray):
                np_array = self.outputPorts[port].get_array()
                self.allocateSharedMemoryArray(port, numpy.ctypeslib._typecodes[np_array.dtype.str], np_array.shape)
                self.sharedMemOutputPorts[port][0][:] = rpyc.classic.obtain(np_array)
                if debug: print "#We created a NDArray shared memory case for port: %s"%port
                self.outputPorts[port] = NDArray()
                self.outputPorts[port].set_array(self.sharedMemOutputPorts[port][0])
            elif isinstance(self.outputPorts[port], numpy.ndarray):
                np_array = self.outputPorts[port]
                self.allocateSharedMemoryArray(port, numpy.ctypeslib._typecodes[np_array.dtype.str], np_array.shape)
                self.sharedMemOutputPorts[port][0][:] = rpyc.classic.obtain(np_array)
                if debug: print "#We created a ndarray shared memory case for port: %s"%port
                self.outputPorts[port] = self.sharedMemOutputPorts[port][0]
            else:
                if debug: print "#Obtaining a local copy for port: %s"%port
                if port == 'self':
                    try:
                        self.outputPorts[port] = rpyc.classic.obtain(self.outputPorts[port])
                    except TypeError:
                        self.outputPorts[port] = self
                else:
                    try:
                        self.outputPorts[port] = rpyc.classic.obtain(self.outputPorts[port])
                    except TypeError:
                        keepConn = True
            #try:
            #    Shared.cachedResults[id(self.outputPorts[port])] = self.outputPorts[port]
            #except TypeError:
            #    print "Cache is not set up for port %s, oid %s"%(port, id(self.outputPorts[port]))
        elif isRemote:
            if isinstance(self.outputPorts[port], BaseNetref):
                try:                    
                    if debug: print "#making sure the Remote cache is set up for port %s, oid %s"%(port, id(self.outputPorts[port]))                    
                    self.conn.namespace['Shared'].cachedResults[id(self.outputPorts[port])] = self.outputPorts[port]
                except TypeError:
                    if debug: print "Remote Cache is not set up for port %s, oid %s"%(port, id(self.outputPorts[port]))
                #try:
                #    Shared.cachedResults[id(self.outputPorts[port])] = self.outputPorts[port]
                #except TypeError:
                #    print "#Cache is not set up for port %s, oid %s"%(port, id(self.outputPorts[port]))
        return keepConn
        
class RPyCNodeWidget(ComboBoxWidget):
    """TODO: Add docstring
    """

    discoveredSlaves = None
    default = ('main', 0)

    def getKeyValues(self):
        if not self.discoveredSlaves:
            self.discoveredSlaves = {
                'Own Process': ('own', 0), 
                'Main Process': ('main', 0)
                }
            try:
                discoveredSlavesTuple = list(rpyc.discover("slave"))
                for slaveTuple in discoveredSlavesTuple:
                    try:
                        nslookup = socket.gethostbyaddr(slaveTuple[0])
                    except:
                        nslookup = (slaveTuple[0],[],[slaveTuple[0]])
                    self.discoveredSlaves["%s:%s"%(nslookup[0].split(".",1)[0], slaveTuple[1])] = (nslookup[0], slaveTuple[1])
            except rpyc.utils.factory.DiscoveryError:
                pass
        return self.discoveredSlaves

#Add ComboBox
RPyCNode = basic_modules.new_constant('RpyCNode',
                                       staticmethod(eval),
                                       ('main', 0),
                                       staticmethod(lambda x: type(x) == tuple),
                                       RPyCNodeWidget,
                                       base_class=basic_modules.Constant)

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 14:19:42 2011

@author: tvzyl
"""
from RPyC import RPyCSafeModule
from core.modules.vistrails_module import Module
from packages.eo4vistrails.utils.ThreadSafe import ThreadSafeMixin
import ctypes
from packages.NumSciPy.Array import NDArray

@RPyCSafeModule(['packages.NumSciPy'])
class RPyCTestModule(ThreadSafeMixin, Module):
    """This Test Module is to check that ThreadSafe is working and also provides
    a template for others to use ThreadSafe"""
    _input_ports = [('input', '(edu.utah.sci.vistrails.basic:Integer)'),
                    ('inarray', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')]    
    _output_ports = [('output', '(edu.utah.sci.vistrails.basic:String)'),
                     ('narray', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)'),
                     ('sharedArray', '(edu.utah.sci.vistrails.numpyscipy:Numpy Array:numpy|array)')]
    
    
    
    def __init__(self):
        ThreadSafeMixin.__init__(self)
        Module.__init__(self)
        self.theShape = (10000, 1000)
    
    def preCompute(self):
        self.allocateSharedMemoryArray('sharedArray', ctypes.c_float, self.theShape)
        
    def compute(self):
        from time import ctime, sleep
        import os
        import numpy

        print ctime()," ", os.getpid(), " Started RPyCSafe Module, Waiting 1 Seconds"
        #sleep(1)
        print ctime()," ", os.getpid(), " Stoped RPyCSafe Module"
        self.setResult('output', 'hello world I''m %s'%os.getpid())

        case = self.forceGetInputFromPort("input", 0)
        print "Hello", case
        inarray = self.forceGetInputFromPort("inarray", None)
        if inarray is not None: 
            if isinstance(inarray, NDArray):
               inarray = inarray.get_array()
            inarray += 1
        print "oid for inarray: %s"%id(inarray)
        print "value for inarray:"
        print inarray
        
        if case == 1 or case==0:
            self.setResult('narray', numpy.ones(self.theShape))
        if case == 2 or case==0:
            numpy.dot(self.sharedPorts['sharedArray'][0], self.sharedPorts['sharedArray'][0].T)
            self.sharedPorts['sharedArray'][0][:] = 2
            self.setResult('sharedArray', None, True)
        if case == 3:
            self.setResult('sharedArray', numpy.zeros(self.theShape)+2, True)
        if case == 4:
            theShape = (400, 400)
            
            a = [[] for _ in xrange(theShape[0]) ]
            b = [[] for _ in xrange(theShape[1]) ]
            c = [[] for _ in xrange(theShape[0]) ]
            
            for i in xrange(theShape[0]):
                a[i] = [1 for _ in xrange(theShape[1]) ]
            
            for i in xrange(theShape[1]):
                b[i] = [1 for _ in xrange(theShape[0]) ]
            
            for i in xrange(theShape[0]):
                c[i] = [0 for _ in xrange(theShape[0]) ]            
            
            for i in xrange(theShape[0]):
                for j in xrange(theShape[0]):
                    for k in xrange(theShape[0]):
                        c[i][j] += a[i][k] * b[k][j]                        

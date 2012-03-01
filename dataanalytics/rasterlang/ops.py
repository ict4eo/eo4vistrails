#!/usr/bin/env python
#
# Rasterlang (c) Barry Rowlingson 2008
#
#    This file is part of "rasterlang"
#
#    Rasterlang is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Rasterlang is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Rasterlang.  If not, see <http://www.gnu.org/licenses/>.


### TODO:
### make boolean ops return 1/0
### implement min/max (global minmax functions) and minimum/maximum (array-wise minmax)

import numpy
import debug

global allOps
allOps = None

class Op:
    def __init__(self,name,function,minarg,maxarg,help):
        self.name = name
        self.function = function
        self.minarg=minarg
        self.maxarg=maxarg
        self.help = help
    def __call__(self,*args):
        debug.msg(1,"call args are ",args)
        if len(args) > self.maxarg:
            raise TypeError," operator %s takes at most %s args, %s given" % (self.name,self.maxarg,len(args))
        if len(args) < self.minarg:
            raise TypeError," operator %s takes at least %s args, %s given" % (self.name,self.minarg,len(args))
        return self.function(*args)
    def __repr__(self):
        return "<Op "+self.name+":"+str(self.function)+">"
    def helpString(self):
        if self.minarg == self.maxarg:
            return "%s\t%s\t(%s parameters)" % (self.name, self.help, self.maxarg)
        return "%s\t%s\t(%s to %s parameters)" % (self.name, self.help, self.minarg, self.maxarg)



def bind(*args):
    debug.msg(1, "bind args are: ")
    debug.msg(1, args)
    res = numpy.array(args)
    if len(res.shape) == 3:
        if res.shape[0] == 1:
            res=res[0]
    return res

def band(ar,n):
    if len(ar.shape) == 3:
        return ar[int(n)]
    if len(ar.shape) == 2:
        if n == 0:
            return ar
        else:
            raise ValueError,"cant get band "+str(n)+" from single band"
    raise ValueError,"array not 2 or 3d"

def add(*args):
    return reduce(operator.add,args)

def mul(*args):
    return reduce(operator.mul,args)

def notter(*args):
    return args[0] == False

def eq(*args):
    debug.msg(1,"eq test ",args)
    for i in range(1,len(args)):
        if args[0]!=args[i]:
            return False
    return True

import operator
def ops():
    global allOps
    if  allOps:
        return allOps
    allOps =  {
        '+': Op('+',add,2,99,"add arguments"),
        '-': Op('-',operator.sub,2,2,"subtract arguments"),
        '^': Op('^',operator.pow,2,2,"raise to power"),
        '*': Op('*',mul,2,99,"multiply argument"),
        '/': Op('/',operator.truediv,2,2,"divide arguments"),
        '>': Op('>',operator.gt,2,2,"test greater than"),
        '>=': Op('>=',operator.ge,2,2,"test greater than or equal to"),
        '<': Op('<',operator.lt,2,2,"test less than"),
        '<=': Op('<=',operator.le,2,2,"test less than or equal to"),
        '=': Op('=',operator.eq,2,2,"test equality"),
        '&': Op('&',operator.and_,2,2,"logical _and_"),
        '|': Op('|',operator.or_,2,2,"logical _or_"),
        '!': Op('!',notter,1,1,"logical _not_"),
        'sin': Op('sin',numpy.sin,1,1,"sine function"),
        'cos': Op('cos',numpy.cos,1,1,"cosine function"),
        'tan': Op('tan',numpy.tan,1,1,"tangent function"),
        'asin': Op('asin',numpy.arcsin,1,1,"inverse sine function"),
        'acos': Op('acos',numpy.arccos,1,1,"inverse cosine function"),
        'atan': Op('atan',numpy.arctan,1,1,"inverse tangent function"),
        'log': Op('log',numpy.log,1,1,"natural logarithm"),
        'exp': Op('exp',numpy.exp,1,1,"exponential power"),
        'clip': Op('clip',numpy.clip,3,3,"clip lower and upper values"),
        'bind': Op('bind',bind,1,99,"create multi-band raster from argument"),
        'band': Op('band',band,2,2,"get band from raster"),
        }
    return allOps

def tryop(op,*args):
    print "Testing ",op
    oper = ops()[op].function
    return oper(*args)


def main():
    t1 = numpy.array([[1,2,3],[4,5,6],[7,8,9]])
    t2 = numpy.array([[1,2,3],[4,9,1],[7,8,9]])
    t3 = numpy.array([[1,1,1],[1,1,1],[2,2,2]])

    print "basics"
    print tryop('+',t1,t2)
    print tryop('-',t1,t2)
    print tryop('^',t1,2)
    print tryop('*',t1,2)
    print tryop('/',t1,2)

    print "boolean"
    print tryop('=',t1,4)
    print tryop('=',t1,t2)
    print tryop('>',t1,t2)
    print tryop('>=',t1,t2)
    print tryop('<',t1,t2)
    print tryop('<=',t1,t2)

    t4 = t1 > t2
    t5 = t1 > 2
    print tryop("&",t4,t5)
    print tryop("|",t4,t5)
    print tryop("!",t4)

    print "trig"
    print tryop('sin',t1)
    print tryop('cos',t1)
    print tryop('tan',t1)
    print tryop('asin',t1/9.0)
    print tryop('acos',t1/9.0)
    print tryop('atan',t1)

    print "math"
    print tryop('log',t1)
    print tryop('exp',t2)

    print "misc"
    print tryop('clip',t1,2.5,7.5)

    print "slicing"
    print tryop('bind',t1,t2,t3)
    aa=numpy.array([t1,t2])
    print tryop('band',aa,1)

    print "evaluation"
    clip=ops()['clip']
    print clip(2,3,4)

if __name__ == "__main__":
    main()
    

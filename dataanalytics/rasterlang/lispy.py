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

from pyparsing import *
import sys
import ops
import rasters

import pprint
"""
expression := ( op valuelist )
valuelist := listelement + ZeroOrMore(, + listelement)
listelement := constant | ( expression )
"""

def rasterSyntax():
    return Word(alphas,alphanums+"-+")

rasterList = set()

def gotRaster(a,b,c):
    global rasterList
    rasterList.add(c[0])
    return rasters.getRaster(c[0])

def operize(str,loc,toks):
    opers = ops.ops()
    return opers[toks[0]]

import math
def pify(str,loc,toks):
    return math.pi

def buildParser():
    # define punctuation literals
    LPAR, RPAR, LBRK, RBRK, LBRC, RBRC, VBAR = map(Suppress, "()[]{}|")

    pi = Literal('Pi').setParseAction(pify)
    E = Literal('e').setParseAction(lambda a,b,c: math.e)
    point = Literal('.')
    e = CaselessLiteral('E')
    plusorminus = Literal('+') | Literal('-')
    number = Word(nums)
    integer = Combine( Optional(plusorminus) + number )
    floatnumber = Combine( integer +
                           Optional( point + Optional(number) ) +
                           Optional( e + integer )
                           ).setParseAction( lambda s,l,t: [ float(t[0]) ] )
    raster = rasterSyntax().setParseAction(gotRaster)
#    numeric =  floatnumber | integer
    const = E | pi | raster | floatnumber

    expression = Forward()
    value = expression | const
    values = value + ZeroOrMore(value)

    #ops = [Literal(x) for x in ['+','-','*','/','>','<','==','!=','foo','bar','baz']]
    opers = [Literal(x) for x in ops.ops().keys()]
    op = reduce(lambda x,y: x|y,opers[1:],opers[0])

    expression << LPAR + Group(op.setParseAction(operize) + values) + RPAR
    line = expression + LineEnd()

    return line

# tests are now in ptest.py

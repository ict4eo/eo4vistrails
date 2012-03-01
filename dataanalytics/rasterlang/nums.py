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

def isItArray(a):
    return isNumeric(a) or isNumpy(a)

def isNumeric(a):
    try:
        import Numeric
        if isinstance(a,Numeric.arraytype):
            return True
    except:
        pass
    return False

def isNumpy(a):
    try:
        import numpy
        if isinstance(a,numpy.ndarray):
            return True
    except:
        pass
    return False

def arrayType(a):
    if isNumeric(a):
        return "Numeric"
    if isNumpy(a):
        return "Numpy"
    return None

def checkSameAs(a,b):
    """ a and b are either numpy or Numeric. Return "a" as the same type as "b", 
    or True if no change needed, that saves a copy."""
    aType = arrayType(a)
    bType = arrayType(b)
    
    if aType == bType:
        return (True,None)

    if bType == "Numpy":
        import numpy
        a = numpy.array(a)
        return (False,a)
    
    if bType == "Numeric":
        import Numeric
        a = Numeric.array(a)
        return (False,a)

    raise ValueError,"not numpy or numeric"

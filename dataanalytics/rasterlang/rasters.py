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

import numpy

rasterList = {}

def setRasters(rasterDict):
    global rasterList
    rasterList = rasterDict


def getRaster(name):
    return rasterList[name]


def main():
    setRasters({'foo': 1,'bar': numpy.array([[1,2,3],[4,5,6]])})
    print getRaster('foo')
    print getRaster('bar')

    
if __name__=="__main__":
    main()
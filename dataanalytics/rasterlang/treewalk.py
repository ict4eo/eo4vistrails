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

import debug

def walkit(alist):
    debug.msg(1,"op",alist[0])
    for e in alist[1:]:
        if isinstance(e, list):
            walkit(e)
        else:
            pass

    
def evaluate(alist):
    debug.msg(1, "evaluate:")
    debug.msg(1,alist)
    op = alist[0]
    args = []
    for e in alist[1:]:
        debug.msg(1," partial: ",e)
        if isinstance(e,list):
            debug.msg(1,"recursing:",alist)
            args.append(evaluate(e))
        else:
            debug.msg(1,"appending ",e)
            args.append(e)
    return op(*args)


def main():
    import numpy
    import ops
    a=numpy.array([1,2,3])
    o = ops.ops()
    test1 = [o['+'], a, [o['-'], 3, 1]]
    print evaluate(test1)
                        
if __name__=="__main__":
    main()

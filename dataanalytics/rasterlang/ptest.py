
from pyparsing import *

import lispy
import numpy
import rasters
import treewalk

import math

import debug

debug.level = -1

######### Test data ###########

R1 = numpy.array([[1],[2]])
R2 = numpy.array([[2],[4]])
R3 =  numpy.array([[33],[55]])

eqtests = [ 
    """ (= 3 3) """,True,
    """ (= 5 2) """,False,
    """ (= 5 5 4) """,False,
    """ (= 5 5 5) """,True,
    """ (= 4 5 5) """,False,
    """ (= 4 5 4) """,False,
]

mathtests = [
    """(+ 1 2 3)""",1+2+3,
    """(* 1 2 3 4 5)""",5*4*3*2*1,
    """(+ 3 7)""",10,
    """(+ (+ 1 2) (+ 3 4))""",10,
    """(+ (+ (+ 1 2) (+ 3 4)) 2 )""",12,
    """(/1 2)""",1.0/2.0,
    """(+ 1 -1.2)""",1-1.2,
    """(+ R1 (+ R1 100))""",R1+100+R1,
    """(+ R1 (> R1 100))""",R1 + (R1 > 100),
    """(+ R1 (+ R2 -2.45)) """,R1 + (R2 - 2.45),
    """(> R1 R2 ) """,R1 > R2,
] 
trigtests = [
    """(cos e)""",math.cos(math.e),
    """(sin Pi)""",math.sin(math.pi),
    """(+ (sin Pi ) (cos e ))""",math.cos(math.e) + math.sin(math.pi),
    """(sin 1e4)""",math.sin(1e4),
    """(sin (+ R1 R2))""",numpy.sin(R1+R2),
    """(cos (* R1 R2))""",numpy.cos(R1*R2),
]

bandtests = [
    """ (bind R1 R2 R3) """,numpy.array([R1,R2,R3]),
    """ (bind R1 (+ R1 1)  (+ R1 2) (+ R1 3)) """,numpy.array([R1,R1+1,R1+2,R1+3]),
    """ (band R1 0) """,R1[0],
    ]

alltests = eqtests+mathtests+trigtests+bandtests




def main():

    line = lispy.buildParser()
    t = None
    
    rasters.setRasters({'R1': numpy.array([[1],[2]]),
                              'R2': numpy.array([[2],[4]]),
                              'R3': numpy.array([[33],[55]]),
                              'layer-1': numpy.array([[0],[4]])})

    debug.level = -1
    for it in range(0,len(alltests),2):
        t = alltests[it]
        v = alltests[it+1]
        print '-'*50
        print "Test expression: ",t
        try:
            lispy.rasterList=set()
            sexpr = line.parseString(t)
            e = treewalk.evaluate(sexpr.asList()[0])
            print "Evals to:\n",e
            skip = numpy.array(v) == numpy.array(None)
            if skip.any():
                print "Not checked"
            else:
                if (numpy.array(e) == numpy.array(v)).any():
                    print "Pass"
                else:
                    print "**FAIL**\nExpected:\n",v,"\nGot:\n",e

            #print "Uses rasters ",lispy.rasterList
        except ParseFatalException, pfe:
            print "Error:", pfe.msg
            print line(pfe.loc,t)
            print pfe.markInputline()
        print

if __name__=="__main__":
    main()


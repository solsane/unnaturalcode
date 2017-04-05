from __future__ import print_function

import pymitlm
#import numpy as np
#import numpy.linalg as nl
from copy import copy
print("import")
w = 5
padding = w * 2
test = "a b c d e f g h"
cd = len(test.split(" "))
cstart = padding
cend = padding + cd
test = "S " * padding + test + " E" * padding
with open("testcorpus", "w") as testcorpus:
    for i in range(0, 1000):
        print(test, file=testcorpus)
    print("S " * padding + "a b c d e f g H"  + " E" * padding, file=testcorpus)
    print("S " * padding + "a b c d e f g H"  + " E" * padding, file=testcorpus)
    print("S " * padding + "a b c x e f g h"  + " E" * padding, file=testcorpus)
    print("S <unk> E", file=testcorpus)
m = pymitlm.PyMitlm("testcorpus", 10, "KN", True)
print("init")
def testx(string):
      print("Testing %s" % string)
      print("Result %e" % m.xentropy(string))
testx("a b c d e f g h E E")
#testx("a b c a e f g")
testx("a b c x e f g h E E")
testx("x")
testx("a")
testx("a x")

#assert False
arr = test.split(" ")
d = len(arr)

#A = (np.tril(np.ones((d,d)),0) - np.tril(np.ones((d,d)),-w))
##print A
#pA = nl.inv(A)
#print(pA)
for f in range(cstart,cend):
    #print m.xentropy(test)
    tarr = copy(arr)
    print(tarr[f])
    tarr[f] = "XXX"
    #print repr(arr)
    ents = []
    x = []
    for i in range(0, d):
            qarr = tarr[max(0,i+1-w):i+1]
            #print(len(qarr))
            q = " ".join(qarr)
            #print q
            ents.append(m.xentropy(q))
            #print(sum([ents[j] for j in xrange(i,-1,-w)]))
            #print(ents[i-1:-1:-w])
            if i >= cstart and i < cend:
                x.append(sum([ents[j] for j in xrange(i,-1,-w)])
                     -sum([ents[j] for j in xrange(i-1,-1,-w)]))
            else: x.append(0)
            #print ents[i-1]
    #ents = np.array(ents)
    #print(ents)
    #i = np.dot(pA,ents)
    #x[0:w] = 0
    #x[w+cd:d] = 0
    #print(np.dot(ents,pA[11,:]))
    
    #print(" ".join(map(str, (i[11], x[11]))))
    print(str(f) + " vs " + str(max(enumerate(x), key=lambda x: x[1])))
    

import pymitlm
print "import"
m = pymitlm.PyMitlm("testcorpus", 10, "ModKN", True)
print "init"
print m.xentropy("a b c d e")

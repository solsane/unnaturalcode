import pymitlm
print "import"
m = pymitlm.PyMitlm("pymitlm/testcorpus", 10, "ModKN", True)
print "init"
print m.xentropy("a b c d e")
print m.predict("a b c d")

# other code in repo is py2 but this only works on py3?
try:
    from .pymitlm import *
except:
    from pymitlm import *
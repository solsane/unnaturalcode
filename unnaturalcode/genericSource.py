#!/usr/bin/python
#    Copyright 2013, 2014 Joshua Charles Campbell, Alex Wilson, Eddie Santos
#
#    This file is part of UnnaturalCode.
#    
#    UnnaturalCode is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    UnnaturalCode is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with UnnaturalCode.  If not, see <http://www.gnu.org/licenses/>.


from unnaturalcode.ucUtil import *
from unnaturalcode.unnaturalCode import *
from logging import debug, info, warning, error
import urllib
import re

allWhitespace = re.compile('^\s+$')
whitespace = re.compile('\s')


class genericLexeme(ucLexeme):
    
    @classmethod
    def stringify_build(cls, t, v):
        """
        Stringify a lexeme: produce a string describing it. For MITLM the
        string can't contain any whitespace.
        """
        if t is None:
            t = "UNKNOWN"
        if len(v) > 20:
            v = v[0:20]
        # quote all whitespace, colons, backslashes, control and unicode, and quotes
        v = urllib.quote(v, "!#$%&()*+,-./;<=>?@[]^_`{|}~")
        assert(re.match('\w+$', t) is not None), "Lexeme type should be a word %s %s." % (t, v)
        return t + ":" + v
        
    

class genericSource(ucSource):
    
    lexemeClass = genericLexeme

    def deLex(self):
        line = 1
        col = 0
        src = ""
        for l in self:
            for i in range(line, l.start.line):
                src += os.linesep
                col = 0
                line += 1
            for i in range(col, l.start.col):
                src += " "
                col += 1
            src += l.val
            col += len(l.val)
            nls = l.val.count(os.linesep)
            if (nls > 0):
                line += nls
                col = len(l.val.splitlines().pop())
        return src
    
    def scrubbed(self):
        """Clean up generic source code removing extra whitespace tokens and comments"""
        ls = copy(self)
        assert len(ls)
        i = 0
        r = []
        for i in range(0, len(ls)):
            #if allWhitespace.match(ls[i].val) and i < len(ls)-1 and allWhitespace.match(ls[i+1]):
                #continue
            if allWhitespace.match(ls[i].val):
                continue
            else:
                val = ls[i].val
                val = whitespace.sub("", val)
                r.append(ls[i].__class__((ls[i][0], val, ls[i][2], ls[i][3], ls[i][4])))
        assert len(r)
        return genericSource(r)


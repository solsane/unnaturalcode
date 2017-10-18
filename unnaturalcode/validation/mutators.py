#    Copyright 2013, 2014, 2017 Joshua Charles Campbell
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

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical


from copy import copy
from random import randint

from unnaturalcode.change import Change

class Mutators(object):

    def delete_token(self, v_file):
        """Delete a random token from a file."""
        ls = copy(v_file.good_lexed)
        assert ls.n_lexemes > 2, repr([ls.n_lexemes, ls.lexemes])
        idx = randint(1, ls.n_lexemes-2)
        after = ls.lexemes[idx+1]
        token = ls.pop(idx)
        if token.type == 'ENDMARKER':
          return self.delete_token(v_file)
        change = Change(
            'delete',
            idx,
            idx+1,
            idx,
            idx,
            [token],
            []
            )
        DEBUG("Deleted %i (%s)" % (idx, token[4]))
        v_file.mutate(ls, change)
        return None
            
    def insert_token(self, v_file):
        ls = copy(v_file.good_lexed)
        token = ls[randint(0, ls.n_lexemes-1)]
        pos = randint(1, ls.n_lexemes-2)
        inserted = ls.insert(pos, [token])
        if inserted[0].type == 'ENDMARKER':
          return self.insertRandom(v_file)
        change = Change(
            'insert',
            idx,
            idx,
            idx,
            idx+1,
            [],
            [token])
        v_file.mutate(ls, change)
        return None
            
    def replace_token(self, v_file):
        ls = copy(v_file.good_lexed)
        token = ls[randint(0, ls.n_lexemes-1)]
        pos = randint(1, ls.n_lexemes-2)
        oldToken = ls.pop(pos)
        if oldToken.type == 'ENDMARKER':
          return self.replaceRandom(v_file)
        inserted = ls.insert(pos, [token])
        if inserted[0].type == 'ENDMARKER':
          return self.replaceRandom(v_file)
        change = Change(
            'replace',
            idx,
            idx+1,
            idx,
            idx+1,
            [token],
            [inserted])
        v_file.mutate(ls, change)
        return None
        
    def dedentRandom(self, v_file):
        s = copy(v_file.original)
        lines = s.splitlines(True);
        while True:
          line = randint(0, len(lines)-1)
          if beginsWithWhitespace.match(lines[line]):
            lines[line][0] = ''
            break
        v_file.mutatedLexemes = v_file.lm("".join(lines))
        v_file.mutatedLocation = pythonLexeme.fromTuple((token.INDENT, ' ', (line+1, 0), (line+1, 0)))
        return None
        
    def indentRandom(self, v_file):
        s = copy(v_file.original)
        lines = s.splitlines(True);
        line = randint(0, len(lines)-1)
        if beginsWithWhitespace.match(lines[line]):
          lines[line] = lines[line][0] + lines[line]
        else:
          lines[line] = " " + lines[line]
        v_file.mutatedLexemes = v_file.lm("".join(lines))
        v_file.mutatedLocation = pythonLexeme.fromTuple((token.INDENT, ' ', (line+1, 0), (line+1, 0)))
        return None
    
    def punctRandom(self, v_file):
        s = copy(v_file.original)
        charPos = randint(1, len(s)-1)
        linesbefore = s[:charPos].splitlines(True)
        line = len(linesbefore)
        lineChar = len(linesbefore[-1])
        c = s[charPos:charPos+1]
        if (funny.match(c)):
          new = s[:charPos] + s[charPos+1:]
          v_file.mutatedLexemes = v_file.lm(new)
          v_file.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
          return None
        else:
          return self.punctRandom(v_file)
    
    #def keyRandom(self, v_file):
        #s = copy(v_file.original)
        
    def nameRandom(self, v_file):
      return self.deleteWordRandom(v_file)

    def insertWordRandom(self, v_file):
        s = copy(v_file.original)
        while True:
          char = s[randint(1, len(s)-1)]
          charPos = randint(1, len(s)-1)
          linesbefore = s[:charPos].splitlines(True)
          line = len(linesbefore)
          lineChar = len(linesbefore[-1])
          c = s[charPos:charPos+1]
          if (name.match(char)):
            break
        new = s[:charPos] + char + s[charPos:]
        v_file.mutatedLexemes = v_file.lm(new)
        v_file.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def deleteWordRandom(self, v_file):
        s = copy(v_file.original)
        while True:
          charPos = randint(1, len(s)-1)
          linesbefore = s[:charPos].splitlines(True)
          line = len(linesbefore)
          lineChar = len(linesbefore[-1])
          c = s[charPos:charPos+1]
          if (name.match(c)):
            break
        new = s[:charPos] + s[charPos+1:]
        v_file.mutatedLexemes = v_file.lm(new)
        v_file.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None
        
    def insertPunctRandom(self, v_file):
        s = copy(v_file.original)
        if not punct.search(s):
          return "No punctuation"
        while (True):
          char = s[randint(1, len(s)-1)]
          if (punct.match(char)):
            break
        charPos = randint(1, len(s)-1)
        linesbefore = s[:charPos].splitlines(True)
        line = len(linesbefore)
        lineChar = len(linesbefore[-1])
        c = s[charPos:charPos+1]
        new = s[:charPos] + char + s[charPos:]
        v_file.mutatedLexemes = v_file.lm(new)
        v_file.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def deleteNumRandom(self, v_file):
        s = copy(v_file.original)
        if not numeric.search(s):
          return "No numbers"
        positions = [x.start() for x in numeric.finditer(s)]
        while True:
          if (len(positions) == 1):
            charPos = positions[0]
          else:
            charPos = positions[randint(1, len(positions)-1)]
          linesbefore = s[:charPos].splitlines(True)
          line = len(linesbefore)
          lineChar = len(linesbefore[-1])
          c = s[charPos:charPos+1]
          if (numeric.match(c)):
            break
        new = s[:charPos] + s[charPos+1:]
        v_file.mutatedLexemes = v_file.lm(new)
        v_file.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def insertNumRandom(self, v_file):
        s = copy(v_file.original)
        char = str(randint(0, 9))
        charPos = randint(1, len(s)-1)
        linesbefore = s[:charPos].splitlines(True)
        line = len(linesbefore)
        lineChar = len(linesbefore[-1])
        c = s[charPos:charPos+1]
        new = s[:charPos] + char + s[charPos:]
        v_file.mutatedLexemes = v_file.lm(new)
        v_file.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def deletePunctRandom(self, v_file):
        s = copy(v_file.original)
        if not punct.search(s):
          return "No punctuation"
        while True:
          charPos = randint(1, len(s)-1)
          linesbefore = s[:charPos].splitlines(True)
          line = len(linesbefore)
          lineChar = len(linesbefore[-1])
          c = s[charPos:charPos+1]
          if (punct.match(c)):
            break
        new = s[:charPos] + s[charPos+1:]
        v_file.mutatedLexemes = v_file.lm(new)
        v_file.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def colonRandom(self, v_file):
        s = copy(v_file.original)
        while True:
          charPos = randint(1, len(s)-1)
          linesbefore = s[:charPos].splitlines(True)
          line = len(linesbefore)
          lineChar = len(linesbefore[-1])
          c = s[charPos:charPos+1]
          if (c == ':'):
            break
        new = s[:charPos] + s[charPos+1:]
        v_file.mutatedLexemes = v_file.lm(new)
        v_file.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

def get_mutation_by_name(name):
    name = name.replace('-', '_')
    return getattr(Mutators(), name)

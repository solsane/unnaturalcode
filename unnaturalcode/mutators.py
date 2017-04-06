from copy import copy
from random import randint


class Mutators(object):

    def deleteRandom(self, vFile):
        """Delete a random token from a file."""
        ls = copy(vFile.scrubbed)
        idx = randint(1, len(ls)-2)
        after = ls[idx+1]
        token = ls.pop(idx)
        if token.type == 'ENDMARKER':
          return self.deleteRandom(vFile)
        vFile.mutate(ls, ls[idx-1], token, after)
        return None
            
    def insertRandom(self, vFile):
        ls = copy(vFile.scrubbed)
        token = ls[randint(0, len(ls)-1)]
        pos = randint(1, len(ls)-2)
        inserted = ls.insert(pos, token)
        if inserted[0].type == 'ENDMARKER':
          return self.insertRandom(vFile)
        vFile.mutate(ls, ls[pos-1], inserted[0], ls[pos+1])
        return None
            
    def replaceRandom(self, vFile):
        ls = copy(vFile.scrubbed)
        token = ls[randint(0, len(ls)-1)]
        pos = randint(1, len(ls)-2)
        oldToken = ls.pop(pos)
        if oldToken.type == 'ENDMARKER':
          return self.replaceRandom(vFile)
        inserted = ls.insert(pos, token)
        if inserted[0].type == 'ENDMARKER':
          return self.replaceRandom(vFile)
        vFile.mutate(ls, ls[pos-1], inserted[0], ls[pos+1])
        return None
        
    def dedentRandom(self, vFile):
        s = copy(vFile.original)
        lines = s.splitlines(True);
        while True:
          line = randint(0, len(lines)-1)
          if beginsWithWhitespace.match(lines[line]):
            lines[line][0] = ''
            break
        vFile.mutatedLexemes = vFile.lm("".join(lines))
        vFile.mutatedLocation = pythonLexeme.fromTuple((token.INDENT, ' ', (line+1, 0), (line+1, 0)))
        return None
        
    def indentRandom(self, vFile):
        s = copy(vFile.original)
        lines = s.splitlines(True);
        line = randint(0, len(lines)-1)
        if beginsWithWhitespace.match(lines[line]):
          lines[line] = lines[line][0] + lines[line]
        else:
          lines[line] = " " + lines[line]
        vFile.mutatedLexemes = vFile.lm("".join(lines))
        vFile.mutatedLocation = pythonLexeme.fromTuple((token.INDENT, ' ', (line+1, 0), (line+1, 0)))
        return None
    
    def punctRandom(self, vFile):
        s = copy(vFile.original)
        charPos = randint(1, len(s)-1)
        linesbefore = s[:charPos].splitlines(True)
        line = len(linesbefore)
        lineChar = len(linesbefore[-1])
        c = s[charPos:charPos+1]
        if (funny.match(c)):
          new = s[:charPos] + s[charPos+1:]
          vFile.mutatedLexemes = vFile.lm(new)
          vFile.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
          return None
        else:
          return self.punctRandom(vFile)
    
    #def keyRandom(self, vFile):
        #s = copy(vFile.original)
        
    def nameRandom(self, vFile):
      return self.deleteWordRandom(vFile)

    def insertWordRandom(self, vFile):
        s = copy(vFile.original)
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
        vFile.mutatedLexemes = vFile.lm(new)
        vFile.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def deleteWordRandom(self, vFile):
        s = copy(vFile.original)
        while True:
          charPos = randint(1, len(s)-1)
          linesbefore = s[:charPos].splitlines(True)
          line = len(linesbefore)
          lineChar = len(linesbefore[-1])
          c = s[charPos:charPos+1]
          if (name.match(c)):
            break
        new = s[:charPos] + s[charPos+1:]
        vFile.mutatedLexemes = vFile.lm(new)
        vFile.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None
        
    def insertPunctRandom(self, vFile):
        s = copy(vFile.original)
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
        vFile.mutatedLexemes = vFile.lm(new)
        vFile.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def deleteNumRandom(self, vFile):
        s = copy(vFile.original)
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
        vFile.mutatedLexemes = vFile.lm(new)
        vFile.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def insertNumRandom(self, vFile):
        s = copy(vFile.original)
        char = str(randint(0, 9))
        charPos = randint(1, len(s)-1)
        linesbefore = s[:charPos].splitlines(True)
        line = len(linesbefore)
        lineChar = len(linesbefore[-1])
        c = s[charPos:charPos+1]
        new = s[:charPos] + char + s[charPos:]
        vFile.mutatedLexemes = vFile.lm(new)
        vFile.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def deletePunctRandom(self, vFile):
        s = copy(vFile.original)
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
        vFile.mutatedLexemes = vFile.lm(new)
        vFile.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

    def colonRandom(self, vFile):
        s = copy(vFile.original)
        while True:
          charPos = randint(1, len(s)-1)
          linesbefore = s[:charPos].splitlines(True)
          line = len(linesbefore)
          lineChar = len(linesbefore[-1])
          c = s[charPos:charPos+1]
          if (c == ':'):
            break
        new = s[:charPos] + s[charPos+1:]
        vFile.mutatedLexemes = vFile.lm(new)
        vFile.mutatedLocation = pythonLexeme.fromTuple((token.OP, c, (line, lineChar), (line, lineChar)))
        return None

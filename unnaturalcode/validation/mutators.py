from copy import copy
from random import randint

class Mutators(object):

    def delete_token(self, v_file):
        """Delete a random token from a file."""
        ls = copy(v_file.good_scrubbed)
        idx = randint(1, ls.n_lexemes-2)
        after = ls.lexemes[idx+1]
        token = ls.pop(idx)
        if token.type == 'ENDMARKER':
          return self.delete_token(v_file)
        v_file.mutate(ls)
        return None
            
    def insert_token(self, v_file):
        ls = copy(v_file.good_scrubbed)
        token = ls[randint(0, len(ls)-1)]
        pos = randint(1, len(ls)-2)
        inserted = ls.insert(pos, token)
        if inserted[0].type == 'ENDMARKER':
          return self.insertRandom(v_file)
        v_file.mutate(ls, ls[pos-1], inserted[0], ls[pos+1])
        return None
            
    def replace_token(self, v_file):
        ls = copy(v_file.good_scrubbed)
        token = ls[randint(0, len(ls)-1)]
        pos = randint(1, len(ls)-2)
        oldToken = ls.pop(pos)
        if oldToken.type == 'ENDMARKER':
          return self.replaceRandom(v_file)
        inserted = ls.insert(pos, token)
        if inserted[0].type == 'ENDMARKER':
          return self.replaceRandom(v_file)
        v_file.mutate(ls, ls[pos-1], inserted[0], ls[pos+1])
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

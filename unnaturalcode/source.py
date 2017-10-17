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
import sys, os

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

from copy import copy
from six import StringIO, string_types

if hasattr(sys, 'maxint'): # Python 2/3 Compatibility
  maxint = sys.maxint
else:
  maxint = sys.maxsize

PARANOID = os.getenv("PARANOID", False)

class Position(tuple):
    if PARANOID:
        def __init__(self, *args):
            assert len(self) == 3
            assert isinstance(self[0], int)
            assert isinstance(self[1], int)
            if self[2] is not None:
                assert isinstance(self[2], int)
            assert self[0] >= 1
            assert self[1] >= 0
            if self[2] is not None:
                assert self[2] >= 0
    
    def __getattr__(self, name):
        if name[0] == 'l':
            return self[0]
        elif name[0] == 'c':
            return self[1]
        elif name[0] == 'i':
            return self[2]
        else:
            raise AttributeError()
    
    def __str__(self):
        return str(self[0]) + ":" + str(self[1]) + ":" + str(self[2])
    
    def __eq__(self, other):
        return (self[0] == other[0]) and (self[1] == other[1])
    
    def __ne__(self, other):
      return not self.__eq__(other)
    
    def __gt__(self, other):
        return (self[0] > other[0]) or ((self[0] == other[0]) and (self[1] > other[1]))
      
    def __lt__(self, other):
        return not self.__gt__(other)
    
    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)
      
    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)
    
    @classmethod
    def from2Tuple(cls, tup, lines):
        l, c = tup
        # sometimes python reports the same position on two differetn lines
        # i.e.
        # (5, 6, 123) == (6, 0, 123)
        if (l < len(lines)) and (lines[l-1]+c >= lines[l]+0):
            c -= (lines[l] - lines[l-1])
            l += 1
        return cls((l, c, lines[l-1]+c))
        

class Lexeme(tuple):
    if PARANOID:
        def __init__(self, *args):
            assert len(self) == 5
            assert self[0]
            assert isinstance(self[0], string_types), self[0]
            assert len(self[0]) > 0
            assert isinstance(self[1], string_types)
            assert isinstance(self[2], Position)
            assert isinstance(self[3], Position)
            assert self[2] <= self[3], "%s > %s" % (self[2], self[3])
            assert isinstance(self[4], string_types)
            assert len(self[4]) > 0
            
    
    def __getattr__(self, name):
        if name == 'ltype' or name == 'type':
            return self[0]
        elif name == 'val' or name == 'value':
            return self[1]
        elif name == 'start':
            return self[2]
        elif name == 'end':
            return self[3]
        raise AttributeError

    def comment(self):
        return False
    
    def last_line_columns(self):
        """
        How many columns this token takes on its last line. If it doesn't
        contain line breaks, just returns how many colums. If it does contain
        line breaks, returns columns from the .
        """
        if self[2][0] == self[3][0]:
            return self[3][1] - self[2][1]
        else:
            return self[3][1] + 1
    
    def lines(self):
        return self[3][0] - self[2][0]
     
    def chars(self):
        return self[3][2] - self[2][2]
    
    @classmethod
    def stringify_build(cls, t, v):
        if v:
            return v
        else:
            return '<'+t+'>'

    def stringify(self):
        return self.__class__.stringify_build(self.ltype, self.val)

    @classmethod
    def fromTuple(cls, tup):
        if len(args[0] == 4):
            t = (args[0][0], args[0][1], Position(args[0][2]), Position(args[0][3]), cls.stringify_build(args[0][0], args[0][1]))
        elif len(args[0] == 5):
            t = (args[0][0], args[0][1], Position(args[0][2]), Position(args[0][3]), args[0][4])
        else:
            raise TypeError("Constructor argument cant be " + str(type(args[0])))
        return cls(t)

    
    @classmethod
    def fromDict(cls, d):
        if isinstance(d, dict):
            t = (d['type'], d['value'],  Position(d['start']),  Position(d['end']), cls.stringify_build(d['type'], d['value']))
        else:
            raise TypeError("Constructor argument cant be " + str(type(d)))
        return cls(t)
    
    @classmethod
    def build(cls, *args):
        """Initialize a lexeme object."""
        if isinstance(args[0], cls):
            return args[0]
        elif len(args) == 4:
            t = (args[0], args[1], Position(args[2]), Position(args[3]), cls.stringify_build(args[0], args[1]))
        elif len(args) == 5:
            t = (args[0], args[1], Position(args[2]), Position(args[3]), args[4])
        else:
            raise TypeError("Constructor arguments cant be " + str(type(args)))
        return cls(t)
    
    def new_position(self, start, end):
        """Return a copy of this lexeme object but with the positions modified"""
        return self.__class__((self[0], self[1], start, end, self[4]))
                              
    def scoot(self, from_, to):
        """
        Return a copy of this lexeme object but with the positions shifted.
        """
        startL = self.start.l - from_.l + to.l 
        endL = self.end.l - from_.l + to.l 
        if self.start.l == from_.l:
            startC = self.start.c - from_.c + to.c
        else:
            startC = self.start.c
        if self.end.l == from_.l:
            endC = self.end.c - from_.c + to.c
        else:
            endC = self.end.c
        startI = self.start.i - from_.i + to.i
        endI = self.end.i - from_.i + to.i
        start = Position((startL, startC, startI))
        end = Position((endL, endC, endI))
        return self.new_position(start, end)
    
    #def position_after(self):
        #if self.value[-1] == '\n':
            #return Position((self.end.l+1, 0, self.end.i+1))
        #else:
            #return Position((self.end.l, self.end.c+1, self.end.i+1))

    def __str__(self):
        return self[4]
    
    def approx_equal(self, other):
        return self.type == other.type and self.value == other.value

def lexemes_approx_equal(a, b):
    if len(a) != len(b):
        return False
    for i in range(0, len(a)):
        if not a[i].approx_equal(b[i]):
            return False
    return True
    
class Source(object):
    """
    Base class for source code, essentially a list of lexemes that can do
    a bunch of stuff.
    
    Remember to override lexeme_class in subclasses so that the code here
    fills the source list with lexemes of the correct class!
    """
  
    lexeme_class = Lexeme
    
    def lex(self, code):
        """
        Perform lexical analysis, return the result.
        """
        raise NotImplementedError()

    def __init__(self, lexed=None, text=None, **kwargs):
        self.text = text
        if isinstance(lexed, Source):
            assert isinstance(lexed.lexemes, list)
            self.lexemes = copy(lexed.lexemes)
        elif isinstance(lexed, list):
            self.lexemes = [
                self.lexeme_class(i) for i in lexed
                ]
        elif lexed is None:
            self.lexemes = lexed
        else:
            raise AttributeError(type(lexed).__name__)
        self.lexer_args = kwargs
        self.linesep = None
        if self.lexemes is None and self.text is None:
            raise AttributeError(type(lexed).__name__)
        elif self.lexemes is None:
            self.compute_line_char_indices()
            self.lex()
            if PARANOID:
                self.check()
        elif self.text is None:
            self.text = self.de_lex()
        assert self.lexemes is not None
        assert self.text is not None
    
    def __copy__(self):
        return self.__class__(
            lexed=copy(self.lexemes), 
            text=self.text, 
            **self.lexer_args)
    
    @property
    def n_lexemes(self):
        return len(self.lexemes)

    def guess_linesep(self):
        if self.text is not None:
            if '\r' in self.text and '\n' in self.text:
                self.linesep = '\r\n'
                return
            elif '\n' in self.text:
                self.linesep = '\n'
                return
            elif '\r' in self.text:
                self.linesep = '\r'
                return
        if self.lexemes is not None:
            for l in self.lexemes:
                if '\r' in l.value and '\n' in l.value:
                    self.linesep = '\r\n'
                    return
                elif '\n' in l.value:
                    self.linesep = '\n'
                    return
                elif '\r' in l.value:
                    self.linesep = '\r'
                    return
            for i in range(1, len(self.lexemes)):
                cur = self.lexemes[i]
                prev = self.lexemes[i-1]
                if cur.start.l > prev.end.l:
                    distance = cur.start.i - prev.end.i
                    distance -= 1 # tokens don't overlap
                    distance -= cur.start.c # remove tokens
                    lines = cur.start.l - prev.end.l
                    if distance == (lines * 2):
                        self.linesep = '\r\n'
                        return
                    elif distance == lines:
                        self.linesep = '\n'
                        return
        self.linesep = os.linesep # give up
        return
    
    def compute_line_char_indices(self):
        assert self.text is not None
        assert not hasattr(self, 'line_char_indices')
        if self.linesep is None:
            self.guess_linesep()
        if '\r' in self.text and '\n' not in self.text:
            raise NotImplementedError("I don't understand mac format line endings!")
        lpos = 0
        lines = [0]
        while True:
            lpos = self.text.find(self.linesep, lpos)
            if lpos < 0:
                break
            lpos += len(self.linesep)
            lines.append(lpos)
        assert len(lines) == (self.text.count(self.linesep) + 1), repr((
            len(lines),
            lines,
            self.text
            ))
        # add a ghost newline to end of file if none
        if not self.text.endswith(self.linesep):
            lines.append(len(self.text)+len(self.linesep))
        self.line_char_indices = lines
    
    def compute_line_lexeme_indices(self):
        assert self.lexemes is not None
        l = 0
        lines = [0]
        for i in range(0, len(self.lexemes)):
            lexeme = self.lexemes[i]
            if lexeme.start.line > l:
                for li in range(l+1, lexme.start.line+1):
                    assert len(lines) == li
                    lines.append(i)
                l = lexeme.start.line
    
    def get_line_start(self, line_nr):
        if self.line_char_indices is None:
            self.compute_line_char_indices()
        return self.line_char_indices[line_nr]
    
    def char_i_to_pos(self, i):
        if self.line_char_indices is None:
            self.compute_line_char_indices()
        line = bisect_right(self.line_char_indices, i)
        col = i-self.line_char_indices[line-1]
        return Position(line, col, i)
    
    def char_lc_to_pos(self, l, c):
        if self.line_char_indices is None:
            self.compute_line_char_indices()
        i = self.line_char_indices[l]+c
        return Position(l, c, i)
    
    
    def settle(self):
        """
        Contents may settle during shipping.
        """
        first = self.lexemes[0].start
        self.lexemes = [
            l.scoot(first, Position(0,1,0)) for l in self.lexemes
            ]
        if self.text is not None:
            self.text = self.text[first.i:]
        if PARANOID:
            self.check()
        return self
    
    def check(self, start=0, end=maxint):
        if self.linesep is None:
            self.guess_linesep()
        start = max(start, 0)
        end = min(end, len(self.lexemes))
        #debug(str(start) + "-" + str(end))
        for i in range(start, end):
            cur = self.lexemes[i]
            assert isinstance(cur, self.lexeme_class)
            assert self.text[cur.start.i:cur.end.i] == cur.value, (
                "%s %s %s %s" % (repr(self.text[cur.start.i:cur.end.i]),
                            repr(cur.value),
                            repr(cur.start),
                            repr(cur.end)))
            lines = cur.end.l - cur.start.l
            value = cur.value
            assert lines == value.count(self.linesep), (
                " ".join(map(repr, [
                        cur.start,
                        cur.end,
                        lines,
                        value
                    ]))
                )
        for i in range(start+1, end):
            cur = self.lexemes[i]
            prev = self.lexemes[i-1]
            # reminder: these are python range-style start,end pairs
            # so the character at end is after the end of the lexeme
            assert prev.end <= cur.start, repr(cur)
            assert prev.end.i <= cur.start.i
            if prev.end.l < cur.start.l:
                assert prev.end.i < cur.start.i
            if prev.end.c < cur.start.c:
                assert prev.end.i < cur.start.i
            if prev.end.l == cur.start.l and prev.end.c == cur.start.c:
                assert prev.end.i == cur.start.i
            lines = cur.start.l - prev.end.l
            space = self.text[prev.end.i:cur.start.i]
            if cur.start.i < len(self.text):
                assert lines == space.count(self.linesep), (
                    os.linesep.join(map(repr, ["Space between tokens contains wrong"
                                " number of newlines.",
                            prev,
                            cur,
                            lines,
                            space
                        ]))
                    )
    
    def extend(self, x):
        if x.lexemes is None or len(x.lexemes) == 0: # no-op
            return self.lexemes
        assert isinstance(x, self.__class__)
        if self.lexemes is None or len(self.lexemes) == 0:
            self.lexemes = copy(x.lexemes)
            self.text = x.text
            self.line_char_indices = value.line_char_indices
            self.line_lexeme_indices = value.line_lexeme_indices
            return self.lexemes
        from_ = x[0].start
        after = self.lexemes[-1].after_pos()
        scooted = [
                l.scoot(from_, after) for l in x.lexemes
            ]
        self.lexemes = self.lexemes + scooted
        self.text += x.text[from_.i:]
        return self.scooted
    
    def append(self, x):
        raise NotImplementedError()
    
    @property
    def start(self):
        if len(self.lexemes) > 0:
            return self.lexemes[0].start
        else:
            return Position((0,1,0))
      
    @property
    def end(self):
        if len(self.lexemes) > 0:
            return self.lexemes[-1].end
        else:
            return Position((0,1,0))
    
    #def position_after(self):
        #if len(self.lexemes) > 0:
            #return self.lexemes[-1].position_after()
        #else:
            #return Position((0,1,0))
        

    def insert(self, i, x):
        assert i <= len(self.lexemes), str(i) + " " + str(len(self.lexemes))
        assert i >= 0
        if isinstance(x, list):
            x = self.__class__(x)
        if len(x.lexemes) == 0: # no-op
            return self.lexemes
        assert isinstance(x, self.__class__)
        before = self.lexemes[0:i]
        after = self.lexemes[i:len(self.lexemes)]
        
        if len(after) > 0:
            to_x = after[0].start
        elif len(before) > 0:
            to_x = before[-1].end
        else:
            to_x = Position((0,1,0))
        first_x = x.start
        after_x = x.end
        scooted = [
                l.scoot(first_x, to_x) for l in x.lexemes
                ]
        part = before + scooted
        
        if len(part) > 0:
            to_after = part[-1].end
        else:
            to_after = Position((0,1,0))
        if len(after) > 0:
            first_after = after[0].start
        else:
            first_after = Position((0,1,0))
            self.lexemes = (
                part
                + [
                    l.scoot(first_after, to_after) for l in after
                    ]
                )
        
        self.line_char_indices = None
        self.line_lexeme_indices = None
        
        self.text = (self.text[:to_x.i] 
                     + x.text[first_x.i:after_x.i]
                     + self.text[to_x.i:])
        
        if PARANOID:
            self.check()
        return scooted
    
    def delete(self, i, j):
        assert i < len(self.lexemes)
        assert i >= 0
        assert j <= len(self.lexemes)
        assert i >= 0
        assert j >= i
        if i == j:
            return []
        removed = self.lexemes[i:j]
        from_ = removed[-1].end
        to = removed[0].start
        self.text = (
            self.text[:to.i] + self.text[from_.i:])
        self.lexemes = (
            self.lexemes[:i]
            + [
                l.scoot(from_, to) for l in self.lexemes[j:]
                ]
            )
        if PARANOID:
          self.check()
        return removed
    
    def pop(self, i):
        removed = self.delete(i, i+1)
        assert len(removed) == 1
        return removed[0]
    
    def replace(self, i, j, x):
        removed = self.delete(i, j)
        self.insert(i, x)
        return removed

    def scrubbed(self):
        raise NotImplementedError()
        
    def whitespace(self, lines, cols, chars):
        """
        compute a string with chars characters of whitespace with lines number
        of line breaks and cols number of cols in the last line
        """
        extra = chars - (lines * len(self.linesep) + cols)
        assert extra >= 0, repr((
            lines,
            cols,
            chars,
            extra
            ))
        return " " * extra + self.linesep * lines + " " * cols
    
    def de_lex(self):
        assert self.text is None
        if self.linesep is None:
            self.guess_linesep()
        line = 1
        col = 0
        idx = 0
        src = StringIO()
        for j in range(0, len(self.lexemes)):
            l = self.lexemes[j]
            lines = l.start.line - line
            if lines == 0:
                cols = l.start.col - col
            else:
                cols = l.start.col
            chars = l.start.index_ - idx
            src.write(self.whitespace(lines, cols, chars))
            src.write(l.value)
            line = l.end.line
            col = l.end.column
            idx = l.end.idx
        src.flush()
        self.text = src.getvalue()
        return self.text
    
# rwfubmqqoiigevcdefhmidzavjwg

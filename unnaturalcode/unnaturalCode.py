#    Copyright 2013, 2014 Joshua Charles Campbell
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
import sys, os, zmq
import logging
from logging import debug, info, warning, error
from copy import copy

if hasattr(sys, 'maxint'): # Python 2/3 Compatibility
  maxint = sys.maxint
else:
  maxint = sys.maxsize

zctx = None

ucParanoid = os.getenv("PARANOID", False)

@singleton
class unnaturalCode(object):
    """Singleton class for UC."""
    
    def __init__(self, logFilePath=None, logLevel=None):
        """Initialize global context."""
        self.logFilePath = (logFilePath or os.getenv("ucLogFile", "/tmp/ucLog-%i" % os.getpid()))
        self.logLevel = (logLevel or os.getenv("ucLogLevel", "DEBUG").upper())
        # from http://docs.python.org/2/howto/logging.html#logging-basic-tutorial 2013-10-04
        # LICENSE: PSF
        numeric_level = getattr(logging, self.logLevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        # end from
        if not logging.getLogger():
            logging.basicConfig(filename=self.logFilePath, level=numeric_level)
        debug("UC Init")
        global zctx
        if not zctx:
            self.zctx = zmq.Context()
            zctx = self.zctx
        self.forceTrain = toBool(os.getenv("ucForceTrain", "false"))
        self.forceValidate = toBool(os.getenv("ucValidate", "false"))
        
class ucPos(tuple):
    def __new__(cls, *args):
        if isinstance(args[0], ucPos):
            return args[0]
        elif len(args) == 2:
            l = args[0]
            c = args[1]
        elif isinstance(args[0], tuple):
            (l, c) = args[0]
        elif isinstance(args[0], list):
            (l, c) = args[0]
        else:
          raise TypeError("Bad constructor arguments.")
        return tuple.__new__(cls, (l, c))
    
    if ucParanoid:
        def __init__(self, *args):
            assert isinstance(self[0], int)
            assert isinstance(self[1], int)
            assert self[0] >= 1
            assert self[1] >= 0
    
    def __getattr__(self, name):
        if name[0] == 'l':
          return self[0]
        elif name[0] == 'c':
          return self[1]
        raise AttributeError
    
    def __str__(self):
        return str(self[0]) + ":" + str(self[1])
    
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
      
class ucLexeme(tuple):
    if ucParanoid:
        def __init__(self, *args):
            assert len(self) == 5
            assert self[0]
            assert isinstance(self[0], basestring), self[0]
            assert len(self[0]) > 0
            assert isinstance(self[1], basestring)
            assert (len(self[1]) > 0 
                    or self[0] == "LMEndPadding"
                    or self[0] == "LMStartPadding"), repr(self)
            assert isinstance(self[2], ucPos)
            assert isinstance(self[3], ucPos)
            assert self[2] <= self[3], "%s > %s" % (self[2], self[3])
            assert isinstance(self[4], basestring)
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
    
    def columns(self):
        if self[2][0] == self[3][0]:
            return self[3][1] - self[2][1]
        else:
            return 0
    
    def lines(self):
         return self[3][0] - self[2][0]
    
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
            t = (args[0][0], args[0][1], ucPos(args[0][2]), ucPos(args[0][3]), cls.stringify_build(args[0][0], args[0][1]))
        elif len(args[0] == 5):
            t = (args[0][0], args[0][1], ucPos(args[0][2]), ucPos(args[0][3]), args[0][4])
        else:
            raise TypeError("Constructor argument cant be " + str(type(args[0])))
        return cls(t)

    
    @classmethod
    def fromDict(cls, d):
        if isinstance(d, dict):
            t = (d['type'], d['value'],  ucPos(d['start']),  ucPos(d['end']), cls.stringify_build(d['type'], d['value']))
        else:
            raise TypeError("Constructor argument cant be " + str(type(d)))
        return cls(t)
    
    @classmethod
    def build(cls, *args):
        """Initialize a lexeme object."""
        if isinstance(args[0], cls):
            return args[0]
        elif len(args) == 4:
            t = (args[0], args[1], ucPos(args[2]), ucPos(args[3]), cls.stringify_build(args[0], args[1]))
        elif len(args) == 5:
            t = (args[0], args[1], ucPos(args[2]), ucPos(args[3]), args[4])
        else:
            raise TypeError("Constructor arguments cant be " + str(type(args)))
        return cls(t)
        

    def __str__(self):
        return self[4]

    
class ucSource(list):

    """
    Base class for source code, essentially a list of lexemes that can do
    a bunch of stuff.
    
    Remember to override lexemeClass in subclasses so that the code here
    fills the source list with lexemes of the correct class!
    """
  
    lexemeClass = ucLexeme

    def __init__(self, value=[], **kwargs):
        if isinstance(value, basestring):
            self.extend(self.lex(value, **kwargs))
        elif isinstance(value, list):
            if len(value) == 0:
                return
            elif isinstance(value[0], dict):
                self.extend(map(self.lexemeClass.fromDict, value))
            else:
                self.extend(map(self.lexemeClass, value))
        else:
            raise AttributeError, type(value).__name__

    def settle(self):
        """Contents may settle during shipping."""
        first = ucPos(self[0].start)
        for i in range(0, len(self)):
            if (self[i].end.l - self[i].start.l) > 1:
                endL = self[i].start.l + 1
            else:
                endL = self[i].end.l
            if self[i].start.l == first.l:
                startL = 1
                startC = self[i].start.c - first.c
            else:
                startL = self[i].start.l - first.l-1
                startC = self[i].start.c
            if endL == first.l:
                endL = 1
                endC = self[i].end.c - first.c
            else:
                endL = endL - (first.l-1)
                endC = self[i].end.c
            self[i] = self[i].__class__((self[i][0], self[i][1], ucPos((startL, startC)), ucPos((endL, endC)), self[i][4]))
        if ucParanoid:
            self.check()
        return self
    
    def check(self, start=0, end=maxint):
      start = max(start, 0)
      end = min(end, len(self))
      #debug(str(start) + "-" + str(end))
      for i in range(start, end-1):
        assert isinstance(self[i], ucLexeme)
        assert self[i].end <= self[i+1].start, repr(self[i:i+2])
    
    if ucParanoid:
        def extend(self, arg):
            for a in arg:
                assert isinstance(a, ucLexeme)
            s = len(self)-1
            r = super(ucSource, self).extend(arg)
            if s >= 0:
                self.check(start=s)
            return r
    
        def append(self, *args):
            return self.extend(args)
      
    def insert(self, i, arg):
        assert i <= len(self), str(i) + " " + str(len(self))
        assert i >= 0
        if not isinstance(arg, list):
          arg = [arg]
        if not isinstance(arg, ucSource):
          arg = ucSource(arg)
        a = copy(arg)
        a.settle()
        width = 0
        if (a[0].start.l == a[-1].end.l):
          width = a[-1].end.c - a[0].start.c
        height = a[-1].end.l - a[0].start.l
        oldend = self[-1].end.l
        for j in range(0, len(a)):
          ((startL, startC), (endL, endC)) = (a[j].start, a[j].end)
          #info(repr(self[i-1]))
          #info(repr(a[j]))
          #info(repr(self[i]))
          if startL == 1:
            startC += self[i-1].end.c
          if endL == 1:
            endC += self[i-1].end.c
          startL += self[i-1].end.l-1
          endL += self[i-1].end.l-1
          a[j] = a[j].__class__((a[j][0], a[j][1], ucPos((startL, startC)), ucPos((endL, endC)), a[j][4]))
          #info(" >" + repr(self[i-1]))
          #info(" >" + repr(a[j]))
          #info(" >" + repr(self[i]))
        for j in range(i, len(self)):
          ((startL, startC), (endL, endC)) = (self[j].start, self[j].end)
          if startL == a[-1].end.l:
            startC += width+1
          if endL == a[-1].start.l:
            endC += width+1
          startL += height
          endL += height
          self[j:j+1] = [self[j].__class__((self[j][0], self[j][1], ucPos((startL, startC)), ucPos((endL, endC)), self[j][4]))]
        #info(" >>" + repr(self[i-1]))
        #info(" >>" + repr(a[0]))
        #info(" >>" + repr(self[i]))
        for j in range(0, len(a)):
          r = super(ucSource, self).insert(i+j, a[j])
        #info(" >>>" + repr(self[i-1]))
        #info(" >>>" + repr(self[i]))
        #info(" >>>" + repr(self[i+1]))
        #if ( self[-1].end.l > oldend +1):
          #info(str(self[-1].end.l) + " > " + str(oldend + 1))
          #assert(false, 'waugh!')
        if ucParanoid:
            self.check()
        return a
    
    def pop(self, i):
        assert i < len(self)
        assert i >= 0
        r = super(ucSource, self).pop(i)
        removedLines = r.lines()
        for j in range(i, len(self)):
          ((startL, startC), (endL, endC)) = (self[j].start, self[j].end)
          if startL == r.end.l:
            startC += r.start.c - r.end.c
            if endL == startL:
              endC += r.start.c - r.end.c
          startL -= r.lines()
          endL -= r.lines()
          self[j:j+1] = [self[j].__class__((self[j][0], self[j][1], ucPos((startL, startC)), ucPos((endL, endC)), self[j][4]))]
        if ucParanoid:
            self.check()
        return r

    def scrubbed(self):
        raise NotImplementedError
        
    if ucParanoid:
        def __setitem__(self, index, value):
            if isinstance(value, list):
                for i in value:
                    assert isinstance(i, ucLexeme)
            else:
                assert isinstance(value, ucLexeme)
            r = super(ucSource, self).__setitem__(index, value)
            if isinstance(index, int):
                self.check(index-1, index+2)
            return r
       
        # Taken from the python documentation: http://docs.python.org/2/reference/datamodel.html v2.7.5 November 2013
        # Licesne: PSF
        def __setslice__(self, i, j, seq):
            self[max(0, i):max(0, j):] = seq
        # End License
    
    def sort():
      raise TypeError("Je refuse!")
    
    def deLexWithCharPositions(self):
        from StringIO import StringIO
        line = 1
        col = 0
        src = StringIO()
        charpositions = {}
        for j in range(0, len(self)):
            l = self[j]
            if line < l[2][0]:
                src.write(os.linesep * (l[2][0] - line))
                col = 0
                line += (l[2][0] - line)
            if col < l[2][1]:
                src.write(" "  * (l[2][1] - col))
                col += (l[2][1] - col)
            #for i in range(len(src), len(src) + len(l[1])):
              #charpositions[i] = j
            src.write(l[1])
            nls = l[1].count(os.linesep)
            if (nls > 0):
                line += nls
                col = len(l[1].splitlines().pop())
            else:
                col += len(l[1])
        src.flush()
        return (src.getvalue(), charpositions)
        
    
    def deLex(self):
        src, charpositions = self.deLexWithCharPositions()
        return src
      
# rwfubmqqoiigevcdefhmidzavjwg

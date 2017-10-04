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

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

import sys
from copy import copy
import token
import tempfile
import py_compile

try:
  from cStringIO import StringIO
except ImportError:
  from io import StringIO

from unnaturalcode.util import *
from unnaturalcode.source import Source, Lexeme, Position
from unnaturalcode import flexibleTokenize
from unnaturalcode.compile_error import CompileError

COMMENT = 53

ws = re.compile('\s')

class pythonLexeme(Lexeme):
    
    @classmethod
    def stringify_build(cls, t, v):
        """
        Stringify a lexeme: produce a string describing it.
        In the case of comments, strings, indents, dedents, and newlines, and
        the endmarker, a string with '<CATEGORY-NAME>' is returned.  Else, its
        actual text is returned.
        """
        if t == 'COMMENT':
            return '<'+t+'>'
        # Josh though this would be a good idea for some strange reason:
        elif len(v) > 20 :
            return '<'+t+'>'
        elif ws.match(str(v)) :
            return '<'+t+'>'
        elif t == 'STRING' :
            return '<'+t+'>'
        elif len(v) > 0 :
            return v
        else:
            # This covers for <DEDENT> case, and also, probably some other
            # special cases...
            return '<' + t + '>'
    
    @classmethod
    def fromTuple(cls, tup, lines):
        if isinstance(tup[0], int):
            t0 = token.tok_name[tup[0]]
        else:
            t0 = tup[0]
        new = tuple.__new__(cls, (t0,
                                  tup[1], 
                                  Position.from2Tuple(tup[2], lines), 
                                  Position.from2Tuple(tup[3], lines),  
                                  cls.stringify_build(t0, tup[1])))
        return new
          
    def comment(self):
        return (self.ltype == 'COMMENT')
      

class pythonSource(Source):
    
    lexemeClass = pythonLexeme
    
    def lex(self, mid_line=False):
        
        tokGen = flexibleTokenize.generate_tokens(
            StringIO(self.text).readline,
            mid_line)
        self.lexemes = [pythonLexeme.fromTuple(t, self.line_char_indices)
                            for t in tokGen]
   
    def unCommented(self):
        assert len(self)
        return filter(lambda a: not a.comment(), copy(self))
    
    def scrubbed(self):
        """Clean up python source code removing extra whitespace tokens and comments"""
        ls = copy(self.lexemes)
        assert len(ls)
        i = 0
        r = []
        for i in range(0, len(ls)):
            if ls[i].comment():
                continue
            elif ls[i].ltype == 'NL':
                continue
            elif ls[i].ltype == 'NEWLINE' and i < len(ls)-1 and ls[i+1].ltype == 'NEWLINE':
                continue
            elif ls[i].ltype == 'NEWLINE' and i < len(ls)-1 and ls[i+1].ltype == 'INDENT':
                continue
            else:
                r.append(ls[i])
        assert len(r)
        return pythonSource(r)
    
    def check_syntax(self):
        temp_path = None
        errors = []
        with tempfile.NamedTemporaryFile(
                suffix=".py", 
                mode="w", 
                delete=False) as f:
            temp_path = f.name
            f.write(self.text)
        try:
            py_compile.compile(temp_path, temp_path+"c", doraise=True)
        except Exception as e:
            ei = sys.exc_info();
            success = False
            ERROR(e)
            ERROR(repr(e[1][1]))
            errors.append(CompileError(
                    filename=e.filename,
                    line=e.lineno
                ))
        os.unlink(temp_path)
        os.unlink(temp_path+"c")
        return errors


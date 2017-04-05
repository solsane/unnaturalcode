#!/usr/bin/python
#    Copyright 2017 Joshua Charles Campbell, Eddie Antonio Santos
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

from logging import debug, info, warning, error
import json
import subprocess
import tempfile
from unnaturalcode.unnaturalCode import ucLexeme, ucSource, ucPos
import os
from copy import copy

from unnaturalcode.jsTokenize import JSTokenizer
js = JSTokenizer()

class jsLexeme(ucLexeme):
    pass

class jsSource(ucSource):
  
    lexemeClass = ucLexeme
    
    def esprima_to_uc(self,d):
        string = d["value"]
        if d["type"] == "String":
            string = '"string"'
        if d["type"] == "Identifier":
            string = 'Identifier'
        if d["type"] == "Numeric":
            string = '0'
        elif d["type"] == "RegularExpression":
            string = '/regexp/'
        elif d["type"] == "Template":
            text = d["value"]
            assert len(text) >= 2
            if text.startswith('`'):
                if text.endswith('`'):
                    string = '`standalone-template`'
                elif text.endswith('${'):
                    string = '`template-head${'
                else:
                    raise Exception('Unhandled template literal: ' + text)
            elif text.startswith('}'):
                if text.endswith('`'):
                    string = '}template-tail`'
                elif text.endswith('${'):
                    string = '}template-middle${'
                else:
                    raise Exception('Unhandled template literal: ' + text)
            else:
                raise Exception('Unhandled template literal: ' + text)
        if " " in string:
            raise Exception('Whitespace in my string')
        return self.lexemeClass((
                    d["type"], 
                    d["value"], 
                    ucPos(d["loc"]["start"]["line"], d["loc"]["start"]["column"]),
                    ucPos(d["loc"]["end"]["line"], d["loc"]["end"]["column"]),
                    string, 
                ))
    
    def lex(self, code):
        #file_obj = tempfile.TemporaryFile('w+b')
        #file_obj.write(code.encode("UTF-8"))
        #file_obj.flush()
        #raw = tokenize_file(file_obj)
        raw = js.tokenize(code)
        return map(self.esprima_to_uc, raw)
        
    def check_syntax(self):
        #file_obj = tempfile.TemporaryFile('w+b')
        src, charpositions = self.deLexWithCharPositions()
        #file_obj.write(src.encode("UTF-8"))
        #file_obj.flush()
        raw = js.check_syntax(src)
        if len(raw) == 0:
            return (None, None, None, None, None)
        if raw['index'] in charpositions:
            #error(json.dumps(raw, indent=2))
            #error(json.dumps(charpositions[raw['index']]))
            tok = charpositions[raw['index']]
            return (None, raw['lineNumber'], None, tok.value, raw['description'])
        else:
            return (None, raw['lineNumber'], None, None, raw['description'])

    def scrubbed(self):
        ls = copy(self)
        assert (len(ls) > 0)
        return jsSource(ls)
        
        
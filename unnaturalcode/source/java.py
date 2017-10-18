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

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)
ERROR = logger.error
WARN = logger.warn
INFO = logger.info
DEBUG = logger.debug

from unnaturalcode.source import Lexeme, Source, Position
from unnaturalcode.compile_error import CompileError

import re

from javac_parser import Java

java = Java()

whitespace = re.compile(r'[\s]')

class JavaLexeme(Lexeme):
    @classmethod
    def from_tuple(cls, t):
        return cls((t[0], t[1], Position(t[2]), Position(t[3]), t[4]))

class JavaSource(Source):
    lexemeClass = JavaLexeme
    
    def lex(self):
        tokens = java.lex(self.text)
        self.lexemes = [JavaLexeme.from_tuple(t) for t in tokens]
    
    def check_syntax(self):
        source = self.text
        errors = []
        for i in java.check_syntax(source):
            sev, code, mess, line, col, start, end = i
            errors.append(CompileError(
                line=line,
                column=col,
                errorname=code,
                text=mess))
        return errors


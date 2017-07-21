#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright 2017 Eddie Antonio Santos <easantos@ualberta.ca>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

import javalang
from javalang.parser import JavaSyntaxError
from javalang.tokenizer import LexerError


class Lexeme(object):
    """
    A lexeme is an abstract token.

    Lexeme pg. 111

    From "Compilers Principles, Techniques, & Tools, 2nd Ed." (WorldCat)
    by Aho, Lam, Sethi and Ullman:

    > A lexeme is a sequence of characters in the source program that matches
    > the pattern for a token and is identified by the lexical analyzer as an
    > instance of that token.
    """
    __slots__ = 'name', 'value'

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return "Lexeme(name=" + repr(self.name) +\
            ", value=" + repr(self.value) + ")"


class Position(object):
    """
    A line/column position in a text file.
    """
    __slots__ = 'line', 'column'

    def __init__(self, line, column):
        self.line = line
        self.column = column

    def __eq__(self, other):
        return (isinstance(other, Position)
                and self.line == other.line
                and self.column == other.column)

    def __repr__(self):
        return "Position(line=" + repr(self.line) +\
            ", column=" + repr(self.column) + ")"


class Location(object):
    """
    Represents the exact location of a token in a file.
    """
    __slots__ = 'start', 'end'

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return (isinstance(other, Location)
                and self.start == other.start
                and self.end == other.end)

    @property
    def spans_single_line(self):
        """
        True if the token spans multiple lines.
        """
        return self.start.line == self.end.line

    def __repr__(self):
        return "Location(start=" + repr(self.start) +\
            ", end=" + repr(self.end) + ")"

    @classmethod
    def from_string(self, text, line, column):
        r"""
        Determine the location from the size of the string.
        """
        start = Position(line=line, column=column)
        # How many lines are in the token?
        # NOTE: this may be different than what the tokenizer thinks is the
        # last line, due to handling of CR, LF, and CRLF, but I won't worry
        # too much about it.
        lines = text.split('\n')
        end_line = start.line + len(lines) - 1
        end_col = len(lines[-1]) - 1
        if len(lines) == 1:
            end_col += start.column
        end = Position(line=end_line, column=end_col)
        return Location(start=start, end=end)


class Token(Lexeme):
    """
    A lexeme with a location.  Includes location information.

    From "Compilers Principles, Techniques, & Tools, 2nd Ed." (WorldCat) by
    Aho, Lam, Sethi and Ullman:

    > A token is a pair consisting of a token name and an optional attribute
    > value.  The token name is an abstract symbol representing a kind of
    > lexical unit, e.g., a particular keyword, or sequence of input
    > characters denoting an identifier. The token names are the input symbols
    > that the parser processes.
    """
    __slots__ = 'start', 'end'

    def __init__(self, name, value, start, end):
        super(Token, self).__init__(name=name, value=value)
        self.start = start
        self.end = end

    @property
    def column(self):
        """
        Column number of the beginning of the token.
        """
        return self.start.column

    @property
    def line(self):
        """
        Line number of the beginning of the token.
        """
        return self.start.line

    @property
    def lines(self):
        """
        An order list of all the lines in this file
        """
        for line in range(self.start.line, self.end.line + 1):
            yield line

    @property
    def location(self):
        """
        Location of the token.
        """
        return Location(start=self.start, end=self.end)

    @property
    def loc(self):
        """
        Deprecated. Location of the token.
        """
        return self.location

    @property
    def spans_single_line(self):
        """
        True if the token spans multiple lines.
        """
        return self.location.spans_single_line

    def __repr__(self):
        return ("Token(name=" + repr(self.name) +
                ", value=" + repr(self.value) +
                ", start=" + repr(self.start) +
                ", end=" + repr(self.end) + ")")


class Java:
    """
    Defines the Java 8 programming language.
    """

    def vocabularize(self, source):
        """
        Produces a stream of normalized types (string representations of
        vocabulary entries) to be insterted into a language model.
        """
        stream = self.vocabularize_tokens(self._as_tokens(source))
        return (tok for _loc, tok in stream)

    def vocabularize_with_locations(self, source):
        """
        As with vocabularize, but also emits locations.
        """
        return self.vocabularize_tokens(self._as_tokens(source))

    def _as_tokens(self, source):
        """
        Ensures that anything that goes is returned as tokens.
        """
        if isinstance(source, (str, bytes)) or hasattr(source, 'read'):
            return self.tokenize(source)
        else:
            return source

    def tokenize(self, source):
        """
        Converts source code into an iterable of tokens (type, text,
        location).
        """
        tokens = javalang.tokenizer.tokenize(source)
        for token in tokens:
            loc = Location.from_string(token.value,
                                       line=token.position[0],
                                       column=token.position[1])
            yield Token(name=type(token).__name__,
                        value=token.value,
                        start=loc.start, end=loc.end)

    def check_syntax(self, source):
        try:
            javalang.parse.parse(source)
            return True
        except (JavaSyntaxError, LexerError):
            return False

    def vocabularize_tokens(self, source):
        """
        Given tokens, this should produce a stream of normalized types (string
        representations of vocabulary entries) to be insterted into a language
        model, attached with their location in the original source.
        """
        for token in source:
            yield token.location, java2sensibility(token)


RESERVED_WORDS = {
    'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch',
    'char', 'class', 'const', 'continue', 'default', 'do', 'double',
    'else', 'enum', 'extends', 'final', 'finally', 'float', 'for', 'goto',
    'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long',
    'native', 'new', 'package', 'private', 'protected', 'public', 'return',
    'short', 'static', 'strictfp', 'super', 'switch', 'synchronized',
    'this', 'throw', 'throws', 'transient', 'try', 'void', 'volatile',
    'while', 'abstract', 'default', 'final', 'native', 'private',
    'protected', 'public', 'static', 'strictfp', 'synchronized',
    'transient', 'volatile', 'boolean', 'byte', 'char', 'double', 'float',
    'int', 'long', 'short', 'true', 'false', 'null'
}
SYMBOLS = {
    '>>>=', '>>=', '<<=',  '%=', '^=', '|=', '&=', '/=',
    '*=', '-=', '+=', '<<', '--', '++', '||', '&&', '!=',
    '>=', '<=', '==', '%', '^', '|', '&', '/', '*', '-',
    '+', ':', '?', '~', '!', '<', '>', '=', '...', '->', '::',
    '(', ')', '{', '}', '[', ']', ';', ',', '.', '@'
}
CLOSED_CLASSES = {
    'Keyword', 'Modifier', 'BasicType', 'Boolean', 'Null',
    'Separator', 'Operator', 'Annotation', 'EndOfInput'
}

INTEGER_LITERALS = {
    'Integer',
    'DecimalInteger', 'OctalInteger', 'BinaryInteger', 'HexInteger',
}
FLOATING_POINT_LITERALS = {
    'FloatingPoint',
    'DecimalFloatingPoint', 'HexFloatingPoint',
}
STRING_LITERALS = {
    'Character', 'String',
}
OPEN_CLASSES = (
    INTEGER_LITERALS | FLOATING_POINT_LITERALS | STRING_LITERALS |
    {'Identifier'}
)


def java2sensibility(lex):
    # > Except for comments (§3.7), identifiers, and the contents of character
    # > and string literals (§3.10.4, §3.10.5), all input elements (§3.5) in a
    # > program are formed only from ASCII characters (or Unicode escapes
    # > (§3.3) which result in ASCII characters).
    # https://docs.oracle.com/javase/specs/jls/se7/html/jls-3.html
    if lex.name == 'EndOfInput':
        return '</s>'
    if lex.name in CLOSED_CLASSES:
        assert lex.value in RESERVED_WORDS | SYMBOLS
        return lex.value
    else:
        assert lex.name in OPEN_CLASSES
        if lex.name in INTEGER_LITERALS | FLOATING_POINT_LITERALS:
            return '<NUMBER>'
        elif lex.name in STRING_LITERALS:
            return '<STRING>'
        else:
            assert lex.name == 'Identifier'
            return '<IDENTIFIER>'


java = Java()


def test_lang():
    example = b'''class Herp {{
        const int herp = 5;
        goto fail;
    }
    '''
    tokens = list(java.tokenize(example))
    assert 14 == len(tokens)
    assert [
        'class', '<IDENTIFIER>', '{', '{',
        'const', 'int', '<IDENTIFIER>', '=', '<NUMBER>', ';',
        'goto', '<IDENTIFIER>', ';',
        '}'
    ] == list(java.vocabularize(example))

    assert 1 == tokens[0].line
    assert 4 == tokens[-1].line


def test_location():
    assert Location.from_string("from", line=2, column=13) == (
        Location(start=Position(line=2, column=13),
                 end=Position(line=2, column=16))
    )
    code = "'''hello,\nworld\n'''"
    assert Location.from_string(code, line=14, column=6) == (
        Location(start=Position(line=14, column=6),
                 end=Position(line=16, column=2))
    )

#    Copyright 2017 Joshua Charles Campbell
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

from collections import namedtuple

from unnaturalcode.source import Lexeme

class Change(namedtuple('_Change', [
    'opcode', 'from_start', 'from_end', 'to_start', 'to_end', 'from_', 'to'])):
    """
        opcode - same as difflib
        from_start - start index of token (token index) of original
        from_end - one after the end index (python range() sytle)
        to_start - start index of destination token
        to_end - end index
        from_ - list of Lexemes (length = from_end-from_start)
        to - list of Lexemes (length = to_end-to_start)
    """
    def __init__(self, *args):
        assert self.opcode in set([
            'replace',
            'delete',
            'insert',
            'equal'])
        assert self.from_start <= self.from_end
        assert self.to_start <= self.to_end
        for l in self.from_:
            assert isinstance(l, Lexeme)
        for l in self.to:
            assert isinstance(l, Lexeme)
        assert self.from_end - self.from_start == len(self.from_)
        assert self.to_end - self.to_start == len(self.to)
        
    def reverse(self):
        opcode = self.opcode
        if self.opcode == 'delete':
            opcode = 'insert'
        elif self.opcode == 'insert':
            opcode = 'delete'
        return self.__class__((
                opcode,
                self.to_start,
                self.to_end,
                self.from_start,
                self.from_end,
                self.to,
                self.from_
            ))

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
from copy import copy

from unnaturalcode.source import Lexeme, Source

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
        if self.opcode == 'delete':
            assert self.from_end - self.from_start > 0
            assert self.to_end - self.to_start == 0
        elif self.opcode == 'insert':
            assert self.from_end - self.from_start == 0
            assert self.to_end - self.to_start > 0
        elif self.opcode == 'replace':
            assert self.from_end - self.from_start > 0
            assert self.to_end - self.to_start > 0
        elif self.opcode == 'equal':
            assert self.from_ == self.to
        
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
    
    @property
    def token_index(self):
        assert self.from_start == self.to_start
        assert max(self.from_end - self.from_start, 
                   self.to_end - self.to_start) == 1
        return self.from_start
    
    @property
    def change_start(self):
        if len(self.from_) > 0:
            return self.from_[0].start
        elif len(self.to) > 0:
            return self.to[0].start
        else:
            assert False
    
    @property
    def change_end(self):
        if len(self.from_) > 0:
            return self.from_[-1].end
        elif len(self.to) > 0:
            return self.to[-1].end
        else:
            assert False
    
    @property
    def change_token(self):
        """ 
        Returns the token for a single-token change, preferring 
        the new token for 'replace'.
        """
        if len(self.to) > 0:
            assert len(self.to) == 1
            return self.to[0]
        elif len(self.from_) > 0:
            assert len(self.from_) == 1
            return self.from_[0]
        else:
            assert False
            
    def do(self, source, strict=False):
        changed = copy(source)
        if self.opcode == 'delete':
            from_ = changed.delete(self.from_start, self.from_end)
            if strict:
                assert from_ == self.from_
        elif self.opcode == 'insert':
            changed.insert(self.from_start, self.to)
        elif self.opcode == 'replace':
            from_ = changed.replace(self.from_start, self.from_end, self.to)
            if strict:
                assert from_ == self.from_
        else:
            pass
        return changed
    
    def approx_equal(self, other):
        if self.opcode != other.opcode:
            return False
        if self.from_start != other.from_start:
            return False
        if self.from_end != other.from_end:
            return False
        if self.opcode == 'insert' or self.opcode == 'replace':
            if not lexemes_approx_equal(self.to, other.to):
                return False
        return True

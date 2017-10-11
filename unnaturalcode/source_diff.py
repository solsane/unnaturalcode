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

import difflib

from unnaturalcode.source import Lexeme, Source
from unnaturalcode.change import Change


class Diff(object):
    @staticmethod
    def distill(s):
        return [
            tuple((l.type, l.value)) for l in s.lexemes
            ]
    
    def opcode_to_change(self, opcode):
        op, i1, i2, j1, j2 = opcode
        return Change(
            op,
            i1,
            i2,
            j1,
            j2,
            self.from_.lexemes[i1:i2],
            self.to.lexemes[j1:j2]
            )
    
    def __init__(self, from_, to):
        assert isinstance(from_, Source)
        assert isinstance(to, Source)
        self.from_ = from_
        self.to = to
        self.from_lite = self.distill(from_)
        self.to_lite = self.distill(to)
        self.sm = difflib.SequenceMatcher(a=self.from_lite, b=self.to_lite,
                                          autojunk=False)
        self.changes = [
            self.opcode_to_change(opcode) for opcode in self.sm.get_opcodes()
                if opcode[0] != 'equal'
            ]
    
    

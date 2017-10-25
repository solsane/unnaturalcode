#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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

import unittest
from unnaturalcode.change import Change
from unnaturalcode.source import Source
from unnaturalcode.source.java import JavaSource
from unnaturalcode.validation.tools.sensibility import Sensibility
from sensibility import Insertion, Deletion, Substitution, language
from sensibility.evaluation.distance import determine_edit


class TestConvertEditToChange(unittest.TestCase):
    def setUp(self):
        language.set('java')

    def test_insertion(self):
        before = b"class Hello {"
        after = b"class Hello {}"
        edit = determine_edit(before, after)
        assert isinstance(edit, Insertion)

        tool = Sensibility(fixer=MockFixer(edit), **kwargs())
        fixes = tool.query(make_source(before))

        assert len(fixes) == 1
        change = fixes[0]
        assert change.opcode == 'insert'
        assert change.from_start == 3
        assert change.from_end == 3
        assert change.to_start == 3
        assert change.to_end == 4

    def test_deletion(self):
        before = b"class Hello {}}"
        after = b"class Hello {}"
        edit = determine_edit(before, after)
        assert isinstance(edit, Deletion)

        tool = Sensibility(fixer=MockFixer(edit), **kwargs())
        fixes = tool.query(make_source(before))

        assert len(fixes) == 1
        change = fixes[0]
        assert change.opcode == 'delete'
        assert change.from_start == 4
        assert change.from_end == 5
        assert change.to_start == 4
        assert change.to_end == 4

    def test_substitution(self):
        before = b"class synchronized {}"
        after = b"class Synchronized {}"
        edit = determine_edit(before, after)
        assert isinstance(edit, Substitution)

        tool = Sensibility(fixer=MockFixer(edit), **kwargs())
        fixes = tool.query(make_source(before))

        assert len(fixes) == 1
        change = fixes[0]
        assert change.opcode == 'replace'
        assert change.from_start == 1
        assert change.from_end == 2
        assert change.to_start == 1
        assert change.to_end == 2

    def test_oov(self):
        """
        Regression: do not crash when given OOV tokens.
        """
        before = b"interface Synchronizable {#}"
        after = b"interface Synchronizable {}"

        edit = determine_edit(before, after)
        assert isinstance(edit, Deletion)

        tool = Sensibility(fixer=MockFixer(edit), **kwargs())
        fixes = tool.query(make_source(before))

        assert len(fixes) == 1
        change = fixes[0]
        assert change.opcode == 'delete'
        assert change.from_start == 3
        assert change.from_end == 4
        assert change.to_start == 3
        assert change.to_end == 3
        assert change.from_[0][0] == 'ERROR'


def kwargs():
    return dict(
        N=1,
        language_file=JavaSource,
        results_dir="/tmp",
        train=False,
        keep=True,
        type_only=True
    )


def make_source(source):
    return JavaSource(text=source.decode('UTF-8'))


class MockFixer(object):
    """
    Simply returns the given value when asked to fix a file.
    """
    def __init__(self, ret_value):
        self.ret_value = ret_value

    def fix(self, _who_cares):
        return [self.ret_value]

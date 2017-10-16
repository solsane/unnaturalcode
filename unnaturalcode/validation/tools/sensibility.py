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


from unnaturalcode.validation.tools import Tool


class Sensibility(Tool):
    name = "sensibility"

    def __init__(self, train, keep, fixer=None):
        from sensibility.fix import LSTMFixerUpper
        from sensibility.model.lstm import KerasDualLSTMModel

        assert keep is True, "Will not delete LSTM models"
        assert train is False, "Cannot retrain LSTM models"

        # XXX: Hardcoded to work with Java. There is a better way, but ¯\_(ツ)_/¯
        from sensibility import language
        language.set('java')

        # Allow for that dank dependency injection.
        if fixer is None:
            # Load the models from the results dir.
            model = KerasDualLSTMModel.from_directory(self.results_dir)
            # NOTE: Set k to ⌈MRR ** -1⌉
            self.fixer = LSTMFixerUpper(model, k=4)
        else:
            self.fixer = fixer

    def train_files(self, train):
        raise NotImplementedError("Train the models seperately")

    def query(self, bad_source):
        # Sensibility likes to defer reading the bytestream to the parser;
        # consequently it only takes bytes objects as inputs; so just reencode
        # the string to something sane.
        if isinstance(bad_source.text, str):
            bad_source_code = bad_source.text.encode('UTF-8')

        # Ensure that we both have the same number of tokens
        assert 'EOF' not in bad_source.lexemes[-1].type.upper()
        assert len(to_source_vector(bad_source_code)) == len(bad_source.lexemes)

        # The fixes are returned in Sensibility's format. They must be adapted
        # to Change objects.
        fixes = self.fixer.fix(bad_source_code)

        from sensibility.source_vector import to_source_vector
        from sensibility.edit import Insertion, Deletion, Substitution

        changes = []  # that's just the way it is
        for fix in fixes:
            if isinstance(fix, Insertion):
                opcode = 'insert'
                from_start = fix.index
                from_end = fix.index
                to_start = fix.index
                to_end = fix.index + 1
                from_ = []
                to = [vind_to_lexeme(fix.token)]
            elif isinstance(fix, Deletion):
                opcode = 'delete'
                from_start = fix.index
                from_end = fix.index + 1
                to_start = fix.index
                to_end = fix.index
                from_ = [bad_source.lexemes[from_start]]
                to = []
            elif isinstance(fix, Substitution):
                opcode = 'replace'
                from_ = [bad_source.lexemes[from_start]]
                from_start = fix.index
                from_end = fix.index + 1
                to_start = from_start
                to_end = from_end
                from_ = [bad_source.lexemes[from_start]]
                to = [vind_to_lexeme(fix.token)]
            else:
                raise ValueError("what even is this:" + repr(fix))
            changes.append(Change(opcode, from_start, from_end, to_start,
                                  to_end, from_, to))

        return changes  # things will never be the same


def vind_to_lexeme(vocab_id):
    from sensibility import language
    from sensibility.vocabulary import VocabularyError
    ltype = language.vocabulary.to_text(vocab_id)
    # For some tokens, there's no source representation
    try:
        value = language.vocabulary.to_source_text(vocab_id)
    except VocabularyError:
        value = None
    # A dummy position; this is not really used.
    dummy = (1, 0, None)
    return Lexeme.build(ltype, value, dummy, dummy)

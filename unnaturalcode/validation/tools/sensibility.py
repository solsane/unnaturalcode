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
from unnaturalcode.change import Change
from unnaturalcode.source import Lexeme


class Sensibility(Tool):
    name = "sensibility"

    def __init__(self, fixer=None, **kwargs):
        from sensibility import language

        super(Sensibility, self).__init__(**kwargs)

        assert self.type_only, "Can't do that for you, hun"
        assert kwargs.get('keep', True), "Will not delete LSTM models"
        assert not kwargs.get('train', False), "Cannot retrain LSTM models"

        language.set(self.language)

        # Allow for that dank dependency injection.
        if fixer is None:
            from sensibility.fix import LSTMFixerUpper
            from sensibility.model.lstm import KerasDualLSTMModel

            # Load the models from the results dir.
            model = KerasDualLSTMModel.from_directory(self.results_dir)
            # NOTE: Set k to ⌈MRR ** -1⌉
            self.fixer = LSTMFixerUpper(model, k=4)
        else:
            self.fixer = fixer

    def train_files(self, train):
        raise NotImplementedError("Train the models seperately")

    def query(self, bad_source):
        from sensibility.source_vector import to_source_vector
        from sensibility.edit import Insertion, Deletion, Substitution

        # Sensibility likes to defer reading the bytestream to the parser;
        # consequently it only takes bytes objects as inputs; so just reencode
        # the string to something sane.
        if isinstance(bad_source.text, str):
            bad_source_code = bad_source.text.encode('UTF-8')

        # Ensure that we both agree the on the token stream.
        n_sensibility_tokens = len(to_source_vector(bad_source_code))
        n_unnaturalcode_tokens = len(bad_source.lexemes)
        assert 'EOF' in bad_source.lexemes[-1].type, "Expected EOF as last token"
        # Sensibilty's token streams always omit the EOF, but UC keeps it (I think)
        assert n_sensibility_tokens + 1 == n_unnaturalcode_tokens

        # The fixes are returned in Sensibility's format. They must be adapted
        # to Change objects.
        fixes = self.fixer.fix(bad_source_code)

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
                from_ = [bad_source.lexemes[fix.index]]
                to = []
            elif isinstance(fix, Substitution):
                opcode = 'replace'
                from_start = fix.index
                from_end = fix.index + 1
                to_start = fix.index
                to_end = fix.index + 1
                from_ = [bad_source.lexemes[fix.index]]
                to = [vind_to_lexeme(fix.token)]
            else:
                raise ValueError("what even is this?" + repr(fix))
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

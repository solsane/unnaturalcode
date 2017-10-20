#    Copyright 2013, 2014, 2017 Joshua Charles Campbell
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

from __future__ import division

TYPE_WEIGHT = 0.9
VALUE_WEIGHT = 0.1

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

from unnaturalcode.source import Lexeme, Position
from unnaturalcode.change import Change
from unnaturalcode.ngram_model import NgramModel

class DualNgramModel(object):
    def __init__(self, 
                cm, 
                language, 
                window_size=21, 
                type_only=False, 
                corpus_base="validationCorpus"):
        assert type_only == False
        self.language = language
        self.window_size = window_size
        self.corpus_base = corpus_base
        self.corpus_t = corpus_base + ".types"
        self.corpus_v = corpus_base + ".values"
        self.sm_t = NgramModel(cm=cm,
                                language=self.language,
                                type_only=True,
                                corpus_base=self.corpus_t)
        self.sm_v = NgramModel(cm=cm,
                                language=self.language,
                                type_only=False,
                                corpus_base=self.corpus_v)
    
    def delete_corpus(self):
        self.sm_t.delete_corpus()
        self.sm_v.delete_corpus()
    
    def save_corpus(self):
        self.sm_t.save_corpus()
        self.sm_v.save_corpus()
        
    def train(self, lexemes):
        self.sm_t.train(lexemes)
        self.sm_v.train(lexemes)
        
    def n_unique_tokens(self):
        return self.sm_v.n_unique_tokens()
        
    def try_delete(self, window, i, real_i):
        window_t, window_v, originalEntropy = window
        query_t = self.sm_t.stringify_all(window_t[:i] + window_t[i+1:])
        assert query_t == self.sm_t.stringify_all(window_v[:i] + window_v[i+1:])
        assert len(query_t) == self.window_size-1
        query_v = self.sm_v.stringify_all(window_v[:i] + window_v[i+1:])
        assert len(query_v) == self.window_size-1
        newEntropy = (
            TYPE_WEIGHT * self.sm_t.cm.queryCorpus(query_t)
            + VALUE_WEIGHT * self.sm_v.cm.queryCorpus(query_v))
        if newEntropy < originalEntropy:
            return [
                (
                    Change('delete',
                           real_i,
                           real_i+1,
                           real_i,
                           real_i,
                           [window_v[i]],
                           []),
                    originalEntropy - newEntropy
                    )
                ]
        else:
            return []

    def try_insert(self, window, i, real_i, what):
        window_t, window_v, originalEntropy = window
        query_t = self.sm_t.stringify_all(window_t[:i] + [what] + window_t[i:])
        assert len(query_t) == self.window_size+1
        query_v = self.sm_v.stringify_all(window_v[:i] + [what] + window_v[i:])
        assert len(query_v) == self.window_size+1
        newEntropy = (
            TYPE_WEIGHT * self.sm_t.cm.queryCorpus(query_t)
            + VALUE_WEIGHT * self.sm_v.cm.queryCorpus(query_v))
        if newEntropy < originalEntropy:
            #DEBUG("    Insert %i (%s) %f %f" % (real_i, what[4], originalEntropy, newEntropy))
            return [
                (
                    Change('insert',
                           real_i,
                           real_i,
                           real_i,
                           real_i+1,
                           [],
                           [what]),
                    originalEntropy - newEntropy
                    )
                ]
        else:
            return []

    def try_replace(self, window, i, real_i, what):
        window_t, window_v, originalEntropy = window
        query_t = self.sm_t.stringify_all(window_t[:i] + [what] + window_t[i+1:])
        assert len(query_t) == self.window_size
        query_v = self.sm_v.stringify_all(window_v[:i] + [what] + window_v[i+1:])
        assert len(query_v) == self.window_size
        newEntropy = (
            TYPE_WEIGHT * self.sm_t.cm.queryCorpus(query_t)
            + VALUE_WEIGHT * self.sm_v.cm.queryCorpus(query_v))
        if newEntropy < originalEntropy:
            return [
                (
                    Change('replace',
                           real_i,
                           real_i+1,
                           real_i,
                           real_i+1,
                           [window_v[i]],
                           [what]),
                    originalEntropy - newEntropy
                    )
                ]
        else:
            return []

    def fix(self, lexemes):
        lexemes = lexemes.lexemes
        MAX_POSITIONS = 10
        windows_t, unwindows_t = self.sm_t.unwindowed_query(lexemes)
        windows_v, unwindows_v = self.sm_v.unwindowed_query(lexemes)
        windows = len(windows_t)
        assert len(unwindows_t) == windows
        assert len(windows_v) == windows
        assert len(unwindows_v) == windows
        centre = self.window_size//2
        weighted = []
        for  i in range(0, windows):
            weight = (TYPE_WEIGHT * unwindows_t[i][1]
                      + VALUE_WEIGHT * unwindows_v[i][1])
            #DEBUG(repr([unwindows_t[i][1], unwindows_v[i][1]]))
            weighted.append(weight)
        keys = list(range( 0, windows))
        keys = sorted(keys, key=lambda i: weighted[i], reverse=True)
        #assert keys == sorted(keys, key=lambda i: unwindows_t[i][1], reverse=True)
        suggestions = []
        for i in range(0, min(len(keys), MAX_POSITIONS)):
            windowi = keys[i]
            DEBUG("Position: %i" % (windowi))
            assert windows_v[i][0][centre] == unwindows_v[i][0]
            assert windows_t[i][0][0].ltype == windows_v[i][0][0].ltype
            suggestions += self.try_delete(
                (windows_t[windowi][0], windows_v[windowi][0], weighted[windowi]), 
                centre, 
                windowi)
            for string, (token, count) in self.sm_v.listOfUniqueTokens.items():
                if count < 100:
                    continue
                suggestions += self.try_insert(
                    (windows_t[windowi][0], windows_v[windowi][0], weighted[windowi]), 
                    centre, windowi, 
                    token)
                suggestions += self.try_replace(
                    (windows_t[windowi][0], windows_v[windowi][0], weighted[windowi]),
                    centre, windowi, 
                    token)
            #DEBUG("Suggestions: %i" % (len(suggestions)))
        suggestions = sorted(suggestions, key=lambda s: s[1], reverse=True)
        return [suggestion[0] for suggestion in suggestions]

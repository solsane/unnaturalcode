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
        
    def fix(self, lexemes):
        lexemes = lexemes.lexemes
        MAX_POSITIONS = 5
        windows_t, unwindows_t = self.sm_t.unwindowed_query(lexemes)
        windows_v, unwindows_v = self.sm_v.unwindowed_query(lexemes)
        windows = len(windows_t)
        assert len(unwindows_t) == windows
        assert len(windows_v) == windows
        assert len(unwindows_v) == windows
        centre = self.window_size//2
        weighted = []
        for  i in range(0, windows):
            weight = unwindows_t[i] + unwindows_v[i]
            weighted.append(weight)
        keys = list(range( 0, windows))
        keys = sorted(keys, key=lambda i: weighted[i], reverse=True)
        suggestions = []
        for i in range(0, min(len(keys), MAX_POSITIONS)):
            windowi = keys[i]
            DEBUG("Position: %i" % (windowi))
            assert windows_v[i][0][centre] == unwindows_v[i][0]
            suggestions += self.sm_v.try_delete(windows_v[windowi], centre, windowi)
            for string, (token, count) in self.sm_v.listOfUniqueTokens.items():
                if count < 100:
                    continue
                suggestions += self.sm_v.try_insert(windows_v[windowi], centre, windowi, token)
                suggestions += self.sm_v.try_replace(windows_v[windowi], centre, windowi, token)
            DEBUG("Suggestions: %i" % (len(suggestions)))
        suggestions = sorted(suggestions, key=lambda s: s[1], reverse=True)
        return [suggestion[0] for suggestion in suggestions]

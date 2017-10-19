#!/usr/bin/python
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

import sys
import os

from unnaturalcode.validation.tools import Tool
from unnaturalcode.ngram_model import NgramModel
from unnaturalcode.dual_ngram_model import DualNgramModel
from unnaturalcode.mitlmCorpus import mitlmCorpus
from unnaturalcode.source import Lexeme, Position

class Mitlm(Tool):
    name = "mitlm"
    source_model = NgramModel
    def __init__(
            self,
            train,
            keep,
            **kwargs
        ):
        super(Mitlm, self).__init__(**kwargs)
        assert os.access(self.results_dir, os.X_OK & os.R_OK & os.W_OK)
        self.corpus_path = os.path.join(self.results_dir, 'validationCorpus')
        self.corpus=mitlmCorpus
        self.sm = self.source_model(cm=self.corpus, 
                              language=self.language,
                              type_only=self.type_only,
                              corpus_base=self.corpus_path
                              )
        if train:
            if keep:
                pass
            else:
                self.sm.delete_corpus()
            self.train_files(train)
    
    def train_files(self, train):
        self.file_names = open(train).read().splitlines()
        n_skipped = 0
        n_added = 0
        for i in range(0, len(self.file_names)):
            fi = self.file_names[i]
            try:
                valid_fi = self.language_file(good_path=fi,
                                              temp_dir=self.results_dir,
                                              type_only=self.type_only)
                INFO("Using %s for training." % (fi))
                self.sm.train(valid_fi.good_lexed.lexemes)
                if i % 100 == 0:
                    self.sm.save_corpus()
                n_added += 1
                #if (len(valid_fi.lexed) > self.sm.windowSize) and testing:
                    #self.testFiles.append(valid_fi)
                    #info("Using %s in %s mode for testing." % (fi, valid_fi.mode))
                    #nAdded += 1
            except:
                INFO("Skipping %s !!!" % (fi), exc_info=sys.exc_info())
                n_skipped += 1
                #raise
        INFO("Using: %i, Skipped: %i" % (n_added, n_skipped))
        unk = Lexeme(("<unk>", "<unk>", Position((1, 0)), Position((1, 0)), "<unk>"))
        self.sm.train([unk] * 21)
        self.sm.save_corpus()
    
    def query(self, bad_lexemes):
        return self.sm.fix(bad_lexemes)
    
class DualMitlm(Mitlm):
    source_model = DualNgramModel
    name = "dualmitlm"

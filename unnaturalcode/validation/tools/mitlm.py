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

import os
import sys

from unnaturalcode.validation.tools import Tool
from unnaturalcode.sourceModel import sourceModel
from unnaturalcode.mitlmCorpus import mitlmCorpus

class Mitlm(Tool):
    name = "mitlm"
    def __init__(
            self,
            train,
            keep,
            **kwargs
        ):
        super(Mitlm, self).__init__(**kwargs)
        assert os.access(self.results_dir, os.X_OK & os.R_OK & os.W_OK)
        self.corpus_path = os.path.join(self.results_dir, 'validationCorpus')
        self.corpus=mitlmCorpus(readCorpus=self.corpus_path,
                                writeCorpus=self.corpus_path)
        self.sm = sourceModel(cm=self.corpus, 
                              language=self.language,
                              type_only=self.type_only
                              )
        if train:
            if keep:
                pass
            elif os.path.exists(self.corpus_path):
                os.remove(self.corpus_path)
            if keep:
                pass
            elif os.path.exists(self.corpus_path + ".uniqueTokens"):
                os.remove(self.corpus_path + ".uniqueTokens")
            self.train_files(train)
    
    def train_files(self, train):
        self.file_names = open(train).read().splitlines()
        n_skipped = 0
        n_added = 0
        for fi in self.file_names:
            try:
                valid_fi = self.language_file(good_path=fi,
                                              temp_dir=self.results_dir)
                INFO("Using %s for training." % (fi))
                self.sm.trainLexemes(valid_fi.good_lexed.lexemes)
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
    
    def query(self, bad_lexemes):
        return self.sm.fix(bad_lexemes)

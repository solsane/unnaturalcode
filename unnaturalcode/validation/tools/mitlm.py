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

import os

from unnaturalcode.validation.tools import Tool
from unnaturalcode.sourceModel import sourceModel
from unnaturalcode.mitlmCorpus import mitlmCorpus

class Mitlm(Tool):
    def __init__(
            self,
            train,
            keep,
            **kwargs
        ):
        super(MITLM, self).__init__(**kwargs)
        self.corpus=mitlmCorpus
        self.sm = sourceModel(cm=self.corpus, language=self.language)
        assert os.access(self.results_dir, os.X_OK & os.R_OK & os.W_OK)
        self.corpus_path = os.path.join(self.resultsDir, 'validationCorpus')
        if train:
            if keep:
                pass
            elif os.path.exists(self.corpusPath):
                os.remove(self.corpusPath)
            if keep:
                pass
            elif os.path.exists(self.corpusPath + ".uniqueTokens"):
                os.remove(self.corpusPath + ".uniqueTokens")
            self.train_files(train):
    
    def train_files(self, train):
        self.file_names = open(train).read().splitlines()
        n_skipped = 0
        n_added = 0
        for fi in self.file_names:
            try:
                valid_fi = self.language_file(fi, self.results_dir)
                info("Using %s for training." % (fi))
                self.sm.trainLexemes(fi.scrubbed)
                n_added += 1
                #if (len(valid_fi.lexed) > self.sm.windowSize) and testing:
                    #self.testFiles.append(valid_fi)
                    #info("Using %s in %s mode for testing." % (fi, valid_fi.mode))
                    #nAdded += 1
            except:
                info("Skipping %s !!!" % (fi), exc_info=sys.exc_info())
                n_skipped += 1
        info("Using: %i, Skipped: %i" % (n_added, n_skipped))
    
    def query(self, bad_text):
        

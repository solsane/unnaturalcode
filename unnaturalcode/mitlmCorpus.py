#    Copyright 2013, 2014 Joshua Charles Campbell
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

from __future__ import print_function
import os
import os.path
import errno
from unnaturalcode.unnaturalCode import *
import logging
from logging import debug, info, warning, error, getLogger
import codecs
import pymitlm

allWhitespace = re.compile('^\s+$')

ucParanoid = os.getenv("PARANOID", False)

mitlmLogger = getLogger('MITLM')

mitlmLogger.setLevel(logging.DEBUG)

class mitlmCorpus(object):
    """
    Interface to an MITLM corpus.
    """

    def __init__(self, readCorpus=None, writeCorpus=None, uc=unnaturalCode(), order=10):
        self.readCorpus = (readCorpus or os.getenv("ucCorpus", "/tmp/ucCorpus"))
        self.writeCorpus = (writeCorpus or os.getenv("ucWriteCorpus", self.readCorpus))
        self.corpusFile = False
        self.order = order
        self.mitlm = None

    def startMitlm(self):
        """
        Called automatically. Initializes MITLM, however we're interfacing to
        it nowadays.
        """
        if self.mitlm == None:
            self.mitlm = pymitlm.PyMitlm(self.readCorpus, self.order,
                                         "KN", True)

    def corpify(self, lexemes):
        """Stringify lexed source: produce space-seperated sequence of lexemes"""
        assert isinstance(lexemes, list)
        assert len(lexemes)
        return u" ".join(lexemes)

    def openCorpus(self):
        """Opens the corpus (if necessary)"""
        if (self.corpusFile):
            assert not self.corpusFile.closed
            return
        self.corpusFile = codecs.open(self.writeCorpus, 'a', encoding='UTF-8')

    def closeCorpus(self):
        """Closes the corpus (if necessary)"""
        if (self.corpusFile):
            self.corpusFile.close()
            assert self.corpusFile.closed
            self.corpusFile = None

    def addToCorpus(self, lexemes):
        """Adds a string of lexemes to the corpus"""
        assert isinstance(lexemes, list)
        assert len(lexemes)
        self.openCorpus()
        cl = self.corpify(lexemes)
        assert(len(cl))
        assert (not allWhitespace.match(cl)), "Adding blank line to corpus!"
        print(cl, file=self.corpusFile)
        self.corpusFile.flush()
        # MITLM cannot (as of now) update its model, so just throw out the old
        # one.
        self.mitlm = None

    def queryCorpus(self, request):
        self.startMitlm()
        r = self.mitlm.xentropy((" ".join(request)).encode("UTF-8"))
        if r >= 1.0e70:
          qString = self.corpify(request)
          warning("Infinity: %s" % qString)
          warning(str(r))
          self.checkMitlm()
        return r

    def predictCorpus(self, lexemes):
        return self.parsePredictionResult(
            self.mitlm.predict(lexemes),
            remove_prefix=len(lexemes)
        )

    def release(self):
        """Close files and stop MITLM"""
        self.closeCorpus()

    def __del__(self):
        """I am a destructor, but release should be called explictly."""
        assert not self.corpusFile, "Destructor called before release()"

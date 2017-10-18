#!/usr/bin/python
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

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

import os
from os import path
import codecs

from unnaturalcode.source_diff import Diff

PARANOID = os.getenv("PARANOID", False)

class ValidationFile(object):
    language = None
    
    def check_syntax(self, fi):
        """ 
        Check the syntax of either the good or bad file.
        Default behaviour is to use the language class parser.
        """
        return fi.check_syntax()
    
    def __init__(self, 
                 good_path, 
                 temp_dir, 
                 bad_path=None,
                 check=True):
        self.good_path = good_path
        with codecs.open(good_path, 'r', 'UTF-8') as good_fileh:
            self.good_text = good_fileh.read()
        self.good_lexed = self.language(text=self.good_text)
        assert self.good_lexed.text == self.good_text
        #self.good_scrubbed = self.good_lexed.scrubbed()
        if check:
            assert self.check_syntax(self.good_lexed) == []
        self.bad_path = None
        self.bad_text = None
        self.bad_lexed = None
        if bad_path is not None:
            self.bad_path = bad_path
            with codecs.open(bad_path, 'r', 'UTF-8') as bad_fileh:
                self.bad_text = bad_fileh.read()
            self.bad_lexed = self.language(text=self.bad_text)
            if check:
                assert len(self.check_syntax(self.bad_lexed)) > 0
        self.temp_dir = temp_dir
        
    def compute_change(self):
        self.change = Diff(self.good_lexed, self.bad_lexed)
        if len(self.change.changes) == 1:
            self.change = self.change.changes[0]
            DEBUG(repr(self.change))
        else:
            raise RuntimeError("??")
        
    
    def mutate(self, new_lexemes, change=None):
        #TODO: check_syntax?
        self.bad_lexed = new_lexemes
        if change is None:
            assert False
            self.compute_change()
        else:
            if PARANOID:
                self.compute_change()
                assert self.change == change, repr([self.change.changes, change])
            self.change = change


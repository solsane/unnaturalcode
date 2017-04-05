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


from logging import debug, info, warning, error
import logging
import os
import sys
from multiprocessing import Process, Queue
try:
  from Queue import Empty
except ImportError:
  from queue import Empty

from unnaturalcode.modelValidator import ValidationFile, ModelValidation, ValidationMain
from unnaturalcode.mitlmCorpus import mitlmCorpus
from unnaturalcode.mutators import Mutators
from unnaturalcode.jsSource import jsSource


class JsValidationFile(ValidationFile):
    def __init__(self, path, language, tempDir):
        self.mode = "js"
        super(JsValidationFile,self).__init__(path, language, tempDir)
    
    def get_error(self):
        return self.mutatedLexemes.check_syntax()
        
class JsValidation(ModelValidation):
    
    def __init__(self, 
                 test=None, 
                 train=None,
                 resultsDir=None,
                 corpus=mitlmCorpus,
                 keep=False,
                 *args,
                 **kwargs):
       self.languageValidationFile = JsValidationFile
       super(JsValidation,self).__init__(
         test=test,
         train=train,
         language=jsSource,
         resultsDir=resultsDir,
         corpus=mitlmCorpus,
         keep=keep,
         *args,
         **kwargs)
    def get_error(self, fi):
        return fi.get_error()

class JsValidationMain(ValidationMain):
    def add_args(self, parser):
        pass

    def read_args(self, args):
        pass

    def __init__(self, *args, **kwargs):
        self.validation = JsValidation
        super(JsValidationMain,self).__init__(*args, **kwargs)

if __name__ == '__main__':
    JsValidationMain().main()

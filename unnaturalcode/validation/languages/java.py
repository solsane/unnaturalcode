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

from unnaturalcode.validation.test import ValidationTest
from unnaturalcode.validation.main import ValidationMain
from unnaturalcode.validation.file import ValidationFile

from unnaturalcode.source.java import JavaSource


class JavaValidationFile(ValidationFile):
    language = JavaSource
    
    def __init__(self, **kwargs):
        super(JavaValidationFile,self).__init__(**kwargs)
        
class JavaValidationTest(ValidationTest):
    def __init__(self, **kwargs):
        super(JavaValidationTest,self).__init__(**kwargs)
        
    def check_good_file(self, fi):
        pass

class JavaValidationMain(ValidationMain):
    validation_file_class = JavaValidationFile
    validation_test_class = JavaValidationTest

    def add_args(self, parser):
        pass

    def read_args(self, args):
        logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)
        return {}

    def __init__(self, *args, **kwargs):
        super(JavaValidationMain,self).__init__(*args, **kwargs)
        

if __name__ == '__main__':
    
    JavaValidationMain().main()

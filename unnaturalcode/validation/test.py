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

import sqlite3

from unnaturalcode.validation.result import (
    LineLocation,
    WindowLocation,
    ExactLocation,
    ValidFix,
    TrueFix
    )

class ValidationTest(object):
    fields = [  
        "mutation",
        "good_file",
        "bad_file",
        "iteration",
        "tool",
        "change_operation",
        "good_token_type",
        "good_token_value",
        "bad_token_type",
        "bad_token_value",
        "change_token_index",
        "change_start_line",
        "change_start_col",
        "change_end_line",
        "change_end_col",
        ]
    result_types = [
        LineLocation,
        WindowLocation,
        ExactLocation,
        ValidFix,
        TrueFix
        ]
    
    def __init__(self, language_file, output_dir):
        self.language_file = language_file
        self.language = language_file.language
        self.results_dir = output_dir
        self.conn = sqlite3.connect(self.sqlite_file_path())
        self.result_columns = [column
                            for result in self.result_types 
                        for column in result.column_names()]
        
        self.columns = ",".join(
            self.fields + self.result_columns)

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS results ("
                "id PRIMARY KEY,"
                + self.columns +
                ")")
        self.conn.commit()
        tasks = []
        
    def sqlite_file_path(self):
        os.path.join(self.results_dir, "results.sqlite3")
    
    def check_file(self, fi):
        """
        Hook for subclasses to run additional tests on files.
        Raises an exception on a bad file.
        """
        pass
        
    def add_pair_tests(self, test, tools):
        self.file_names = open(test).read().splitlines()
        n_skipped = 0
        n_added = 0
        for fi in self.file_names:
            try:
                after_file_name = fi
                before_file_name = fi.replace("after", "before")
                valid_fi = self.language_file(after_file_name,
                                              self.results_dir,
                                              before_file_name)
                self.check_good_file(valid_fi)
                INFO("Using %s for testing." % (fi))
                n_added += 1
                task = PairTask(self, valid_fi, tools)
            except:
                INFO("Skipping %s !!!" % (fi), exc_info=sys.exc_info())
                n_skipped += 1
            self.tasks.append(task)
        INFO("Using: %i, Skipped: %i" % (n_added, n_skipped)) 
    
    def add_mutation_tests(self, test, retry_valid, mutations, n, tools):
        self.file_names = open(test).read().splitlines()
        n_skipped = 0
        n_added = 0
        for fi in self.file_names:
            try:
                good_file_name = fi
                valid_fi = self.language_file(good_file_name)
                self.check_good_file(valid_fi)
                INFO("Using %s for testing." % (fi))
                n_added += 1
            except:
                INFO("Skipping %s !!!" % (fi), exc_info=sys.exc_info())
                n_skipped += 1
            for mi in mutations:
                mutation_name = mi.replace('-', '_')
                task = MutationTask(self, valid_fi, tools, mutation_name, n)
                self.tasks.append(task)
        INFO("Using: %i, Skipped: %i" % (n_added, n_skipped)) 
            

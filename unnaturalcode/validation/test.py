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
import sys

import sqlite3

from unnaturalcode.validation.result import (
    LineLocation,
    WindowLocation,
    ExactLocation,
    ValidFix,
    TrueFix
    )

from unnaturalcode.validation.task import MutationTask

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
    
    def __init__(self, language_file, output_dir, type_only):
        self.language_file = language_file
        self.language = language_file.language
        assert output_dir is not None
        self.results_dir = output_dir
        self.conn = sqlite3.connect(self.sqlite_file_path())
        self.result_columns = [column
                            for result in self.result_types 
                        for column in result.column_names()]
        
        self.columns = self.fields + self.result_columns
        self.type_only = type_only

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS results ("
                "id PRIMARY KEY,"
                + ",".join(self.columns) +
                ")")
        self.conn.commit()
        self.tasks = []
        
    def sqlite_file_path(self):
        return os.path.join(self.results_dir, "results.sqlite3")
    
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
        self.retry_valid = retry_valid
        self.file_names = open(test).read().splitlines()
        n_skipped = 0
        n_added = 0
        for fi in self.file_names:
            DEBUG(fi)
            try:
                good_file_name = fi
                valid_fi = self.language_file(good_path=good_file_name,
                                              temp_dir=self.results_dir)
                self.check_good_file(valid_fi)
                if valid_fi.good_lexed.n_lexemes < 21:
                    raise RuntimeError("File too short!")
            except:
                INFO("Skipping %s !!!" % (fi), exc_info=sys.exc_info())
                n_skipped += 1
                continue
            else:
                INFO("Using %s for testing." % (fi))
                n_added += 1
                for mutation in mutations:
                    task = MutationTask(self, valid_fi, tools, mutation, n)
                    self.tasks.append(task)
        INFO("Using: %i, Skipped: %i" % (n_added, n_skipped))
    
    def resume(self):
        assert len(self.tasks) > 0
        for task in self.tasks:
            task.resume()
    
    def go(self):
        # we can't call this run because run is the boolean whether we should
        # run the files or just parse them 
        for task in self.tasks:
            task.run()
    
    

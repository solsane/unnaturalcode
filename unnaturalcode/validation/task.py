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

# LOOP ORDER IS:
# for file (for mutation (for tool
        
class Task(object):
    def __init__(self, 
                 test, 
                 validation_file, 
                 tools, 
                 expected_per_tool
                 ):
        self.test = test
        self.conn = test.conn
        self.validation_file = validation_file
        self.tools = tools
        # number of results expected for each tool
        self.expected_per_tool = expected_per_tool
        
    def tool_finished(self, tool):
        return (self.conn.execute("SELECT COUNT(*) FROM results WHERE "
                "good_file = ? AND tool = ? AND mutation = ?",
                (self.validation_file.good_path,
                    tool.name,
                    self.mutation_name
                    )
                )
            .fetchone()[0]
            )
        
    def ran_tool(self, tool):
        if self.tool_finished(tool) >= self.expected_per_tool:
            return True
        else:
            return False
    
    def resume(self):
        self.remaining = set()
        self.finished = set()
        for tool in self.tools:
            if self.ran_tool(tool):
                self.finished.add(tool)
            else:
                self.remaining.add(tool)
    
    def run_tool(self, tool):
        """Called by self.run()"""
        if self.ran_tool(tool):
            raise ValueError()
        tool_results = tool.query(self.validation_file.bad_lexed)
        insert = "INSERT INTO results(%s) values (?)" % (self.test.columns)
        values = [None] * len(self.test.columns)
        values[self.test.columns.indexof("mutation")] = self.mutation_name
        values[self.test.columns.indexof("good_file")] = (
            self.validation_file.good_path)
        values[self.test.columns.indexof("bad_file")] = (
            self.validation_file.bad_path)
        values[self.test.columns.indexof("iteration")] = (
            self.tool_finished())
        values[self.test.columns.indexof("tool")] = tool
        values[self.test.columns.indexof("change_operation")] = (
            self.validation_file.change_operation)
        values[self.test.columns.indexof("new_token_type")] = (
            self.validation_file.new_lexeme.type)
        values[self.test.columns.indexof("new_token_value")] = (
            self.validation_file.new_lexeme.value)
        values[self.test.columns.indexof("old_token_type")] = (
            self.validation_file.old_lexeme.type)
        values[self.test.columns.indexof("old_token_value")] = (
            self.validation_file.old_lexeme.value)
        values[self.test.columns.indexof("change_token_index")] = (
            self.validation_file.change_index)
        values[self.test.columns.indexof("change_start_line")] = (
            self.validation_file.new_lexeme.start.line)
        values[self.test.columns.indexof("change_start_col")] = (
            self.validation_file.new_lexeme.start.col)
        values[self.test.columns.indexof("change_end_line")] = (
            self.validation_file.new_lexeme.end.line)
        values[self.test.columns.indexof("change_end_col")] = (
            self.validation_file.new_lexeme.end.col)
        for result_type in self.test.result_types:
            result = result_type(tool_results, self.validation_file)
            result.save(values)
        for i in range(0,len(values)):
            assert values[i] is not None, self.test.columns[i]
            
    def run(self):
        for tool in self.tools:
            self.run_tool(tool)

class PairTask(Task):
    def __init__(self, test, validation_file, tools):
        super(PairTask, self).__init__(test, validation_file, tools, 1)
        self.mutation_name = "pair"

class MutationTask(Task):
    def __init__(self, test, validation_file, tools, mutation, n):
        super(MutationTask, self).__init__(test, validation_file, tools, n)
        self.mutation_name = mutation.__name__
        self.mutation = mutation
    
    def run_tool(self, tool):
        left = self.expected_per_tool - self.tool_finished(tool)
        for i in range(0, left):
            valid = True
            while valid: # look for an invalid mutation
                self.mutation(self.validation_file)
                valid = ((
                        len(self.validation_file.bad_lexed.check_syntax()) == 0
                        ) 
                    or (not self.test.retry_valid)
                    )
            super(MutationTask, self).run_tool(tool)


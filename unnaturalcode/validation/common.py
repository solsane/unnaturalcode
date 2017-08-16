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

from unnaturalcode.ucUtil import *
from unnaturalcode.unnaturalCode import *
from unnaturalcode.pythonSource import *
from unnaturalcode.mitlmCorpus import *
from unnaturalcode.sourceModel import *
from unnaturalcode.mutators import Mutators
from unnaturalcode.ucUser import pyUser

mutators = Mutators()

from logging import debug, info, warning, error
import logging
from os import path

import csv
from shutil import copyfile
from tempfile import mkstemp, mkdtemp
import os, re, site
import sqlite3

from unnaturalcode import flexibleTokenize

nonWord = re.compile('\\W+')
beginsWithWhitespace = re.compile('^\\w')
numeric = re.compile('[0-9]')
punct = re.compile('[~!@#$%^%&*(){}<>.,;\\[\\]`/\\\=\\-+]')
funny = re.compile(flexibleTokenize.Funny)
name = re.compile(flexibleTokenize.Name)

class HaltingError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)
    
class ValidationFile(object):
    language = None
    
    def __init__(self, 
                 good_path, 
                 tempDir, 
                 bad_path=None,
                 check=True):
        self.good_path = path
        with codecs.open(path, 'r', 'UTF-8') as good_fileh:
            self.good_text = self.good_fileh.read()
        self.good_lexed = self.language(self.good_text)
        self.good_scrubbed = self.good_lexed.scrubbed()
        if check:
            assert self.good_lexed.check_syntax() == []
        self.bad_path = None
        self.bad_text = None
        self.bad_lexed = None
        if bad_path is not None:
            self.bad_path = bad_path
            with codecs.open(path, 'r', 'UTF-8') as bad_fileh:
                self.bad_text = self.bad_fileh.read()
            self.bad_lexed = self.language(self.bad_text)
            if check:
                assert len(self.bad_lexed.check_syntax()) > 0
        self.tempDir = tempDir
        
    def compute_change(self):
        assert isinstance(self.bad_lexemes, ucSource)
    
    def mutate(self, new_lexemes):
        #TODO: check_syntax?
        self.bad_lexemes = lexemes
        self.bad_lexemes.check()
        self.compute_change()

class ValidationCorpus(object):
    def __init__(
            language_file,
            train,
            keep,
            corpus,
            results_dir,
        ):
        self.language_file=language_file
        self.language=language_file.language
        self.corpus=corpus
        self.sm = sourceModel(cm=self.corpus, language=self.language)
        self.results_dir = results_dir
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
    
    def train_files(train):
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
        
class ModelValidation(object):
    
    def validate(self, mutations, n):
        """Run main validation loop."""
        wtrr = 0 # total reciprocal rank
        wtr = 0 # total rank
        wttn = 0 # total in top n
        ltrr = 0 # total reciprocal rank
        ltr = 0 # total rank
        lttn = 0 # total in top n
        ttrr = 0 # total reciprocal rank
        ttr = 0 # total rank
        tttn = 0 # total in top n
        n_so_far = 0
        trues = 0
        valids = 0
        deletions = 0
        insertions = 0
        substitutions = 0
        assert n > 0
        for mutation in mutations:
         for fi in self.testFiles:
          assert isinstance(fi, ValidationFile)
          if fi.path in self.progress:
            progress = self.progress[(fi.path, mutation.__name__)]
          else:
            progress = 0
          info("Testing " + str(progress) + "/" + str(n) + " " + fi.path)
          for i in range(progress, n):
            merror = mutation(mutators, fi)
            if merror is not None:
              info(merror)
              break
            filename, line, func, text, exceptionName = self.get_error(fi)
            if self.retry_valid:
                while exceptionName is None:
                    info("Syntatically valid mutant, retrying.")
                    merror = mutation(mutators, fi)
                    filename, line, func, text, exceptionName = self.get_error(fi)
            if (fi.change_location.start.line == line):
              online = True
            else:
              online = False
            worst, un = self.sm.unwindowedQuery(fi.bad_lexemes)
            for uc_result in range(0, len(worst)):
                #debug(str(worst[i][0][0].start) + " " + str(fi.change_location.start) + " " + str(worst[i][1]))
                if ((worst[uc_result][0][0].start 
                     <= fi.change_location.start) 
                    and worst[uc_result][0][-1].end >= fi.change_location.end):
                    #debug(">>>> Rank %i (%s)" % (i, fi.path))
                    break
            for line_result in range(0, len(un)):
                if (un[line_result][0].start.line == fi.change_location.start.line):
                  info(" ".join(map(str,(un[0][0].start.line, worst[0][0][10].start.line, fi.change_location.start.line))))
                  break
                  #if ((un[line_result][0].start >= worst[0][0][0].start)
                    #and (un[line_result][0].end <= worst[0][0][-1].end)):
                    #break
                  #else:
                    #line_result += 20
                    #break
            tok_result_rank_found = False
            for tok_result in range(0, len(un)):
                if (un[tok_result][0].start >= fi.change_locationPrev.end) and (un[tok_result][0].start <= fi.change_locationNext.start):
                  info(" ".join(map(str,(un[0][0].start, worst[0][0][10].start, fi.change_location.start))))
                  tok_result_rank_found = True
                  break
            if not tok_result_rank_found:
                error("tok_result: " +  str(tok_result))
                error(repr(fi.change_locationPrev.end) + " < " + " > " + repr(fi.change_locationNext.start))
                for tok_result in range(0, len(un)):
                  if un[tok_result][0].start.line == fi.change_location.start.line or tok_result < 20:
                    error(" > " + repr(un[tok_result][0].start) + " " + repr(un[tok_result][0].start) + " < ")
                assert(False)
            info(" ".join(map(str, [mutation.__name__, uc_result, fi.change_location.start.line, exceptionName, line])))
            fix_k = 4
            fix = "NoFix"
            validfix = False
            fixop = "None"
            fixed = None
            sm = self.sm
            fixent = 1e70
            if tok_result < fix_k:
                (validfix, fixed, fixop, fixloc, fixtok, fixent) = self.sm.fixQuery(fi.bad_lexemes, un[tok_result][0])
            if validfix:
                if sm.stringifyAll(fi.scrubbed) == sm.stringifyAll(fixed):
                    fix = "TrueFix"
                    valids += 1
                    trues += 1
                else:
                    fix = "ValidFix"
                    valids += 1
                if fixop == "Delete":
                    deletions += 1
                elif fixop == "Insert":
                    insertions += 1
                elif fixop == "Replace":
                    substitutions += 1
            info(fix + " " + fixop)
            if uc_result >= len(worst):
              error(repr(worst))
              error(repr(fi.change_location))
              assert False
            self.csv.writerow([
              fi.path, 
              mutation.__name__, 
              uc_result, 
              worst[uc_result][1], 
              fi.change_location.type,
              fi.change_location.start.line,
              nonWord.sub('', fi.change_location.value), 
              exceptionName, 
              online,
              filename,
              line,
              func,
              worst[uc_result][0][0].start.line,
              un[tok_result][0].start.line,
              line_result,
              tok_result,
              fix,
              validfix,
              fixop
            ])
            self.csvFile.flush()
            wtrr += 1/float(uc_result+1)
            wtr += float(uc_result+1)
            if uc_result < 5:
                wttn += 1
            ltrr += 1/float(line_result+1)
            ltr += float(line_result+1)
            if line_result < 5:
                lttn += 1
            ttrr += 1/float(tok_result+1)
            ttr += float(tok_result+1)
            if tok_result < 5:
                tttn += 1
            n_so_far += 1
            wmrr = wtrr/float(n_so_far)
            wmr = wtr/float(n_so_far)
            wmtn = wttn/float(n_so_far)
            info("Window MRR %f MR %f M5+ %f" % (wmrr, wmr, wmtn))
            lmrr = ltrr/float(n_so_far)
            lmr = ltr/float(n_so_far)
            lmtn = lttn/float(n_so_far)
            info("Line MRR %f MR %f M5+ %f" % (lmrr, lmr, lmtn))
            tmrr = ttrr/float(n_so_far)
            tmr = ttr/float(n_so_far)
            tmtn = tttn/float(n_so_far)
            info("Token MRR %f MR %f M5+ %f" % (tmrr, tmr, tmtn))
            nos = n_so_far-valids
            no = float(nos)/float(n_so_far)
            true = float(valids)/float(n_so_far)
            valid = float(trues)/float(n_so_far)
            info("Fix No %i Valid %i True %i " % (nos, trues, valids))
            info("Fix No %f Valid %f True %f " % (no, true, valid))
            delete_ = float(deletions)/float(n_so_far)
            insert_ = float(insertions)/float(n_so_far)
            subs_ = float(substitutions)/float(n_so_far)
            info("Fix D %i I %i R %i " % (deletions, insertions, substitutions))
            info("Fix D %f I %f R %f " % (delete_, insert_, subs_))
      
    def __init__(self, 
                 test=None,
                 train=None,
                 language=pythonSource, 
                 resultsDir=None,
                 corpus=mitlmCorpus,
                 keep=False,
                 retry_valid=False):
        self.retry_valid = retry_valid
        if isinstance(test, str):
            raise NotImplementedError
        elif isinstance(test, list):
            self.testFileNames = test
        else:
            raise TypeError("Constructor arguments!")
        if isinstance(train, str):
            raise NotImplementedError
        elif isinstance(train, list):
            self.trainFileNames = train
        else:
            raise TypeError("Constructor arguments!")
        self.csvPath = path.join(self.resultsDir, 'results.csv')
        self.progress = dict()
        try:
          self.csvFile = open(self.csvPath, 'r')
          self.csv = csv.reader(self.csvFile)
          for row in self.csv:
            if (row[0], row[1]) in self.progress:
              self.progress[(row[0], row[1])] += 1 
            else:
              self.progress[(row[0], row[1])] = 1
          self.csvFile.close()
        except (IOError):
          pass
        self.csvFile = open(self.csvPath, 'a')
        self.csv = csv.writer(self.csvFile)
        self.cm = corpus(readCorpus=self.corpusPath, writeCorpus=self.corpusPath, order=10)
        self.lm = language
        self.sm = sourceModel(cm=self.cm, language=self.lm)
        self.trainFiles = list()
        self.testFiles = list()
        self.addValidationFile(self.trainFileNames, testing=False, training=True)
        self.genCorpus()
        del self.trainFiles
        self.addValidationFile(self.testFileNames, testing=True, training=False)

    def release(self):
        """Close files and stop MITLM"""
        self.cm.release()
        self.cm = None
        
    def __del__(self):
        """I am a destructor, but release should be called explictly."""
        assert not self.cm, "Destructor called before release()"
        
class Result(object):
    @classmethod
    def column_names(cls):
        return [i % (cls.db_name)
                for i in ["%s_rank",
                "%s_start_line",
                "%s_start_col",
                "%s_end_line",
                "%s_end_col",
                "%s_top_distance_lines",
                "%s_top_distance_toks"
                ]
            ]

class LineLocation(Result):
    db_name = "line_location"
    
class WindowLocation(Result):
    db_name = "window_location"

class ExactLocation(Result):
    db_name = "exact_location"
    
class ValidFix(Result):
    db_name = "valid_fix"
    
class TrueFix(Result):
    db_name = "true_fix"
    
        
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
                "good_file = ?, tool = ?", 
                (self.validation_file.good_path,
                    tool.name
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
            return
        bad_text = self.validation_file.bad_text
        assert bad_text is not None
        tool_results = tool.query(bad_text)
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
            
class PairTask(Task):
    def __init__(self, test, validation_file, tools):
        super(PairTask, self).__init__(test, validation_file, tools, 1)
        
    def run(self):
        for tool in tools:
            self.run_tool(tool)

class ValidationTest(object):
    fields = [  
        "mutation",
        "good_file",
        "bad_file",
        "iteration",
        "tool",
        "change_operation",
        "new_token_type",
        "new_token_value",
        "old_token_type",
        "old_token_value",
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
    
    def __init__(self, corpus):
        self.corpus=corpus
        self.language=corpus.language
        self.sm=corpus.sm
        self.results_dir=corpus.results_dir
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
        
    def add_pair_tests(self, test):
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
                
                info("Using %s for testing." % (fi))
                n_added += 1
                task = PairTask(self, valid_fi)
            except:
                info("Skipping %s !!!" % (fi), exc_info=sys.exc_info())
                n_skipped += 1
        info("Using: %i, Skipped: %i" % (n_added, n_skipped)) 
            
class ValidationMain(object):
    
    self.validation_corpus_class = ValidationCorpus
    self.validation_file_class = ValidationFile
    self.validation_test_class = ValidationTest
    
    def add_args(self, parser):
        """For overriding in subclasses to add more args."""
        pass 
    
    def read_args(self, args):
        """For overriding in subclasses to add more args."""
        pass
   
    def main(self):
        from argparse import ArgumentParser
        parser = ArgumentParser(description="Test and Valide UnnaturalCode")
        parser.add_argument('-t', '--mutation-file-list', nargs='?', 
                            help='List of files to Test')
        parser.add_argument('-T', '--train-file-list', nargs='?', 
                            help='List of files to train on.'
                                ' Default same as test.')
        parser.add_argument('-k', '--keep-corpus', action='store_true', 
                            help="Don't reset the corpus")
        parser.add_argument('-n', '--iterations', type=int, 
                            help='Number of times to iterate', default=50)
        parser.add_argument('-o', '--output-dir', 
                            help='Location to store output files', default='.')
        parser.add_argument('-m', '--mutation', 
                            help='Mutation to use', 
                            required=True, action='append')
        parser.add_argument('-r', '--retry-valid', action='store_true', 
                            help='Retry until a syntactically incorrect'
                            ' mutation is found')
        parser.add_argument('-p', '--pair-file-list', nargs='?',
                            help='File containing comma-seperated pairs of'
                                ' bad, good files to'
                                ' test')
        self.add_args(parser) # get more args from subclasses
        
        args=parser.parse_args()
        logging.getLogger().setLevel(logging.DEBUG)

        self.read_args(args) # let subclasses read their args
        
        resultsDir = ((args.output_dir 
                                or os.getenv("ucResultsDir", None)) 
                            or mkdtemp(prefix='ucValidation-'))

        testFileList = args.test_file_list
        testProjectFiles = open(testFileList).read().splitlines()
        
        corpus = self.validation_corpus_class(
                                language_file=self.validation_file_class,
                                train=args.train_file_list,
                                keep=args.keep_corpus,
                                corpus=mitlmCorpus,
                                resultsDir=resultsDir,
            )
        
        test = self.validation_test_class(
            corpus=corpus
        )
        
        if args.mutation_file_list:
            test.add_mutation_tests(
                test=args.mutation_file_list,
                retry_valid=args.retry_valid,
                mutations=args.mutations,
                n=args.iterations,
                )
        
        if args.pair_file_list:
            test.add_pair_tests(
                test=args.mutation_file_list
            )
            
        test.resume()
        
        test.run()
            
        #else:
            #self.read_args(args)
            #v = self.validation(test=testProjectFiles,
                                #retry_valid=args.retry_valid)
            #mutations=[getattr(Mutators, mutation) for mutation in args.mutation]
            #v.validate(mutations=mutations, n=args.iterations)
            ## TODO: assert csvs
            #v.release()


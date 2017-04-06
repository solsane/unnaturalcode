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
    
    def __init__(self, path, language, tempDir):
        self.path = path
        self.lm = language
        self.f = codecs.open(path, 'r', 'UTF-8')
        self.original = self.f.read()
        self.lexed = self.lm(self.original)
        self.scrubbed = self.lexed.scrubbed()
        self.f.close()
        self.mutatedLexemes = None
        self.mutatedLocation = None
        self.tempDir = tempDir
    
    def mutate(self, lexemes, locationPrev, location, locationNext):
        assert isinstance(lexemes, ucSource)
        #self.mutatedLexemes = self.lm(lexemes.deLex())
        self.mutatedLexemes = lexemes
        self.mutatedLocationPrev = locationPrev
        self.mutatedLocation = location
        self.mutatedLocationNext = locationNext
        assert self.mutatedLocationPrev.end <= self.mutatedLocation.start, (
          repr(self.mutatedLocationPrev.end) 
          + " </= " + repr(self.mutatedLocation.start)
          + "\n" + repr(self.lexed))
        assert self.mutatedLocation.end <= self.mutatedLocationNext.start, (
          repr(self.mutatedLocation.end) 
          + " </= " 
          + repr(self.mutatedLocationNext.start))
        
class ModelValidation(object):
    
    def addValidationFile(self, files, training, testing):
          """Add a file for validation..."""
          files = [files] if isinstance(files, str) else files
          assert isinstance(files, list)
          nSkipped = 0
          nAdded = 0
          for fi in files:
            try:
                vfi = self.languageValidationFile(fi, self.lm, self.resultsDir)
                if training:
                    self.trainFiles.append(vfi)
                    info("Using %s for training." % (fi))
                if (len(vfi.lexed) > self.sm.windowSize) and testing:
                    self.testFiles.append(vfi)
                    info("Using %s in %s mode for testing." % (fi, vfi.mode))
                    nAdded += 1
            except:
                info("Skipping %s !!!" % (fi), exc_info=sys.exc_info())
                nSkipped += 1
          info("Using: %i, Skipped: %i" % (nAdded, nSkipped)) 
    
    def genCorpus(self):
          """Create the corpus from the known-good file list."""
          for fi in self.trainFiles:
            self.sm.trainLexemes(fi.scrubbed)
    
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
            if (fi.mutatedLocation.start.line == line):
              online = True
            else:
              online = False
            worst, un = self.sm.unwindowedQuery(fi.mutatedLexemes)
            for uc_result in range(0, len(worst)):
                #debug(str(worst[i][0][0].start) + " " + str(fi.mutatedLocation.start) + " " + str(worst[i][1]))
                if ((worst[uc_result][0][0].start 
                     <= fi.mutatedLocation.start) 
                    and worst[uc_result][0][-1].end >= fi.mutatedLocation.end):
                    #debug(">>>> Rank %i (%s)" % (i, fi.path))
                    break
            for line_result in range(0, len(un)):
                if (un[line_result][0].start.line == fi.mutatedLocation.start.line):
                  info(" ".join(map(str,(un[0][0].start.line, worst[0][0][10].start.line, fi.mutatedLocation.start.line))))
                  break
                  #if ((un[line_result][0].start >= worst[0][0][0].start)
                    #and (un[line_result][0].end <= worst[0][0][-1].end)):
                    #break
                  #else:
                    #line_result += 20
                    #break
            tok_result_rank_found = False
            for tok_result in range(0, len(un)):
                if (un[tok_result][0].start >= fi.mutatedLocationPrev.end) and (un[tok_result][0].start <= fi.mutatedLocationNext.start):
                  info(" ".join(map(str,(un[0][0].start, worst[0][0][10].start, fi.mutatedLocation.start))))
                  tok_result_rank_found = True
                  break
            if not tok_result_rank_found:
                error("tok_result: " +  str(tok_result))
                error(repr(fi.mutatedLocationPrev.end) + " < " + " > " + repr(fi.mutatedLocationNext.start))
                for tok_result in range(0, len(un)):
                  if un[tok_result][0].start.line == fi.mutatedLocation.start.line or tok_result < 20:
                    error(" > " + repr(un[tok_result][0].start) + " " + repr(un[tok_result][0].start) + " < ")
                assert(False)
            info(" ".join(map(str, [mutation.__name__, uc_result, fi.mutatedLocation.start.line, exceptionName, line])))
            fix_k = 4
            fix = "NoFix"
            validfix = False
            fixop = "None"
            fixed = None
            sm = self.sm
            fixent = 1e70
            if tok_result < fix_k:
                (validfix, fixed, fixop, fixloc, fixtok, fixent) = self.sm.fixQuery(fi.mutatedLexemes, un[tok_result][0])
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
              error(repr(fi.mutatedLocation))
              assert False
            self.csv.writerow([
              fi.path, 
              mutation.__name__, 
              uc_result, 
              worst[uc_result][1], 
              fi.mutatedLocation.type,
              fi.mutatedLocation.start.line,
              nonWord.sub('', fi.mutatedLocation.value), 
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
        self.resultsDir = ((resultsDir or os.getenv("ucResultsDir", None)) or mkdtemp(prefix='ucValidation-'))
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
        assert os.access(self.resultsDir, os.X_OK & os.R_OK & os.W_OK)
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
        self.corpusPath = os.path.join(self.resultsDir, 'validationCorpus')
        if keep:
            pass
        elif os.path.exists(self.corpusPath):
            os.remove(self.corpusPath)
        if keep:
            pass
        elif os.path.exists(self.corpusPath + ".uniqueTokens"):
            os.remove(self.corpusPath + ".uniqueTokens")
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

class ValidationMain(object):
  
    def add_args(self, parser):
        """For overriding in subclasses to add more args."""
        pass 
    
    def read_args(self, args):
        """For overriding in subclasses to add more args."""
        pass
   
    def main(self):
        from argparse import ArgumentParser
        parser = ArgumentParser(description="Test and Valide UnnaturalCode")
        parser.add_argument('-t', '--test-file-list', nargs='?', help='List of files to Test')
        parser.add_argument('-T', '--train-file-list', nargs='?', help='List of files to train on. Default same as test.')
        parser.add_argument('-k', '--keep-corpus', action='store_true', help="Don't reset the corpus")
        parser.add_argument('-n', '--iterations', type=int, help='Number of times to iterate', default=50)
        parser.add_argument('-o', '--output-dir', help='Location to store output files', default='.')
        parser.add_argument('-m', '--mutation', help='Mutation to use', required=True, action='append')
        parser.add_argument('-r', '--retry-valid', action='store_true', help='Retry until a syntactically incorrect mutation is found')
        self.add_args(parser) # get more args from subclasses
        args=parser.parse_args()
        logging.getLogger().setLevel(logging.DEBUG)
        testFileList = args.test_file_list
        trainFileList = testFileList
        if args.train_file_list:
            trainFileList = args.train_file_list
        testProjectFiles = open(testFileList).read().splitlines()
        trainProjectFiles = open(trainFileList).read().splitlines()
        
        self.read_args(args)
        v = self.validation(test=testProjectFiles,
                            train=trainProjectFiles,
                            keep=args.keep_corpus,
                            corpus=mitlmCorpus,
                            resultsDir=args.output_dir,
                            retry_valid=args.retry_valid)
        mutations=[getattr(Mutators, mutation) for mutation in args.mutation]
        v.validate(mutations=mutations, n=args.iterations)
        # TODO: assert csvs
        v.release()


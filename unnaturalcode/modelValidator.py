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

import pdb



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
    
    def mutate(self, lexemes, location):
        assert isinstance(lexemes, ucSource)
        #self.mutatedLexemes = self.lm(lexemes.deLex())
        self.mutatedLexemes = lexemes
        self.mutatedLocation = location
        
        
class ModelValidation(object):
    
    def addValidationFile(self, files):
          """Add a file for validation..."""
          files = [files] if isinstance(files, str) else files
          assert isinstance(files, list)
          nSkipped = 0
          nAdded = 0
          for fi in files:
            try:
                vfi = self.languageValidationFile(fi, self.lm, self.resultsDir)
                if len(vfi.lexed) > self.sm.windowSize:
                    self.validFiles.append(vfi)
                    info("Using %s in %s mode." % (fi, vfi.mode))
                    nAdded += 1
            except:
                info("Skipping %s !!!" % (fi), exc_info=sys.exc_info())
                nSkipped += 1
          info("Using: %i, Skipped: %i" % (nAdded, nSkipped)) 
    
    def genCorpus(self):
          """Create the corpus from the known-good file list."""
          for fi in self.validFiles:
            self.sm.trainLexemes(fi.scrubbed)
    
    def validate(self, mutation, n):
        """Run main validation loop."""
        trr = 0 # total reciprocal rank
        tr = 0 # total rank
        ttn = 0 # total in top n
        n_so_far = 0
        assert n > 0
        for fi in self.validFiles:
          assert isinstance(fi, ValidationFile)
          if fi.path in self.progress:
            progress = self.progress[fi.path]
          else:
            progress = 0
          info("Testing " + str(progress) + "/" + str(n) + " " + fi.path)
          for i in range(progress, n):
            merror = mutation(mutators, fi)
            if merror is not None:
              info(merror)
              break
            filename, line, func, text, exceptionName = self.get_error(fi)
            if (fi.mutatedLocation.start.line == line):
              online = True
            else:
              online = False
            worst = self.sm.worstWindows(fi.mutatedLexemes)
            for uc_result in range(0, len(worst)):
                #debug(str(worst[i][0][0].start) + " " + str(fi.mutatedLocation.start) + " " + str(worst[i][1]))
                if ((worst[uc_result][0][0].start 
                     <= fi.mutatedLocation.start) 
                    and worst[uc_result][0][-1].end >= fi.mutatedLocation.end):
                    #debug(">>>> Rank %i (%s)" % (i, fi.path))
                    break
            info(" ".join(map(str, [mutation.__name__, uc_result, fi.mutatedLocation.start.line, exceptionName, line])))
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
              worst[uc_result][0][0].start.line])
            self.csvFile.flush()
            trr += 1/float(uc_result+1)
            tr += float(uc_result+1)
            if uc_result < 5:
                ttn += 1
            n_so_far += 1
            mrr = trr/float(n_so_far)
            mr = tr/float(n_so_far)
            mtn = ttn/float(n_so_far)
            info("MRR %f MR %f M5+ %f" % (mrr, mr, mtn))
            
      
    def __init__(self, 
                 source=None, 
                 language=pythonSource, 
                 resultsDir=None,
                 corpus=mitlmCorpus):
        self.resultsDir = ((resultsDir or os.getenv("ucResultsDir", None)) or mkdtemp(prefix='ucValidation-'))
        if isinstance(source, str):
            raise NotImplementedError
        elif isinstance(source, list):
            self.validFileNames = source
        else:
            raise TypeError("Constructor arguments!")

        assert os.access(self.resultsDir, os.X_OK & os.R_OK & os.W_OK)
        self.csvPath = path.join(self.resultsDir, 'results.csv')
        self.progress = dict()
        try:
          self.csvFile = open(self.csvPath, 'r')
          self.csv = csv.reader(self.csvFile)
          for row in self.csv:
            if row[0] in self.progress:
              self.progress[row[0]] += 1 
            else:
              self.progress[row[0]] = 1
          self.csvFile.close()
        except (IOError):
          pass
        self.csvFile = open(self.csvPath, 'a')
        self.csv = csv.writer(self.csvFile)
        self.corpusPath = os.path.join(self.resultsDir, 'validationCorpus')
        self.cm = corpus(readCorpus=self.corpusPath, writeCorpus=self.corpusPath, order=10)
        self.lm = language
        self.sm = sourceModel(cm=self.cm, language=self.lm)
        self.validFiles = list()
        self.addValidationFile(self.validFileNames)
        self.genCorpus()

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
        parser.add_argument('-n', '--iterations', type=int, help='Number of times to iterate', default=50)
        parser.add_argument('-o', '--output-dir', help='Location to store output files', default='.')
        parser.add_argument('-m', '--mutation', help='Mutation to use', required=True)
        parser.add_argument('-M', '--mitlm', help='Location of MITLM binary')
        self.add_args(parser) # get more args from subclasses
        args=parser.parse_args()
        logging.getLogger().setLevel(logging.DEBUG)
        testFileList = args.test_file_list
        testProjectFiles = open(testFileList).read().splitlines()
        
        if (args.mitlm):
            os.environ["ESTIMATENGRAM"] = args.mitlm
            os.environ["LD_LIBRARY_PATH"] = os.path.dirname(args.mitlm)
            error(os.environ["LD_LIBRARY_PATH"])
        
        self.read_args(args)
        v = self.validation(source=testProjectFiles, 
                            corpus=mitlmCorpus, 
                            resultsDir=args.output_dir)
        
        v.validate(mutation=getattr(Mutators, args.mutation), n=args.iterations)
        # TODO: assert csvs
        v.release()


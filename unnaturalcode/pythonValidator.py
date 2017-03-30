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
import sys
import traceback
import runpy


from unnaturalcode.modelValidator import ValidationFile, ModelValidation, ValidationMain
from unnaturalcode.mitlmCorpus import mitlmCorpus
from unnaturalcode.pythonSource import pythonSource
from unnaturalcode.mutators import Mutators

def runFile(q,path,mode):
    if not virtualEnvActivate is None:
      if sys.version_info >= (3,0):
        exec(compile(open(virtualEnvActivate, "rb").read(), virtualEnvActivate, 'exec'), dict(__file__=virtualEnvActivate))
      else:
        execfile(virtualEnvActivate, dict(__file__=virtualEnvActivate))
    parent = path
    runit = None
    while len(parent) > 1:
        parent = os.path.dirname(parent)
        sys.path = sys.path + [parent]
        if mode == 'module':
            moduleSite = ""
            #info("Path: %s" % path)
            for s in sys.path:
                if s in path:
                    if ('site-packages' in path and
                        (not 'site-packages' in os.path.basename(s))):
                        continue
                    if len(s) > len(moduleSite):
                        moduleSite = s
                        break
            #info("Python path: %s" % moduleSite)
            relpath = os.path.relpath(path, moduleSite)
            #info("Relative path: %s" % relpath)
            components = relpath.split(os.path.sep)
            components[-1] = components[-1].replace(".py", "", 1)
            module = ".".join(components)
            #info("Module name: %s" % module)
            runit = lambda: runpy.run_module(module)
        elif mode == 'script':
            runit = lambda: runpy.run_path(path)
        elif mode == 'module_indir':
            moduledir = os.path.dirname(path)
            filename = os.path.basename(path)
            os.chdir(moduledir)
            runit = lambda: runpy.run_path(filename)
        else:
            raise ValueError("Mode not recognized?") 
    old_stdout = os.dup(sys.stdout.fileno())
    old_stderr = os.dup(sys.stderr.fileno())
    old_stdin = os.dup(sys.stdin.fileno())
    devnull = os.open('/dev/null', os.O_RDWR)
    os.dup2(devnull, sys.stdout.fileno())
    os.dup2(devnull, sys.stderr.fileno())
    os.dup2(devnull, sys.stdin.fileno())
    try:
        runit()
    except SyntaxError as se:
        os.dup2(old_stdout, sys.stdout.fileno())
        os.dup2(old_stderr, sys.stderr.fileno())
        os.dup2(old_stdin, sys.stdin.fileno())
        ei = sys.exc_info();
        #info("run_path exception:", exc_info=ei)
        eip = (ei[0], str(ei[1]), traceback.extract_tb(ei[2]))
        try:
          eip[2].append(ei[1][1])
        except IndexError:
          eip[2].append((se.filename, se.lineno, None, None))
        q.put(eip)
        return
    except Exception as e:
        os.dup2(old_stdout, sys.stdout.fileno())
        os.dup2(old_stderr, sys.stderr.fileno())
        os.dup2(old_stdin, sys.stdin.fileno())
        ei = sys.exc_info();
        #info("run_path exception:", exc_info=ei)
        eip = (ei[0], str(ei[1]), traceback.extract_tb(ei[2]))
        q.put(eip)
        return
    finally:
        os.dup2(old_stdout, sys.stdout.fileno())
        os.dup2(old_stderr, sys.stderr.fileno())
        os.dup2(old_stdin, sys.stdin.fileno())
    q.put((None, "None", [(path, None, None, None)]))

class PythonValidationFile(ValidationFile):
    def run(self, path):
        q = Queue()
        p = Process(target=runFile, args=(q,path,self.mode))
        p.start()
        try:
          r = q.get(True, 10)
        except Empty as e:
          r = (HaltingError, "Didn't halt.", [(path, None, None, None)])
        p.terminate()
        p.join()
        assert not p.is_alive()
        #assert r[2][-1][2] != "_get_code_from_file" # This seems to be legit
        return r
  
    def __init__(self, path, language, tempDir):
        super(PythonValidationFile,self).__init__(path, language, tempDir)
        self.mode = 'script'
        r = self.run(path)
        rscript = r
        if (r[0] != None):
            self.mode = 'module'
            r = self.run(path)
            if (r[0] != None):
                self.mode = 'module_indir'
                r = self.run(path)
        #info("Ran %s as a %s, got %s" % (self.path, self.mode, r[1]))
        if (r[0] != None):
          raise Exception("Couldn't run file: %s because %s" % (self.path, r[1]))

    def runMutant(self):
        (mutantFileHandle, mutantFilePath) = mkstemp(suffix=".py", prefix="mutant", dir=self.tempDir)
        mutantFile = os.fdopen(mutantFileHandle, "w")
        mutantFile.write(self.mutatedLexemes.deLex())
        mutantFile.close()
        r = self.run(mutantFilePath)
        os.remove(mutantFilePath)
        return r


class PythonValidation(ModelValidation):
    def get_error(self, fi):
      runException = fi.runMutant()
      if (runException[0] == None):
        exceptionName = "None"
      else:
        exceptionName = runException[0].__name__
      filename, line, func, text = runException[2][-1]
      return (filename, line, func, text, exceptionName)

    def __init__(self, 
                 source=None, 
                 resultsDir=None,
                 corpus=mitlmCorpus):
       self.languageValidationFile = PythonValidationFile
       super(PythonValidation,self).__init__(source=source,
                                             language=pythonSource,
                                             resultsDir=resultsDir,
                                             corpus=mitlmCorpus)

class PythonValidationMain(ValidationMain):
    def add_args(self, parser):
        parser.add_argument('-v', '--virtualenv', help='VirtualEnv to use when running the files under test. Must be the location of activate_this.py')

    def read_args(self, args):
        global virtualEnvActivate
        virtualEnvActivate = args.virtualenv
        # wow, this is actually how virtualenv does it...
        virtualEnvBase = os.path.basename(os.path.basename(virtualEnvActivate))
        virtualEnvSite = os.path.join(virtualEnvBase, 'lib', 'python%s' % sys.version[:3], 'site-packages')

    def __init__(self, *args, **kwargs):
        self.validation = PythonValidation
        super(PythonValidationMain,self).__init__(*args, **kwargs)

if __name__ == '__main__':
    PythonValidationMain().main()

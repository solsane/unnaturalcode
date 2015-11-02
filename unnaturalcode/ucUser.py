#    Copyright 2013, 2014 Joshua Charles Campbell
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
from unnaturalcode.genericSource import *
import shutil


class genericUser(object):

  def getHome(self):
      self.homeDir = os.path.expanduser("~")
      self.ucDir = os.getenv("UC_DATA", os.path.join(self.homeDir, ".unnaturalCode"))
      if not os.path.exists(self.ucDir):
        os.makedirs(self.ucDir)
      assert os.access(self.ucDir, os.X_OK & os.R_OK & os.W_OK)
      assert os.path.isdir(self.ucDir)
  
  def __init__(self, ngram_order=10):
      self.getHome()
      
      self.readCorpus = os.path.join(self.ucDir, 'genericCorpus') 
      if not os.path.exists(self.readCorpus):
        with open(self.readCorpus, 'wb') as f:
            corpus = 'for i in range ( 10 ) : <NEWLINE> <INDENT> print i\n'
            f.write(corpus)
      self.logFilePath = os.path.join(self.ucDir, 'genericLogFile')
      self.lm = genericSource
      self.basicSetup(ngram_order)
   
  def basicSetup(self, ngram_order=10):
      self.uc = unnaturalCode(logFilePath=self.logFilePath)
      # Oiugh... thank you, dependecy injection.
      self.cm = mitlmCorpus(readCorpus=self.readCorpus,
                            writeCorpus=self.readCorpus,
                            uc=self.uc,
                            order=ngram_order)
      self.sm = sourceModel(cm=self.cm, language=self.lm)
      
  def release(self):
      self.cm.release()
      
  def delete(self):
        # Ain't gotta do nothing if the file doesn't exist.
        if os.path.exists(self.readCorpus):
            replacementPath = self.readCorpus + '.bak'
            shutil.move(self.readCorpus, replacementPath)
      

class pyUser(genericUser):
  
  def __init__(self, ngram_order=10):
      self.getHome()
      self.readCorpus = os.path.join(self.ucDir, 'pyCorpus') 
      if not os.path.exists(self.readCorpus):
        with open(self.readCorpus, 'wb') as f:
            corpus = 'for i in range ( 10 ) : <NEWLINE> <INDENT> print i\n'
            f.write(corpus)
      self.logFilePath = os.path.join(self.ucDir, 'pyLogFile')
      self.lm = pythonSource
      self.basicSetup(ngram_order)
      

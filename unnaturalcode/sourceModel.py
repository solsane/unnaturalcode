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
from unnaturalcode.mitlmCorpus import *
from unnaturalcode.pythonSource import *
from unnaturalcode.unnaturalCode import ucLexeme
from operator import itemgetter
from logging import debug, info, warning, error
import os.path
import pickle

class sourceModel(object):

    def __init__(self, cm=mitlmCorpus(), language=pythonSource, windowSize=20):
        self.cm = cm
        self.lang = language
        self.windowSize = windowSize
        self.listOfUniqueTokens = {}
        self.uTokenFile = self.cm.writeCorpus + ".uniqueTokens"
        readTokenFile = self.cm.readCorpus + ".uniqueTokens"
        if os.path.isfile(readTokenFile):
          with open(readTokenFile, "rb") as f:
            self.listOfUniqueTokens = pickle.load(f)

    def trainFile(self, files):
        """Blindly train on a set of files whether or not it compiles..."""
        files = [files] if isinstance(files, str) else files
        assert isinstance(files, list)
        for fi in files:
            sourceCode = slurp(fi)
            self.trainString(sourceCode)

    def stringifyAll(self, lexemes):
        """Clean up a list of lexemes and convert it to a list of strings"""
        return [i[4] for i in lexemes]

    def corpify(self, lexemes):
        """Corpify a string"""
        return self.cm.corpify(self.stringifyAll(lexemes))

    def sourceToScrubbed(self, sourceCode):
        return self.lang(sourceCode).scrubbed()

    def trainLexemes(self, lexemes):
        """Train on a lexeme sequence."""
        lexemes = lexemes.scrubbed()
        for l in lexemes:
            if l[4] not in self.listOfUniqueTokens:
                self.listOfUniqueTokens[l[4]] = l
        with open(self.uTokenFile, "wb") as f:
            pickle.dump(self.listOfUniqueTokens, f)
        windowlen = self.windowSize
        padding = windowlen
        lstrings = self.stringifyAll(lexemes)
        qstrings = ((["/*<START>*/"] * windowlen)
                    + lstrings 
                    + (["/*<END>*/"] * windowlen)
                   )
        return self.cm.addToCorpus(qstrings)

    def trainString(self, sourceCode):
        """Train on a source code string"""
        return self.trainLexemes(self.sourceToScrubbed(sourceCode))

    def queryString(self, sourceCode):
        return self.queryLexed(self.lang(sourceCode))

    def queryLexed(self, lexemes):
        return self.cm.queryCorpus(self.stringifyAll(lexemes))

    def predictLexed(self, lexemes):
        return self.cm.predictCorpus(self.stringifyAll(lexemes))

    def windowedQuery(self, lexemes, returnWindows=True):
        lastWindowStarts = len(lexemes)-self.windowSize
        #error("Query was %i long:" % (len(lexemes),)) 
        if lastWindowStarts < 1:
            if returnWindows:
                return [(lexemes, self.queryLexed(lexemes))]
            else:
                return [(False, self.queryLexed(lexemes))]                
        r = []
        for i in range(0,lastWindowStarts+1): # remember range is [)
            end = i+self.windowSize
            w = lexemes[i:end] # remember range is [)
            e = self.queryLexed(w)
            if returnWindows:
                r.append( (w,e) )
            else:
                r.append( (False,e) )
        return r

    def worstWindows(self, lexemes):
        lexemes = lexemes.scrubbed()
        unsorted = self.windowedQuery(lexemes)
        return sorted(unsorted, key=itemgetter(1), reverse=True)
    
    def unwindowedQuery(self, lexemes):
        lexemes = lexemes.scrubbed()
        windowlen = self.windowSize
        padding = windowlen
        lstrings = self.stringifyAll(lexemes)
        content_len = len(lstrings)
        content_start = padding
        content_end = padding + content_len
        qstrings = ((["/*<START>*/"] * windowlen)
                    + lstrings 
                    + (["/*<END>*/"] * windowlen)
                   )
        start_pos = lexemes[0].start
        end_pos = lexemes[-1].end
        qtokens = (([ucLexeme(("LMStartPadding", "", start_pos, start_pos, "/*<START>*/"))]
                      * windowlen)
                    + lexemes
                    + ([ucLexeme(("LMEndPadding", "", end_pos, end_pos, "/*<END>*/"))]
                       * windowlen)
                   )
        total_len = len(qstrings)
        window_entropies = []
        windows = []
        unwindow_entropies = []
        for token_i in range(0, total_len):
            qstart = max(0,token_i+1-windowlen)
            qend = token_i+1
            query = qstrings[qstart:qend]
            windows.append(qtokens[qstart:qend])
            entropy = self.cm.queryCorpus(query)
            window_entropies.append(entropy)
            unwindow_entropies.append(0)
            for token_j in range(qstart, qend):
                unwindow_entropies[token_j] += window_entropies[token_i]/(qend-qstart)
            #if token_i >= content_start and token_i < content_end:
                #"""
                #This part is magical. It comes from building an array with a moving
                #band of 1s representing the window and then inverting it.
                #It could be made non-quadratic if necessary by saving earlier sums
                #and reusing them.
                #Apprently doesn't work that well, however.
                #"""
                #unwindow_entropies.append(
                    #sum([window_entropies[i] for i in xrange(token_i,-1,-windowlen)])
                    #- sum([window_entropies[i] for i in xrange(token_i-1,-1,-windowlen)])
                #)
            #else:
                #unwindow_entropies.append(0) # don't consider padding tokens
        windows = zip(windows, window_entropies)
        windows = windows[content_start:content_end]
        unwindows = zip(qtokens, unwindow_entropies)
        unwindows = unwindows[content_start:content_end]
        return (sorted(windows, key=itemgetter(1), reverse=True),
                sorted(unwindows, key=itemgetter(1), reverse=True))
      
    def isValid(self, lexemes):
        (filename, line, func, text, exceptionName) = lexemes.check_syntax()
        if exceptionName is None:
            return True
        else:
            return False
    
    def tryDelete(self, lexemes, loci):
        ta = lexemes[loci]
        attempt = copy(lexemes)
        deleted = attempt.pop(loci)
        window = lexemes[max(0, loci-self.windowSize):
                           min(len(lexemes),loci+self.windowSize+1)]
        tb = window.pop(min(self.windowSize, loci))
        assert ta == tb, "\n".join((repr(ta), repr(tb)))
        qattempt = (["/*<START>*/"] * max(0, self.windowSize-loci) +
                    self.stringifyAll(window) +
                    ["/*<END>*/"] * max(0, (loci-len(lexemes))+self.windowSize+1))
        assert len(qattempt) == (2*self.windowSize), len(qattempt)
        entropy = self.cm.queryCorpus(qattempt)
        assert len(attempt) == len(lexemes)-1
        if self.isValid(attempt):
            return (True, attempt, "Delete", loci, deleted, entropy)
        else:
            return (False, attempt, "Delete", loci, deleted, entropy)
    
    def tryInsert(self, lexemes, loci):
        window = lexemes[max(0, loci-self.windowSize):
                           min(len(lexemes),loci+self.windowSize)]
        results = []
        for string, token in self.listOfUniqueTokens.items():
            wattempt = copy(window)
            wattempt.insert(min(self.windowSize, loci), token)
            qattempt = (["/*<START>*/"] * max(0, self.windowSize-loci) +
                        self.stringifyAll(wattempt) +
                        ["/*<END>*/"] * max(0, (loci-len(lexemes))+self.windowSize))
            assert len(qattempt) == (2*self.windowSize)+1, len(qattempt)
            entropy = self.cm.queryCorpus(qattempt)
            results.append((token, entropy))
        bestresults = sorted(results, key=itemgetter(1), reverse=False)    
        attempt = copy(lexemes)
        attempt.insert(loci,bestresults[0][0])
        assert len(attempt) == len(lexemes)+1
        if self.isValid(attempt):
            return (True, attempt, "Insert", loci, attempt[loci], bestresults[0][1])
        else:
            return (False, attempt, "Insert", loci, attempt[loci], bestresults[0][1])

    def tryReplace(self, lexemes, loci):
        ta = lexemes[loci]
        window = lexemes[max(0, loci-self.windowSize):
                           min(len(lexemes),loci+self.windowSize+1)]
        results = []
        for string, token in self.listOfUniqueTokens.items():
            wattempt = copy(window)
            tb = wattempt.pop(min(self.windowSize, loci))
            assert ta == tb, "\n".join((repr(ta), repr(tb)))
            wattempt.insert(self.windowSize, token)
            qattempt = (["/*<START>*/"] * max(0, self.windowSize-loci) +
                        self.stringifyAll(wattempt) +
                        ["/*<END>*/"] * max(0, (loci-len(lexemes))+self.windowSize+1))
            assert len(qattempt) == (2*self.windowSize)+1, len(qattempt)
            entropy = self.cm.queryCorpus(qattempt)
            results.append((token, entropy))
        bestresults = sorted(results, key=itemgetter(1), reverse=False)    
        attempt = copy(lexemes)
        attempt.pop(loci)
        attempt.insert(loci,bestresults[0][0])
        assert len(attempt) == len(lexemes)
        if self.isValid(attempt):
            return (True, attempt, "Replace", loci, attempt[loci], bestresults[0][1])
        else:
            return (False, attempt, "Replace", loci, attempt[loci], bestresults[0][1])

    def fixQuery(self, lexemes, location):
        found = False
        for loci in range(0, len(lexemes)):
            if location.start == lexemes[loci].start:
                found = True
                break
        assert found
        #TODO: This is wrong and needs to be fixed, but its compatible
        # with the ICSME paper
        fixes = [(False, None, "None", loci, None, 1e70)]
        fix = self.tryDelete(lexemes, loci)
        if fix[0]: fixes.append(fix)
        fix = self.tryInsert(lexemes, loci)
        if fix[0]: fixes.append(fix)
        fix = self.tryReplace(lexemes, loci)
        if fix[0]: fixes.append(fix)
        fixes = sorted(fixes, key=itemgetter(5), reverse=False)
        return fixes[0]

    def release(self):
        self.cm.release()

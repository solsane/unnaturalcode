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

from __future__ import division

import logging
logger = logging.getLogger(__name__)
DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
ERROR = logger.error
CRITICAL = logger.critical

from unnaturalcode.source import Lexeme, Position
from unnaturalcode.change import Change
from operator import itemgetter
import os.path
import os
import msgpack

class sourceModel(object):

    def __init__(self, cm, language, windowSize=21, type_only=False):
        self.cm = cm
        self.lang = language
        self.windowSize = windowSize
        self.listOfUniqueTokens = {}
        self.uTokenFile = self.cm.writeCorpus + ".uniqueTokens"
        readTokenFile = self.cm.readCorpus + ".uniqueTokens"
        if os.path.isfile(readTokenFile):
          with open(readTokenFile, "rb") as f:
            try:
                uts = msgpack.unpackb(f.read(), encoding='utf-8')
                for (string, ((t, v, s, e, r), count)) in uts.items():
                    if type_only:
                        assert string == t
                    else:
                        assert string == r
                    self.listOfUniqueTokens[string] = (
                        Lexeme((t, v, Position(s), Position(e), r)),
                        count)
            except:
                raise IOError("%s is corrupt!" % (readTokenFile))
        self.type_only = type_only

    def trainFile(self, files):
        """Blindly train on a set of files whether or not it compiles..."""
        files = [files] if isinstance(files, str) else files
        assert isinstance(files, list)
        for fi in files:
            sourceCode = slurp(fi)
            self.trainString(sourceCode)

    def stringifyAll(self, lexemes):
        """Clean up a list of lexemes and convert it to a list of strings"""
        if self.type_only:
            return [i[0] for i in lexemes]
        else:
            return [i[4] for i in lexemes]

    def stringify(self, l):
        """Convert it to a string"""
        if self.type_only:
            return l[0]
        else:
            return l[4]

    def corpify(self, lexemes):
        """Corpify a string"""
        return self.cm.corpify(self.stringifyAll(lexemes))

    def sourceToScrubbed(self, sourceCode):
        return self.lang(sourceCode).scrubbed()
    
    def saveTraining(self):
        with open(self.uTokenFile + ".swp", "wb") as f:
            f.write(msgpack.packb(self.listOfUniqueTokens))
        os.rename(self.uTokenFile + ".swp", self.uTokenFile)

    def trainLexemes(self, lexemes):
        """Train on a lexeme sequence."""
        for l in lexemes:
            if self.stringify(l) not in self.listOfUniqueTokens:
                self.listOfUniqueTokens[self.stringify(l)] = (l, 1)
            else:
                l, count = self.listOfUniqueTokens[self.stringify(l)]
                self.listOfUniqueTokens[self.stringify(l)] = (l, count+1)
        windowlen = self.windowSize
        padding = windowlen
        lstrings = self.stringifyAll(lexemes)
        qstrings = ((["<s>"] * (windowlen-1))
                    + lstrings 
                    + (["</s>"] * (windowlen-1))
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
        windowlen = self.windowSize
        padding = windowlen-1
        content_len = len(lexemes)
        # first and last window are half padding
        content_start = padding
        content_end = padding + content_len
        useful_windows_start = padding//2
        useful_windows_end = padding//2 + content_len
        start_pos = lexemes[0].start
        end_pos = lexemes[-1].end
        qtokens = (([Lexeme(("<s>", "", start_pos, start_pos, "<s>"))]
                      * padding)
                    + lexemes
                    + ([Lexeme(("</s>", "", end_pos, end_pos, "</s>"))]
                       * padding)
                   )
        total_len = len(qtokens)
        window_entropies = []
        windows = []
        unwindow_entropies = [0] * (windowlen-1)
        for token_i in range(0, total_len-windowlen+1):
            qstart = token_i
            qend = token_i+windowlen
            query = self.stringifyAll(qtokens[qstart:qend])
            #DEBUG(query)
            windows.append(qtokens[qstart:qend])
            assert len(query) == self.windowSize
            entropy = self.cm.queryCorpus(query)
            #DEBUG(entropy)
            #DEBUG(" ".join(query))
            window_entropies.append(entropy)
            unwindow_entropies.append(0)
            for token_j in range(qstart, qend):
                additional_entropy = window_entropies[token_i]/(windowlen)
                unwindow_entropies[token_j] += additional_entropy
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
        assert len(windows) == content_len + (windowlen - 1)
        assert len(unwindow_entropies) == total_len
        windows = list(zip(windows, window_entropies))
        windows = windows[useful_windows_start:useful_windows_end]
        unwindows = list(zip(qtokens, unwindow_entropies))
        unwindows = unwindows[padding:(padding+content_len)]
        assert unwindows[0][0] == lexemes[0]
        assert windows[0][0][windowlen//2] == lexemes[0], repr(windows[0][0])
        return (windows, unwindows)
        #return (sorted(windows, key=itemgetter(1), reverse=True),
                #sorted(unwindows, key=itemgetter(1), reverse=True))
      
    def isValid(self, lexemes):
        (filename, line, func, text, exceptionName) = lexemes.check_syntax()
        if exceptionName is None:
            return True
        else:
            return False
    
    def tryDelete(self, window, i, real_i):
        window, originalEntropy = window
        query = self.stringifyAll(window[:i] + window[i+1:])
        #DEBUG(" ".join(query))
        assert len(query) == self.windowSize-1
        newEntropy = self.cm.queryCorpus(query)
        #DEBUG("    Delete %i (%i) %f %f" % (real_i, i, originalEntropy, newEntropy))
        if newEntropy < originalEntropy:
            return [
                (
                    Change('delete',
                           real_i,
                           real_i+1,
                           real_i,
                           real_i,
                           [window[i]],
                           []),
                    originalEntropy - newEntropy
                    )
                ]
        else:
            return []
    
    def tryInsert(self, window, i, real_i, what):
        window, originalEntropy = window
        query = self.stringifyAll(window[:i] + [what] + window[i:])
        assert len(query) == self.windowSize+1
        newEntropy = self.cm.queryCorpus(query)
        if newEntropy < originalEntropy:
            #DEBUG("    Insert %i (%s) %f %f" % (real_i, what[4], originalEntropy, newEntropy))
            return [
                (
                    Change('insert',
                           real_i,
                           real_i,
                           real_i,
                           real_i+1,
                           [],
                           [what]),
                    originalEntropy - newEntropy
                    )
                ]
        else:
            return []

    def tryReplace(self, window, i, real_i, what):
        window, originalEntropy = window
        query = self.stringifyAll(window[:i] + [what] + window[i+1:])
        assert len(query) == self.windowSize
        newEntropy = self.cm.queryCorpus(query)
        if newEntropy < originalEntropy:
            return [
                (
                    Change('replace',
                           real_i,
                           real_i+1,
                           real_i,
                           real_i+1,
                           [window[i]],
                           [what]),
                    originalEntropy - newEntropy
                    )
                ]
        else:
            return []

    def fix(self, lexemes):
        lexemes = lexemes.lexemes
        MAX_POSITIONS = 5
        windows, unwindows = self.unwindowedQuery(lexemes)
        keys = list(range(0, len(windows)))
        keys = sorted(keys, key=lambda i: unwindows[i][1], reverse=True)
        # keys is now a list of indices into windows/unwindows
        # sorted with unwindow of highest entropy first
        centre = self.windowSize//2
        suggestions = []
        for i in range(0, min(len(keys), MAX_POSITIONS)):
            windowi = keys[i]
            DEBUG("Position: %i" % (windowi))
            assert windows[i][0][centre] == unwindows[i][0]
            suggestions += self.tryDelete(windows[windowi], centre, windowi)
            for string, (token, count) in self.listOfUniqueTokens.items():
                if count < 10:
                    continue
                suggestions += self.tryInsert(windows[windowi], centre, windowi, token)
                suggestions += self.tryReplace(windows[windowi], centre, windowi, token)
            DEBUG("Suggestions: %i" % (len(suggestions)))
        suggestions = sorted(suggestions, key=lambda s: s[1], reverse=True)
        return [suggestion[0] for suggestion in suggestions]
    
    def release(self):
        self.cm.release()

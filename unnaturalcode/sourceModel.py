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


class sourceModel(object):

    def __init__(self, cm=mitlmCorpus(), language=pythonSource, windowSize=20):
        self.cm = cm
        self.lang = language
        self.windowSize = windowSize

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
            window_entropies.append(self.cm.queryCorpus(query))
            if token_i >= content_start and token_i < content_end:
                """
                This part is magical. It comes from building an array with a moving
                band of 1s representing the window and then inverting it.
                It could be made non-quadratic if necessary by saving earlier sums
                and reusing them.
                """
                unwindow_entropies.append(
                    sum([window_entropies[i] for i in xrange(token_i,-1,-windowlen)])
                    - sum([window_entropies[i] for i in xrange(token_i-1,-1,-windowlen)])
                )
            else:
                unwindow_entropies.append(0) # don't consider padding tokens
        windows = zip(windows, window_entropies)
        windows = windows[content_start:content_end]
        unwindows = zip(qtokens, unwindow_entropies)
        unwindows = unwindows[content_start:content_end]
        return (sorted(windows, key=itemgetter(1), reverse=True),
                sorted(unwindows, key=itemgetter(1), reverse=True))

    def release(self):
        self.cm.release()

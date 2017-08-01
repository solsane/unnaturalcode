#!/usr/bin/python
#    Copyright 2017 Dhvani Patel
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

# Takes in a string of Java code and checks for errors
# NOTE: FOR ECLIPSE

import os
import subprocess
import sys
import tempfile
from compile_error import CompileError

# Method for finding index of certain characters in a string, n being the n'th occurence of the character/string
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

# Main method
def checkEclipseSyntax(src):
		with open(src) as f:
      		  for i, l in enumerate(f):
            		pass
  		numTotLines = i + 1

		with open (src, "r") as myfile:
   			data = myfile.read()
		#print data
		myFile = open("ToCheckEc.java", "w")
		myFile.write(data)
		myFile.close()
		proc = subprocess.Popen(['java', '-jar', '../Downloads/ecj-4.7.jar', 'ToCheckEc.java', '-nowarn'], stderr=subprocess.PIPE)
		streamdata, err = proc.communicate()
		rc = proc.returncode
		if rc == 0:
			# No errors, all good
			os.remove("ToCheckEc.java")
			return None
		else:
			# Error, disect data for constructor		
			#print err
			err = err[:len(err)-1]
			#print err

			lastLine = err.rfind("\n")
			#print lastLine
			#print "split"
			#print len(err)
			lastErrorNum = err[lastLine:]
			cutOff = find_nth(lastErrorNum, '(', 1)
			lastError = lastErrorNum[cutOff+1:lastErrorNum.index('error')-1]
			numError = int(lastError)
			
			
			lineNums = []
			insToks = []
			indRepeats = []
			typeErrors = []
			for ind in range(numError):
				#print numError
				fileInd = find_nth(err, "(at line ", ind+1)
				temp = err[fileInd:]
				#print "OK"
				#print temp
				before = len(insToks)
				#print before
				synErrInd = find_nth(temp, "Syntax error", 1)
				flagInd = find_nth(temp, "----------", 1)
				if synErrInd != -1 and synErrInd < flagInd:
					actLine = temp[synErrInd:]
					tokInsInd = find_nth(actLine, ", insert", 1)
					#print tokInsInd
					#print "dhvani"
					if tokInsInd != -1 and tokInsInd < flagInd:
						cut = find_nth(actLine, "\" ", 1)
						typeErrors.append('i')
						toksIns = actLine[tokInsInd+10:cut]
						#print toksIns
						insToks.append(toksIns)
				stringInd = find_nth(temp, "String literal is not properly closed by a double-quote", 1)
				if stringInd != -1 and stringInd < flagInd:
					typeErrors.append('i')
					toksIns = "\""
					insToks.append(toksIns)
				subErrInd = find_nth(temp, "Syntax error on token", 1)
				if subErrInd != -1 and subErrInd < flagInd:
					cutLine = temp[subErrInd:]
					fixTok = find_nth(cutLine, "expected after this token", 1)
					if fixTok != -1 and fixTok < flagInd:
						cutInd = find_nth(cutLine,"\", ", 1)
						toksSub = cutLine[cutInd+3:fixTok-1] 
						typeErrors.append('i')
						insToks.append(toksSub)
					if fixTok == -1:
						fixTokCheck = find_nth(cutLine, "expected before this token", 1)
						if fixTokCheck != -1 and fixTokCheck < flagInd:
							cutInd = find_nth(cutLine,"\", ", 1)
							toksSub = cutLine[cutInd+3:fixTokCheck-1] 
							typeErrors.append('i')
							insToks.append(toksSub)			
						if fixTokCheck == -1:
							checkSub = find_nth(cutLine, "expected", 1)
							if checkSub != -1 and checkSub < flagInd:
								cutInd = find_nth(cutLine,"\", ", 1)
								toksSub = cutLine[cutInd+3:checkSub-1] 
								typeErrors.append('s')
								insToks.append(toksSub)	
					delInd = find_nth(cutLine, ", delete this token", 1)	
					if delInd != -1 and delInd < flagInd:
						delTok = temp[subErrInd+23:subErrInd+delInd-1]
						typeErrors.append('d')
						insToks.append(delTok)
				checkAsserInd = temp.find("must be defined in its own file")	
				#print checkAsserInd
				#print flagInd
				if checkAsserInd == -1 or checkAsserInd > flagInd:
					#print "HERE-------------------------------------------------------------"
					if len(insToks) != before+1:
						typeErrors.append('')
						insToks.append('')	
				cutColInd = find_nth(temp, ")", 1)
				line = err[fileInd+9:cutColInd+fileInd]
				lineNums.append(int(line))
			#print insToks
			#print lineNums
			#print "----OUT----"
			checkInd = err.find("must be defined in its own file")
			#print msgNo
			#print lineNums
			if checkInd != -1:
				check = err[:checkInd]
				lastCheck = check.rfind("(at line ")
				tempR = err[lastCheck:]
				cutColInd = find_nth(tempR, ")", 1)
				lineRemov = err[lastCheck+9:cutColInd+lastCheck]
				rid = int(lineRemov)
				goOver = lineNums[:]	
				flag = False		
				for x in goOver:
					if x == rid and flag == False:
						lineNums.remove(rid)
						flag = True

			checkIndAgain = find_nth(err, 'must be defined in its own file', 2)
			count = 2
			while checkIndAgain != -1:
				check = err[:checkIndAgain]
				lastCheck = check.rfind("(at line ")
				tempR = err[lastCheck:]
				cutColInd = find_nth(tempR, ")", 1)
				lineRemov = err[lastCheck+9:cutColInd+lastCheck]
				rid = int(lineRemov)
				goOver = lineNums[:]	
				flag = False		
				for x in goOver:
					if x == rid and flag == False:
						lineNums.remove(rid)
						flag = True
				count += 1
				checkIndAgain = find_nth(err, 'must be defined in its own file', count)

			msgNo = []
			for x in range(len(lineNums)):
				msgNo.append(x+1)

			#print msgNo
			#print lineNums

			if len(msgNo) == 0 and len(lineNums) == 0:
				os.remove("ToCheckEc.java")
				return None
			else:
				#errorObj = CompileError(fileName, line, column, None, text, errorname)
				#print err
				#print msgNo
				#print lineNums
				#print typeErrors
				#print insToks
				#print len(msgNo)
				#print len(lineNums)
				#print len(insToks)
				#print len(typeErrors)	
				os.remove("ToCheckEc.java")
				return numTotLines, msgNo, lineNums, insToks, typeErrors	

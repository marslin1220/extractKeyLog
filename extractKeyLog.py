import re
import os
import getopt
import sys

__author__ = 'Mars'
__doc__ = '''Usage:
    \tpython extractKeyLog.py -h
    \tpython extractKeyLog.py --error-folder=<error-log-folder> [--normal-folder=<normal-log-folder>]

    \t-h, --help
    \t\tPrint this help document.

    \t--error-folder=<error-log-folder>
    \t\tAssign the folder which includes the error log(s).

    \t--normal-folder=<normal-log-folder>
    \t\tAssign the folder which includes the normal log(s).
'''


class KeyLogExtractor:
    def listAllFiles(self, targetFolder):
	fileList = []

	for r,d,f in os.walk(targetFolder):
	    for files in f:
		fileList.append(os.path.join(r,files))

	return fileList


    def extractLogFromFile(self, logName):
	logFile = open(logName,'r')
	keyLog = [];

	while 1:
	    line = logFile.readline().strip()
	    # Remove Process ID
	    line = re.sub(r"\([^)]*\)", "", line)

	    # Only extrace warning(W/) and error (E/)
	    if (len(line) != 0 and (line.startswith("W/") or line.startswith("E/"))):
		if line not in keyLog:
		    keyLog.append(line)
	    
	    if not line: # i.e. line == EOF
		break

        logFile.close()

	return keyLog


    def integrateLogUnderFolder(self, folderName, integraterOpt):
	fileKeyLogMap = {}
	logFileList = self.listAllFiles(folderName)

	integratedKeyLog = []
        ignoreNumber = True;
	for logName in logFileList:
            logInFile = self.extractLogFromFile(logName)

            # Remove the duplicated log
            logInFileTemp = [];
            for var in logInFile[:]:
                varTemp = re.sub(r"[0-9]", "", var) if ignoreNumber else var # Only work in v2.5 above

                if varTemp in logInFileTemp:
                    logInFile.remove(var)
                else:
                    logInFileTemp.append(varTemp)

	    if len(integratedKeyLog) == 0:
		integratedKeyLog = logInFile
		continue

	    if integraterOpt == '&': # intersection
                integratedTemp = []

                for integratedLog in integratedKeyLog:
                    for log in logInFile:
                        if re.sub(r"[0-9]", "", integratedLog) == re.sub(r"[0-9]", "", log):
                            integratedTemp.append(integratedLog);
                            break
                integratedKeyLog = integratedTemp
                del integratedTemp

                integratedTemp = []
                for var in integratedKeyLog:
                    varTemp = re.sub(r"[0-9]", "", var) if ignoreNumber else var

                    if varTemp in integratedTemp:
                        integratedKeyLog.remove(var)
                    else:
                        integratedTemp.append(varTemp)

                del integratedTemp

	    elif integraterOpt == '|': # union
                for log in logInFile:
                    for integratedLog in integratedKeyLog:
                        if re.sub(r"[0-9]", "", integratedLog) == re.sub(r"[0-9]", "", log):
                            logInFile.remove(log)
                            break

		integratedKeyLog = integratedKeyLog + logInFile
            '''
	    elif integraterOpt == '-': # difference
		integratedKeyLog = [var for var in integratedKeyLog if var not in logInFile]
	    elif integraterOpt == '^': # symmetric difference
		integratedKeyLog = integratedKeyLog ^ fileKeyLogMap[logName]
            '''

	return integratedKeyLog


def main(argv):
    errorLogIntersection = []
    normalLogUnion = []
    extractor = KeyLogExtractor()

    try:
	opts, args = getopt.getopt(argv, "h", ["help", "error-folder=", "normal-folder="])
    except getopt.GetoptError, err:
	print str(err)
	print __doc__
	sys.exit(2)

    if len(opts) == 0:
	print __doc__
        sys.exit(1)

    for opt, arg in opts:
	if opt in ("-h", "--help"):
	    print __doc__
	    sys.exit(2)
	elif opt == "--error-folder":
	    errorLogIntersection = extractor.integrateLogUnderFolder(arg, '&');
	elif opt == "--normal-folder":
	    normalLogUnion = extractor.integrateLogUnderFolder(arg, '|');
	else:
	    print >> sys.stderr, "unhandled option %s" % (opt,)

    keyLog = [var for var in errorLogIntersection if var not in normalLogUnion]

    for var in keyLog:
        print var

    print "extractLogFromFile done!"

if __name__ == "__main__":
    main(sys.argv[1:]) # skip the name of this python script

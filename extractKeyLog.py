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

	    # Remove all the number
	    line = re.sub(r"[0-9]", "", line)

	    # Only extrace warning(W/) and error (E/)
	    if (len(line) != 0
		    and (line.startswith("W/") or line.startswith("E/"))):

		if line not in keyLog:
		    keyLog.append(line)
	    
	    if not line: # i.e. line == EOF
		break

	return keyLog


    def integrateLogUnderFolder(self, folderName, integraterOpt):
	fileKeyLogMap = {}
	logFileList = self.listAllFiles(folderName)

	for logName in logFileList:
	    fileKeyLogMap[logName] = self.extractLogFromFile(logName)

	integratedKeyLog = []
	for logName in fileKeyLogMap.keys():
	    if len(integratedKeyLog) == 0:
		integratedKeyLog = fileKeyLogMap[logName]
		continue

            fileKeyLogMapWithLogName = fileKeyLogMap[logName]
	    if integraterOpt == '&': # intersection
		integratedKeyLog =  [val for val in integratedKeyLog if val in fileKeyLogMapWithLogName]
	    elif integraterOpt == '|': # union
                fileKeyLogMapDiff = [] + fileKeyLogMapWithLogName
                for var in set(integratedKeyLog) & set(fileKeyLogMapWithLogName):
                    if var in fileKeyLogMapWithLogName:
                        fileKeyLogMapDiff.remove(var)

		integratedKeyLog = integratedKeyLog + fileKeyLogMapDiff
	    elif integraterOpt == '-': # difference
		integratedKeyLog = [var for var in integratedKeyLog if var not in fileKeyLogMapWithLogName]
            '''
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

    for line in keyLog:
	print line

    print "extractLogFromFile done!"

if __name__ == "__main__":
    main(sys.argv[1:]) # skip the name of this python script

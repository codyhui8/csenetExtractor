import csv
import os
import exportVariables
import re

# Return fileName given the Function code
def getFunctionCodeFileName(functionCode):
    dirName = os.path.dirname(__file__)
    return os.path.join(dirName, 'CSENetTableExtractions/', functionCode + '.csv')

# Remove stringValue of all non-ascii characters and returns the lowercase version 
def cleanStringPeriodDashLower(stringValue):
    return re.compile('[\W_]+').sub('', stringValue.lower().replace(" ", ""))

def returnDataBlockID(currentDataBlock, dataBlockFields):
    if currentDataBlock not in dataBlockFields:
        return len(exportVariables.dataBlocksFieldExtractions) + 1
    if dataBlockFields[currentDataBlock] is not None:
        return dataBlockFields[currentDataBlock]
    return None

def returnStartEnd(startEndValue):
    tempValue = startEndValue.split('-')
    if len(tempValue) == 1:
        return [tempValue[0], tempValue[0]]
    # print([tempValue[0], tempValue[1].lstrip("\n")])
    return [tempValue[0], tempValue[1].lstrip("\n")]

def returnAlphaNumeric(value):
    if value.strip("[]") == 'A/N':
        return 'A'
    elif value == 'A' or value == 'N':
        return value
    else:
        return None

def returnRequired(commentString):
    if commentString.startswith('Required'):
        return True
    else:
        return False

def returnOpenFileLocation(fileName):
    dirName = os.path.dirname(__file__)
    return os.path.join(dirName, 'CSENetTableExtractions/', fileName + '.csv')

def removeAsterisk(value):
    if value[0] == '*':
        return value[1:].rstrip(' (2)')
    else:
        return value.rstrip(' (2)')

def isFarCode(firstThreeWords):
        if len(firstThreeWords[0]) > 4 or len(firstThreeWords[0]) < 3:
            return False
        elif len(firstThreeWords[1]) != 1:
            return False
        elif len(firstThreeWords[2]) > 8:
            return False
        return True

def isUpper(words):
    for i in words:
        if not i[:2].isupper():
            return False
    return True
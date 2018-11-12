import csv
import os
import exportVariables
import xlsxwriter

class mainExtractor(object):

    def __init__(self):
        self.fileName = input("Filename of the data that you want to extract:  ")
        # self.saveLocation = input("Save location of file: ")
        dirName = os.path.dirname(__file__)
        self.saveLocation = os.path.join(dirName, 'generatedFiles/', self.fileName + '.csv')
        if self.fileName == 'ALL':
            self.saveLocationFARCode = os.path.join(dirName, 'generatedFiles/', 'ALL_FAR_CODE.csv')
        else:
            self.saveLocationFARCode = os.path.join(dirName, 'generatedFiles/', self.fileName + '_FAR_CODE.csv')

    # Main class to extract data for CSENet CSV files
    def extractData(self):
        if self.fileName == 'ALL':
            self.extractAllFARCode()
        else:
            dirName = os.path.dirname(__file__)
            fileName = os.path.join(dirName, 'CSENetTableExtractions/', self.fileName + '.csv')
            # print(fileName)
            FARCodes = self.extractCSV(fileName)
            self.exportDataBlocks(FARCodes)
            self.exportFARCode(FARCodes, None, 1)

    # Start reader and extract the FAR codes with relevant Data Block information
    def extractCSV(self, fileName):
        with open(fileName, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            extractedFAR = self.extractBlocks(csv_reader)

        return extractedFAR

    # Extract the FAR codes with the relevant Data Blocks that exists/required for each FAR Code
    def extractBlocks(self, extractedFile):
        codes = []
        lineNumber = 0
        for rows in extractedFile:
            if len(rows) > 0:
                if rows[0][4:8] == 'R, U':
                    firstFourWords = rows[0].split()[:4]
                    firstFarCode = [firstFourWords[0], firstFourWords[1][:1], firstFourWords[3]]
                    secondFarCode = [firstFourWords[0], firstFourWords[2], firstFourWords[3]]
                    # print(firstFarCode)
                    # print(secondFarCode)
                    # print(codes)
                    codes = self.extractFromFirstThreeWords(firstFarCode, lineNumber, codes, rows)
                    codes = self.extractFromFirstThreeWords(secondFarCode, lineNumber, codes, rows)
                    # print(codes)
                else:
                    firstThreeWords = rows[0].split()[:3]
                    codes = self.extractFromFirstThreeWords(firstThreeWords, lineNumber, codes, rows)

            lineNumber += 1

        return codes

    # Extract from first three words either a FAR code or a Data Block for the FAR code
    def extractFromFirstThreeWords(self, firstThreeWords, lineNumber, codes, rows):
        # The following IF/ELIF statement will check to see if the FAR code already exists in the 'codes' array.
        # If it does not exist, then it inputs the FAR code and then the 'Header' block, since all FAR codes will have a Header Block
        if (len(firstThreeWords) > 1 and self.isUpper(firstThreeWords)):
            if ((len(firstThreeWords[0]) == 3 and len(firstThreeWords[1]) == 1 and len(firstThreeWords[2]) == 5)):
                FARCode = ' '.join(firstThreeWords)
                if (FARCode not in [i[0] for i in codes]):
                    codes.append([FARCode, lineNumber, ['HEADER']])
            elif ((len(firstThreeWords[0]) == 4 and len(firstThreeWords[1]) == 1 and len(firstThreeWords[2]) == 5)):
                FARCode = firstThreeWords[0][1:] + ' ' + ' '.join(firstThreeWords[1:])
                if (FARCode not in [i[0] for i in codes]):
                    codes.append([FARCode, lineNumber, ['HEADER']])
        elif (len(firstThreeWords) > 2 and firstThreeWords[2] == 'âˆ’'):
            if (
                    (len(firstThreeWords[0]) == 3 and len(firstThreeWords[1]) == 1)):
                FARCode = ' '.join(firstThreeWords[:2])
                if (FARCode not in [i[0] for i in codes]):
                    codes.append([FARCode, lineNumber, ['HEADER']])
            elif (
                    (len(firstThreeWords[0]) == 4 and len(firstThreeWords[1]) == 1)):
                FARCode = firstThreeWords[0][1:] + ' ' + ' '.join(firstThreeWords[1])
                if (FARCode not in [i[0] for i in codes]):
                    codes.append([FARCode, lineNumber, ['HEADER']])

        # Store FAR code data block if it is not linked to the FAR code yet.
        if (rows[0][1:].isupper() and
                (rows[0][1:] in exportVariables.dataBlocks or rows[0] in exportVariables.dataBlocks)):
            codes[len(codes) - 1][2].append(rows[0])
        elif (len(rows) > 1):
            if (rows[1][1:].isupper() and
                    (rows[1][1:] in exportVariables.dataBlocks or rows[1] in exportVariables.dataBlocks)):
                if (len(codes) == 0):
                    codes[len(codes)][2].append(rows[1])
                else:
                    codes[len(codes) - 1][2].append(rows[1])
        return codes

    def isUpper(self, words):
        for i in words:
            if not i[:2].isupper():
                return False
        return True

    def exportDataBlocks(self, csenetTransactions):
        with open(self.saveLocation, mode='w') as transactionsTypes:
            transactionsCSV = csv.writer(transactionsTypes, delimiter=',', quotechar='"', lineterminator='\n')
            header = ['FAR Code']
            for blocks in exportVariables.dataBlocks:
                header.append(blocks)
            transactionsCSV.writerow(header)

            for farCodes in csenetTransactions:
                farType = [farCodes[0]]
                for blocks in exportVariables.dataBlocks:
                    if blocks in farCodes[2] or blocks in [i[1:] for i in farCodes[2]]:
                        farType.append('1')
                    else:
                        farType.append('')
                transactionsCSV.writerow(farType)

    def exportFARCode(self, csenetTransactions, transactionsCSV, currentCount):
        if self.fileName == 'ALL':
            self.writeFARCode(transactionsCSV, currentCount, csenetTransactions)
        else:
            with open(self.saveLocationFARCode, mode='w') as transactionsTypes:
                transactionsCSV = csv.writer(transactionsTypes, delimiter=',', quotechar='"', lineterminator='\n')
                header = ['FAR_CODE_CD', 'ACTION_CD', 'FUNCTION_CD', 'ACTION_REASON_CD', 'FAR_CODE_ID', 'FAR_CODE_DESCRIPTION_TXT']
                transactionsCSV.writerow(header)
                self.writeFARCode(transactionsCSV, currentCount, csenetTransactions)

    # Write the FAR Codes to the column with an input of the Starting ID and the available transactions.
    def writeFARCode(self, transactionsCSV, currentCount, csenetTransactions):
        for count, farCodes in enumerate(csenetTransactions):
            farType = [farCodes[0].replace(" ", "")]
            functionCode = farType[0][:3]
            actionCode = farType[0][3:4]
            actionReasonCode = farType[0][4:]

            farType.append(actionCode)
            farType.append(functionCode)
            if actionReasonCode is not '':
                farType.append(actionReasonCode)
            else:
                farType.append('BLANK')
            farType.append(count + currentCount)
            farType.append('')

            transactionsCSV.writerow(farType)

    # Write CSV defintion of values for a PostgreSQL import on the table of FAR_CODES
    def extractAllFARCode(self):
        dirName = os.path.dirname(__file__)
        with open(self.saveLocationFARCode, mode='w') as transactionsTypes:
            transactionsCSV = csv.writer(transactionsTypes, delimiter=',', quotechar='"', lineterminator='\n')
            header = ['FAR_CODE_CD', 'ACTION_CD', 'FUNCTION_CD', 'ACTION_REASON_CD', 'FAR_CODE_ID',
                      'FAR_CODE_DESCRIPTION_TXT']
            transactionsCSV.writerow(header)
            transactionsTypes.close()
        currentLocation = 1
        for functionType in exportVariables.allFunctionCodes:
            with open(self.saveLocationFARCode, mode='a') as transactionsTypes:
                transactionsCSV = csv.writer(transactionsTypes, delimiter=',', quotechar='"', lineterminator='\n')
                print(functionType)
                currentFileName = os.path.join(dirName, 'CSENetTableExtractions/', functionType + '.csv')
                FARCodes = self.extractCSV(currentFileName)
                self.exportFARCode(FARCodes, transactionsCSV, currentLocation)
                currentLocation += len(FARCodes)
                transactionsTypes.close()

extractor = mainExtractor()
extractor.extractData()
import csv
import os
import exportVariables
import re
import helperFunctions as helper


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
            # print(FARCodes)
            self.exportDataBlocks(FARCodes)
            self.exportFARCode(FARCodes, None, 1)

    # Start reader and extract the FAR codes with relevant Data Block information
    def extractCSV(self, fileName):
        with open(fileName, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')
            extractedFAR = self.extractBlocks(csv_reader)

        return extractedFAR

    # Extract the FAR codes with the relevant Data Blocks that exists/required for each FAR Code
    def extractBlocks(self, extractedFile):
        codes = []
        lineNumber = 0
        isDescriptionLine = True
        for rows in extractedFile:
            # print(rows)
            if len(rows) > 0:
                if rows[0][4:8] == 'R, U':
                    firstFourWords = rows[0].split()[:4]
                    firstFarCode = [firstFourWords[0], firstFourWords[1][:1], firstFourWords[3]]
                    secondFarCode = [firstFourWords[0], firstFourWords[2], firstFourWords[3]]

                    firstFarCode = ''.join(firstFarCode)
                    description = rows[1].lstrip(' âˆ’').replace("\n", "")
                    codes.append([firstFarCode, lineNumber, ['HEADER'], description])

                    secondFarCode = ''.join(secondFarCode)
                    description = rows[1].lstrip(' âˆ’').replace("\n", "")
                    codes.append([secondFarCode, lineNumber, ['HEADER'], description])

                elif len(rows[0]) == 11 and re.search(r'\w[A-Z]{2,3}\b\s\w{1,1}\b\s\w{5,5}\b', rows[0]):
                    firstThreeWords = rows[0].split()[:3]
                    farCode = ''.join(firstThreeWords)
                    if (farCode not in [i[0] for i in codes]):
                        description = rows[1].lstrip(' âˆ’').replace("\n", "")
                        codes.append([farCode, lineNumber, ['HEADER'], description])


                elif re.search(r'\w[A-Z]{2,3}\b\s\w{1,1}\b\s\w{5,5}\b', rows[0]) and isDescriptionLine:
                    # print(rows[0])
                    firstThreeWords = rows[0].split()[:3]
                    tempExtractWords = self.extractFromFirstThreeWords(firstThreeWords, lineNumber, codes, rows,
                                                                       isDescriptionLine)
                    codes = tempExtractWords[0]
                    codes[len(codes) - 1][3] = (rows[1].replace("\n", ""))
                    # print(codes)
                    isDescriptionLine = tempExtractWords[1]

                else:
                    firstThreeWords = rows[1].split()[:3]
                    # print(firstThreeWords)
                    tempExtractWords = self.extractFromFirstThreeWords(firstThreeWords, lineNumber, codes, rows,
                                                                       isDescriptionLine)
                    codes = tempExtractWords[0]
                    isDescriptionLine = tempExtractWords[1]

            lineNumber += 1

        return codes

    # Extract from first three words either a FAR code or a Data Block for the FAR code
    def extractFromFirstThreeWords(self, firstThreeWords, lineNumber, codes, rows, isDescriptionLine):
        # The following IF/ELIF statement will check to see if the FAR code already exists in the 'codes' array.
        # If it does not exist, then it inputs the FAR code and then the 'Header' block, since all FAR codes will have a Header Block
        # print(rows)
        if (len(firstThreeWords) > 1 and helper.isUpper(firstThreeWords) and helper.isFarCode(firstThreeWords)):
            if ((len(firstThreeWords[0]) == 3 and len(firstThreeWords[1]) == 1 and len(firstThreeWords[2]) == 5)):
                FARCode = ' '.join(firstThreeWords)
                if FARCode not in (temp[0] for temp in codes):
                    # print("Append the Header")
                    self.appendHeader(codes, FARCode, lineNumber, rows)
                    isDescriptionLine = True

            elif ((len(firstThreeWords[0]) == 4 and len(firstThreeWords[1]) == 1 and len(firstThreeWords[2]) == 5)):
                FARCode = firstThreeWords[0][1:] + ' ' + ' '.join(firstThreeWords[1:])
                if FARCode not in (temp[0] for temp in codes):
                    # print("Append the Header")
                    self.appendHeader(codes, FARCode, lineNumber, rows)
                    isDescriptionLine = True
        # # This will run if we have a file with a UTF-8 value of 'âˆ’'. Otherwise, this can be commented out
        # elif (len(firstThreeWords) > 2 and 'âˆ’' in firstThreeWords[2] and helper.isFarCode(firstThreeWords)):
        #     if ((len(firstThreeWords[0]) == 3 and len(firstThreeWords[1]) == 1)):
        #         FARCode = ' '.join([firstThreeWords[0], firstThreeWords[1], firstThreeWords[2][:4]])
        #         if FARCode not in (temp[0] for temp in codes):
        #             self.appendHeader(codes, FARCode, lineNumber, rows)
        #             isDescriptionLine = True
        #
        #     elif (
        #             (len(firstThreeWords[0]) == 4 and len(firstThreeWords[1]) == 1)):
        #         FARCode = firstThreeWords[0][1:] + ' ' + ' '.join(firstThreeWords[1])
        #         if FARCode not in (temp[0] for temp in codes):
        #             self.appendHeader(codes, FARCode, lineNumber, rows)
        #             isDescriptionLine = True

        # Append additional lines to the Description text
        elif isDescriptionLine and not rows[1].startswith('Description'):
            # print(codes[len(codes) - 1][3])
            # print(rows[1])
            # print(codes)
            description = codes[len(codes) - 1][3] + rows[0] + " " + rows[1]
            # print(description)
            codes[len(codes) - 1][3] = description
            # print(codes)
        else:
            isDescriptionLine = False

        # Store FAR code data block if it is not linked to the FAR code yet.
        if (rows[0][1:].isupper() and
                (rows[0][1:] in exportVariables.dataBlocks or rows[0] in exportVariables.dataBlocks)):
            codes[len(codes) - 1][2].append(helper.removeAsterisk(rows[0]))
            # print(codes)
        elif (len(rows) > 1):
            if (rows[1][1:].isupper() and
                    (rows[1][1:] in exportVariables.dataBlocks or rows[1] in exportVariables.dataBlocks)):
                if (len(codes) == 0):
                    codes[len(codes)][2].append(helper.removeAsterisk(rows[1]))
                else:
                    codes[len(codes) - 1][2].append(helper.removeAsterisk(rows[1]))

        # print(isDescriptionLine)
        return [codes, isDescriptionLine]

    def appendHeader(self, codes, FARCode, lineNumber, rows):
        if (FARCode not in [i[0] for i in codes]):
            # print(rows)
            if rows[1][0] == '[':
                description = rows[1][12:].lstrip(' ')
            else:
                description = rows[1][11:].lstrip(' ')
            # print(description)
            codes.append([FARCode, lineNumber, ['HEADER'], description])
            # print(codes)

        return codes

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
                header = ['FAR_CODE_CD', 'ACTION_CD', 'FUNCTION_CD', 'ACTION_REASON_CD', 'FAR_CODE_ID',
                          'FAR_CODE_DESCRIPTION_TXT']
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
            farType.append(farCodes[3].replace("âˆ’", "").lstrip(" "))
            # print(farCodes[3])

            transactionsCSV.writerow(farType)

    # # Get the description of the FAR Codes
    # # Input: String in the format of 'AAA A AAAAA'. Whitespaces are important here
    # def getFARDescription(self, farCode):
    #     return None

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
                # print(functionType)
                currentFileName = os.path.join(dirName, 'CSENetTableExtractions/', functionType + '.csv')
                FARCodes = self.extractCSV(currentFileName)
                self.exportFARCode(FARCodes, transactionsCSV, currentLocation)
                currentLocation += len(FARCodes)
                transactionsTypes.close()


extractor = mainExtractor()
extractor.extractData()

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

    # Main class to extract data for CSENet CSV files
    def extractData(self):
        dirName = os.path.dirname(__file__)
        fileName = os.path.join(dirName, 'CSENetTableExtractions/', self.fileName + '.csv')
        # print(fileName)
        FARCodes = self.extractCSV(fileName)
        self.exportDataBlocks(FARCodes)

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
                firstThreeWords = rows[0].split()[:3]
                # Extract the FAR code and Line start of the data block
                if(len(firstThreeWords) > 1 and self.isUpper(firstThreeWords)):
                    if((len(firstThreeWords[0]) == 3 and len(firstThreeWords[1]) == 1 and len(firstThreeWords[2]) == 5)):
                        FARCode = ' '.join(firstThreeWords)
                        if(FARCode not in [i[0] for i in codes]):
                            codes.append([FARCode, lineNumber, ['HEADER']])
                    elif((len(firstThreeWords[0]) == 4 and len(firstThreeWords[1]) == 1 and len(firstThreeWords[2]) == 5)):
                        FARCode = firstThreeWords[0][1:] + ' ' + ' '.join(firstThreeWords[1:])
                        if (FARCode not in [i[0] for i in codes]):
                            codes.append([FARCode, lineNumber, ['HEADER']])
                elif(len(firstThreeWords) > 2 and firstThreeWords[2] == 'âˆ’'):
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

                if(rows[0][1:].isupper() and
                        (rows[0][1:] in exportVariables.dataBlocks or rows[0] in exportVariables.dataBlocks)):
                    codes[len(codes) - 1][2].append(rows[0])
                elif(len(rows) > 1):
                    if(rows[1][1:].isupper() and
                            (rows[1][1:] in exportVariables.dataBlocks or rows[1] in exportVariables.dataBlocks)):
                        if(len(codes) == 0):
                            codes[len(codes)][2].append(rows[1])
                        else:
                            codes[len(codes) - 1][2].append(rows[1])

            lineNumber += 1
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


extractor = mainExtractor()
extractor.extractData()
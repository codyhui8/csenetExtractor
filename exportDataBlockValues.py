import csv
import os
import exportVariables
import re
import helperFunctions as helper

class exportDataBlockValues(object):
    def __init__(self):
        self.functionToRun = input("Filename of the table you want to create (DATA_BLOCK, DATA_BLOCK_FIELDS, FAR_CODE_DATA_BLOCK): ")
        if self.functionToRun not in ['DATA_BLOCK', 'DATA_BLOCK_FIELDS', 'FAR_CODE_DATA_BLOCK']:
            print("No Valid Values were entered. Please run again.")
            return
        # self.saveLocation = input("Save location of file: ")
        self.dirName = os.path.dirname(__file__)
        self.saveLocation = os.path.join(self.dirName, 'generatedFiles/', self.functionToRun + '.csv')

        # Initialize extraction
        self.extractData()

    def extractData(self):
        if self.functionToRun == 'DATA_BLOCK':
            self.saveLocation = os.path.join(self.dirName, 'generatedFiles/', self.functionToRun + '.csv')
            self.extractDataBlock()
            return None
        elif self.functionToRun == 'DATA_BLOCK_FIELDS':
            dataBlockFields = self.extractDataBlockFields(None)
            self.writeDataBlockFieldsToFile(dataBlockFields)
        elif self.functionToRun == 'FAR_CODE_DATA_BLOCK':
            farCodeDataBlockDefintion = self.extractFarCodeDataBlock()
            self.writeFarCodeDataBlock(farCodeDataBlockDefintion)
            return None

    # Create FAR_CODE_DATA_BLOCK table definition
    def extractFarCodeDataBlock(self):
        dataBlockFieldsData = self.extractDataBlockFields(os.path.join(self.dirName, 'CSENetTableExtractions/', 'DataBlockFields_EDITED'))
        # print(dataBlockFieldsData)
        allFarCode = self.extractAllFarCodeValues(os.path.join(self.dirName, 'generatedFiles/', 'ALL_FAR_CODE.csv'))
        # print(allFarCode)
        with open(self.saveLocation, mode='w', encoding="utf-8") as farCodeDataBlockFields:
            storedDataBlocks = csv.writer(farCodeDataBlockFields, delimiter=',', quotechar='"', lineterminator='\n')
            header = ['FAR_CODE_DATA_BLOCK_ID', 'DATA_BLOCK_FIELDS_ID', 'VALUE_TXT', 'FAR_CODE_ID']
            storedDataBlocks.writerow(header)
            farCodeDataBlockFields.close()
        farCodeDataBlockDefintion = []
        for farCodes, farCodeId in allFarCode.items():
            
            farCodeFileName = helper.getFunctionCodeFileName(farCodes[:3])
            farCodes = farCodes[:3] + ' ' + farCodes[3:4] + ' ' + farCodes[4:]
            farCodeDataBlockDefintion = self.extractRelevantRows(farCodeFileName, farCodes, dataBlockFieldsData, farCodeId, farCodeDataBlockDefintion)

        return farCodeDataBlockDefintion

    # Write FAR_CODE_DATA_BLOCK table definition
    def writeFarCodeDataBlock(self, farCodeDataBlockDefintion):
        with open(self.saveLocation, mode='a', encoding="utf-8") as farCodeDataBlockFields:
            storedDataBlocks = csv.writer(farCodeDataBlockFields, delimiter=',', quotechar='"', lineterminator='\n')
            count = 1
            for i in farCodeDataBlockDefintion:
                tempValue = [count]
                for p in i:
                    tempValue.append(p)
                storedDataBlocks.writerow(tempValue)
                count += 1

        print('Everything is written')

    # Processes files and gets the relevant fields and descriptions
    def extractRelevantRows(self, farCodeFileName, farCodes, dataBlockFieldsData, farCodeId, farCodeDataBlockDefintion):
        with open(farCodeFileName, mode='r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"', lineterminator='\n')
            isCurrentlyFarCode = False
            hasReachedFarCode = False

            currentDataBlock = 'Header'
            # print(farCodes)
            # print(dataBlockFieldsData)
            mappedDataBlockFields = {}
            for i in dataBlockFieldsData: 
                mappedDataBlockFields[self.hash(i)] = [i[1], i[0]]
            # print(mappedDataBlockFields)
            # print(allDataBlockFields)
            for rows in csv_reader:
                if farCodes in rows[1] and not hasReachedFarCode:
                    # print(farCodes)
                    isCurrentlyFarCode = True
                    hasReachedFarCode = True
                elif farCodes[:3] + ' ' in rows[1] and farCodes not in rows[1] and hasReachedFarCode:
                    isCurrentlyFarCode = False
                    break

                if rows[0] is not None and rows[0] != '' and hasReachedFarCode:
                    # print(helper.removeAsterisk(rows[0]))
                    if rows[0] != currentDataBlock and helper.removeAsterisk(rows[0]) in exportVariables.dataBlocks:
                        # print(helper.removeAsterisk(rows[0]))
                        currentDataBlock = helper.removeAsterisk(rows[0])
                        # print("-----" + currentDataBlock)

                if isCurrentlyFarCode:
                    if rows[0].isupper():
                        # print(rows)
                        changedCurrentDataBlock = exportVariables.dataBlocks.index(currentDataBlock.upper()) + 1
                        # print(currentDataBlock)
                        rowDetail = self.determineRowDetail(rows, mappedDataBlockFields, farCodeId, changedCurrentDataBlock)
                        if rowDetail is not None:
                            farCodeDataBlockDefintion.append(rowDetail)

            # print(tempExtract)
        return farCodeDataBlockDefintion

    def hash(self, value): 
        return helper.cleanStringPeriodDashLower(value[2]) + str(value[0])
    

    def unhash(self, value): 
        length = len(value)
        return [ value[:length - 1], value[length - 1] ]
    

    # Determines the relevant information in the Row Detail.
    # This will include the following:
    #    1. DATA_BLOCK_FIELD.DATA_BLOCK_FIELD_ID
    #    2. FAR_CODE_DATA_BLOCK.VALUE_TXT
    #    3. FAR_CODE.FAR_CODE_ID
    def determineRowDetail(self, row, mappedDataBlockFields, farCodeId, changedCurrentDataBlock):
        tempReturnDetails = []
        currentString = helper.cleanStringPeriodDashLower(row[0])
        tempMappedDataBlockFields = []
        tempTempMappedDataBlockFields = []
        for i in mappedDataBlockFields.keys():
            tempMappedDataBlockFields.append(self.unhash(i))
        for i in tempMappedDataBlockFields:
            tempTempMappedDataBlockFields.append(i[0])

        if currentString in tempTempMappedDataBlockFields:
            # if "informationtext" in currentString:
            #     print(row)
            # print(currentString)
            dataBlockFieldId = mappedDataBlockFields[currentString + str(changedCurrentDataBlock)][0]

            return [dataBlockFieldId, row[1], int(farCodeId)]
        return None


    # Extract information from the FAR_CODE table definiton
    def extractAllFarCodeValues(self, fileName):
        farCodeValues = {}
        with open(fileName, mode='r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"', lineterminator='\n')
            count = 0
            for rows in csv_reader:
                if count != 0:
                    farCodeValues[rows[0]] = rows[4]
                count += 1
        return farCodeValues

    # Create DATA_BLOCK table definition
    def extractDataBlock(self):
        with open(self.saveLocation, mode='w') as dataBlocks:
            storedDataBlocks = csv.writer(dataBlocks, delimiter=',', quotechar='"', lineterminator='\n')
            header = ["BLOCK_NAME_CD", "DATA_BLOCK_ID"]
            storedDataBlocks.writerow(header)
            countOfRow = 1
            for blockNames in exportVariables.dataBlocksFieldExtractions:
                currRow = [blockNames, countOfRow]
                storedDataBlocks.writerow(currRow)
                countOfRow += 1
        dataBlocks.close()
        print("File written" + str(self.saveLocation))

    # Create DATA_BLOCK_FIELDS table definition
    def extractDataBlockFields(self, checkFileName):
        if checkFileName == None:
            fileName = input('Name of the DataBlock table extract: ')
        else:
            fileName = checkFileName
        with open(helper.returnOpenFileLocation(fileName), mode='r', encoding="utf-8-sig") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"', lineterminator='\n')
            typesOfDataBlocks = exportVariables.dataBlocksFieldExtractions
            countDataBlock = 0
            currentDataBlock = typesOfDataBlocks[countDataBlock]

            currentDataBlockField = 1

            rowData = []
            dataBlockTableExtraction = self.returnAllDataBlockID()
            for rows in csv_reader:
                # if 'SERVER ERROR FILE' in rows[1]:
                #     break
                if 'CHART' in rows[1] and currentDataBlock not in rows[1]:
                    countDataBlock += 1
                    currentDataBlock = typesOfDataBlocks[countDataBlock]

                elif rows[0] != '':
                    rowData = self.returnDataBlockFieldsFromRow(rows, currentDataBlockField,
                                                                currentDataBlock, rowData, dataBlockTableExtraction)
                    currentDataBlockField += 1
        return rowData

    # Order or Array is as follows:
    # 'DATA_BLOCK_ID',
    # 'DATA_BLOCK_FIELDS_ID',
    # 'FIELD_NAME_CD',
    # 'LOCATION_START',
    # 'LOCATION_END',
    # 'LENGTH',
    # 'ALPHA_NUMERIC_CD',
    # 'COMMENT_TXT',
    # 'REQUIRED_CD'
    def returnDataBlockFieldsFromRow(self, rows, count, currentDataBlock, rowData, dataBlockTableExtraction):
        if "Continued" in rows[1]:
            tempString = rowData[len(rowData) - 1][2]
            tempString += rows[1]
            rowData[len(rowData) - 1][2] = tempString
            return rowData
        # 'DATA_BLOCK_ID'
        currRowData = [helper.returnDataBlockID(currentDataBlock, dataBlockTableExtraction)]

        # 'DATA_BLOCK_FIELDS_ID'
        currRowData.append(count)

        # 'FIELD_NAME_CD'
        currRowData.append(rows[1].replace("\n", ""))

        # 'LOCATION_START'
        # 'LOCATION_END'
        startEndValue = helper.returnStartEnd(rows[2])
        if len(startEndValue) == 2:
            currRowData.append(startEndValue[0])
            currRowData.append(startEndValue[1])
        else:
            currRowData.append(None)
            currRowData.append(None)

        # 'LENGTH'
        currRowData.append(rows[3])

        # 'ALPHA_NUMERIC_CD'
        currRowData.append(helper.returnAlphaNumeric(rows[4]))

        # 'COMMENT_TXT'
        if helper.returnRequired(rows[5]):
            currRowData.append(rows[5].replace("\n", "\\n").replace("Required\\n", "", 1))
        else: 
            currRowData.append(rows[5].replace("\n", "\\n"))

        # 'REQUIRED_CD'
        currRowData.append(helper.returnRequired(rows[5]))

        rowData.append(currRowData)
        # print(currRowData)
        return rowData

    def writeDataBlockFieldsToFile(self, dataBlockFields):
        with open(self.saveLocation, mode='w', encoding="utf8") as dataBlocks:
            storedBlockFields = csv.writer(dataBlocks, delimiter=',', quotechar='"', lineterminator='\n')
            header = [columnNames for columnNames in exportVariables.DATA_BLOCK_FIELDS_DEFINITION]
            storedBlockFields.writerow(header)
            for rows in dataBlockFields:
                storedBlockFields.writerow(rows)
        print('File is written. ')


    def returnAllDataBlockID(self):
        allDataBlocks = {}
        for count, values in enumerate(exportVariables.dataBlocksFieldExtractions):
            allDataBlocks[values] = count + 1
        return allDataBlocks

temp = exportDataBlockValues()
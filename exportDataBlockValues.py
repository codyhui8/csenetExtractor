import csv
import os
import exportVariables
import re

class exportDataBlockValues(object):
    def __init__(self):
        self.fileName = input("Filename of the table you want to create (DATA_BLOCK, DATA_BLOCK_FIELDS, FAR_CODE_DATA_BLOCK):  ")
        # self.saveLocation = input("Save location of file: ")
        dirName = os.path.dirname(__file__)
        self.saveLocation = os.path.join(dirName, 'generatedFiles/', self.fileName + '.csv')

        # Initialize extraction
        self.extractData()

    def extractData(self):
        if self.fileName == 'DATA_BLOCK':
            self.extractDataBlock()
            return None
        elif self.fileName == 'DATA_BLOCK_FIELDS':
            self.extractDataBlockFields()
            return None
        elif self.fileName == 'FAR_CODE_DATA_BLOCK':
            return None
        else:
            print("No Valid Values were entered. Please run again.")
            return

    def extractDataBlock(self):
        with open(self.saveLocation, mode='w') as dataBlocks:
            storedDataBlocks = csv.writer(dataBlocks, delimiter=',', quotechar='"', lineterminator='\n')
            header = ["BLOCK_NAME_CD", "DATA_BLOCK_ID"]
            storedDataBlocks.writerow(header)
            count = 1
            for blockNames in exportVariables.dataBlocks:
                currRow = [blockNames, count]
                storedDataBlocks.writerow(currRow)
                count += 1
        dataBlocks.close()

    def extractDataBlockFields(self):

        return None

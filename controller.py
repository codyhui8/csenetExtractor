import exportDataBlockValues
import mainExtractor

functionToRun = input("Choose FARCode Extraction (FAR) or Data Block Extraction (DATA):  ")
if functionToRun == 'FAR':
    extractor = mainExtractor()
    extractor.extractData()
elif functionToRun == 'DATA':
    exportDataBlockValues.exportData()
else:
    print("Choice Invalid.")

import pandas as pd
import joblib
import json

class Utility(object):
    def convertToExcel(self,filename,data,sheet):
        import xlsxwriter
        
        # convert to excel
        excel = pd.ExcelWriter(filename,engine='openpyxl')
        data.to_excel(excel,sheet_name=sheet,index=False)
        excel.save()

        print(filename + " successfully saved as Excel file!")

        #load json file
    def loadJSON(self, filename):
        with open(filename) as file:
            data = json.load(file)

        return data

    def loadPickle(self,filename):
        pkl = joblib.load(filename)
        return pkl

        # reading CSV 
    def loadCSV(self, filename,separator,encode="utf-8"):
        dataset = pd.read_csv(filename, sep=separator,encoding=encode)
        return dataset

util = Utility()
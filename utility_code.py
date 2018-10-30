import pandas as pd
import json
class Utility(object):
    def convertToExcel(self,filename,data,sheet):
        import xlsxwriter
        # convert to excel
        print (filename)
        excel = pd.ExcelWriter(filename,engine='openpyxl')
        print (excel)
        print (sheet)
        print (data)
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

util = Utility()
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

    def convertToNumeric(self,dataset):
        # convert categorical feature to numeric
        dataset['type'] = dataset['type'].map({'PERSON': 1, 'LOCATION': 2, 'ORGANIZATION': 3,'NP': 4}).astype(int)
        dataset['occ_title'] = dataset['occ_title'].map({False: 0, True: 1}).astype(int)
        return dataset
        
        #load json file
    def loadJSON(self, filename):
        with open(filename) as file:
            data = json.load(file)

        return data

    def loadPickle(self,filename):
        pkl = joblib.load(filename)
        return pkl

        # reading CSV 
    def loadCSV(self, filename,delimiter,encode="utf-8"):
        dataset = pd.read_csv(filename,skipinitialspace=True,sep='\s+,\s+',delimiter=delimiter,encoding=encode)
        return dataset

    def oneHotEncoding(self,dataset):
        from sklearn.preprocessing import OneHotEncoder

        onehot_encoder = OneHotEncoder(categories='auto')

        # onehot encode the type column (pisahin)
        type_encoded = onehot_encoder.fit_transform(dataset['type'].values.reshape(-1,1)).toarray()
        dfOneHot = pd.DataFrame(type_encoded,columns = ["Type_"+str(int(i+1)) for i in range(type_encoded.shape[1])])
        dataset = dataset.drop('type',axis = 1)
        dataset = pd.concat([dataset, dfOneHot], axis=1)

        # change order of dataframe alphabetically
        dataset = dataset.reindex(sorted(dataset.columns), axis=1)

        return dataset

util = Utility()
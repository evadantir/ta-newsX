# -*- coding: utf-8 -*-
import pandas as pd
from preprocessing import Preprocess

class ExtractIntNews(object):
    def __init__(self):
        self.pre = Preprocess()

    def cleansingText(self, text):
        return self.pre.normalizePunctuation(text)

    def extractContentCSV(self,filename,news,filesave):
        data = pd.read_csv(filename,sep=',')

        #get only needed news
        # data = data.loc[data['publication'] == news]
        # #filter needed data
        temp = pd.DataFrame()
        temp['url'] = data['url']
        temp['date'] = data['date']
        try:
            # temp['title'] = data['title']
            # temp['content'] = data['content']
            #normalize punctuation
            temp['title'] = data['title'].apply(lambda x: self.cleansingText(x))
            # if code == 'CNN':
            #     temp['content'] = self.cleansingCNN(data['content'])
            # else:
            temp['content'] = data['content'].apply(lambda x: self.cleansingText(x))
        # print data
        # exit()
            #save filtered data to CSV
            temp.to_csv(filesave,sep=',', encoding='utf-8')
            print "done"
        except:
            pass
    # def cleansingCNN(self, data):
    # pola: Kota - (CNN)
    #     import re

    #     temp = pd.DataFrame()
    #     temp = self.cleansingText(data)
    #     temp['content'] = re.sub('')

    # def cleansingReuter(self, data):
    # pola: ( )
    #     import re

    #     temp = pd.DataFrame()
    #     temp = self.cleansingText(data)
    #     temp['content'] = re.sub('')
        

ex = ExtractIntNews()

# ex.extractContentCSV('CNN.csv','CNN','cnn.csv')
# ex.extractContentCSV('Guardian.csv','Guardian','guardian_edit.csv')
# ex.extractContentCSV('Guardian_Reuter.csv','Reuters','reuters.csv')
ex.extractContentCSV('reuters.csv','Reuters','reuters_edit.csv')
# data = pd.read_csv('reuters.csv',sep=';')
# print data
# -*- coding: utf-8 -*-
import pandas as pd
import re
from preprocessing import Preprocess

class ExtractIntNews(object):
    def __init__(self):
        self.pre = Preprocess()

    def cleansingText(self, text):
        return self.pre.normalizePunctuation(text)

    def extractContentCSV(self,filename,news,filesave):
        data = pd.read_csv(filename,sep=';')
        # print data

        #get only needed news
        # data = data.loc[data['publication'] == news]

        # #filter needed data
        temp = pd.DataFrame()
        # temp['url'] = data['url']
        temp['date'] = data['date']
        # temp['title'] = data['title']
        # temp['content'] = data['content']
        #normalize punctuation
        temp['title'] = data['title'].apply(lambda x: self.cleansingText(x))
        # if news == 'CNN':
        temp['content'] = data['content'].apply(lambda x: self.cleansingCNN(x))
        # elif news == 'Reuters':
        #     temp['content'] = data['content'].apply(lambda x: self.cleansingReuter(x))
        # else:
        #     temp['content'] = data['content'].apply(lambda x: self.cleansingText(x))
        
        #save filtered data to CSV
        temp.to_csv(filesave,sep=';', encoding='utf-8', index=False)
        print "done"

    def cleansingCNN(self, data):
        # pola: Kota - (CNN)
        
        temp = self.cleansingText(data)
        # print 'done cleansing'
        temp= re.sub(r'(.*?)\(CNN\) ','',temp)
        # print 'done remove cnn'
        return temp

    def cleansingReuter(self, data):
        # pola: ( )

        temp = pd.DataFrame()
        temp = self.cleansingText(data)
        temp['content'] = re.sub('')
        

ex = ExtractIntNews()


# ex.extractContentCSV('CNN.csv','CNN','cnn_only.csv')
# ex.extractContentCSV('cnn_only1.csv','CNN','cnn_edit1.csv')
# ex.extractContentCSV('Guardian.csv','Guardian','guardian_edit.csv')
# ex.extractContentCSV('Guardian_Reuter.csv','Reuters','reuters.csv')
# ex.extractContentCSV('reuters.csv','Reuters','reuters_edit.csv')
# data = pd.read_csv('reuters.csv',sep=';')
# print data
# print ex.cleansingCNN('Washington (CNN) Testing')
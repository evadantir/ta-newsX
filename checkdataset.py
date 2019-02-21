from nlp_helper import NLPHelper
from utility_code import Utility
from feature_extractor import FeatureExtractor
import nltk
import os
import pandas as pd

class CheckDataset(object):
    def __init__(self):
        self.nlp = NLPHelper()
        self.ut = Utility()
        self.fex = FeatureExtractor()

    def checkData(self):
        path = "scenario2_fullidn_pickle/"
        filelist = os.listdir(path)
        data = pd.DataFrame()

        for idx, file in enumerate(filelist):

            #buka file pickle yang isinya data ner, coref, dan pos dari suatu teks berita
            pkl_dict = self.ut.loadPickle(os.path.join(path, file))
            # print(pkl_dict['ner'])
            # entities = self.fex.extractBefEntity(pkl_dict['ner'])
            filename = pkl_dict['filename']

            df = pd.DataFrame()

            df = self.countTermFrequency(pkl_dict['text'])
            df['filename'] = filename
            data = data.append(df)
            # df['entities'] = entities
        self.ut.convertToExcel("TF.xlsx",data,'Sheet1')

    def countTermFrequency(self,text):
        import nltk

        words = nltk.word_tokenize(text)
        fdist = nltk.FreqDist(words)

        df = pd.DataFrame.from_dict(fdist,orient='index').reset_index()
        df.columns = ['term','frequency']
        # for word, frequency in fdist.most_common(50):
        #     print(u'{}:{}'.format(word, frequency))
        return df



cd = CheckDataset()

cd.checkData()
# cd.countTermFrequency("Malea Emma Tjandrawidjaja, the 7-year-old Indonesian prodigy who amazed the crowd at the StubHub Center stadium in Los Angeles back in September, participated in an auditionfor American Idol on Oct. 14 in Coeur d'Alene, Idaho. Wearing a dress, Malea stoodbefore the judges  Lionel Richie, Katy Perry and Luke Bryan  accompanied by host Ryan Seacrest. She performed the United States' national anthem \"The Star-Spangled Banner\" and Aretha Franklin's \"Think\" garnering praise and standing ovations from the celebrated singers. \"You made Ryan cry!\" said Perry after Malea had finished singing the national anthem.Arman Tjandrawidjaja, Malea's father, told The Jakarta Post via email that Malea received a golden ticket, meaning that she could go to Hollywood  but in 2027. \"Because she has to be 15 years old [by June 1]to compete,\" Arman said. As the time of writing, Malea's Idol audition had been liked by more than 2.000 users on YouTube. The young singer reportedly caught Seacrest's attention due to her interview with David Muir from ABC World News following her StubHub Center Stadium performance. At that time Muir encouraged Seacrest to watch the show as there was a 7-year-old girl \"who is definitely an American Idol\". Arman stated that Seacrest had watched the show and noticed Malea's video as well. \"He then contacted American Idol's producers to invite Malea for an audition,\" Arman said, adding that Seacrest once interviewed her daughter on the On Air with Ryan Seacrest radio show back in September. Recently Seacrest shared his story about the audition alongside presenter Kelly Ripa on Live with Kelly and Ryan. \"She went full Christina Aguilera,\" said Seacrest, recalling the audition. \"They [the judges] loved it;they thought it was very cute, but it was because David [Muir] said on the air.\" Malea is scheduled to perform in several events until November, among them a Los Angeles Clippers game at the Staples Center in Los Angeles on Oct. 21, Skechers Pier to Pier Friendship Walk in Manhattan Beach on Oct. 28, SEMA Show Industry Awards Banquet in Las Vegas on Nov. 1 and a Los Angeles Lakers game at the Staples Center in Los Angeles on Nov. 25.")
# -*- coding: utf-8 -*-
from preprocessing import Preprocess
from nlp_helper import NLPHelper
from feature_extractor import FeatureExtractor
from utility_code import Utility
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from nltk.tag import StanfordPOSTagger
from nltk.tree import *
from dateutil.parser import parse
import dateutil.parser as parser
import re
import os
import pandas as pd
import json
from meta_parser import parse_date
from pprint import pprint


class FiveWExtractor(object):

    def __init__(self):
        self.pre = Preprocess()
        self.nlp = NLPHelper()
        self.fex = FeatureExtractor()
        self.ut = Utility()
    
    def extractNerCorefFromTxt(self, text,title):

        ner = self.nlp.getNER(text)
        print ("NER extraction completed")
        coref = self.nlp.getCoref(text)
        print ("Coref extraction completed")
        nlp_dict = {
            'title' : title,
            'text' : text,
            'ner' : ner,
            'coref' : coref,
        }
        
        return nlp_dict

    def extractINANerAndCoref(self,text,title):
        ner = self.nlp.getIdnNER(text)
        print ("NER extraction completed")
        coref = self.nlp.getCoref(text)
        print ("Coref extraction completed")
        nlp_dict = {
            'title' : title,
            'text' : text,
            'ner' : ner,
            'coref' : coref,
        }
        
        return nlp_dict 

    def extractWhoOrWhere(self,text,title,ml,ner_coref):

        # load machine learning model
        model = self.fex.loadPickle(ml)

        # extracting features and convert it to numeric type
        features = self.fex.extractFeaturesDirectFromText(ner_coref)
        print(features)
        features = self.convertToNumeric(features)
        
        # predicting who or where by it's feature, dropping unused column
        predict_candidate = model.predict(features.drop('entity', axis=1))

        candidate = []

        for i in range(len(predict_candidate)):
            if predict_candidate[i] == 1:
                # insert candidate to list
                candidate.append(features.iloc[i,1])
        
        return candidate
    
    def convertToNumeric(self,dataset):
        # convert categorical feature to numeric
        dataset['type'] = dataset['type'].map({'PERSON': 1, 'LOCATION': 2, 'ORGANIZATION': 3,'NP': 4,'DATE':5,'TIME':6}).astype(int)
        dataset['occ_title'] = dataset['occ_title'].map({False: 0, True: 1}).astype(int)
        return dataset

    def getWhenCandidatefromNER(self,ner_list):

        # getting when candidate (date and time) from extracted NER

        list_date = []
        list_time = []
        when_candidates = []

        date = []
        time = []

        for ner in ner_list:
            if ner[1] == 'DATE':
                date.append(ner[0])
            elif ner[1] == 'TIME':
                time.append(ner[0])
            else:
                if date != []:
                    list_date.append(self.pre.joinText(date))
                    date = []
                if time != []:
                    list_time.append(self.pre.joinText(time))
                    time = []

        list_date = self.pre.sieveSubstring(list_date)
        list_time = self.pre.sieveSubstring(list_time)
        when_candidates = list_date + list_time

        if when_candidates:
            return when_candidates
        else:
            return None

    def extractWhenFromText(self,text,ner):
        when_candidates = self.getWhenCandidatefromNER(ner)

        if when_candidates:
            when = None
            when_score = None

            for candidate in when_candidates:
                candidate_score = self.scoreWhenCandidate(candidate,text)
                if not when_score or candidate_score > when_score:
                    when = candidate
                    when_score = candidate_score

            return when
        else:
            return None

    def findPositioninText(self, candidate, sent_list):
        for i in range(len(sent_list)):
            pos = i+1
            
            match = re.search(candidate.lower(),sent_list[i].lower())
            if match:
                return pos
            else:
                return None
                
            
    def scoreWhenCandidate(self, candidate,text): 
        # w0, w1, w2, w3 = weight of value
        # d = the document length measured in sentences
        # pc || p(c) = the position measured in sentences of candidate c within the document

        w0 = 10
        w1 = w2 = 1
        w3 = 5

        sent_list = sent_tokenize(text)
        d = len(sent_list)
        pc = self.findPositioninText(candidate,sent_list)

        if pc:
            score = w0 * ((d-pc) / d) + w1 * self.isDate(candidate) + w2 * self.isTime(candidate) + w3 * self.isDateTime(candidate)
        else:
            score = 0

        return score

    def isDate(self,candidate):
        # check if candidate is date instance, else return 0

        parser.parser.parse = parse_date
        try:
            parsed_candidate = parser.parser().parse(candidate,None)
            # if contain date
            if parsed_candidate[0].day or parsed_candidate[0].month or parsed_candidate[0].year or parsed_candidate[0].weekday:
                return 1
            # if doesnt contain time and/or date
            else:
                return 0

        except (ValueError,AttributeError) as e:
            return 0

    def isDateTime(self,candidate):
        # check if it's parseable to datetime type
    
        try:
            parsed_candidate = parse(candidate)
            return 1
        except (ValueError,AttributeError) as e:
            return 0

    def isTime(self,candidate):
        # check if when candidate contains date+time, time only, or neither

        parser.parser.parse = parse_date
        try:
            parsed_time = parser.parser().parse(candidate,None)

            # if contain time
            if parsed_time[0].hour or parsed_time[0].minute or parsed_time[0].second or parsed_time[0].microsecond:
                # if contain date too
                if parsed_time[0].day or parsed_time[0].month or parsed_time[0].year or parsed_time[0].weekday:
                    return 0.8
                # if time only
                else:
                    return 1
            # if doesnt contain time and/or date
            else:
                return 0

        except (ValueError,AttributeError) as e:
            return 0

    def extractWhatFromText(self,who_candidates,title,text):
        what = []
        for who in who_candidates:
            # If one of our WHO candidates occurs in the title, we look for the subsequent verb phrase of it
            match = re.findall(r'\b'+re.escape(who.lower()) + r'\b',title.lower())
            if match:
                anno = list(self.nlp.getConstituencyParsing(title))
                # print(anno)
                # returning verb phrase from title
                for sub_tree in anno[0].subtrees(lambda t: t.label() == 'VP'):
                    what.append(' '.join(sub_tree.leaves()))
            # If there is no WHO in the headline, we search within the text for the first occurrence of our highest ranked WHO and also take the subsequent verb phrase as WHAT
            else:
                sent_list = sent_tokenize(text)
                for sent in sent_list:
                    # find first occurrence of who in sentence
                    match = re.findall(r'\b'+re.escape(who.lower()) + r'\b',sent.lower())
                    if match:
                        # getting verb phrase
                        anno = list(self.nlp.getConstituencyParsing(sent))
                        # print(anno)
                        break
                # returning verb phrase from text
                for sub_tree in anno[0].subtrees(lambda t: t.label() == 'VP'):
                    what.append(' '.join(sub_tree.leaves()))

        what = self.pre.sieveSubstring(what)

        return what

    def extractWhyFromText(self,what_candidates,text):
        regexWhy = [('since',0.2),('cause',0.3),('because',0.3),('hence',0.2),('therefore',0.3),('why',0.3),('result',0.4),('reason',0.3),('provide',0.1),('s behind',0.1),('Due to',0.2)]

        #for returning reason candidates from inputted text(s)
        why_candidates = []

        #extract sentence from the text
        sentence_list = sent_tokenize(text)

        for sent in sentence_list:
            matched_key = []
            # why = {}
            for reg in regexWhy:
                #check every word in sentence to see if there are same word with the keyword
                match = re.findall(r'\b'+re.escape(reg[0].lower()) + r'\b',sent.lower())
                if match:
                    matched_key.append(reg)

            if what_candidates:
                # check if what is in sentence
                # anggap 1 kalimat hanya punya 1 what
                for what in what_candidates:
                    match = re.findall(r'\b' + what.lower() + r'\b',sent.lower())
                    if match:
                        # check with WHAT(.*)to/TO(.*)/VB rule
                        pos = self.nlp.getPOS(sent)
                        for i in range(len(pos)):
                            if pos[i][1] == 'TO':
                                if pos[i+1][1] == 'VB':
                                    rule = ('(WHAT(.*)to/TO(.*)/VB)',0.5)
                                    matched_key.append(rule)
                        # check with (WHAT(.*)will) rule
                        checked = re.findall(r'\b'+re.escape('will') + r'\b',sent.lower())
                        if checked:
                            rule = ('(WHAT(.*)will)',0.5)
                            matched_key.append(rule)
                    
            #store all reason list found from one text in  container
            if matched_key != []:
                why = sent
                # why['sentence'] = sent
                # why['keys'] = list(set(matched_key))
                # why['total_confidence'] = sum([value[1] for value in why['keys']])
                why_candidates.append(why)

        return why_candidates

    def extract5w(self,text,title):

        # getting ML model for classifying who and where
        who_model = "./model/train_who_idnhalf.pkl"
        where_model = "./model/train_where_idnhalf.pkl"

        # getting NER and Coref of the text
        ner_coref = self.extractNerCorefFromTxt(text,title)
        # extracting 5w
        who = self.extractWhoOrWhere(text,title,who_model,ner_coref)
        where = self.extractWhoOrWhere(text,title,where_model,ner_coref)
        when = self.extractWhenFromText(text,ner_coref['ner'])
        if who:
            what = self.extractWhatFromText(who,title,text)
        else:
            what = None
        why = self.extractWhyFromText(what,text)

        result_dict = {
            'title':title,
            'text': text,
            "who" : who,
            'where' : where,
            'what' : what,
            'when' : when,
            'why' : why
        }
        return result_dict

    def extract5wLocalNews(self,text,title):

        # getting ML model for classifying who and where
        who_model = "./model/train_who_idnhalf.pkl"
        where_model = "./model/train_where_idnhalf.pkl"

        # getting NER and Coref of the text
        ner_coref = self.extractINANerAndCoref(text,title)
        # extracting 5w
        who = self.extractWhoOrWhere(text,title,who_model,ner_coref)
        where = self.extractWhoOrWhere(text,title,where_model,ner_coref)
        when = self.extractWhenFromText(text,ner_coref['ner'])
        if who:
            what = self.extractWhatFromText(who,title,text)
        else:
            what = None
        why = self.extractWhyFromText(what,text)

        result_dict = {
            'title':title,
            'text': text,
            "who" : who,
            'where' : where,
            'what' : what,
            'when' : when,
            'why' : why
        }
        return result_dict

    def prettyPrint5w(self, result):
        print("News Title: ",result['title'])
        print()
        if result['who']:
            print("WHO is in the news?: ",result['who'])
        else:
            print("Sorry, can not detect the WHO in the news")

        if result['where']:
            print("WHERE does the news take place?: ",result['where'])
        else:
            print("Sorry, can not detect the WHERE in the news")

        if result['when']:
            print("WHEN did the news happen: ",result['when'])
        else:
            print("Sorry, can not detect the WHEN in the news")

        if not result['who']:
            print("WHAT in the news is not detected, because the WHO element in the news was not detected")
        else:
            print("WHAT happened in the news: ",result['what'])

        if not result['why']:
            if no result['what']:
                print("WHY in the news is not detected, because the WHAT element in the news was not detected")
            else:
                print("Sorry, can not detect the WHY in the news")
        else:
            print("WHY did the news happen: ",result['why'])

fw = FiveWExtractor()

# text="\"I must say that he surprised me,\" said father, Jos, who competed in Formula One from 1994 to 2003. \"I've seen many races of this, and this was incredible. Although Red Bull didn't have the right strategy and were unlucky with the weather, it was almost worth them having a bad stop to see what he did afterwards. It's good for F1, everyone is enthusiastic. What more do you want?\" Equally enraptured was Niki Lauda, the former world champion and Mercedes' non-executive chairman. Congratulating the Verstappen family, he said: \"Max was outstanding with the passes he performed. He did a job that was impressive. I knew the guy was good, but he has proved again to everybody what he can do.\""
# title="Max Verstappen even stuns his dad by storming home into third place at Brazilian Grand Prix"

# title = "Formula One star Max Verstappen shows nerves of steel to avoid serious accident after losing control of his car at 180mph in treacherous conditions at the Brazilian Grand Prix"
# text =  "Teenage Formula One star Max Verstappen showed nerves of steel as he somehow managed to avoid a serious accident despite spinning his car at 180mph in dangerous conditions at the Brazilian Grand Prix. Travelling flat out at the Interlagos circuit, Verstappen lost control as he clipped the curb on the entrance to the long home straight, spinning his car sideways and sliding dangerously down the track. But just as it looked as though he was going to smash the nose of his car into the metal side hoardings, which would likely have seen his car catapulted into the middle of the track and into the path of other cars, he was able to straighten up and regain control. Max Verstappen clipped the curb on his way up the hill towards the home straight in Brazil. That caused Verstappen to lose control of his car as his back end slid round as he spun. With the nose of his Red Bull car pointing towards the wall, Verstappen slid down the track. Verstappen produced an incredible display to finish third at the Brazilian Grand Prix. Immediately after the incident a member of Verstappen's Red Bull pit crew calmly said 'well held Max, well held' on the team radio before the driver himself joked 'my heartbeat went a little higher there.' While many would have been shaken by such a high-speed incident, Verstappen showed maturity beyond his years as he recovered to eventually secure third place in the Grand Prix, behind Lewis Hamilton and Nico Rosberg. Verstappen is one of the hottest teenage talents F1 has ever seen and in his two seasons in the sport has thrilled and frustrated in equal measure, with an aggressive driving style which has split opinion both in the pits and in the stands. But the 19-year-old gained universal praise for the way he avoided a serious accident in hazardous conditions in Brazil, during a race in which a number of spectacular crashes caused major delays as drivers struggled to cope with the wet weather. The back of Verstappen's car slid out as the camera cut to show the view of the home straight. That left Verstappen in a vulnerable position, with his car side on and facing the barrier. But as he slid further and further down the track, Verstappen was able to straighten up. Miraculously he was able to drive away from the incident without hitting the wall of the track. The young Dutchman overcame adverse weather to produce a masterclass at Interlagos. The young Dutchman then produced one of the drives of the season as he sliced his way through the field from 16th to third, as the rain continued to fall, having found himself stranded down the field after being caught out by one of the numerous yellow flags deployed during the race. The safety car, which appears on the track to lead drivers round following a crash, was deployed five times during the race while a red flag was produced twice - taking the drivers off the track as conditions became too bad to race in. 'This is just mad,' said a furious Sebastian Vettel, who also spun earlier in the race, over the team radio. 'Stupid. What this race needs is a red flag. How many people do we want to crash?' It was a difficult afternoon for the race organisers, with some drivers calling for the grand prix to be abandoned due to hazardous conditions. Hamilton was not among their number. 'It is understandable for the first red flag with everyone going off,' he said. Kimi Raikkonen was fortunate to see his other Formula One drivers avoid colliding into his car. Raikkonen's Ferrari is removed from the track following his crash which brought a red flag. Felipe Massa also crashed out of the race, his last in his homeland before his retirement 'I don't really understand why the second stop came. But safety comes first and obviously it was thought it was needed. 'This is Formula One and the rain is the trickiest condition. If people didn't make mistakes, it would be too easy and everyone could do it. 'We run at serious speeds and there is a lot of water to disperse by the tyres and they struggle the faster we go.' The champagne was flowing once again for Lewis Hamilton (left) after he won in Brazil. Hamilton led the race in Brazil from start to finish after winning from pole position Hamilton revealed victory in Brazil had been an ambition of his since watching Ayrton Senna. For Hamilton to win the title, He must win in Abu Dhabi and hopes Rosberg finishes fourth or lower. If Rosberg finishes third in Abu Dhabi on Nov 27, he wins the championship. While Verstappen was one of a number of drivers involved in dramatic incidents during the race, things proved to be a lot more simple for Hamilton as he produced a masterful drive in the wet to win the race from pole position. The victory meant the reigning world champion stays in the race to win this year's title, but he faces a tough task to overhaul team-mate and rival Nico Rosberg at the final Grand Prix of the season, in Abu Dhabi on Sunday. 'I was genuinely chilling up front,' he said. 'When it rains it is usually good for me. There were no mistakes, no issues, no spins. It was interesting hearing about so many people having slips, but I didn't have any.' Rosberg leads the championship by 12 points heading into the final round, meaning third place for the German in Abu Dhabi will secure his first world title. "
# title = "All England champ Kevin Sanjaya showered with bonuses"
# text = """Shuttler Kevin Sanjaya Sukamuljo, half of the men's doubles pair that retained their title at the 2018 All England Open Badminton World Championships, has been awarded a cash bonus from his club Djarum Kudus and several sponsors on Wednesday for his achievements in Birmingham. \"It was a big responaibility to defend such a prestigious title like the All England,\" Kevin said in a statement. \"Support from [my] coaches and the experience of training in the club have been of great help for me to do my best,\" he added. Kevin won the All England men's doubles title with Marcus Fernaldi Gideon, who plays for the Tangkas Intiland Jakarta badminton club, defending the title they won in 2017. At Wednesday's event, Kevin received a check for Rp 200 million (US$14,550) from Djarum. The top-ranking doubles shuttler also received sponsors' vouchers worth Rp 40 million from e-commerce platform Bli-Bli and Rp 10 million from online travel agent Tiket.com, as well as a 55-inch LED television from home appliance company Polytron. Earlier, the Youth and Sports Ministry gave Kevin and Marcus each a Rp 250 million cash award. Djarum Foundation program director Yoppy Rosimin said he hoped that Kevin's success would set an example for junior shuttlers and inspired them to replicate his achievements. Djarum Foundation also awarded a cash bonus of Rp 70 million each to men's doubles coaches Herry IP and Aryono Miranat, who led their ace pair to win the prestigious badminton title."""
# title = "It's official: Prabowo to join 2019 race"
# text = "Gerindra Party chairman and chief patron Prabowo Subianto accepted his party's mandate to run for the presidency at its national coordination meeting in Hambalang, West Java, on Wednesday.His decision ended speculation over whether he was considering sitting the election out to endorse another candidate in the 2019 race. It also increased the likelihood that the upcoming election sees a rematch between the former commander of the Army's Special Forces and President Joko \"Jokowi\" Widodo.\"As the party's mandatary, as the holder of your mandate [...] I declare that I have submitted and complied with your decision,\" Prabowo said in a video of the closed-door meeting provided by a Gerindra politician.Earlier in the day, the opposition leader made it clear that he would only contest the election if the party built a strong alliance with other parties.Arriving to the meeting's main stage on horseback, to the strains of a brassy rendition of traditional marching song \"The British Grenadiers\", Prabowo cut an imposing figure in Gerindra's trademark white shirt, khaki pants, and black peci fez. \"With all my energy, body and soul, if Gerindra orders me to run in the upcoming presidential election, I am ready to carry out that task,\" he said, according to a Gerindra politician that was present, to the applause of the party members in attendance, who broke out in chants of \"Prabowo, president!\"Prabowo cut off the chanting, however, and asked for patience.\"I said 'if', 'if the party orders me,'\" he said. \"There is one condition. Even if the party orders me [to run], I need the support of friendly parties.\" Over the past few weeks, Prabowo has seemed hesitant over whether to run against President Jokowi again.Maksimus Ramses Lalongkoe, the executive director of the Institute of Indonesian Political Analysis, said Prabowo's apparent hesitation rested mostly on the lack of a clear coalition backing his candidacy.The 2017 Elections Law specifies that political parties seeking to nominate a presidential candidate are required to secure at least 20 percent of seats at the House of Representatives or 25 percent of the popular vote.Gerindra currently holds only 13 percent of House seats and 11.81 percent of the popular vote, which means it needs to join forces with other parties to be able to nominate Prabowo or any other potential candidate.Four parties with significant vote shares have yet to officially back a candidate: the National Mandate Party (PAN), the Prosperous Justice Party (PKS), the National Awakening Party (PKB) and the Democratic Party (PD).PAN and the PKS have worked together with Gerindra in recent times, most notably during the contentious Jakarta gubernatorial election last year. "

title = "Bootleg liquor claims more lives in Bekasi"
text = "Five residents of Kodau Ambara Pura housing complex in Jatiasih, Bekasi, have reportedly died after drinking oplosan (bootleg liquor). The victims have been identified as Emo or Imron, 47, Alvian or Pokin, 52, Yopi, 45, Mambo or Hermadi, 58, and Heri Bayo, 57. \"My brother died on Thursday evening,\" said Hermadi's brother, Suryadi, as quoted by tribunnews.com on Friday. The five were close friends, Suryadi said, adding that the group might have drunk together last week after getting bootleg liquor for free from a man named Untung. Imron was the first to die on April 13 after suffering from severe stomach pains and respiratory problems. Alvian and Yopi died five days later. \"[Other residents and I] started suspecting that it was the bootleg liquor that had killed them, because we knew they all drank together last week,\" Suryadi explained. Jatiasih Police chief Comr. Illi Anas said that his team is investigating the case. \"We're attempting to gather as much information,\ Illi said."

fw.prettyPrint5w(fw.extract5w(text,title))

# print(fw.nlp.getIdnNER(text))

# Simple usage
# import logging
from stanfordcorenlp import StanfordCoreNLP
from tokenization import *

def phraseChunking(ner):
	ent_list = []
	temp = []

	for entity in ner:
		if(entity[1] == 'ORGANIZATION'):
			temp.append(entity[0])
		else:
			if len(temp) > 0:
				ent_list.append(" ".join(temp))
				temp = []

	return ent_list

nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2018-02-27')
# text = "Ethiopian Airlines is expecting to kick off its inaugural direct flight connecting Jakarta and Addis Ababanext month. Foreign Minister Retno LP Marsudi met with Ethiopian Airlines CEO Tewolde Gebremariam on the sidelines of the Indonesia-Africa Forum in Nusa Dua, Bali, on Wednesday. We talked about connectivity because it matters in supporting economic, trade and people-to-people cooperation, said Retno after the meeting. Hence, the agreement on the direct flight is a breakthrough for Indonesia-Africa economic ties,she added. Retno further said a lack of connectivity had been an issue that hindered Indonesia and Africa from boostingtrade and investment cooperation. In the meeting, I also expressed our interest to designate Addis Ababa as the hub of Indonesias visa services for other African countries, the minister said. Retno also suggested Ethiopian Airlinescooperate with national flag carrier Garuda Indonesia for maintenance services. Separately, Indonesian Ambassador to Ethiopia Imam Santosa said the Jakarta-Addis Ababa direct flight would likely kick off within a month or two, depending on the progress of technical preparations. It depends on technical readiness, like offices, partnerships for catering services and airport facilities, he said. Once they are ready, the flights can start. Ethiopian Airlines plans to provide the direct flightthree times a week via Bangkok. (ebf)"
# text = 'My sister has a friend called John. Really, tell me more about him? She think he is so funny!'
text="""The Jakarta State Administrative Court (PTUN Jakarta) granted the Indonesian Justice and Unity Party's (PKPI) petition to contest the 2019 legislative election on Wednesday.\"We declare KPU\'s (General Elections Commission) decision letter [...] on the determination of political parties participating in the 2019 legislative election void,\" presiding judge Nasrifal said as quoted by tribunnews.com. The judge also ordered the KPU to issue a new letter naming the PKPI, which is led by former spy chief AM Hendropriyono, one of the political parties eligible to contest the 2019 election. In February, the KPU declared the PKPI ineligible to contest the election because it had failed to meet the proscribed membership criteria. The party appealed the KPU\'s decision with the Elections Supervisory Agency (Bawaslu), and then petitioned the court when the appeal was rejected. The ruling makes the PKPI the 16th party eligible to contest the election."""
# text = "Microsoft is a company built by Bill Gates. It has a lot of branch all over the world"
# text = "Clinton and Gates visit Korean Demilitarized Zone. The US Secretary of State, Hillary Clinton, and Defence Secretary, Robert Gates have visited the Demilitarized Zone separating North and South Korea. Mr. Gates said they wanted to show solidarity with their allies in Seoul"
# sentence = sentence_extraction(text)
# print sentence
# exit()
# print 'Tokenize:', nlp.word_tokenize(sentence)
# print 'Part of Speech:', nlp.pos_tag(sentence)
ner = nlp.ner(text)
print ner
print phraseChunking(ner)
# print 'Constituency Parsing:', nlp.parse(sentence)
# print 'Dependency Parsing:', nlp.dependency_parse(sentence)

# Each tuple represents (sentence_index, start_index, end_index, text), starts with 1-index
coref = nlp.coref(text)
for cr in coref:
	print 'Coreference:',cr

# pros = {'annotators': 'coref', 'pinelineLanguage': 'en'}
# result_dict = json.loads(nlp.annotate(text, properties=pros))

# for idx, mentions in result_dict['corefs'].items():
#     print('Entity:', idx)
#     for m in mentions:
#         print(m)

nlp.close() # Do not forget to close! The backend server will consume a lot memory.

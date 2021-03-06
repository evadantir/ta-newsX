# import re
# import string
import json
import joblib
from pprint import pprint
from nlp_helper import NLPHelper as nlp
# def loadPickle(filename):
#     pkl = joblib.load(filename)
#     return pkl

# data = loadPickle('./nlp_object/e8a979de28fef3fdc3a5f6ee1c971260273dd814493fa1760d0b098c.json.pkl')
# pprint(data['ner'])
# # print (data['coref'])
# exit()

# candidate = [u'October', u'29', u',', u'2016']

# text = ""
# for c in candidate:
#     if not text:
#         text = c
#     elif c in string.punctuation:
#         text += c
#     else:
#         text += " " + c

# print text
# exit()

# candidate = "October 29, 2016"

# sent = u"pic.twitter.com/C2VD3DjppE -- Alana Cartwright (@AlanaCartwrigh3) October 29, 2016  @HelenRyles Hi Helen, yes this is just our smaller bar."

# match = re.search(candidate.lower(),sent.lower())
# print match.group()

# from stanfordcorenlp import StanfordCoreNLP
# from nltk.tokenize import sent_tokenize 
# import json
# to run server: java --add-modules java.se.ee -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
# nlp = StanfordCoreNLP('http://localhost', port=9000)
# nlp = StanfordCoreNLP(r'stanford-corenlp-full-2018-02-27',quiet=False)
# props = {'annotators': 'coref', 'pipelineLanguage': 'en'}
# text = ('GOP Sen. Rand Paul was assaulted in his home in Bowling Green, Kentucky, on Friday, '
#     'according to Kentucky State Police. State troopers responded to a call to the senator\'s '
#     'residence at 3:21 p.m. Friday. Police arrested a man named Rene Albert Boucher, who they '
#     'allege "intentionally assaulted" Paul, causing him "minor injury". Boucher, 59, of Bowling '
#     'Green was charged with one count of fourth-degree assault. As of Saturday afternoon, he '
#     'was being held in the Warren County Regional Jail on a $5,000 bond.')
# text = "My sister has a friend called John. Really, tell me more about him? She think he is so funny!"
# hehe =  nlp.coref(text)
# text = "Speaking from the Oval Office, Nov. 10, President Obama said he was \"very encouraged\" following a meeting with President-elect Donald Trump. Trump said the meeting lasted longer than expected and easily could have gone longer. (The Washington Post) President-elect Donald Trump and President Obama met for the first time Thursday and pledged to work together, starting the whirlwind transition that will unfold over the next 10 weeks until Trump is sworn into office Jan. 20. Trump later met with House Speaker Paul D. Ryan (R-Wis.) at the Capitol and said they also would work together -- but on Republican goals that are opposed by Obama and his fellow Democrats. \"We're going to lower taxes,\" Trump told reporters, with Ryan seated by his side. \"We're going to fix health care and make it affordable and better.\" He appeared to be referring to a plan to lower taxes that heavily benefits top earners and to the GOP's aim of repealing the Affordable Care Act, Obama's signature domestic policy achievement. Following his meeting with Ryan, Trump conferred with Senate Majority Leader Mitch McConnell (R) in the Kentucky senator's Capitol office. An hour and a half after Trump entered the White House through the South Lawn entrance -- avoiding news cameras and the president's staff -- a group of reporters was ushered into the Oval Office, where the president and president-elect were seated in the high-backed armchairs at the end of the room. In a sign of how tensions between the two politicians have not disappeared in the immediate aftermath of the election, the White House did not arrange for the traditional photo-op between the current first couple and the incoming one, a custom that George W. Bush and his wife Laura observed when the Obamas visited the White House in 2008. Melania Trump met separately with Michelle Obama. [Trump maps out a new administration to bring a seismic shift to Washington] Still, Trump told reporters Thursday that he expects to work closely with Obama now and in the future to seek his advice in guiding the country. He noted that a session that was supposed to last 10 to 15 minutes went on for an hour and a half. \"As far as I'm concerned, it could have lasted a lot longer,\" Trump said. \"We discussed a lot of different situations, some wonderful and some difficulties. I very much look forward to dealing with the president in the future, including counsel.\" \"So Mr. President, it was a great honor being with you, and I look forward to being with you many, many more times in the future,\" he added, calling Obama \"a very good man.\" 1 of 22 Full Screen Autoplay Close Skip Ad x What President-elect Donald Trump did on his trip to Washington View Photos Trump arrives at the White House for a meeting with Obama and on Capitol Hill to meet with Republican congressional leaders. Caption Trump arrives at the White House for a meeting with Obama and on Capitol Hill to meet with Republican congressional leaders. Nov. 10, 2016 President Obama talks with President-elect Donald Trump in the Oval Office of the White House in Washington. Jabin Botsford/The Washington Post Buy Photo Wait 1 second to continue. Obama, for his part, said, he was encouraged by \"the interest in President-elect Trump's wanting to work with my team around many of the issues that this great country faces. And I believe that it is important for all of us, regardless of party and regardless of political preferences, to now come together, work together, to deal with the many challenges that we face.\" The president said that the men's two wives had enjoyed spending time together Thursday morning. \"We want to make sure they feel welcome as they prepare to make this transition,\" Obama said. \"Most of all, I want to emphasize to you, Mr. President-elect, that we now are going to want to do everything we can to help you succeed -- because if you succeed, then the country succeeds.\" [Trump's victory exposes Obama's inability to connect with white working class] Later, Trump and his wife, along with Vice President-elect Mike Pence, met with Ryan at the Capitol, where Trump pledged to work closely with Republican congressional leaders. Ryan ushered Trump out onto the Speaker's Balcony and gestured toward the Washington skyline and the monuments west of the Capitol. He pointed to an inaugural platform being built on the Capitol grounds, appearing to show Trump where he would be taking the oath of office as president. McConnell joined Trump and his entourage on a walking tour through part of the building. At the White House, first lady Michelle Obama and Melania Trump met for tea in the private residence and took a tour that included stepping onto Truman Balcony, as well as a tour of the State Floor with the White House curator. They talked about raising children in the White House, and then they visited the Oval Office to meet the president and president-elect. As the two leaders met, White House Chief of Staff Denis McDonough gave a tour to Trump's son-in-law, Jared Kushner, and other aides, notably Dan Scavino, across the edge of the Rose Garden. Afterward McDonough led Kushner on a walk down the South Lawn for nearly 20 minutes, at which point the two men rejoined Trump's senior staff and reentered the White House. During Obama and Trump's press availability, Kushner snapped photos with his iPhone. A slew of journalists, including international reporters, milled about on the driveway leading to the West Wing ahead of Trump's arrival. Some did live updates to their networks. Across West Executive Drive, dozens of White House staffers gathered on a steps in hopes of a glimpse of the president-elect. This is the scene on the West Wing driveway right now. pic.twitter.com/KoLxqek8qo -- David Nakamura (@DavidNakamura) November 10, 2016 Obama has pledged his administration's full cooperation with Trump's transition team, citing the close working relationship he enjoyed with President George W. Bush during their transfer of power eight years ago. The White House said that Pence met with Vice President Biden in the afternoon. \"I have instructed my team to follow the example that President Bush's team set eight years ago and work as hard as we can to make sure that this is a successful transition for the president-elect,\" Obama said in the Rose Garden on Wednesday. The president said he called to congratulate Trump early Wednesday morning after news networks had formally announced Trump as the winner over Democratic nominee Hillary Clinton.' White House press secretary Josh Earnest told reporters after the meeting that the two men did not try to resolve all of their differences, but he said it was \"a little less awkward\" than reporters might have anticipated. Obama and Trump met privately without any other staff in the room. A large part of the Oval Office session was devoted to talking about how to staff and organize the White House. \"That's complicated business,\" Earnest said, noting that presidents have to deal with multiple challenges and crises at the same time. It is \"something President Obama has thought about extensively over the past eight years.\"  Obama had denounced Trump as \"temperamentally unfit\" for the White House during a long and brutal campaign. But he said that \"we are now all rooting for his success in uniting and leading the country. The peaceful transition of power is one of the hallmarks of our democracy. And over the next few months, we are going to show that to the world.\" Trump, and Clinton, already had been receiving national-security briefings as the nominees of the two major political parties. The White House said Thursday that Obama has convened a coordinating council to facilitate a smooth transition, including providing briefings from federal agencies to Trump's transition team, headed by New Jersey Gov. Chris Christie (R). Officials from the Trump transition team are starting to set up shop in agencies across the federal government, where they can consult with top Obama officials as they assemble their staffs. The current White House has already begun to transfer a massive amount of information to the National Archives and Records Administration: so far it has sent 283 million files, comprising 122,000 gigabytes of data. In an interview Wednesday, White House communications director Jennifer Psaki said the president has talked privately with his staff, as well as publicly, about putting institutional interests ahead of political ones. Referring to the speeches Obama delivered upon winning the presidency and at his first inaugural, she said: \"He reflects a lot about the cog in the wheel that you are as president. He was taking the baton, he's handing it off. But I think it's a recognition that it's bigger than individual aspirations and it's bigger than yourself, and bigger than anything that you've accomplished. Because we as a country need to be stable, need to have continuity.\" In the wake of protests over Trump's win, Earnest said that while the president believes the protesters have a right to express their opinions, his message to them is that \"we're Americans and patriots first\" and that an orderly transfer of power ranks as a top White House priority. Ohio Gov. John Kasich (R), who ran unsuccessfully in the GOP presidential primary and harshly criticized Trump, was at the White House on Thursday to attend Obama's ceremony for the NBA champion Cleveland Cavaliers. Speaking to reporters outside the West Wing, Kasich said he saw people protesting Trump's election as he entered the White House gates, and he called for unity. \"I just want to remind everyone in our country that the office of the presidency needs to be respected,\" he said. \"Today, I said my prayers on the plane for the success of Donald Trump. And I think as Americans, we all need to come together.\" There is long-standing bad blood between Trump and Obama, after the New York businessman led a public campaign to try to force the president to disclose his long-form birth certificate in 2011 over unfounded questions from some conservatives who thought the president was not born in the United States. As a candidate, Donald Trump vowed to dismantle some of President Obama's key achievements. Washington Post White House reporter David Nakamura breaks down what the Obama administration is worried about going forward. (Sarah Parnass/The Washington Post) During the White House Correspondents' Association dinner that year, Obama lit into Trump, mocking him before a ballroom of 2,000 guests and on live television. During the campaign, Trump promised to repeal the president's signature health-care law and overturn many of his executive actions. Obama said Trump was not to be trusted with the nation's nuclear codes and represented an existential threat to democracy. Obama sought to play down their differences and said Trump's victory speech was magnanimous and set the right tone to help try to heal the nation's political divisions that were exposed and inflamed over the past 15 months. \"They do not have an extensive personal relationship,\" Earnest said Wednesday, drawing laughs from reporters. \"This is not a situation where they've had many conversations or played golf together or any of that business. So I guess that will be among the many, many, many reasons that tomorrow's meeting will be rather interesting.\" After his meeting with Trump, Obama welcomed another high-profile visitor with his own large media contingent: LeBron James and the NBA champion Cleveland Cavaliers."
# text = "A girl named Kendall Jenner praises Manchester's 'incredible resilience' after bombing. Jenner said it because she thinks that they will never going to let anyone forget about those victims"
# print hehe

# sent = sent_tokenize(text)
# print(text)
# for s in sent:
#     print(nlp.ner(s))
# try:
#     data = json.loads(nlp.annotate(text,props))
#     print(data)
#     coref = data['corefs']
#     for idx,mentions in coref.items():
#         for m in mentions:
#             print(m['text'])
#             print(m['isRepresentativeMention'])
# except json.decoder.JSONDecodeError:
#     print("oleeee")
# # print(data)
# # print(data[0][0][3])
# nlp.close()

# result = json.loads(nlp.annotate(text, properties=props))
# num, mentions = result['corefs'].items()[0]
# for mention in mentions:
#     print(mention)
# print(result)
# nlp.close()


# from pynlp import StanfordCoreNLP

# annotators = 'tokenize, ssplit, pos, lemma, ner, entitymentions, coref, sentiment, quote, openie'
# options = {'openie.resolve_coref': True}

# nlp = StanfordCoreNLP(annotators=annotators, options=options)
# document = nlp(text)

# chain = document.coref_chains[0]
# print(chain)

# title = "It's official: Prabowo to join 2019 race"
# text = "Gerindra Party chairman and chief patron Prabowo Subianto accepted his party's mandate to run for the presidency at its national coordination meeting in Hambalang, West Java, on Wednesday.His decision ended speculation over whether he was considering sitting the election out to endorse another candidate in the 2019 race. It also increased the likelihood that the upcoming election sees a rematch between the former commander of the Army's Special Forces and President Joko \"Jokowi\" Widodo.\"As the party's mandatary, as the holder of your mandate [...] I declare that I have submitted and complied with your decision,\" Prabowo said in a video of the closed-door meeting provided by a Gerindra politician.Earlier in the day, the opposition leader made it clear that he would only contest the election if the party built a strong alliance with other parties.Arriving to the meeting's main stage on horseback, to the strains of a brassy rendition of traditional marching song \"The British Grenadiers\", Prabowo cut an imposing figure in Gerindra's trademark white shirt, khaki pants, and black peci fez. \"With all my energy, body and soul, if Gerindra orders me to run in the upcoming presidential election, I am ready to carry out that task,\" he said, according to a Gerindra politician that was present, to the applause of the party members in attendance, who broke out in chants of \"Prabowo, president!\"Prabowo cut off the chanting, however, and asked for patience.\"I said 'if', 'if the party orders me,'\" he said. \"There is one condition. Even if the party orders me [to run], I need the support of friendly parties.\" Over the past few weeks, Prabowo has seemed hesitant over whether to run against President Jokowi again.Maksimus Ramses Lalongkoe, the executive director of the Institute of Indonesian Political Analysis, said Prabowo's apparent hesitation rested mostly on the lack of a clear coalition backing his candidacy.The 2017 Elections Law specifies that political parties seeking to nominate a presidential candidate are required to secure at least 20 percent of seats at the House of Representatives or 25 percent of the popular vote.Gerindra currently holds only 13 percent of House seats and 11.81 percent of the popular vote, which means it needs to join forces with other parties to be able to nominate Prabowo or any other potential candidate.Four parties with significant vote shares have yet to officially back a candidate: the National Mandate Party (PAN), the Prosperous Justice Party (PKS), the National Awakening Party (PKB) and the Democratic Party (PD).PAN and the PKS have worked together with Gerindra in recent times, most notably during the contentious Jakarta gubernatorial election last year. "

# print(nlp.getIdnNER(text))
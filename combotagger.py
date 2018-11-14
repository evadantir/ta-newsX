from nltk.tag import StanfordNERTagger

class NERComboTagger(StanfordNERTagger):

  def __init__(self, *args, **kwargs):
    self.stanford_ner_models = kwargs['stanford_ner_models']
    kwargs.pop("stanford_ner_models")
    super(NERComboTagger,self).__init__(*args, **kwargs)

  @property
  def _cmd(self):
    return ['edu.stanford.nlp.ie.NERClassifierCombiner',
            '-ner.model',
            self.stanford_ner_models,
            '-textFile',
            self._input_file_path,
            '-outputFormat',
            self._FORMAT,
            '-tokenizerFactory',
            'edu.stanford.nlp.process.WhitespaceTokenizer',
            '-tokenizerOptions',
            '\"tokenizeNLs=false\"']

classifier_path2 = "stanford/id-ner-model-id.ser.gz"
classifier_path1 = "stanford/english.muc.7class.distsim.crf.ser.gz"

ner_jar_path = "stanford/stanford-ner.jar"

st = NERComboTagger(classifier_path1,ner_jar_path,stanford_ner_models=classifier_path1+","+classifier_path2)

text="\"I must say that he surprised me,\" said father, Jos, who competed in Formula One from 1994 to 2003. \"I've seen many races of this, and this was incredible. Although Red Bull didn't have the right strategy and were unlucky with the weather, it was almost worth them having a bad stop to see what he did afterwards. It's good for F1, everyone is enthusiastic. What more do you want?\" Equally enraptured was Niki Lauda, the former world champion and Mercedes' non-executive chairman. Congratulating the Verstappen family, he said: \"Max was outstanding with the passes he performed. He did a job that was impressive. I knew the guy was good, but he has proved again to everybody what he can do.\" He will be arrived in Hambalang today"
print (st.tag(text.split(" ")))
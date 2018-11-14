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

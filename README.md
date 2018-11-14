# ta-newsX
Creating my own version of NewsX (Wunderwald, 2011) for my last project

run server : java --add-modules java.se.ee -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
create indonesian NER model: java --add-modules java.se.ee -mx4g -cp stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -prop
prop.txt
combine indonesian model with english model: java --add-modules java.se.ee -mx4g -cp stanford-ner.jar:lib/* edu.stanford.nlp.ie.NERClassifierCombiner -ner.model english.muc.7class.distsim.crf.ser.gz,id-ner-model-id.ser.gz
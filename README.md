# ta-newsX
Creating my own version of NewsX (Wunderwald, 2011) for my last project

* **run server** : java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000 (mine is using Java 8, **if using java 10, use java --add-modules java.se.ee -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000**)
* **create indonesian NER model**: java -mx4g -cp stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -prop
prop.txt
* **combine indonesian model with english model**: java -mx4g -cp stanford-ner.jar:lib/* edu.stanford.nlp.ie.NERClassifierCombiner -ner.model english.muc.7class.distsim.crf.ser.gz,id-ner-model-id.ser.gz
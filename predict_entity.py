from extract_feature import ExtractFeaturesValue

class PredictObject(object):
    def __init__(self):
        self.exf = ExtractFeaturesValue()

    def predictEntity(self,filename,testval):
        model = exf.loadPickle(filename)

        result = model.predict([testval])
        return result

po  = PredictObject()
from sklearn.base import TransformerMixin

from corenlp.client import StanfordNLP

class StanfordDependenciesTransformer(TransformerMixin):
    
    def __init__(self, port=8080):
        self.stanford_nlp = StanfordNLP(port)

    def transform(self, X, **transform_params):
        transformed = []
        for docs in X:
            doc_dependencies = []
            parsed = self.stanford_nlp.parse(docs.lower())
            for sentence_parse in parsed['sentences']:
                for deps in sentence_parse['dependencies']:
                    doc_dependencies.append('_'.join(deps))
            transformed.append(' '.join(doc_dependencies))
        
        return transformed

    def fit(self, X, y=None, **fit_params):
        return self

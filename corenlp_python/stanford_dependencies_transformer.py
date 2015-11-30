from sklearn.base import TransformerMixin
from nltk.tree import ParentedTree

from corenlp.client import StanfordNLP

class StanfordDependenciesTransformer(TransformerMixin):
    
    def __init__(self, stanford_nlp):
        self.stanford_nlp = stanford_nlp
        self.adjTags = ['JJ', 'JJR', 'JJS']
        self.nounTags = ['NN', 'NNS', 'NNP', 'NNPS']
        self.advTags = ['RB', 'RBR', 'RBS']
        self.verbTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

    def transform(self, X, **transform_params):
        transformed = map(self.get_dependency, X)
        #transformed = [self.get_pos(x, self.nounTags) for x in X]
        return transformed
    
    def get_dependency(self, doc):  
        doc_dependencies = []
        parsed = self.stanford_nlp.parse(doc.lower())
        for sentence_parse in parsed['sentences']:
            for deps in sentence_parse['dependencies']:
                doc_dependencies.append('_'.join(deps))
        return ' '.join(doc_dependencies)

    def get_pos(self, doc, posTags):
        pos_words = []
        parsed = self.stanford_nlp.parse(doc.lower())
        for sentence_parse in parsed['sentences']:
            nlpparsetree= sentence_parse['parsetree']
            if '(ROOT' in nlpparsetree:
                parsetree = nlpparsetree[nlpparsetree.index('(ROOT'):]
                tree = ParentedTree.fromstring(parsetree)
                tree.pretty_print()
                for word, pos in tree.pos():
                    if pos in posTags:
                        pos_words.append(word)
        return ' '.join(pos_words) 

    def fit(self, X, y=None, **fit_params):
        return self

if __name__ == '__main__':
    sdt = StanfordDependenciesTransformer()
    transformed = sdt.transform(['I like boats. You like boats.', 'He makes money.'])
    print(transformed)

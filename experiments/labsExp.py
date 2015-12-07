from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier
from model_tester import FeaturePipeline
from baseline_transformer import GetLabsCountDictTransformer, GetLabsLowCountsDictTransformer, GetLabsHighCountsDictTransformer
from sklearn.feature_extraction import DictVectorizer

def get_pipeline():
    features = FeatureUnion([
        ('Labs_Counts', FeaturePipeline([
            ('labs_counts_transformer', GetLabsCountsDictTransformer()),
            ('dict_vectorizer', DictVectorizer())
        ])),
        ('Labs_Low_Counts', FeaturePipeline([
            ('labs_low_counts_transformer', GetLabsLowCountsDictTransformer()),
           ('dict_vectorizer', DictVectorizer())
        ])),
        ('Labs_High_Counts', FeaturePipeline([
            ('labs_high_counts_transformer', GetLabsHighCountsDictTransformer()),
            ('dict_vectorizer', DictVectorizer())
        ])),
    ])

    #clf = LogisticRegression({'C': 1})
    clf = AdaboostClassifier(n_estimators=500)

    return Pipeline([
        'feature_union': features,
        'Classifier': clf
    ])

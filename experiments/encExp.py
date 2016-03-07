from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier
from model_tester import FeaturePipeline
from baseline_transformer import GetLabsCountDictTransformer, GetLabsLowCountsDictTransformer, GetLabsHighCountsDictTransformer
from sklearn.feature_extraction import DictVectorizer

def get_pipeline():
    features = FeatureUnion([
        ('Enc', GetEncountersFeaturesTransformer(100, True)),
    ])

    #clf = LogisticRegression({'C': 1})
    clf = AdaboostClassifier(n_estimators=50)

    return Pipeline([
        'feature_union': features,
        'Classifier': clf
    ])

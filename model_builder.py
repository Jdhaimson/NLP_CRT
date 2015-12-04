from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier
from sklearn.pipeline import FeatureUnion, Pipeline
from decision_model import ClinicalDecisionModel
from model_tester import FeaturePipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from baseline_transformer import GetConcatenatedNotesTransformer, GetLatestNotesTransformer, GetEncountersFeaturesTransformer, GetLabsCountsDictTransformer, GetLabsLowCountsDictTransformer, GetLabsHighCountsDictTransformer, GetLabsLatestHighDictTransformer, GetLabsLatestLowDictTransformer, GetLabsHistoryDictTransformer
from icd_transformer import ICD9_Transformer
from value_extractor_transformer import EFTransformer, LBBBTransformer, SinusRhythmTransformer, QRSTransformer, NYHATransformer, NICMTransformer

regex_baseline = {  'method' : 'adaboost',
                    'model_args' : {'n_estimators' : 500}
                    'features' : {  'all_ef' :  (EFTransformer, {'method' = 'all', 'num_horizon' = 1}),
                                    'mean_ef' : (EFTransformer, {'method' = 'mean', 'num_horizon' = 5}),
                                    'max_ef' :  (EFTransformer, {'method' = 'max', 'num_horizon' = 5}),
                                    'LBBB':     (LBBBTransformer, {'time_horizon' = 30*3}),
                                    'SR':       (SinusRhythmTransformer, {'time_horizon' = 30*3}),
                                    'NYHA':     (NYHATransformer, {'time_horizon' = 30*3}),
                                    'NICM':     (NICMTransformer, {'time_horizon' = 30*3}),
                                    'all_qrs':  (QRSTransformer, {'method' = 'all', 'num_horizon' = 1})
                                 }
                 }

    

def build_model(control, method = None, model_args = None, features = None, features_add = None, features_change = None, features_remove = None):

    if method == None:
        method = control['method']
        method_diff = False
    else: 
        method_diff = not method == control['method']

    if model_args == None and method_diff:
        model_args = dict()
        args_diff = True
    elif model_args == None:
        model_args = control['model_args']
        args_diff = False
    else:
        args_diff = True

    #keep in mind that features are a dictionary of tuples, e.g. 'name': (transformer_class, transformer_args)
    feature_diff = {'+': [], '-' : []}
    if features == None:
        features = control['features']
        if features_remove != None:
            feature_diff['-'] += features_remove
            for remove in features_remove:
                if remove in features:
                    features.pop(remove)
        if features_change != None:
            for change in features_change:#not robust to handle changing FeaturePipeline
                if change[0] in features:
                    transformer, args = features[change[0]]
                    feature_diff['-'] += [(change[0], args)]
                    args = change_args(transformer, args, change[1])
                    features[change[0]] = (transformer, args)
                    feature_diff['+'] += [(change[0], args)]
        if features_add != None:
            for add in features_add:
                features[add[0]] = (add[1], add[2])
            feature_diff['+'] += features_add

    if method in ['clinical', 'decision', 'cdm', 'clinical decision model']:
        is_regression = False
        clf = ClinicalDecisionModel()
        model = clf
    else:
        if method in ['logistic regression', 'lr', 'logitr', 'logistic']:
            is_regression = False
            clf = LogisticRegression(**model_args)
        elif method in ['svm']:
            is_regression = False
            clf = SVC(**model_args)
        elif method in ['boosting', 'adaboost']:
            is_regression = False
            clf = AdaBoostClassifier(**model_args)
        else:
            raise ValueError("'" + method + "' is not a supported classification method")

        transformer_list = []
        for feature_name in features:
            transformer_list += [build_transformer(feature_name, features[feature_name])]
        model =  Pipeline([
                ('feature_union', FeatureUnion(transformer_list)),
                ('Classifier', clf)
            ])
    return model

def build_transformer(transformer_name, transformer_values):
    if issubclass(transformer_values[0], Pipeline):
        steps = [build_transformer(step[0], (step[1], step[2])) for step in transformer_values]
        transformer = transformer_values[0](steps))
    else:
        transformer = transformer_values[0](**transformer_values[1])
    return (transformer_name, transformer)

def change_args(transformer, args, params):
    for param in params:
        if issubclass(transformer, Pipeline):
            args[param] = (args[param][0], args[param][1], change_args(args[param][1], args[param][2], params[param]))
        else:
            args[param] = params[param]
    return args

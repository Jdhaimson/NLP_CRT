from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.pipeline import FeatureUnion, Pipeline
from decision_model import ClinicalDecisionModel
from model_tester import FeaturePipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from baseline_transformer import GetConcatenatedNotesTransformer, GetLatestNotesTransformer, GetEncountersFeaturesTransformer, GetLabsCountsDictTransformer, GetLabsLowCountsDictTransformer, GetLabsHighCountsDictTransformer, GetLabsLatestHighDictTransformer, GetLabsLatestLowDictTransformer, GetLabsHistoryDictTransformer
from icd_transformer import ICD9_Transformer
from value_extractor_transformer import EFTransformer, LBBBTransformer, SinusRhythmTransformer, QRSTransformer, NYHATransformer, NICMTransformer
import logging

#from neural_network import NeuralNetwork
logger = logging.getLogger("DaemonLog")

#This should make adding transformers easier. You could add a transformer like
# features_add = [baseline_features[x] for x in ['Labs_Latest_High', 'Car_tfidf']

control_features = {   'all_ef' :  ('all_ef', EFTransformer, {'method' : 'all', 'num_horizon' : 1}),
                        'mean_ef' : ('mean_ef', EFTransformer, {'method' : 'mean', 'num_horizon' : 5}),
                        'max_ef' :  ('max_ef', EFTransformer, {'method' : 'max', 'num_horizon' : 5}),
                        'lbbb':     ('lbbb', LBBBTransformer, {'time_horizon' : 30*3}),
                        'sr':       ('sr', SinusRhythmTransformer, {'time_horizon' : 30*3}),
                        'nyha':     ('nyha', NYHATransformer, {'time_horizon' : 30*3}),
                        'nicm':     ('nicm', NICMTransformer, {'time_horizon' : 30*3}),
                        'all_qrs':  ('all_qrs', QRSTransformer, {'method' : 'all', 'num_horizon' : 1}),
                        'icd9':     ('icd9', ICD9_Transformer, {}),
                        'car_tfidf':('car_tfidf', FeaturePipeline, [('notes_car', GetConcatenatedNotesTransformer, {'note_type' : 'Car'}),
                                                                    ('tfidf_car', TfidfTransformer, {})]),    
                        'lno_tfidf':('lno_tfidf', FeaturePipeline, [('notes_lno', GetConcatenatedNotesTransformer, {'note_type' : 'Lno'}),
                                                                    ('tfidf_lno', TfidfTransformer, {})]),
                        'car_trigram':('car_ngram', FeaturePipeline, [('notes_car', GetConcatenatedNotesTransformer, {'note_type' : 'Car'}),
                                                                    ('ngram_car', CountVectorizer, {'ngram_range' : (3, 3), 'min_df' : .05})]),    
                        'lno_trigram':('lno_ngram', FeaturePipeline, [('notes_lno', GetConcatenatedNotesTransformer, {'note_type' : 'Lno'}),
                                                                    ('ngram_lno', CountVectorizer, {'ngram_range' : (3, 3), 'min_df' : .05})]),
                        'car_bigram':('car_ngram', FeaturePipeline, [('notes_car', GetConcatenatedNotesTransformer, {'note_type' : 'Car'}),
                                                                    ('ngram_car', CountVectorizer, {'ngram_range' : (2, 2), 'min_df' : .05})]),    
                        'lno_bigram':('lno_ngram', FeaturePipeline, [('notes_lno', GetConcatenatedNotesTransformer, {'note_type' : 'Lno'}),
                                                                    ('ngram_lno', CountVectorizer, {'ngram_range' : (2, 2), 'min_df' : .05})]),
                        'enc':      ('enc', GetEncountersFeaturesTransformer, {'max_encounters' : 5}),
                        'lab_all' : ('lab_all', FeaturePipeline, [('lab_to_dict', GetLabsCountsDictTransformer, {}), ('dict_to_vect', DictVectorizer, {})]),                         
                        'lab_low' : ('lab_low', FeaturePipeline, [('lab_to_dict', GetLabsLowCountsDictTransformer, {}), ('dict_to_vect', DictVectorizer, {})]),                         
                        'lab_high' : ('lab_high', FeaturePipeline, [('lab_to_dict', GetLabsHighCountsDictTransformer, {}), ('dict_to_vect', DictVectorizer, {})]),                         
                        'lab_low_recent' : ('lab_low_recent', FeaturePipeline, [('lab_to_dict', GetLabsLatestLowDictTransformer, {}), ('dict_to_vect', DictVectorizer, {})]),                         
                        'lab_high_recent' : ('lab_high_recent', FeaturePipeline, [('lab_to_dict', GetLabsLatestHighDictTransformer, {}), ('dict_to_vect', DictVectorizer, {})]),                         
                        'lab_hist' : ('lab_hist', FeaturePipeline, [('lab_to_dict', GetLabsHistoryDictTransformer, {'time_thresholds_months' : [1]}), ('dict_to_vect', DictVectorizer, {})]),                         
                     }  

control_groups = { 'regex' : ['all_ef', 'mean_ef', 'max_ef', 'lbbb', 'sr', 'nyha', 'nicm', 'all_qrs'],
                   'structured_only' : ['icd9', 'enc', 'lab_all', 'lab_low', 'lab_high', 'lab_low_recent', 'lab_high_recent', 'lab_hist'],
                   'notes_tfidf' : ['car_tfidf', 'lno_tfidf'],
                   'labs':  ['lab_all', 'lab_low', 'lab_high', 'lab_low_recent', 'lab_high_recent', 'lab_hist']
                 }

#These are empty, but might be useful
adaboost_baseline = {  'method' : 'adaboost', 'model_args' : {'n_estimators' : 500}, 'features' : {} } 
lr_baseline = {  'method' : 'lr', 'model_args' : {'C' : 1}, 'features' : {} } 
#nn_baseline = { 'method' : 'nn',  'model_args' : {'layers' : [(10, 'logistic'), (None, 'softmax')], 'obj_fun' : 'maxent'}, 'features' : {}}

regex_baseline = {  'method' : 'adaboost',
                    'model_args' : {'n_estimators' : 500},
                    'features' : {  'all_ef' :  (EFTransformer, {'method' : 'all', 'num_horizon' : 1}),
                                    'mean_ef' : (EFTransformer, {'method' : 'mean', 'num_horizon' : 5}),
                                    'max_ef' :  (EFTransformer, {'method' : 'max', 'num_horizon' : 5}),
                                    'lbbb':     (LBBBTransformer, {'time_horizon' : 30*3}),
                                    'sr':       (SinusRhythmTransformer, {'time_horizon' : 30*3}),
                                    'nyha':     (NYHATransformer, {'time_horizon' : 30*3}),
                                    'nicm':     (NICMTransformer, {'time_horizon' : 30*3}),
                                    'all_qrs':  (QRSTransformer, {'method' : 'all', 'num_horizon' : 1})
                                 }
                 }



##################
# control : this is the pre-loaded set of method, model_args, and features. If any of the below are none, will default to these
#
# method : this is a string that is interpreted as a switch statement below
# model_args : the **kwargs dict that are passed to your model, e.g. AdaBoostClassifier(**model_args)    
# features: this ia a dictionary of transformer name : (transformer class, transformer args)
#           eventually this will become a tuple (name, class(**args)) to go into a FeatureUnion
#           However, I have included functionality to handle FeaturePipelines. In this one case, 
#           the transformer args are a list of (name, class, args) triples. For example:
#           'Car' : (FeaturePipeline, [('car_notes', CarNotesTransformer, {'horizon' :3}), ('tfidf', TfidfTransformer, {})])
#
#   ADD     For features_add, you must give a triple (name, class, args). You can write this yourself, or reference the lists above
#               features_add = control_groups['labs'] + [control_features[x] for x in ['icd9', 'lbbb']]
#
#   CHANGE  Besides making features, you can also change them. I thought this was an inutitive option. The simplest change
#           just calls the transformer by name and assigns a new value to one of the args. For example:
#               features_change = {'ef_all' : {'num_horizon' : 10, 'time_horizon' : 30*4}}
#           But you can also change thing inside feature pipelines. For example, to change the feature above:
#               features_change = {('Car', 0) : {'horizon' : 10}}
#   
#   REMOVE  Lastly, you can remove features. This is easy. No error will be thrown if you remove a feature not included.
#               features_remove = ['icd9', 'max_ef', 'lab_high']
#               features_remove = control_groups['regex'] + control_groups['labs']
################

def build_model(control, method = None, model_args = None, features = None, features_add = None, features_change = None, features_remove = None):

    #Modify method
    if method == None:
        method = control['method']
        method_diff = False
    else: 
        model_args = {}
        method_diff = not method == control['method']

    #Modify model args
    if model_args == None and method_diff:
        model_args = dict()
        args_diff = True
    elif model_args == None:
        model_args = control['model_args']
        args_diff = False
    else:
        args_diff = True

    #Modify the model features
    #keep in mind that features are a dictionary of tuples, e.g. 'name': (transformer_class, transformer_args)
    feature_diff = {'+': [], '-' : []}
    if features == None:
        features = control['features']
        #add features
        if features_add != None:
            for add in features_add:
                features[add[0]] = (add[1], add[2])
            feature_diff['+'] += features_add
        #remove features
        if features_remove != None:
            feature_diff['-'] += features_remove
            for remove in features_remove:
                if remove in features:
                    features.pop(remove)
        #change features
        if features_change != None:
            for change in features_change:#not robust to handle changing FeaturePipeline
                if change[0] in features:
                    transformer, args = features[change[0]]
                    feature_diff['-'] += [(change[0], args)]
                    args = change_args(transformer, args, change[1]) #recursive change call
                    features[change[0]] = (transformer, args)
                    feature_diff['+'] += [(change[0], args)]

    #select classifier and build pipeline
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
        elif method in ['decision tree', 'dtree']:
            is_regression = False
            clf = DecisionTreeClassifier(**model_args)
        elif method in ['nn', 'neural', 'net', 'neuralnet', 'network']:
            is_regression = False
            clf = NeuralNetwork(**model_args)
        else:
            raise ValueError("'" + method + "' is not a supported classification method")

        #build the transformers
        transformer_list = []
        for feature_name in features:
            transformer_list += [build_transformer(feature_name, features[feature_name])] #recursive build call

        #assemble pipeline
        model =  Pipeline([
                ('feature_union', FeatureUnion(transformer_list)),
                ('Classifier', clf)
            ])
    return model

def build_transformer(transformer_name, transformer_values):
    if issubclass(transformer_values[0], Pipeline):
        steps = [build_transformer(step[0], (step[1], step[2])) for step in transformer_values[1]]
        transformer = transformer_values[0](steps)
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

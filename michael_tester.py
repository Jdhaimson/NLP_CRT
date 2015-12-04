import sys
import cProfile

from model_tester import FeaturePipeline, test_model
from sklearn.pipeline import FeatureUnion
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from baseline_transformer import GetConcatenatedNotesTransformer, GetLatestNotesTransformer, GetEncountersFeaturesTransformer, GetLabsCountsDictTransformer, GetLabsLowCountsDictTransformer, GetLabsHighCountsDictTransformer, GetLabsLatestHighDictTransformer, GetLabsLatestLowDictTransformer, GetLabsHistoryDictTransformer
from extract_data import get_doc_rel_dates, get_operation_date, get_ef_values
from extract_data import get_operation_date,  is_note_doc, get_date_key
from icd_transformer import ICD9_Transformer
from value_extractor_transformer import EFTransformer, LBBBTransformer, SinusRhythmTransformer, QRSTransformer, NYHATransformer, NICMTransformer
from language_processing import parse_date 

def main():

    transformer_list = []

    regex_features = True
    icd9_features = False
    labs_features = False
    text_features = False

    if regex_features:
        transformer_list += [ 
                    ('EF', EFTransformer('all', 1, None)),
                    ('EF', EFTransformer('mean', 5, None)),
                    ('EF', EFTransformer('max', 5, None)),
                    ('LBBB', LBBBTransformer(30*3)),
                    ('SR', SinusRhythmTransformer(30*3)),
                    ('NYHA', NYHATransformer(30*3)),
                    ('NICM', NICMTransformer(30*3)),
                    ('QRS', QRSTransformer('all', 1, None)),
                    ('QRS', QRSTransformer('mean', 5, None)),
                ]
    if icd9_features:
        transformer_list += [
                    ('Dia', ICD9_Transformer())
                ]
    if text_features:
        transformer_list += [
                    ('Car', FeaturePipeline([
                        ('notes_transformer_car', GetConcatenatedNotesTransformer('Car')),
                        ('tfidf', TfidfTransformer())
                    ])),
                    ('Lno', FeaturePipeline([
                       ('notes_transformer_lno', GetConcatenatedNotesTransformer('Lno')),
                       ('tfidf', TfidfTransformer)
                    ]))
                ]
    if labs_features:
        transformer_list += [
                    ('Enc', GetEncountersFeaturesTransformer(5)),
                    ('Labs_Counts',FeaturePipeline([
                        ('labs_counts_transformer', GetLabsCountsDictTransformer()),
                        ('dict_vectorizer', DictVectorizer())
                    ])),
                    ('Labs_Low_Counts',FeaturePipeline([
                        ('labs_low_counts_transformer', GetLabsLowCountsDictTransformer()),
                       ('dict_vectorizer', DictVectorizer())
                    ])),
                    ('Labs_High_Counts', FeaturePipeline([
                        ('labs_high_counts_transformer', GetLabsHighCountsDictTransformer()),
                        ('dict_vectorizer', DictVectorizer())
                    ])),
                    ('Labs_Latest_Low', FeaturePipeline([
                        ('labs_latest_low_transformer', GetLabsLatestLowDictTransformer()),
                        ('dict_vectorizer', DictVectorizer())
                    ])),
                    ('Labs_Latest_High',FeaturePipeline([
                        ('labs_latest_high_transformer', GetLabsLatestHighDictTransformer()),
                        ('dict_vectorizer', DictVectorizer())
                    ])),
                    ('Labs_History', FeaturePipeline([
                        ('labs_history_transformer', GetLabsHistoryDictTransformer([1])),
                        ('dict_vectorizer', DictVectorizer())
                    ]))
                ]

    
    features = FeatureUnion(transformer_list)

    if len(sys.argv) > 1 and unicode(sys.argv[1]).isnumeric():
        data_size = min(int(sys.argv[1]), 906)
    else:
        data_size = 25

    if len(sys.argv) > 2 and unicode(sys.argv[2]).isnumeric():
        num_cv_splits = int(sys.argv[2])
    else:
        num_cv_splits = 5

    print "Data size: " + str(data_size)
    print "CV splits: " + str(num_cv_splits)

    if len(sys.argv) > 3:
        method = sys.argv[3]
    else:
        method = 'adaboost'

    #method = 'lr'
    #method = 'svm'
    method = 'adaboost'
    #method = 'cdm'

    model_args = dict()
    if method in ['lr', 'svm']:
        if len(sys.argv) > 4 and unicode(sys.argv[4]).isnumeric():
            model_args['regularization'] = float(sys.argv[4])
        else:
            model_args['regularization'] = 0.
    if method == 'adaboost':
        if len(sys.argv) > 4 and unicode(sys.argv[4]).isnumeric():
            model_args['n_estimators'] = int(sys.argv[4])
        else:
            model_args['n_estimators'] = 50
        

    show_progress = True
    print 'Method:', method
    test_model(features, data_size, num_cv_splits, method, show_progress, model_args)

if __name__ == '__main__':
    main()

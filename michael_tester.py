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
from value_extractor_transformer import EFTransformer, LBBBTransformer, SinusRhythmTransformer, QRSTransformer
from language_processing import parse_date 

def main():
    features = FeatureUnion([
               # ('Dia', icd9 ),
                ('EF', EFTransformer('all', 1, None)),
                ('EF', EFTransformer('mean', 5, None)),
                ('EF', EFTransformer('max', 5, None)),
                ('LBBB', LBBBTransformer()),
                ('SR', SinusRhythmTransformer()),
               # ('QRS', QRSTransformer('all', 1, None)),#Bugs with QRS
               # ('Car', FeaturePipeline([
               #     ('notes_transformer_car', GetConcatenatedNotesTransformer('Car')),
               #     ('tfidf', TfidfTransformer())
               # ])),
               #('Lno', FeaturePipeline([
               #    ('notes_transformer_lno', GetConcatenatedNotesTransformer('Lno')),
               #     ('tfidf', TfidfTransformer)
               # ])),
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
                ])),
            ])


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
    method = 'lr'
    #method = 'svm'
    method = 'adaboost'

    model_args = dict()
    if method in ['lr', 'svm']:
        if len(sys.argv) > 3 and unicode(sys.argv[3]).isnumeric():
            model_args['regularization'] = float(sys.argv[3])
        else:
            model_args['regularization'] = 0.
    if method == 'adaboost':
        if len(sys.argv) > 3 and unicode(sys.argv[3]).isnumeric():
            model_args['n_estimators'] = int(sys.argv[3])
        else:
            model_args['n_estimators'] = 50
        

    show_progress = True

    test_model(features, data_size, num_cv_splits, method, show_progress, model_args)

if __name__ == '__main__':
    main()

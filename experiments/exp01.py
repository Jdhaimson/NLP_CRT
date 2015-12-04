from sklearn.pipeline import FeatureUnion

from doc2vec_transformer import Doc2Vec_Note_Transformer

def get_pipeline():
    features = FeatureUnion([
               # ('Dia', icd9 ),
                #('EF', EFTransformer('all', 1, None)),
                #('EF', EFTransformer('mean', 5, None)),
                #('EF', EFTransformer('max', 5, None)),
                #('LBBB', LBBBTransformer()),
                #('SR', SinusRhythmTransformer()),
                ('Car_Doc2Vec', Doc2Vec_Note_Transformer('Car', '/home/ubuntu/josh_project/doc2vec_models/car_1.model', 10))
               # ('QRS', QRSTransformer('all', 1, None)),#Bugs with QRS
                #('Car', FeaturePipeline([
                #    ('notes_transformer_car', GetConcatenatedNotesTransformer('Car')),
                #    ('tfidf', car_tfidf)
                #])),
                #('Lno', FeaturePipeline([
                #    ('notes_transformer_lno', GetConcatenatedNotesTransformer('Lno')),
                #    ('tfidf', lno_tfidf)
                #])),
                #('Enc', enc),
                #('Labs_Counts',FeaturePipeline([
                #    ('labs_counts_transformer', GetLabsCountsDictTransformer()),
                #    ('dict_vectorizer', DictVectorizer())
                #])),
                #('Labs_Low_Counts',FeaturePipeline([
                #    ('labs_low_counts_transformer', GetLabsLowCountsDictTransformer()),
                #    ('dict_vectorizer', DictVectorizer())
                #])),
                #('Labs_High_Counts', FeaturePipeline([
                #    ('labs_high_counts_transformer', GetLabsHighCountsDictTransformer()),
                #    ('dict_vectorizer', DictVectorizer())
                #])),
                #('Labs_Latest_Low', FeaturePipeline([
                #    ('labs_latest_low_transformer', GetLabsLatestLowDictTransformer()),
                #    ('dict_vectorizer', DictVectorizer())
                #])),
                #('Labs_Latest_High',FeaturePipeline([
                #    ('labs_latest_high_transformer', GetLabsLatestHighDictTransformer()),
                #    ('dict_vectorizer', DictVectorizer())
                #])),
               # ('Labs_History', FeaturePipeline([
               #     ('labs_history_transformer', GetLabsHistoryDictTransformer([1])),
               #     ('dict_vectorizer', DictVectorizer())
               # ])),
            ])

    return features

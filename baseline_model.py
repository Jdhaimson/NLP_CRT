import re

import numpy as np
import cProfile
from sklearn.base import TransformerMixin
from sklearn.cross_validation import train_test_split
from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer 
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score, precision_score, recall_score, f1_score
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import SVC

from baseline_transformer import (GetConcatenatedNotesTransformer, 
    GetLatestNotesTransformer, GetEncountersFeaturesTransformer, 
    GetLabsCountsDictTransformer, GetLabsLowCountsDictTransformer, 
    GetLabsHighCountsDictTransformer, GetLabsLatestHighDictTransformer, 
    GetLabsLatestLowDictTransformer, GetLabsHistoryDictTransformer,
    MultiDocTfidfTransformer)
from extract_data import get_doc_rel_dates, get_operation_date, get_ef_values
from extract_data import get_operation_date,  is_note_doc, get_date_key
from icd_transformer import ICD9_Transformer
from value_extractor_transformer import EFTransformer, LBBBTransformer
from language_processing import parse_date 
from loader import get_data


def get_preprocessed_patients():
    patient_nums = range(906)
    patient_nums = range(15)
    patients_out = []
    delta_efs_out = []
    for i in patient_nums:
        if i%100 == 0:
            print str(i) + '/' + str(patient_nums[-1])
        patient_data = get_data([i])[0]
        if patient_data is not None:
            ef_delta = get_ef_delta(patient_data)
            if ef_delta is not None:
                patients_out.append(patient_data['NEW_EMPI'])
                delta_efs_out.append(ef_delta)
    return patients_out, delta_efs_out


# 6 month followup is best, change above code
def change_ef_values_to_categories(ef_values):
    output = []

    for value in ef_values:
        if value < 5:
            output.append(0)
        else:
            output.append(1)
        '''
        if value <-2:
            output.append("reduction")
        elif value < 5:
            output.append("non-responder")
        elif value < 15:
            output.append("responder")
        else:
            output.append("super-responder")
        '''
    return output
            
def get_ef_delta(patient_data):
    after_threshold = 6*30
    ef_values = get_ef_values(patient_data)
    sorted_ef = sorted(ef_values)
    before = None
    after = None
    dist_from_thresh = float('inf')
    for (rel_date, ef_value) in sorted_ef:
        if rel_date <= 0:
            before = ef_value
        else:
            dist = abs(rel_date - after_threshold)
            if dist < dist_from_thresh:
                after = ef_value
                dist_from_thresh = dist

    if before is not None and after is not None:
        return after - before
    else:
        return None


class PrintTransformer(TransformerMixin):
    def fit(self, X, y=None, **fit_params):
        return self
    def transform(self, X, **transform_params):
        print len(X)
        print X[0].shape
        return X

class DenseArrayTransformer(TransformerMixin):
    def fit(self, X, y=None, **fit_params):
        return self
    def transform(self, X, **transform_params):
        return X.toarray()


class FeaturePipeline(Pipeline):

    def get_feature_names(self):
        return self.steps[-1][1].get_feature_names()

def main():
    is_regression = True

    print 'Preprocessing...'
    X, Y = get_preprocessed_patients()
    is_regression = False
    Y = change_ef_values_to_categories(Y)
    print str(len(X)) + " patients in dataset"
    if not is_regression:
        counts = {}
        for y in Y:
            if y not in counts:
                counts[y] = 0
            counts[y] += 1
        print "Summary:"
        print counts
        
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = .33)

    n_notes = 10
    features = FeatureUnion([
            ('Dia', ICD9_Transformer()),
            ('EF', EFTransformer('all', 5, None)),
            ('LBBB', LBBBTransformer()),
            ('Enc', GetEncountersFeaturesTransformer(10)),
            ('Car', FeaturePipeline([
                #('notes_transformer_car', GetConcatenatedNotesTransformer('Car')),
                #('tfidf', TfidfVectorizer())
                ('notes_transformer_car', GetLatestNotesTransformer('Car', n_notes)),
                ('tfidf', MultiDocTfidfTransformer()),
            ])),
            ('Lno', FeaturePipeline([
                #('notes_transformer_lno', GetConcatenatedNotesTransformer('Lno')),
                #('tfidf', TfidfVectorizer())
                ('notes_transformer_lno', GetLatestNotesTransformer('Lno', n_notes)),
                ('tfidf', MultiDocTfidfTransformer())
            ])),
            ('Labs_History', FeaturePipeline([
                ('labs_history_transformer', GetLabsHistoryDictTransformer([1])),
                ('dict_vectorizer', DictVectorizer())
            ])),
        ])

    '''
            # Old labs features
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
    '''


    logr = LogisticRegression()
    pipeline =  Pipeline([
        ('feature_union', features),
        #('densify', DenseArrayTransformer()),
        #('ipca', IncrementalPCA(n_components=1000, batch_size=10)), 
        #('pca', PCA(1000)), 
        #('print', PrintTransformer()),
        ('logistic_regression', logr)
        #('svm', SVC(kernel='poly'))
    ])

    print "Training..."
    pipeline.fit(X_train, Y_train)

    # Print top 100 features
    try:
        column_names = features.get_feature_names()
        print "Number of column names: " + str( len(column_names))
        if len(column_names) == logr.coef_.shape[1]:
            Z = zip(column_names, logr.coef_[0])
            Z.sort(key = lambda x: abs(x[1]), reverse = True)
            print "100 biggest theta components:"
            print
            for z in Z[:100]:
                print z[1], "\t", z[0]
    except Exception as e:
        print "Feature name extraction failed"
        print e


    print "Predicting..."
    Y_predict = pipeline.predict(X_test)

    print "Evaluating..."
    for i in range(min(20, len(Y_test), len(Y_predict))):
        print "Actual: " + str(Y_test[i]) + ", Predicted: " + str(Y_predict[i])
    if is_regression:
        mse = mean_squared_error(Y_test, Y_predict)
        print "Mean Squared Error: " + str(mse)
        r2 = r2_score(Y_test, Y_predict)
        print "R2 Score: " + str(r2)
    else:
        precision = precision_score(Y_test, Y_predict)
        print "Precision: " + str(precision)
        recall = recall_score(Y_test, Y_predict)
        print "Recall: " + str(recall)
        f1 = f1_score(Y_test, Y_predict)
        print "F1 Score: " + str(f1)
        accuracy = accuracy_score(Y_test, Y_predict)
        print "Accuracy: " + str(accuracy)

if __name__ == "__main__":
    main()
    #cProfile.run('main()')

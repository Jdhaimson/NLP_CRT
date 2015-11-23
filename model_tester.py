import re
import sys

import numpy as np
import cProfile
from sklearn.base import TransformerMixin
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score, precision_score, recall_score, f1_score
from sklearn.pipeline import FeatureUnion, Pipeline

from extract_data import get_doc_rel_dates, get_operation_date, get_ef_values
from extract_data import get_operation_date,  is_note_doc, get_date_key
from language_processing import parse_date 
from loader import get_data


def get_preprocessed_patients(sample_size = 25):
    patients_out = []
    delta_efs_out = []
    patient_nums = range(sample_size)
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
        print X.shape
        print X[0].shape
        return X

class FeaturePipeline(Pipeline):

    def get_feature_names(self):
        return self.steps[-1][1].get_feature_names()


def display_summary(name, values):
    print name 
    print "\tmean:\t", 1.* sum(values) / len(values)
    print "\tmin:\t", min(values)
    print "\tmax:\t", max(values)


def test_model(features, data_size = 25, num_cv_splits = 5, method = 'logistic regression', show_progress = True):

    if method in ['logistic regression', 'lr', 'logitr', 'logistic']:
        is_regression = False
        clf = LogisticRegression()
    elif method in ['svm']:
        is_regression = False
        clf = SVC()
    else:
        raise ValueError("'" + method + "' is not a supported classification method")

    print 'Preprocessing...'
    X, Y = get_preprocessed_patients(data_size)
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
    
    pipeline =  Pipeline([
        ('feature_union', features),
        #('pca', sklearn.decomposition.PCA(1000)), 
        #('print', PrintTransformer()),
        ('Classifier', clf)
    ])

    print "Train, Predict and Evaluate CV"

    mse = []
    r2 = []
    precision = []
    recall = []
    f1 = []
    accuracy = []    

    for cv_run in range(num_cv_splits):

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = .33)
        pipeline.fit(X_train, Y_train)
        Y_predict = pipeline.predict(X_test)

        if is_regression:
            mse += [mean_squared_error(Y_test, Y_predict)]
            r2 += [r2_score(Y_test, Y_predict)]
            if show_progress:
                print "CV Split #" + str(cv_run + 1)
                print "\tMean Squared Error: ", mse[-1]
                print "\tR2 Score: ", r2[-1]
        else:
            precision += [precision_score(Y_test, Y_predict)]
            recall += [recall_score(Y_test, Y_predict)]
            f1 += [f1_score(Y_test, Y_predict)]
            accuracy += [accuracy_score(Y_test, Y_predict)]
            if show_progress:
                print "CV Split #" + str(cv_run + 1)
                print "\tPrecision: " + str(precision[-1])
                print "\tRecall: " + str(recall[-1])
                print "\tF1 Score: " + str(f1[-1])
                print "\tAccuracy: " + str(accuracy[-1])
    print "\n---------------------------------------"
    print
    print "Overall (" + str(num_cv_splits) +  " cv cuts)"
    print
    if is_regression:
        display_summary("Mean Squared Error", mse)
        display_summary("R2 Score", r2)
    else:
        display_summary("Precision", precision)
        display_summary("Recall", recall)
        display_summary("F1 Score", f1)
        display_summary("Accuracy", accuracy)

    print 
    try:
        column_names = features.get_feature_names()
        print "Number of column names: " + str( len(column_names))
        if len(column_names) == clf.coef_.shape[1]:
            Z = zip(column_names, clf.coef_[0])
            Z.sort(key = lambda x: abs(x[1]), reverse = True)
            print "100 biggest theta components of last CV run:"
            print
            for z in Z[:100]:
                print z[1], "\t", z[0]
    except Exception as e:
        print "Feature name extraction failed"
        print e
 

if __name__ == "__main__":
    main()
    #cProfile.run('main()')

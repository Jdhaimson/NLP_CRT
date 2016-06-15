import logging
import os
import re
import sys
import json

import numpy as np
import cProfile
from sklearn.base import TransformerMixin
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.pipeline import FeatureUnion, Pipeline

from extract_data import get_doc_rel_dates, get_operation_date, get_ef_values
from extract_data import get_operation_date,  is_note_doc, get_date_key
from language_processing import parse_date 
from loader import get_data
from decision_model import ClinicalDecisionModel
from mix_of_exp import MixtureOfExperts
logger = logging.getLogger("DaemonLog")

def _specificity_score(y,y_hat):
    mc = confusion_matrix(y,y_hat)
    return float(mc[0,0])/np.sum(mc[0,:])

def get_preprocessed_patients(sample_size = 25, rebuild_cache=False):
    cache_file = '/home/ubuntu/project/data/patient_cache.json'
    
    # Build cache
    if not os.path.isfile(cache_file) or rebuild_cache:
        patients_out = []
        delta_efs_out = []
        patient_nums = range(906)
        for i in patient_nums:
            if i%100 == 0:
                logger.info(str(i) + '/' + str(patient_nums[-1]))
            patient_data = get_data([i])[0]
            if patient_data is not None:
                ef_delta = get_ef_delta(patient_data)
                if ef_delta is not None:
                    patients_out.append(patient_data['NEW_EMPI'])
                    delta_efs_out.append(ef_delta)
        with open(cache_file, 'w') as cache:
            cache_obj = {
                'patients': patients_out,
                'delta_efs': delta_efs_out
            }
            json.dump(cache_obj, cache)

    # Load from cache
    with open(cache_file, 'r') as f:
        cached = json.load(f)
    n = min(sample_size, len(cached['patients']))
    return cached['patients'][:n], cached['delta_efs'][:n]


def change_ef_values_to_categories(ef_values):
    output = []

    for value in ef_values:
        if value < 5:
            output.append(1)
        else:
            output.append(0)
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
    after_threshold = 12*30 #traub: changed to 12mo optimal measurement
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
        logger.info(X.shape)
        print X[0].shape
        return X

class FeaturePipeline(Pipeline):

    def get_feature_names(self):
        return self.steps[-1][1].get_feature_names()


def display_summary(name, values):
    logger.info(name)
    logger.info("\tmean:\t", 1.* sum(values) / len(values))
    logger.info("\tmin:\t", min(values))
    logger.info("\tmax:\t", max(values))

def get_mu_std(values):
    mu = 1. * sum(values) / len(values)
    sq_dev = [(x - mu)**2 for x in values]
    std = (sum(sq_dev) / len(values))**.5
    return (mu, std)

############################################
# Inputs:
#       clf: some model object with a fit(X,y) and predict(X) function
#       data_size: num patients
#       num_cv_splits: number of cv runs
#       status_file: opened status file (status_file.write("hello") should work)
# Outputs: a dictionary with the following
#       precision_mean(_std)
#       recall_mean(_std)
#       f1_mean(_std)
#       accuracy_mean(_std)
#       important_features: a string of the most 100 important features 
############################################

def execute_test(clf, data_size, num_cv_splits): 
    
    logger.info('Preprocessing...')
    X, Y = get_preprocessed_patients(data_size)
    Y = change_ef_values_to_categories(Y)

    logger.info(str(len(X)) + " patients in dataset")
    
    counts = {}
    for y in Y:
        if y not in counts:
            counts[y] = 0
        counts[y] += 1
    logger.info("Summary:")
    logger.info(counts)

    precision = []
    precision_train = []
    recall = []
    recall_train = []
    f1 = []
    specificity = []
    f1_train = []
    accuracy = []    
    accuracy_train = []    

    logger.info("Beginning runs")
    
    for cv_run in range(int(num_cv_splits)):

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = .33)
        logger.info("fitting " + str(len(X_train)) + " patients...")
        if type(clf.steps[-1][1]) == MixtureOfExperts:
            logger.info("alex debug, mixture of experts")
            print "I'm an expert!"
            Y_real = np.zeros((len(Y_train), 2))
            for i in range(len(Y_train)):    
                Y_real[i, Y_train[i]] = 1
            Y_train = Y_real
        print Y_train
        logger.info("alex debug, fitting")
        clf.fit(X_train, Y_train)
        logger.info("predicting")
        Y_predict = clf.predict(X_test)
        logger.info("alex debug, done predicting")
        Y_train_predict = clf.predict(X_train)
        print Y_test
        print Y_predict
        precision += [precision_score(Y_test, Y_predict)]
        precision_train += [precision_score(Y_train, Y_train_predict)]
        recall += [recall_score(Y_test, Y_predict)]
        recall_train += [recall_score(Y_train, Y_train_predict)]
        f1 += [f1_score(Y_test, Y_predict)]
        f1_train += [f1_score(Y_train, Y_train_predict)]
        accuracy += [accuracy_score(Y_test, Y_predict)]
        specificity += [_specificity_score(Y_test, Y_predict)]
        accuracy_train += [accuracy_score(Y_train, Y_train_predict)]

        logger.info("CV Split #" + str(cv_run + 1))
        logger.info("\tPrecision: " + str(precision[-1]))
        logger.info("\tRecall: " + str(recall[-1]))
        logger.info("\tF1 Score: " + str(f1[-1]))
        logger.info("\tAccuracy: " + str(accuracy[-1]))
        logger.info("\tSpecificity: " + str(specificity[-1]))
        logger.info("\tTrain Precision: " + str(precision_train[-1]))
        logger.info("\tTrain Recall: " + str(recall_train[-1]))
        logger.info("\tTrain F1 Score: " + str(f1_train[-1]))
        logger.info("\tTrain Accuracy: " + str(accuracy_train[-1]))

    try:
        features, model = (clf.steps[0][1], clf.steps[-1][1])
        column_names = features.get_feature_names()
        feature_importances = model.coef_[0] if not type(model) in [type(AdaBoostClassifier()), type(DecisionTreeClassifier)]  else model.feature_importances_
        if len(column_names) == len(feature_importances):
            Z = zip(column_names, feature_importances)
            Z.sort(key = lambda x: abs(x[1]), reverse = True)
            important_features = ""
            for z in  Z[:min(100, len(Z))]:
                important_features += str(z[1]) + ": " + str(z[0]) + "\\n" 
    except Exception as e:
        logger.error(e)
        important_features = "error"

    result = dict()
    result['mode'] = max([1. * x/ sum(counts.values()) for x in counts.values()])
    result['precision_mean'], result['precision_std'] = get_mu_std(precision)
    result['recall_mean'], result['recall_std'] = get_mu_std(recall)
    result['f1_mean'], result['f1_std'] = get_mu_std(f1)
    result['accuracy_mean'], result['accuracy_std'] = get_mu_std(accuracy)
    result['train_precision_mean'], result['train_precision_std'] = get_mu_std(precision_train)
    result['train_recall_mean'], result['train_recall_std'] = get_mu_std(recall_train)
    result['train_f1_mean'], result['train_f1_std'] = get_mu_std(f1_train)
    result['train_accuracy_mean'], result['train_accuracy_std'] = get_mu_std(accuracy_train)
    result['important_features'] = important_features
     
    return result    

# DEPRECATED
def test_model(features, data_size = 25, num_cv_splits = 5, method = 'logistic regression', show_progress = True, model_args = dict()):

    if method in ['logistic regression', 'lr', 'logitr', 'logistic']:
        is_regression = False
        clf = LogisticRegression(**model_args)
    elif method in ['svm']:
        is_regression = False
        clf = SVC(**model_args)
    elif method in ['boosting', 'adaboost']:
        is_regression = False
        clf = AdaBoostClassifier(**model_args)
    elif method in ['clinical', 'decision', 'cdm', 'clinical decision model']:
        is_regression = False
        clf = ClinicalDecisionModel()
    else:
        raise ValueError("'" + method + "' is not a supported classification method")

    logger.info('Preprocessing...')
    X, Y = get_preprocessed_patients(data_size)
    Y = change_ef_values_to_categories(Y)
    logger.info(str(len(X)) + " patients in dataset")
    
    if not is_regression:
        counts = {}
        for y in Y:
            if y not in counts:
                counts[y] = 0
            counts[y] += 1
        logger.info("Summary:")
        logger.info(counts)
    
    pipeline =  Pipeline([
        ('feature_union', features),
        ('Classifier', clf)
    ])

    #If using the ClinicalDecisionModel then no pipeline needed
    if method in ['clinical', 'decision', 'cdm', 'clinical decision model']:
        pipeline = clf

    mse = []
    r2 = []
    precision = []
    recall = []
    f1 = []
    accuracy = []
    specificity = []    

    for cv_run in range(num_cv_splits):

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = .33)
        pipeline.fit(X_train, Y_train)
        Y_predict = pipeline.predict(X_test)
        if is_regression:
            mse += [mean_squared_error(Y_test, Y_predict)]
            r2 += [r2_score(Y_test, Y_predict)]
            if show_progress:
                logger.info("CV Split #" + str(cv_run + 1))
                logger.info("\tMean Squared Error: ", mse[-1])
                logger.info("\tR2 Score: ", r2[-1])
        else:
            precision += [precision_score(Y_test, Y_predict)]
            recall += [recall_score(Y_test, Y_predict)]
            f1 += [f1_score(Y_test, Y_predict)]
            accuracy += [accuracy_score(Y_test, Y_predict)]
            specificity += [_specificity_score(Y_test, Y_predict)]
            if show_progress:
                logger.info("CV Split #" + str(cv_run + 1))
                logger.info("\tPrecision: " + str(precision[-1]))
                logger.info("\tRecall: " + str(recall[-1]))
                logger.info("\tF1 Score: " + str(f1[-1]))
                logger.info("\tAccuracy: " + str(accuracy[-1]))
                logger.info("\tSpecificity: " +  str(specificity[-1]))
    logger.info("\n---------------------------------------")
    logger.info("Overall (" + str(num_cv_splits) +  " cv cuts)")
    if is_regression:
        display_summary("Mean Squared Error", mse)
        display_summary("R2 Score", r2)
    else:
        display_summary("Precision", precision)
        display_summary("Recall", recall)
        display_summary("F1 Score", f1)
        display_summary("Accuracy", accuracy)
        display_summary("Specificity", specificity)

    try:
        column_names = features.get_feature_names()
        logger.info("Number of column names: " + str( len(column_names)))
        feature_importances = clf.coef_[0] if not method in ['boosting', 'adaboost'] else clf.feature_importances_
        Z = zip(column_names, feature_importances)
        Z.sort(key = lambda x: abs(x[1]), reverse = True)
        logger.info("100 biggest theta components of last CV run:")
        for z in Z[:min(100, len(Z))]:
            logger.info(str(z[1]) + "\t" + z[0])
    except Exception as e:
        logger.info("Feature name extraction failed")
        logger.info(e)
 

if __name__ == "__main__":
    main()
    #cProfile.run('main()')

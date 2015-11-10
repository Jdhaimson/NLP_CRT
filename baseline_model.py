import re

import numpy as np
from sklearn.base import TransformerMixin
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer 
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import FeatureUnion, Pipeline

from baseline_transformer import GetConcatenatedNotesTransformer
from build_graphs import get_doc_rel_dates, get_operation_date, get_ef_values
from extract_data import get_operation_date, parse_date
from language_processing import is_note_doc, get_date_key
from loader import get_data


def get_preprocessed_patients():
    #patient_nums = range(906)
    # patient_nums = range(25)
    patients_out = []
    delta_efs_out = []
    for i in patient_nums:
        print i
        patient_data = get_data([i])[0]
        if patient_data is not None:
            ef_delta = get_ef_delta(patient_data)
            if ef_delta is not None:
                patients_out.append(patient_data['NEW_EMPI'])
                delta_efs_out.append(ef_delta)
    return patients_out, delta_efs_out
            

def get_ef_delta(patient_data):
    ef_values = get_ef_values(patient_data)
    sorted_ef = sorted(ef_values)
    before = None
    after = None
    for (rel_date, ef_value) in sorted_ef:
        if rel_date <= 0:
            before = ef_value
        else:
            after = ef_value
    if before is not None and after is not None:
        return after - before
    else:
        return None

X, Y = get_preprocessed_patients()
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = .33)

class PrintTransformer(TransformerMixin):
    def fit(self, X, y=None, **fit_params):
        return self
    def transform(self, X, **transform_params):
        print X.shape
        for x in X:
            print x.shape
        return X

class TransposeTransformer(TransformerMixin):
    def fit(self, X, y=None, **fit_params):
        return self
    def transform(self, X, **transform_params):
        return np.array(map(lambda x: np.transpose(x), X))


pipeline =  Pipeline([
    ('feature_union', FeatureUnion([
        ('Car', Pipeline([
            ('notes_transformer_car', GetConcatenatedNotesTransformer('Car')),
            ('bag_of_words', CountVectorizer())
        ])),
        ('Lno', Pipeline([
            ('notes_transformer_lno', GetConcatenatedNotesTransformer('Lno')),
            ('bag_of_words', CountVectorizer())
        ]))
    ])),
    #('transpose', TransposeTransformer()),
    #('print', PrintTransformer()),
    ('logistic_regression', LogisticRegression())
])

pipeline.fit(X_train, Y_train)
Y_predict = pipeline.predict(X_test)
mse = mean_squared_error(Y_test, Y_predict)
r2 = r2_score(Y_test, Y_predict)
print "Mean Squared Error: " + str(mse)
print "R2 Score: " + str(r2)

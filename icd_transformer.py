import datetime

import numpy as np
from sklearn.base import TransformerMixin

import loader
import extract_data
from icd9.icd9_categories import get_diagnosis_categories, get_max_diagnosis_info
from structured_data_extractor import get_diagnoses, get_chronic_diagnoses
import language_processing

class ICD9_Transformer(TransformerMixin):
    """

    """
    def __init__(self):
        self.categories = get_diagnosis_categories()
        self.category_maxes = get_max_diagnosis_info()

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, **transform_params):
        transformed_X = map(self.get_icd9_vector, X)
        return transformed_X 

    def get_icd9_vector(self, empi):
        patient = loader.get_patient_by_EMPI(empi)
        operation_date = extract_data.get_operation_date(patient)
        diagnoses = get_diagnoses(empi)
        for (date, code_type, code, diagnosis_name) in diagnoses:
            if date < operation_date:
                if code_type == 'ICD9':
                    diagnosis_cat = self.categories[code.replace('.','')]
                    base = ''
                    for component in diagnosis_cat.split('.'):
                        base += component
                else:
                    print "Non-ICD9 Code for Patient: " + empi                

    def get_vector_from_category(self, category):
        category_array = map(int, category.split('.'))
        while len(category_array) < len(self.category_maxes):
            category_array.append(0)

        shape = []
        for i in range(len(self.category_maxes)):
            # Codes are 1 indexed- zeroth element represents missing
            shape.append(self.category_maxes[i]+1)
        
        for i in range(len(self.category_maxes)):
            vec = np.zeros(shape[:i])
            subvec = vec
            for j in range(i):
                subvec = subvec[category_array[j]]
            subvec[

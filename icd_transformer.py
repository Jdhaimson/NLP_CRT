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

        # Build a diagnosis history vector for the whole patient
        diagnosis_history = None
        for (date, code_type, code, diagnosis_name) in diagnoses:
            if date < operation_date:
                if code_type == 'ICD9':
                    cleaned_code = code.replace('.','')
                    if cleaned_code in  self.categories:
                        diagnosis_cat = self.categories[cleaned_code]
                        diagnosis_vec = self.get_vector_from_category(diagnosis_cat)
                        if diagnosis_history is None:
                            diagnosis_history = diagnosis_vec
                        else:
                            diagnosis_history += diagnosis_vec
                else:
                    #print "Non-ICD9 Code for Patient: " + empi                
                    pass

        # Normalize array to be 1's or zeros, not counts
        if diagnosis_history is not None:
            diagnosis_history = np.array(map(int, diagnosis_history > 0))

        return diagnosis_history
        

    def get_vector_from_category(self, category):
        '''
        Turns an ICD9 Category into a vector of concatenated vectors where each
        vector is a one-hot vector representing the presence of a diagnosis in
        that level of the hierarchy
        '''
        # Normalize the category array with 0s so they are all the same length
        category_array = map(int, category.split('.'))
        while len(category_array) < len(self.category_maxes):
            category_array.append(0)

        # Build a shape array specifying dimensionality of each category
        shape = []
        for i in range(len(self.category_maxes)):
            # Codes are 1 indexed- zeroth element represents missing
            shape.append(self.category_maxes[i]+1)
        
        # Build an array at each level in the hierarchy
        vectors = []
        for i in range(1,len(self.category_maxes)+1):
            vec = np.zeros(shape[:i])
            subvec = vec
            for j in range(i-1):
                subvec = subvec[category_array[j]]
            subvec[category_array[i-1]] = 1
            vectors.append(vec)
        return reduce(lambda a,b: np.concatenate((a.flatten(), b.flatten())), vectors)


    def get_feature_names(self):
        # Build a shape array specifying dimensionality of each category
        shape = []
        for i in range(len(self.category_maxes)):
            # Codes are 1 indexed- zeroth element represents missing
            shape.append(self.category_maxes[i]+1)

        vectors = []
        for i in range(1,len(self.category_maxes)+1):
            vec = np.empty(shape[:i], 'U30')
            vectors.append(self.label_vector(vec))
        return reduce(lambda a,b: np.concatenate((a.flatten(), b.flatten())), vectors)

    def label_vector(self, vector, root="ICD9_Category"):
        for i in range(len(vector)):
            element = vector[i]

            # Recursive Case
            if isinstance(element, np.ndarray):
                vector[i] = self.label_vector(vector[i], root + "." + str(i))

            # Base Case
            else:
                vector[i] = root + "." + str(i)
        return vector


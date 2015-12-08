import datetime

from gensim.models import Doc2Vec
import numpy as np
from sklearn.base import TransformerMixin

import loader
import extract_data
from structured_data_extractor import get_diagnoses, get_chronic_diagnoses
import language_processing

class Doc2Vec_Note_Transformer(TransformerMixin):
    """

    """ 
    def __init__(self, note_type, model_file, max_notes, dbow_file=None):
        self.note_type = note_type
        self.max_notes = max_notes
        self.model = Doc2Vec.load(model_file)
        if dbow_file:
            self.dbow = Doc2Vec.load(dbow_file)
        else:
            self.dbow = False

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, **transform_params):
        transformed_X = map(self.get_sent_vector, X)
        return np.array(transformed_X)

    def get_sent_vector(self, empi):
        patient = loader.get_patient_by_EMPI(empi)
        operation_date = extract_data.get_operation_date(patient)
        diagnoses = get_diagnoses(empi)

        date_key = extract_data.get_date_key(self.note_type)
        notes = []
        if self.note_type in patient.keys() and date_key != None:
            # Get sorted list of notes before procedure
            time_idx_pairs = []
            for i in range(len(patient[self.note_type])):
                doc = patient[self.note_type][i]
                date = extract_data.parse_date(doc[date_key])
                if date != None and date < operation_date:
                    time_idx_pairs.append((operation_date - date, i))
            time_idx_pairs.sort()

            for time,idx in time_idx_pairs[:self.max_notes]:
                doc = patient[self.note_type][idx]
                notes.append(doc['free_text'])

        # ensure that notes vector length is equal to max_notes
        if len(notes) < self.max_notes:
            delta = self.max_notes - len(notes)
            for i in range(delta):
                notes.append('')  

        # Turn notes into Doc Vectors
        vectors = map(self.get_sent_vector_from_doc, notes)
        return np.array(vectors).flatten()

    def get_sent_vector_from_doc(self, doc):
        split_doc = doc.split()
        vec = self.model.infer_vector(split_doc)
        if self.dbow:
            vec = np.concatenate((vec, self.dbow.infer_vector(split_doc)))
        return vec

    def get_feature_names(self):
        feature_names = []
        for i in range(self.max_notes):
            for j in range(self.model.vector_size):
                feature_names.append(self.note_type 
                                     + '_doc:' + str(i) + '_dim:' + str(j))
        return feature_names

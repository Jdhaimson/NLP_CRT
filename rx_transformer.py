import numpy as np
from sklearn.base import TransformerMixin

import extract_data
import loader

class RX_Transformer(TransformerMixin):
    """

    """ 
    def __init__(self):
        pass

    def fit(self, X, y=None, **fit_params):
        self.all_med_classes = {}
        self.dimensionality = 0
        for empi in X:
            for med in self.get_med_classes(empi):
                if med not in self.all_med_classes:
                    self.all_med_classes[med] = self.dimensionality
                    self.dimensionality += 1
        return self

    def get_feature_names(self):
        reverse_dict = {}
        for med in self.all_med_classes.keys():
            reverse_dict[self.all_med_classes[med]] = med 

        features = []
        for i in range(self.dimensionality):
            features.append(reverse_dict[i])
        return np.asarray(features)

    def transform(self, X, **transform_params):
        transformed_X = map(self.get_med_string, X)
        return np.array(transformed_X)

    def get_med_vector(self, empi):
        vector = np.zeros(self.dimensionality)
        for med in self.get_med_classes(empi):
            vector[self.all_med_classes[med]] = 1.0
        return vector 

    def get_med_classes(self, empi):
        patient = loader.get_patient_by_EMPI(empi)
        operation_date = extract_data.get_operation_date(patient)
        medications = []
        for med in patient['Med']:
            try:
                date = parse_m_d_y(med['Medication_Date'])
                if date <= procedure_date:
                    medications.extend(med['RXNORM_CLASSES'])
            except:
                pass
        return medications

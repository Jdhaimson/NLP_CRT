import numpy as np
from sklearn.base import TransformerMixin
import loader
import extract_data

import datetime
import re

class ExtractValueTransformerMixin(TransformerMixin):

    """
    Abstract class designed to help with transformers that do not need to be fit

    FOLLOWING FUNCTION MUST BE INSTANTIATED

    parse_value: function that returns the desired value from a document
        inputs: dict of the doc, datetime of the procedure, string of doc type
        ouput: value of any type
    """
    
    def __init__(self, doc_types = None, name = "Value" ,method = 'last', num_horizon = 1, time_horizon = None):
        """
        method: in ['mean', 'max', 'min', 'all', 'found', 'count']
        num_horizon: how many of the last values to consider
        time_horizon: how far back to look for these values
        name: name of value
        """
        self.doc_types = doc_types
        self.name = name
        self.method = method
        self.num_horizon = num_horizon
        self.time_horizon = time_horizon
   
    def fit(self, X, y = None):
        return self

    def transform(self, X):
        transformed_X = map(self.__get_feature, X)
        return np.matrix(transformed_X)

    def get_feature_names(self):
        if self.method == 'mean':
            return [self.name + "_mean"]
        elif self.method == 'max':
            return [self.name + "_max"]
        elif self.method == 'min':
            return [self.name + "_min"]
        elif self.method == 'all':
            return [self.name + "_" + str(-1*(x + 1)) for x in range(self.num_horizon)]
        elif self.method == 'count':
            return [self.name + "_count"]
        elif self.method == 'found':
            return [self.name + "_found"]
        else:
            return None

    def __select_doc(self, doc, operation_date, doc_type):
        """
        description: function that returns is specific doc should be used
        inputs: dict of the doc, datetime of the procedure, string of doc type
        output: boolean
        """

        doc_date_text = doc[extract_data.get_date_key(doc_type)]
        doc_date = extract_data.parse_date(doc_date_text)
        time_diff = (doc_date - operation_date).days
        if self.time_horizon != None:    
            return time_diff <= 0 and abs(time_diff) <= abs(self.time_horizon)
        else:
            return time_diff <= 0

    def __transform_values(self, values):
        """
        description: function that returns the columns representing sample
        inputs: list of outputs of parse_function for selected docs
        output: one-dimensional array or list
        """
        if len(values) > 0:
            values.sort(key = lambda x: x[0], reverse = True)
            if self.method == 'found':
                return [1]

            most_recent = [float(values[i][1]) for i in range(min(len(values),self.num_horizon))]
            if self.method == 'mean':
                return [sum(most_recent) * 1. / len(most_recent)]
            elif self.method == 'max':
                return [max(most_recent)]
            elif self.method == 'min':
                return [min(most_recent)]
            elif self.method == 'all':
                return most_recent + [sum(most_recent) / len(most_recent)]*(self.num_horizon - len(most_recent))
            elif self.method == 'count':
                return [sum(most_recent)]
            else:
                return None

        elif self.method in ['found', 'count']:
            return [0]
        else:
            return None

    def __get_feature(self, empi):
        """
        description: performs the loops and conditionals to get at the
            desired documents and then returns the feature associated
            with the patient with the given EMPI
        input: empi string
        output: list or np.array of the feature
        """

        patient = loader.get_patient_by_EMPI(empi)
        operation_date = extract_data.get_operation_date(patient)
        values = []
        for doc_type in patient:
            if self.doc_types == None or doc_type in self.doc_types:
                docs = patient[doc_type]
                if type(docs) != type(list()):
                    docs = [docs]
                for doc in docs:
                    if self.__select_doc(doc, operation_date, doc_type):
                        value = self.parse_value(doc, operation_date, doc_type)
                        if not value in [None, []]:
                            values += value if type(value) == type(list()) else [value]
        return self.__transform_values(values)

class RegexTransformer(ExtractValueTransformerMixin):    
    """
    Class that extends ExtractValueTransformerMixin by providing
        a parse_value method that finds the RegEx matches
    """
    
    def __init__(self, doc_types, name, pattern_strings, method, num_horizon, time_horizon):
        ExtractValueTransformerMixin.__init__(self, doc_types, name,  method, num_horizon, time_horizon)  
        self.patterns = [re.compile(pattern) for pattern in pattern_strings]
       
    def parse_value(self, doc, operation_date, doc_type):
        """
        description: function that returns the desired value from a document
        inputs: dict of the doc, datetime of the procedure, string of doc type
        ouput: value of any type
        """

        note = doc['free_text'].lower()
         
        doc_date_text = doc[extract_data.get_date_key(doc_type)]
        doc_date = extract_data.parse_date(doc_date_text)
        delta_days = (doc_date - operation_date).days
        
        values = []
        for pattern in self.patterns:
            values += [x for x in re.findall(pattern, note) if len(x) > 0 and x != "."]
        if len(values) > 0 and not self.method in ['found', 'count']:
            return (delta_days, sum([float(x) for x in values])/len(values))
        elif self.method == 'found':
            return (delta_days, 1)
        elif self.method == 'count':
            return [(delta_days, len(values))]
            return None

class EFTransformer(RegexTransformer):

    def __init__(self, method, num_horizon, time_horizon = None):
        re_patterns = ['ef[{of}{0, 1}: \t]*([0-9]*\.{0,1}[0-9]*)[ ]*%', 'ejection fraction[{of}{0, 1}: \t]*([0-9]*\.{0,1}[0-9]*)[ ]*%']

        RegexTransformer.__init__(self, ['Car'], 'EF', re_patterns, method, num_horizon, time_horizon)    

    def __select_doc(self, doc, operation_date, doc_type):
        is_in_time_range = ExtractValueTransformerMixin.__select_doc(self, doc, operation_date, doc_type)
        return is_in_time_range and doc['procedure'] in ['CardiacElectrophysiology', 'ECG']


class LBBBTransformer(RegexTransformer):
    
    def __init__(self, time_horizon = None):
        re_patterns = ['left bundle branch block', 'lbbb']
        RegexTransformer.__init__(self, ['Car'], 'LBBB', re_patterns, 'found', None, time_horizon)    

    def __select_doc(self, doc, operation_date, doc_type):
        is_in_time_range = ExtractValueTransformerMixin.__select_doc(self, doc, operation_date, doc_type)
        return is_in_time_range and doc['procedure'] in ['ECG']


import loader
import extract_data
import language_processing
import datetime
from sklearn.base import TransformerMixin

class GetConcatenatedNotesTransformer(TransformerMixin):

    def __init__(self, note_type):
        self.type = note_type

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, **transform_params):
        transformed_X = map(self.get_concatenated_notes, X)
        return transformed_X 

    def get_concatenated_notes(self, empi):
        person = loader.get_patient_by_EMPI(empi)
        operation_date = extract_data.get_operation_date(person)
        date_key = language_processing.get_date_key(self.type)
        notes = []
        if self.type in person.keys() and date_key != None:
            for i in range(len(person[self.type])):
                doc = person[self.type][i]
                date = extract_data.parse_date(doc[date_key])
                if date != None and date < operation_date:
                    notes.append(doc['free_text'])
        return '\n\n'.join(notes)        

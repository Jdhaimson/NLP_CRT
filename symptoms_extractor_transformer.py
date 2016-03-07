from value_extractor_transformer import RegexTransformer

class SymptomsExtractorTransformerGenerator:
    """Class that generates a list of RegexTransformers, one for each
    regular expression given in the symptoms regex file 'symptoms_regex_final.txt'"""
    def __init__(self, doctypes, method, num_horizon, time_horizon = None):
        self.doctypes = doctypes
        self.method = method
        self.num_horizon = num_horizon
        self.time_horizon = time_horizon
        self.symptoms = {}
        with open("symptoms_regex_final.txt") as f:
            content = f.readlines()
        for line in content:
            name, regex = line.split(': ', 1)
            self.symptoms[name] = regex
    
    def getSymptoms(self):
        return [('SYMPTOM_' + symptom, RegexTransformer(self.doctypes, symptom, [self.symptoms[symptom]], self.method, self.num_horizon, self.time_horizon)) for symptom in self.symptoms]

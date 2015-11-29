from sklearn.base import TransformerMixin, ClassifierMixin
from value_extractor_transformer import EFTransformer, QRSTransformer, LBBTransformer, SinusRhythmTransformer, NYHATransformer


class ClinicalDecisionModel(TransformerMixin, ClassifierMixin):

    """
    Replicate prediction of clinical descion tree
    in 'Circulation-2012-Tracy-1784-800.pdf' Appendix 3
    Does not need to be fit and transforms data on its own
    """

    ClinicalDecisionModel.LVEF = 'lvef'
    ClinicalDecisionModel.QRS = 'qrs'
    ClinicalDecisionModel.LBBB = 'lbbb'
    ClinicalDecisionModel.SINUS_RHYTHM = 'sr'
    ClinicalDecisionModel.NYHA = 'nyha'

    def __init__(self):
        self.transformers = dict()
        self.transformers[ClinicalDecisionModel.LVEF]= EFTransformer('mean',3)
        self.transformers[ClinicalDecisionModel.QRS]= QRSTransformer('mean', 3)
        self.transformers[ClinicalDecisionModel.LBBB]= LBBBTransformer()
        self.transformers[ClinicalDecisionModel.SINUS_RHYTHM]= SinusRhythmTransformer()
        self.transformers[ClinicalDecisionModel.NYHA]= NYHATransformer()
        
    def fit(self, X = None, y = None):
        for trans_key in self.transformers:
            self.transformers[trans_key].fit(X, y)
        return self

    def transform(self, X):
        return [self.__find_values(empi) for empi in X]

    def __find_values(self, empi):
        values = dict()
        for trans_key in self.transformers:
            values[trans_key] = self.transformers[trans_key].__get_feature(empi)
        return values

    def predict(self, X):
        X_transformed = self.transform(X)
        predicted_colors = map(self.predict_color, X_transformed)
        y_hat = map(self.prediction_from_color, predicted_colors)
        return y_hat

    def predict_color(self, values):
        nyha_class = values[ClinicalDecisionModel.NHYA]
        ef = values[ClincialDecisionModel.LVEF]
        qrs = values[ClincalDecisionModel.QRS]
        lbbb = bool(values[ClincialDecisionModel.LBBB])
        sr = bool(values[ClinicalDecisionModel.SINUS_RHYTHM])
        if ef > 35: #EF lower than 35 disqualified
            return 'red'
        if nyha_class == 1:
            if ef < 30 and qrs >= 150 and lbbb:
                return 'orange'
            else:
                return 'red'
        elif nyha_class == 2:
            if lbbb:
                if sr:
                    if qrs > 150:
                        return 'green'
                    else:
                        return 'yellow'
                else:
                    return 'red'
            else:
                if qrs > 150:
                    return 'orange'
                else:
                    return 'red'
        elif nyha_class == 3:
            if sr and qrs > 120:
                if qrs > 150 and lbbb:
                    return 'green'
                elif qrs <= 150 and not lbbb:
                    return 'orange'
                else:
                    return 'yellow'
            else:
                return 'red'
        else: #this is None and class 4
            return 'red'

    def prediction_from_color(self, color):
        mapping = ['red' : 0, 'orange' : 0, 'yellow': 1, 'green' ; 1]
        return mapping[color] 

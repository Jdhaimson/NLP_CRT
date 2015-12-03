from sklearn.base import TransformerMixin, ClassifierMixin
from value_extractor_transformer import EFTransformer, QRSTransformer, LBBBTransformer, SinusRhythmTransformer, NYHATransformer


class ClinicalDecisionModel(TransformerMixin, ClassifierMixin):

    """
    Replicate prediction of clinical descion tree
    in 'Circulation-2012-Tracy-1784-800.pdf' Appendix 3
    Does not need to be fit and transforms data on its own
    """

    LVEF = 'lvef'
    QRS = 'qrs'
    LBBB = 'lbbb'
    SINUS_RHYTHM = 'sr'
    NYHA = 'nyha'

    def __init__(self):
        self.transformers = dict()
        self.transformers[self.LVEF]= EFTransformer('max',3)
        self.transformers[self.QRS]= QRSTransformer('mean', 3)
        self.transformers[self.LBBB]= LBBBTransformer()
        self.transformers[self.SINUS_RHYTHM]= SinusRhythmTransformer()
        self.transformers[self.NYHA]= NYHATransformer()
        
    def fit(self, X = None, y = None):
        for trans_key in self.transformers:
            self.transformers[trans_key].fit(X, y)
        return self

    def transform(self, X):
        return [self.__find_values(empi) for empi in X]

    def __find_values(self, empi):
        values = dict()
        for trans_key in self.transformers:
            values[trans_key] = self.transformers[trans_key].get_feature(empi)
        return values

    def predict(self, X):
        X_transformed = self.transform(X)
        predicted_colors = map(self.predict_color, X_transformed)
        y_hat = map(self.prediction_from_color, predicted_colors)
        return y_hat

    def predict_color(self, values):
        """
        Summary of logic (all have ef > 35):
        NYHA I:
            Orange - ef < 30, qrs > 150, lbbb
            Red -    ef > 30 or qrs < 150 or no lbbb
        NYHA II:
            Green -  qrs > 150, lbbb, sinus rhythm
            Yellow - qrs < 150, lbbb, sinus rhythm
            Orange - qrs > 150, no lbbb
            Red -    no lbbb and qrs < 150 or lbbb and no SR
        NYHA III:
            Green -  qrs > 150, lbbb, sinus rhythm
            Yellow - qrs > 150, no lbbb, sinus rhythm
            Orange - qrs < 150, no lbbb, sinus rhythm
            Red -    qrs < 120 or no sinus rhythm
        NYHA IV:
            Red -    for all cases
        """
        nyha_class = values[self.NYHA].index(1) + 1
        ef = values[self.LVEF][0]
        qrs = values[self.QRS][0]
        lbbb = bool(values[self.LBBB][0])
        sr = bool(values[self.SINUS_RHYTHM][0])
        if ef > 35: #EF higher than 35 disqualified
            return 'red'
        #print "NYHA:", nyha_class, "EF:", ef, "QRS:", qrs, "LBBB:", lbbb, "SR:", sr
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
        mapping = {'red' : 0, 'orange' : 0, 'yellow': 1, 'green' : 1}
        return mapping[color] 

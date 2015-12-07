from sklearn.pipeline import FeatureUnion

from doc2vec_transformer import Doc2Vec_Note_Transformer

def get_pipeline():
    features = FeatureUnion([
        ('Car_Doc2Vec', Doc2Vec_Note_Transformer('Car', '/home/ubuntu/josh_project/doc2vec_models/car_1.model', 10))
    ])

    return features

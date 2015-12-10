from neural_network import NeuralNetwork, NeuralLogistic
from mix_of_exp import MixtureOfExperts
from neural_network import NeuralNetwork, NeuralLogistic
from sklearn.linear_model import LogisticRegression, LinearRegression, SGDClassifier, SGDRegressor
import random
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from sklearn.ensemble import AdaBoostClassifier
from utils import generate_data, plot_predictions, prediction_accuracy, sparsify_data
from sklearn.pipeline import FeatureUnion, Pipeline
from model_builder import build_model, regex_baseline
from model_tester import execute_test
import sys
import profile


logistic = NeuralLogistic(restarts = 2, regularization = 0.00)

nn = NeuralNetwork([(8, 'logistic'), (8, 'tanh'), (None, 'softmax')], 'maxent', regularization = 1e0, restarts = 30, max_iter = 10000, init_size = 1, step_size = 1e-2)

#nn = NeuralNetwork([(None, 'softmax')], 'maxent', include_offset = True, max_iter = 5000)

me = MixtureOfExperts([NeuralLogistic(regularization = 1e-1), NeuralLogistic(regularization = 1e-1), NeuralLogistic(regularization = 1e-1)], 
					   NeuralLogistic(regularization = 1e-1), max_iter = 25)
					   #NeuralNetwork([(3, 'tanh'), (None, 'softmax')], 'maxent'))

adaboost = AdaBoostClassifier(n_estimators = 500)

mix_ex_args = {'experts' :[NeuralLogistic(regularization = 1e-1), NeuralLogistic(regularization = 1e-1), NeuralLogistic(regularization = 1e-1)], 
               'gate'    : NeuralLogistic(regularization = 1e-1),
               'max_iter': 15}

model = build_model(regex_baseline, method = 'me', model_args = mix_ex_args)

print execute_test(model, 25, 5)






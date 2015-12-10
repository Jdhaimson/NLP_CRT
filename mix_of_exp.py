import sklearn as skl
import numpy as np
import random
from utils import plot_predictions
from sklearn.base import BaseEstimator, ClassifierMixin
from multiprocessing import Pool, Process
#from main import plot_predictions

class MixtureOfExperts(BaseEstimator, ClassifierMixin):

	def __init__(self, experts, gate, max_iter = 50):

		self.experts = experts
		self.gate = gate
		self.max_iter = max_iter

	def fit(self, X, y):

		show_plots = False

		self.num_experts_ = len(self.experts)
		self.num_classes_ = y.shape[1]
		self.__initialize(X, y)
		obj_vals = []
		while len(obj_vals) <= 1 or (abs(obj_vals[-2] - obj_vals[-1]) > 1e-4 and len(obj_vals) < self.max_iter):
			expert_weights = self.__E_step(X, y)
			obj_val = self.__M_step(X, y, expert_weights)
			obj_vals += [obj_val]
			print obj_val
			if show_plots:
				plot_predictions(X, y, self.gate, "Gate predictions")
				for i in range(self.num_experts_):
					plot_predictions(X, y, self.experts[i], "Expert #" + str(i) + " predictions")
				plot_predictions(X, y, self)
		# print obj_vals
		return self

	def predict(self, X):

		return np.argmax(self.predict_proba(X), axis = 1)

	def score(self, X, y, sample_weight = None):

		"""
		Description: evaluates log-likelihood of the data, sum [ weights * log ( sum g_j(i) * p(y_i | x_i, j) )]
		input:	X - data matrix
				y - label matrix
				sample_weight - vector of the importance of each sample in [1, n]
		output: log-likelihood of data
		"""

		weighted_expert_accuracy = self.__weighted_expert_accuracy(X, y)
		expert_weights = self.__get_expert_weights(weighted_expert_accuracy)
		log_prob = np.multiply(np.log(np.clip(weighted_expert_accuracy, 1e-18, 100)), expert_weights)
		if sample_weight != None:
			log_prob = np.multiply(log_prob, sample_weight)

		return np.sum(log_prob)

		# predictions = self.predict_proba(X)
		# log_prob = np.log(predictions)
		# entropy = np.multiply(y, predictions)
		# return np.sum(entropy)


	def predict_proba(self, X):

		"""
		description: returns the probability that X belongs in each class
		input: X - data matrix
		output: N x K probability matrix, so sum( * , axis = 1) = 1
		"""
		expert_predictions = self.__predict_experts(X)
		gate_proba = self.gate.predict_proba(X)
		gate_proba_big = np.empty((X.shape[0], self.num_classes_, self.num_experts_))
		for k in range(self.num_classes_):
			gate_proba_big[:, k, :] = gate_proba

		gated_expert_accruacy = np.multiply(expert_predictions, gate_proba_big)
		return np.sum(gated_expert_accruacy.reshape(X.shape[0], self.num_classes_, self.num_experts_), axis = 2)

	def __predict_experts(self, X):

		"""
		description: finds the predicted probability for each point, of each class, for each expert
		input: input matrix X
		output: N X K X M matrix where sum( * , axis = 2) = 1
		"""
		predictions = np.zeros((X.shape[0], self.num_classes_, self.num_experts_))
		#predictions = np.empty((X.shape[0], self.num_classes_, self.num_experts_))

		gate_proba = self.gate.predict_proba(X)
		for expert_index in range(self.num_experts_):
			expert = self.experts[expert_index]
			predictions[:, : , expert_index] = expert.predict_proba(X)  ####CHANGE THIS
			#expert_predictions = expert.predict(X)
			#for i in range(X.shape[0]):
				#predictions[i, expert_predictions[i], expert_index] =  1. ####CHANGE THIS
		return predictions

	def __initialize(self, X, y):

		"""
		description: initializes experts and gate by using random initial values and partitions of the data
		input: 	X - data matrix
				y - label matrix
		output: None
		"""

		for expert in self.experts:
			idx = np.array(random.sample(range(X.shape[0]), int(X.shape[0]* (1. - 1/ self.num_experts_))))
			expert.fit(X[idx], y[idx])

		random_init = np.random.rand(X.shape[0], self.num_experts_)

		self.gate.fit(X, random_init)

	def __weighted_expert_accuracy(self, X, y):

		"""
		description: returns matrix A_ij = g_j (x_i) * P(y_i | x_i, j)
		input:	X - input matrix
				y - output matrix
		output: gates expert predictions in N x M matrix as described above
		"""
		expert_predictions = self.__predict_experts(X)
		expert_accuracy = np.multiply(expert_predictions, y[:, :, np.newaxis]) 
		#expert_accuracy = expert_predictions
		#gap = 0
		gate_proba = self.gate.predict_proba(X)
		gate_proba_big = np.empty((X.shape[0], self.num_classes_, self.num_experts_))
		for k in range(self.num_classes_):
			gate_proba_big[:, k, :] = gate_proba

		gated_expert_accruacy = np.multiply(expert_accuracy, gate_proba_big)
		norm_weights = gated_expert_accruacy.reshape(X.shape[0], self.num_classes_, self.num_experts_)
		

		#gated_expert_accruacy = expert_accuracy
		return np.sum(norm_weights, axis = 1)


	def __get_expert_weights(self, weighted_expert_accuracy):
		return np.divide(weighted_expert_accuracy, np.sum(weighted_expert_accuracy, axis = 1)[:, np.newaxis])

	def __E_step(self, X, y):

		"""
		description: finds the contribution of each expert to final prediction
		input:	X - data matrix
				y - label matrix
		output: N x M matrix of feature weights for each point for each expert
		"""

		weighted_expert_accuracy = self.__weighted_expert_accuracy(X, y)
		feature_weights = self.__get_expert_weights(weighted_expert_accuracy)
		
		return feature_weights


	def __M_step(self, X, y, expert_weights):

		"""
		description: fits experts and gate according to weights and returns new obj function value
		input:  X - input matrix
				y - output matrix
				expert_weights - weights obtained from E-step
		output: new obj function value
		"""


		#processes = [Process(target = self.gate.fit, args = (X, expert_weights))]
		self.gate.fit(X, expert_weights)
		#for num in range(10):
        #Process(target=f, args=(lock, num)).start()
        
        #expert_weights = self.__E_step(X, y)
        
		for expert_index in range(self.num_experts_):
			y_expert = np.empty(X.shape[0], )
			fw = expert_weights[:, expert_index]
			#fw = np.array(feature_weights[:, expert_index].transpose().tolist()[0])
			#processes += [Process(target = self.experts[expert_index].fit, args = (X, y, fw))]
			self.experts[expert_index].fit(X, y, fw)

		# for p in processes:
		# 	p.start()
		# for p in processes:
		# 	p.join()
		# print processes

		return self.score(X, y)		


	def get_params(self, deep = True):
		return {'experts' : self.experts, 
				'gate' : self.gate,
				'max_iter' : self.max_iter}

	def set_params(self, **parameters):
	    for parameter, value in parameters.items():
	        self.setattr(parameter, value)
	    return self
	    


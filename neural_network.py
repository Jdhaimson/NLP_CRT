import sklearn as skl
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.cross_validation import train_test_split
import math

#Contains neural network and NeuralLogistic that implements a multi-class logistic that fits to class probabilities

class NeuralNetwork(BaseEstimator, ClassifierMixin):

	def __init__(self, layers, obj_fun = 'maxent', regularization = 0., init_size = 1e-1, include_offset = True, 
				 restarts = 10, step_size = 1e-1, learning_schedule = "bold driver", max_iter = 10000, criterion = 1e-6):
        """
        layers:     list of (number of nodes, string of type) tuples; the last one will often be (None, 'softmax')
        obj_fun:    'maxent' and 'lsq' (least squares) are only ones implemented now
        regularization:  0 means no regularixation
        init_size:  range [-init_size / 2, init_size / 2] for initial weights
        include_offset: always True 
        restarts:   number of reinitializations (returns best model of these according to obj_fun)
        step_size:  initial step
        learning_shcedule: 'fixed' means some determined decay and 'bold driver' implements that algorithm
        max_iter:   maximum descent steps before termination
        criterio:   convergence criterion of obj_value
        """
        
		self.layers = layers
		self.obj_fun = obj_fun
		self.regularization = regularization
		self.init_size = init_size
		self.include_offset = include_offset
		self.restarts = restarts
		self.step_size = step_size
		self.learning_schedule = learning_schedule
		self.max_iter = max_iter
		self.criterion = criterion
		#layers: list of (size, transform_function_1, transform_function_2...) tuples 

	def fit(self, X_all, y_all, sample_weight = None, test_split = 1., val_split = .8):
		show_plots = False
		if test_split < 1:
			if type(sample_weight) == type(None):
				X, X_test, y, y_test = train_test_split(X_all, y_all, train_size = test_split)#, stratify = np.argmax(y_all, axis = 1))
				sample_weight_test = None
			else:
				X, X_test, y, y_test, sample_weight, sample_weight_test = train_test_split(X_all, y_all, sample_weight, train_size = test_split)#, stratify = np.argmax(y_all, axis = 1))
		else:
			X, y, sample_weight = (X_all, y_all, sample_weight)
		self.input_dim_ = X.shape[1]
		self.output_dim_ = y.shape[1]
		self.num_layers_ = len(self.layers)
		self.layers[-1] = tuple([self.output_dim_] + list(self.layers[-1][1:]))

		opt_weights = None
		opt_value = -10e10
		if show_plots:
			plt.figure()
		while opt_weights == None:

			for i in range(self.restarts):

				self.__init_weights()
				obj_vals = []
				val_scores = []
				if val_split < 1:
					if type(sample_weight) == type(None):
						X_train, X_val, y_train, y_val = train_test_split(X, y, train_size = val_split)#, stratify = np.argmax(y, axis = 1))
						sample_weight_train = None
						sample_weight_val = None
					else:
						X_train, X_val, y_train, y_val, sample_weight_train, sample_weight_val = train_test_split(X, y, sample_weight, train_size = val_split)#, stratify = np.argmax(y, axis = 1))
				else:
					X_train, y_train, sample_weight_train = (X, y, sample_weight)

				best_val_value = -1e100
				best_val_weights = None
				#print "Weights: ", [x.shape for x in self.weights_]
				step_size = self.step_size
				while len(obj_vals) <= 1 or (abs(obj_vals[-1] - obj_vals[-2]) > self.criterion and len(obj_vals) <= self.max_iter):
					
					#forward prop
					inputs, weighted_inputs, activations = self.__forward(X_train)
					obj_val = self.__eval_obj_fun(y_train, activations[-1], regularization = self.regularization)
					obj_vals += [obj_val]

					#backward prop
					gradients = self.__backward(inputs, weighted_inputs, activations, y_train, sample_weight_train)

					if len(obj_vals) == 1:
						step_size = self.__get_step_size(len(obj_vals), step_size, -1e100, obj_vals[-1])
					else:
						step_size = self.__get_step_size(len(obj_vals), step_size, obj_vals[-2], obj_vals[-1])
					
					self.update_weights(gradients, step_size)
				
					if val_split < 1: #early termination with validation holdout
						val_score = self.score(X_val, y_val, sample_weight_val)
						val_scores += [val_score]
						if val_score > best_val_value:
							best_val_weights = [w.copy() for w in self.weights_]
							best_val_value = val_score
					else:
						best_val_value = obj_vals[-1]

				if len(obj_vals) >= self.max_iter:
					print "OVERFLOW"
				#print i, "Obj val: ", obj_vals[-1]
				if val_split < 1:
					self.weights_ = best_val_weights

				if test_split < 1:
					test_score = self.score(X_test, y_test, sample_weight_test)
				else:
					test_score = best_val_value
				
				if opt_value < test_score:
					opt_value = test_score
					opt_weights = self.weights_

				if show_plots:
					#print test_score
					
					plt.plot([math.log10(-1.*x) for x in obj_vals], color = 'green', label = "log Train")
					plt.plot([math.log10(-1.*x) for x in val_scores], color = 'red', label = "log Val")
					
				#print opt_weights
		if show_plots:
			#plt.legend()
			plt.show()
		self.weights_ = opt_weights
		
		return self

	def predict(self, X):
		return np.argmax(self.predict_proba(X), axis = 1)

	def predict_proba(self, X):
		return self.__forward(X)[2][-1]

	#the dimension of the weights is (dim_before +1, dim_after, ), with +1 -> 0 if no offset
	def __init_weights(self):
		self.weights_ = []
		offset_size = int(self.include_offset)
		for layer_index in range(self.num_layers_):
			if layer_index == 0:
				before_dim = self.input_dim_
			else:
				before_dim = self.layers[layer_index - 1][0]
			after_dim = self.layers[layer_index][0]
			self.weights_ += [(np.random.rand(before_dim + offset_size, after_dim) - .5)*self.init_size]

	def __forward(self, X):
		inputs = []
		activations = []
		weighted_inputs = []
		current_input = self.__add_offset(X)

		if self.weights_ == None:
			print self.weights_

		for layer_index in range(self.num_layers_):

			weighted_input = np.dot(current_input, self.weights_[layer_index])
			current_activation = self.__transform_function(weighted_input, layer_index)

			inputs += [current_input]
			weighted_inputs += [weighted_input]
			activations += [current_activation]

			current_input = self.__add_offset(current_activation)

		return (inputs, weighted_inputs, activations)

	def __backward(self, inputs, weighted_inputs, activations, y, sample_weight = None, err_gradient = None):
		gradients = []
		if type(err_gradient) == type(None):
			overall_gradient = self.__obj_fun_gradient(y, activations[-1], sample_weight) #N x categories
		else:
			overall_gradient = err_gradient

		#NEED REMOVE OFFSET SOMEWHERE???
		for layer_index in range(self.num_layers_ -1, -1, -1):

			activations_gradient = self.__gradient_function(weighted_inputs[layer_index], activations[layer_index], layer_index)

			layer_gradient = np.multiply(overall_gradient, activations_gradient)

			gradients = [np.dot(inputs[layer_index].transpose(), layer_gradient)  - self.regularization * self.weights_[layer_index]] + gradients

			overall_gradient = self.__remove_offset(np.dot(overall_gradient, self.weights_[layer_index].transpose()))

		return gradients

	def update_weights(self, gradients, step_size):
		for layer_index in range(self.num_layers_):
			self.weights_[layer_index] += step_size * gradients[layer_index]

	def score(self, X, y, sample_weight = None):
		y_hat = self.predict_proba(X)
		return self.__eval_obj_fun(y, y_hat, sample_weight)

	def accuracy(self, X, y):
		y_hat = self.predict(X)
		return 1. * np.sum(int(np.argmax(y, axis = 1) == np.argmax(y_hat, axis = 1))) / y.shape[0]

	def __eval_obj_fun(self, y, y_hat, sample_weight = None, regularization = 0.):
		if self.obj_fun in ['maxent', 'logistic']:
			eps = 1e-10
			y_hat = np.clip(y_hat, eps, 1. - eps)
			err_matrix = np.multiply(y, np.log(y_hat)) + np.multiply(1. - y, np.log(1. - y_hat))
		elif self.obj_fun in ['lsq', 'least squares']:
			err_matrix = -1. * np.square(y - y_hat)
		elif self.obj_fun in ['mll']:
			eps = 1e-10
			y_hat = np.clip(y_hat, eps, 1.)
			err_matrix = np.multiply(y, np.log(y_hat))
		else:
			raise ValueError("Objective function '" + self.obj_fun + "' is not supported.")
		
		if type(sample_weight) != type(None):
			err_matrix = np.dot(np.diag(sample_weight), err_matrix)
		return np.sum(err_matrix) - regularization * np.sum([np.sum(np.square(self.__remove_offset(x))) for x in self.weights_])
		


	def __obj_fun_gradient(self, y, y_hat, sample_weight = None):
		if self.obj_fun in ['maxent', 'logistic']:
			eps = 1e-10
			y_hat = np.clip(y_hat, eps, 1. - eps)
			grad = np.divide(y, y_hat) - np.divide(1. - y, 1. - y_hat)
			if type(sample_weight) != type(None):
				grad = np.dot(np.diag(sample_weight), grad)
			return grad
		elif self.obj_fun in ['lsq', 'least squares']:
			grad = y_hat - y
			if type(sample_weight) != type(None):
				grad = np.multiply(sample_weight, grad)
			return grad
		elif self.obj_fun in ['mll']:
			eps = 1e-10
			y_hat = np.clip(y_hat, eps, 1. - eps)
			grad = np.divide(y, y_hat)
			if type(sample_weight) != type(None):
				grad = np.dot(np.diag(sample_weight), grad)
			return grad
		else:
			raise ValueError("Objective function '" + self.obj_fun + "' is not supported.")

	def __transform_function(self, X, layer_index):
		funct = self.layers[layer_index][1]

		if funct in ['logistic']: #1/ (1 + exp(x))
			X_transformed = 1. / (1. + np.exp(np.clip(-1.*X, -1e100, 50)))
		elif funct in ['tanh']: #tanh(x)
			X_transformed = np.tanh(X)
		elif funct in ['rectifier', 'hinge']: #max(0, x)
			X_transformed = np.clip(X, 0, 1e100)
		elif funct in ['softmax', 'multinomial']:
			exp_X = np.exp(np.clip(X, -1e100, 50))
			X_transformed = np.divide(exp_X, np.sum(exp_X, axis = 1)[:, np.newaxis])
		elif funct in ['linear', 'none', None]:
			X_transformed = X
		else:
			raise ValueError("Transform function '" + funct + "' is not supported.")

		return X_transformed

	def __gradient_function(self, X_weighted, Z, layer_index):
		funct = self.layers[layer_index][1]

		if funct in ['logistic']: #1/ (1 + exp(-x))
			Z_grad = np.multiply(np.square(Z), np.exp(np.clip(-1.*X_weighted, -1e100, 50)))
		elif funct in ['tanh']: #tanh(x)
			Z_grad = 1. - np.square(np.tanh(X_weighted))
		elif funct in ['rectifier', 'hinge']: #max(0, x)
			Z_grad = Z.copy()
			Z_grad[np.nonzero(Z_grad)] = 1.
		elif funct in ['softmax', 'multinomial']:
			sig = 1. / (1 + np.exp(np.clip(-1. * X_weighted, -1e100, 50)))
			Z_grad = np.multiply(Z, 1 - Z)	
		elif funct in ['linear', 'none', None]:
			Z_grad = np.ones(Z.shape) * 1.
		else:
			raise ValueError("Transform function '" + funct + "' is not supported.")

		return Z_grad

	def __add_offset(self, X):
		if self.include_offset:
			results = np.empty((X.shape[0], X.shape[1] + 1))
			results[:, 0] = 1
			results[:, 1:] = X
			return results
		else:
			return X.copy()

	def __remove_offset(self, X):
		if self.include_offset:
			return X[:, 1:]
		else:
			return X.copy()

	def __get_step_size(self, t = None, last_step = None, last_obj_val = None, obj_val = None):
		if self.learning_schedule == 'fixed':
			return self.step_size/(t + 1.)**.5
		elif self.learning_schedule == 'bold driver':
			growth_rate = 1.02
			if last_obj_val < obj_val:
				return last_step * growth_rate
			else:
				return last_step / growth_rate *.5


	def get_params(self, deep = True):
		return {'layers' : self.layers, 
				'obj_fun' : self.obj_fun, 
				'regularization' : self.regularization,
				'init_size' : self.weights,
				'include_offset' : self.include_offset,
				'restarts' : self.restarts,
				'step_size' : self.step_size,
				'learning_schedule' : learning_schedule,
				'max_iter' : self.max_iter,
				'criterion' : self.criterion}

	def set_params(self, **parameters):
	    for parameter, value in parameters.items():
	        self.setattr(parameter, value)
	    return self


class NeuralLogistic(NeuralNetwork):

	def __init__(self, **kwargs):
		layers = [(None, 'softmax')]
		obj_fun = 'maxent'
		NeuralNetwork.__init__(self, layers, obj_fun, restarts = 10, step_size = 1e-1)



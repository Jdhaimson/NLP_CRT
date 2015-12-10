from sklearn.linear_model import LogisticRegression, LinearRegression
import random
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

def plot_predictions(X, y, model = None, title = ""):


	h = .025
	x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
	y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
	plt.figure()
	if model != None:
		xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

		# Obtain labels for each point in mesh. Use last trained model.
		Z = model.predict(np.c_[xx.ravel(), yy.ravel()])


		# Put the result into a color plot
		Z = Z.reshape(xx.shape)
		to_rgb = mcolors.ColorConverter().to_rgb
		
		plt.clf()
		plt.imshow(Z, interpolation='nearest',
		           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
		           cmap=plt.cm.brg,
		           aspect='auto', origin='lower')

	# # Plot also the training points
	colors = ["blue", "red", "green", 'orange']
	if y.shape[1] == 2:
		colors = ['blue', 'green']
	# #print compress(y)
	y_c = compress(y)
	labs = np.unique(list(range(y.shape[1])))

	for i, color in zip(labs, colors):
		#print i
		idx = np.where(y_c == i)
		plt.scatter(X[idx, 0], X[idx, 1], c=color)
	plt.title(title)
	plt.axis('tight')

	# colors = [to_rgb(x) for x in ['red','blue', 'green']]

	# plt.plot(X[:, 0], X[:, 1], '.', markersize=4)
	plt.show()

def sparsify_data(X, sparsity = .5, noise = .01):
	d = X.shape[1]
	d_sparse = int(d / sparsity)
	new_X = np.random.rand(X.shape[0], d_sparse) * noise - noise / 2.
	new_X[:, :d] = X
	return new_X

def compress(array):
	return np.matrix([[i for i in range(len(x)) if x[i] == max(x)][0] for x in array]).transpose()

def prediction_accuracy(X, y, model):
	y_hat = model.predict(X)
	correct = sum([int(y[i,y_hat[i]] == 1) for i in range(len(y_hat))])
	return 1. * correct / len(y_hat)

def generate_data(means = [(0, 0), (5, 0), (2.5, 2.5)], stdev = 1., classes = 3, n = 50):
	#gaussian 1
	K = len(means)
	X = np.empty((n*K, max([len(x) for x in means])))
	y = np.zeros((n*K, classes))
	for k in range(K):
		for i in range(len(means[k])):
			X[k*n : (k+1)*n,i] = [random.gauss(means[k][i], stdev) for j in range(n)]
		y[k*n : (k+1)*n, k % classes] = 1
	return (X, y)

def make_synthetic_data(means = [(0, 0), (2.5, -2.5), (5, 0), (2.5, 2.5)], stdev = 1., classes = 2, n = 50):
	pass
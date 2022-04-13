from keras.datasets import mnist
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score


def logistic(x):
    return 1.0 / (1 + np.exp(-x))


def flatten(x):
    x = np.where(x > 127, 1, 0)
    return x.reshape(x.shape[0], -1)


class RBM:
    def __init__(self, hidden_units, visible_units = (28*28)):
        self.nh = hidden_units
        self.nv = visible_units
        self.weights = np.random.uniform(-1/self.nv, 1/self.nv, (self.nv, self.nh))
        self.bias_h = np.zeros(self.nh)
        self.bias_v = np.zeros(self.nv)
        print("Built a RBM with " + str(self.nv) + " visible units and " + str(self.nh) + " hidden units")


    def train(self, Xtr, epochs = 100, learning_rate = 0.1):
        n = 6000

        print("Training on " + str(n) + " random elements for " + str(epochs) + " epochs")
        for epoch in range(epochs):
            # Clamp data
            idx = np.random.uniform(low = 0, high = Xtr.shape[0], size=n).astype(int)
            cXtr = Xtr[idx,:]

            # Wake phase
            # Hidden probability
            h_prob = logistic(np.dot(cXtr, self.weights) + self.bias_h)
            wake = np.dot(cXtr.T, h_prob)

            # Dream phase
            # Hidden states
            h_state = h_prob > np.random.rand(n, self.nh)
            # Reconstruction probability
            reconstruction_data_prob = logistic(np.dot(h_state, self.weights.T) + self.bias_v)
            # Reconstructed data
            reconstruction_data = reconstruction_data_prob > np.random.rand(n, self.nv)
            h_neg_prob = logistic(np.dot(reconstruction_data, self.weights) + self.bias_h)
            dream = np.dot(reconstruction_data.T, h_neg_prob)

            # Learning phase
            error = np.sum((cXtr - reconstruction_data)**2)/n
            dW = (wake - dream)/n
            dBh = (np.sum(h_prob) - np.sum(h_neg_prob))/n
            dBv = (np.sum(cXtr) - np.sum(reconstruction_data))/n
            self.weights += learning_rate*dW
            self.bias_h += learning_rate*dBh
            self.bias_v += learning_rate*dBv
            print("\rError:\t" + "{:.5f}".format(error), end="")
        print("")


    def get_hidden_activations(self, Xtr):
        n = Xtr.shape[0]

        print("Computing hidden activations for " + str(n) + " elements")
        h_states = np.ones((n, self.nh))

        h_prob = logistic(np.dot(Xtr, self.weights) + self.bias_h)
        h_states[:,:] = h_prob > np.random.rand(n, self.nh)
        return h_states


(Xtr, ytr), (Xts, yts) = mnist.load_data()
print(str(Xtr.shape[0]) + " images of " + str(Xtr.shape[1]) + "x" + str(Xtr.shape[2]) + " pixels =>", end = " ")
Xtr = flatten(Xtr)
Xts = flatten(Xts)
print(str(Xtr.shape[0]) + " vectors " + str(Xtr.shape[1]) + " elements")
RBM = RBM(visible_units = (28*28), hidden_units = 500)
RBM.train(Xtr, epochs=100, learning_rate=0.01)

Xtr_h = RBM.get_hidden_activations(Xtr)
Xts_h = RBM.get_hidden_activations(Xts)
print("")
print("Building the MLP classifier")
classifier = MLPClassifier(hidden_layer_sizes=(300,200,), learning_rate_init=0.001)
print("Classifier training started")
classifier.fit(Xtr_h, ytr)
print("Classifier training ended")
print("Gathering classifier predictions")
predicted = classifier.predict(Xts_h)
print("Computing accuracy score")
accuracy = accuracy_score(yts, predicted)
print("Accuracy on test set of {:.2f}%".format(accuracy*100))
print("")
print("Building the K-NN classifier")
classifier = KNeighborsClassifier(5)
print("Classifier training started")
classifier.fit(Xtr_h, ytr)
print("Classifier training ended")
print("Gathering classifier predictions")
predicted = classifier.predict(Xts_h)
print("Computing accuracy score")
accuracy = accuracy_score(yts, predicted)
print("Accuracy on test set of {:.2f}%".format(accuracy*100))
print("")
print("Building the random classifier")
classifier = DummyClassifier(strategy='uniform')
print("Classifier training started")
classifier.fit(Xtr_h, ytr)
print("Classifier training ended")
print("Gathering classifier predictions")
predicted = classifier.predict(Xts_h)
print("Computing accuracy score")
accuracy = accuracy_score(yts, predicted)
print("Accuracy on test set of {:.2f}%".format(accuracy*100))

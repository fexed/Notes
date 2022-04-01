from keras.datasets import mnist
import numpy as np


def logistic(x):
    return 1.0 / (1 + np.exp(-x))


def flatten(x):
    return x.reshape(x.shape[0], -1)


class RBM:
    def __init__(self, hidden_units, visible_units = (128*128)):
        self.nh = hidden_units
        self.nv = visible_units
        self.weights = np.random.uniform(-1/self.nv, 1/self.nv, (self.nv, self.nh))
        self.bias_h = np.zeros(self.nh)
        self.bias_v = np.zeros(self.nv)

    def train(self, Xtr, epochs = 100, learning_rate = 0.1):
        n = 6000

        print("Training on " + str(n) + " elements for " + str(epochs) + " epochs")
        for epoch in range(epochs):
            # Clamp data
            idx = np.random.uniform(low = 0, high = Xtr.shape[0], size=n).astype(int)
            cXtr = Xtr[idx,:]

            # Wake phase
            # Hidden probability
            h_prob = logistic(-np.dot(cXtr, self.weights) - self.bias_h)
            wake = np.dot(cXtr.T, h_prob)

            # Dream phase
            # Hidden states
            h_state = h_prob > np.random.rand(n, self.nh)
            # Reconstruction probability
            reconstruction_data_prob = logistic(-np.dot(h_state, self.weights.T) - self.bias_v)
            # Reconstructed data
            reconstruction_data = reconstruction_data_prob > np.random.rand(n, self.nv)
            h_neg_prob = logistic(-np.dot(reconstruction_data, self.weights) - self.bias_h)
            dream = np.dot(reconstruction_data.T, h_neg_prob)

            # Learning phase
            error = np.sum(np.abs(cXtr - reconstruction_data) ** 2)/n
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
        #Xtr = np.insert(Xtr, 0, 1, axis = 1)  # bias of 1 in first column
        h_states = np.ones((n, self.nh))  # hidden units plus bias

        h_prob = logistic(-np.dot(Xtr, self.weights) - self.bias_h)
        h_states[:,:] = h_prob > np.random.rand(n, self.nh)
        return h_states


(Xtr, ytr), (Xts, yts) = mnist.load_data()
RBM = RBM(visible_units = (28*28), hidden_units = 25)
print(str(Xtr.shape[0]) + " immagini di " + str(Xtr.shape[1]) + "x" + str(Xtr.shape[2]) + " pixel =>", end = " ")
Xtr = flatten(Xtr)
Xts = flatten(Xts)
print(str(Xtr.shape[0]) + " vettori di " + str(Xtr.shape[1]) + " elementi")
RBM.train(Xtr, epochs=1000, learning_rate=0.01)

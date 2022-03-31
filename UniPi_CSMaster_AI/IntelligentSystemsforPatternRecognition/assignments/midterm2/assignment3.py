from keras.datasets import mnist
import numpy as np


def logistic(x):
    return 1.0 / (1 + np.exp(-x))


class RBM:
    def __init__(self, hidden_units, visible_units = (128*128)):
        self.nh = hidden_units
        self.nv = visible_units
        self.weights = np.random.uniform(-1/self.nv, 1/self.nv, (self.nv, self.nh))
        self.weights = np.insert(self.weights, 0, 0, axis = 0)  # bias on first row
        self.weights = np.insert(self.weights, 0, 0, axis = 1)  # bias on first column

    def train(self, Xtr, epochs = 100, learning_rate = 0.1):
        n = Xtr.shape[0]
        Xtr = np.insert(Xtr, 0, 1, axis = 1)  # bias of 1 in first column

        for epoch in range(epochs):
            # Wake phase
            # Hidden probability
            h_prob = logistic(np.dot(Xtr, self.weights))  # -Xtr?
            wake = np.dot(Xtr.T, h_prob)

            # Dream phase
            # Hidden states
            h_state = h_prob > np.random.rand(n, self.nh + 1)
            # Reconstruction probability
            reconstruction_data_prob = logistic(np.dot(h_state, self.weights.T))
            # Reconstructed data
            reconstruction_data = reconstruction_data_prob > np.random.rand(n, self.nv + 1)
            h_neg_prob = logistic(np.dot(reconstruction_data, self.weights))
            dream = np.dot(reconstruction_data.T, h_neg_prob)

            error = np.sum((Xtr - reconstruction_data) ** 2)
            dW = (wake - dream) / n
            self.weights += learning_rate * dW
            print("\rError is:\t" + "{:.5f}".format(error), end="")
        print("")

    def get_hidden_activations(self, Xtr):
        n = Xtr.shape[0]
        Xtr = np.insert(Xtr, 0, 1, axis = 1)  # bias of 1 in first column
        h_states = np.ones((n, self.nh + 1))  # hidden units plus bias

        h_prob = logistic(np.dot(Xtr, self.weights))  # -Xtr?
        h_states[:,:] = h_prob > np.random.rand(n, self.nh + 1)
        h_states = h_states[:,1:]  # ignore biases
        return h_states


(Xtr, ytr), (Xts, yts) = mnist.load_data()
RBM = RBM(visible_units = (128*128), hidden_units = 50)

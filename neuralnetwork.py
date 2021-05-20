import numpy as np


class NeuralNetwork:

    def __init__(self, layer_sizes):
        self.weights = []
        self.biases = []

    def predict(self, a):
        for w in self.weights:
            #z = np.matmul(w,a) + b
            #print(z[0])
            a = self.activation(np.matmul(w,a))
        return a

    def generate_genome(self, layer_sizes):
        weight_shapes = [(a,b) for a,b in zip(layer_sizes[1:], layer_sizes[:-1])]
        weights = [np.random.standard_normal(s)/s[1]**.5 for s in weight_shapes]
        self.weights = weights
        return np.concatenate([item for sublist in weights for item in sublist])

    def import_genome(self, genome, layer_sizes):
        weight_shapes = [(a,b) for a,b in zip(layer_sizes[1:], layer_sizes[:-1])]
        weights = []
        chunks = []
        pos = 0
        # split genome into array of arrays of size (rows*columns)
        for i in range(len(weight_shapes)):
            length = weight_shapes[i][0] * weight_shapes[i][1]
            chunks.append(genome[pos: pos + length])
            pos += length
        # reshape each chunk into matrix of shape defined in weight_shapes
        for i in range(len(chunks)):
            weights.append(np.reshape(chunks[i], weight_shapes[i]))

        self.weights = weights
        #print("WEIGHTS:\n",self.weights)
        return weights

    def import_biases(self, bias_genome, layer_sizes):
        for layer in range(len(layer_sizes)):
            # Get slice of bias genome that will be each bias array
            self.biases.append(bias_genome[layer*layer_sizes[layer]:(layer+1)*layer_sizes[layer]])

    @staticmethod
    def activation(x):
        return np.tanh(x)
        #return (1/(1+np.exp(-np.clip(x, a_min = -4, a_max = 4))))

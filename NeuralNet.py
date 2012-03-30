from collections import deque
from Graph import Graph

"""
instead of `class Neuron`, each neuron in the net is simply represented as 
    a tuple of (value, threshold, rest_value) at each node of a graph
"""

class NeuralNet:
    
    DEAFULT_REST = 0.5
    DEFAULT_THRESH = 1
    
    def __init__(self, n_inputs, n_layers, layer_sizes=[], weights=[]):
        if n_layers < 2:
            n_layers = 2
        if n_inputs < 1:
            n_inputs = 1
        
        self.graph = Graph()
        edge_index = 0
        
        for i in range(n_inputs)
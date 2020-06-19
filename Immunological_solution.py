import numpy as np 
import math
import utility
import os

from Propagation import Propagation

class Immunological_solution:
    def __init__(self, id_nodes: list, edges: list, real_vect: list, max_age = 5):
        # Id node
        self.id_nodes = id_nodes
        # Lista dei pesi degli archi
        self.edges = np.array(edges)
        # Real vector
        self.real_vect = real_vect
        # Valore di fitness della soluzione
        self.fitness = 0
        # Età massima della soluzione
        self.max_age = max_age

        # Vita della soluzione
        self.age = np.random.randint(0, (2 * max_age) / 3)

        self.propagation = Propagation()

    def __fbeta_score(self, tri_vect, idx: int):
        tp, fp, tn, fn = 0, 0, 0, 0

        for i in range(0, len(self.real_vect[idx])):
            if tri_vect[i] > 0 and self.real_vect[idx][i] == 1:  # tp
                tp += 1
            if tri_vect[i] > 0 and self.real_vect[idx][i] == 0:  # fp
                fp += 1
            if tri_vect[i] == 0 and self.real_vect[idx][i] == 0:   # tn
                tn += 1
            if tri_vect[i] == 0 and self.real_vect[idx][i] == 1:   # fn 
                fn += 1

        ppv = tp / (tp + fp)
        tpr = tp / (tp + fn)
        # beta grande! 
        beta = 3
        fbeta_score = (1 + beta**2) * ppv * tpr / ((beta**2 * ppv) + tpr)
        return fbeta_score

    def __update_weights(self, edges_dict: dict):
        # Prendere il grafo
        G = self.propagation.get_Graph()
        # Aggiornare i pesi
        i = 0
        for u, v in edges_dict:
            G.edges[u, v]['prop_weight'] = float(self.edges[i])
            i += 1
        # Settare il grafo
        self.propagation.set_Graph(G)

    def compute_fitness(self, edges_dict: dict):
        # Aggiornare i pesi
        self.__update_weights(edges_dict)
        # Trivector
        fit_list = []
        for i in range(len(self.id_nodes)):
            tri_vect = self.propagation.trivector_train(self.id_nodes[i])
            # f_beta score
            fit_list.append(self.__fbeta_score(tri_vect, i))
        
        self.fitness = np.mean(fit_list)

    def hypermutation(self, rho):
        alpha = math.exp(-rho * self.fitness)
        number_of_mutation = math.floor((alpha * len(self.edges)))

        std = (1 - self.fitness) / 5
        for _ in range(number_of_mutation):
            r = np.random.randint(0, len(self.edges)-1)
            w = np.random.normal(self.edges[r], std)
            if w < 0:
                w = 0
            if w > 1:
                w = 1
            self.edges[r] = w

    def increment_age(self):
        self.age += 1

    def set_random_age(self):
        self.age = np.random.randint(0, (2 * self.max_age) / 3)

    def set_fitness(self, fitness):
        self.fitness = fitness
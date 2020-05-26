from Genetic_algorithm import Genetic_algorithm
from Propagation import Propagation
import graph_algorithm as ga 
import numpy as np 

real_vect = np.load("Data/real_vectors/2233.npy")

p = Propagation()
tri_vect = p.trivector_train('1867')

SG = ga.get_trivector_subgraph(tri_vect, real_vect)

gen = Genetic_algorithm('1867', SG.edges)
gen.start(epochs=20)
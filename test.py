from Genetic_algorithm import Genetic_algorithm
from Propagation import Propagation
import graph_algorithm as ga 
import numpy as np 
import utility
import networkx as nx
from scipy import sparse

G = utility.load_graph("graphlow.gexf")
for u in G.nodes():
    if "Ragalna" in G.nodes[u]['city_names']:
        G.nodes[u]['priority'] = .5

nx.write_gexf(G, "ragalna.gexf")
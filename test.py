from Genetic_algorithm import Genetic_algorithm
from Propagation import Propagation
import graph_algorithm as ga 
import numpy as np 
import utility
import networkx as nx
from scipy import sparse

G = utility.load_graph()
priority = {}
for u in G.nodes():
    priority[u] = G.nodes[u]["is_city"]

G_new = ga.delete_graph_attribute(G, "is_city", True)
G_new = ga.add_graph_attribute(G, "priority", True, priority)
nx.write_gexf(G_new, "graph_gexf/graphlow_new.gexf")
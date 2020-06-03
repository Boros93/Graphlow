from Genetic_algorithm import Genetic_algorithm
from Propagation import Propagation
import graph_algorithm as ga 
import numpy as np 
import utility
import networkx as nx
from scipy import sparse


""" vent_list = [1503, 1429, 1431, 1575, 1577, 
    1870, 1796, 1798, 1942, 1944,
    1222, 1148, 1150, 1294, 1296]

node_list = []
with open("Data/node_vent_csv.csv", 'r') as csv_file:
    lines = csv_file.readlines()
    for vent in vent_list:
        for line in lines:
            if str(vent) + "," in line:
                node_list.append(line.split(',')[1][:-1])
                break

SG = nx.read_gexf("graph_gexf/genetic_graph.gexf")
g = Genetic_algorithm(vent_list, node_list, SG.edges)
g.start(epochs=100)

 """



def get_vent_chessboard(x, y, size = 10, step = 4):
    node_matrix = np.load("Data/node_matrix.npy")
    node_list = []
    for i in range(0, size):
        if i % 2 == 0:
            j_start = 0
        else:
            j_start = int(step/2)

        for j in range(j_start, size, step):
            node_list.append(node_matrix[x + i][y + j])
    
    return node_list

vent_matrix = np.load("Data/vent_matrix.npy")

node_list = get_vent_chessboard(0, 1)
print(node_list, len(node_list))
G = utility.load_graph()
for node in node_list:
    G.nodes[str(node)]["current_flow"] = 1

nx.write_gexf(G, "grafo.gexf")

""" vents = [1503, 1429, 1431, 1575, 1577, 
    1870, 1796, 1798, 1942, 1944,
    1222, 1148, 1150, 1294, 1296]

real_vect_list = []
for v in vents:
    real_vect_list.append(np.load("Data/real_vectors/" + str(v) + ".npy"))

real_vect = np.load("Data/real_vectors/2210.npy")

p = Propagation()
tri_vect = p.trivector_train('880')

#SG = ga.get_trivector_subgraph(tri_vect, real_vect)

gen = Genetic_algorithm('880', SG.edges)
gen.start(epochs=100) """


""" #trivector neumann 1 in 1503, 1870, 1222
p = Propagation()
tri_vect_list = []
tri_vect_list.append(p.trivector([1503, 1429, 1431, 1575, 1577]))
tri_vect_list.append(p.trivector([1870, 1796, 1798, 1942, 1944]))
tri_vect_list.append(p.trivector([1222, 1148, 1150, 1294, 1296]))

#get real 1503 neu1, 1870 neu1, 1222 neu1

real_vect = np.zeros(5820)
tri_vect = np.zeros(5820)
#scoro real_vect e tri_vect
for i in range(5820):
    # scoro tri_vect_list
    for tri in tri_vect_list:
        if tri[i] > 0:
            tri_vect[i] = 1
            break

    #scoro vect list
    for vect in vect_list:
        if vect[i] > 0:
            real_vect[i] = 1
            break

#get sub graph
SG = ga.get_trivector_subgraph(tri_vect, real_vect)
nx.write_gexf(SG, "graph_gexf/genetic_graph.gexf") """
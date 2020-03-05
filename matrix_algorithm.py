import numpy as np
from numpy import linalg as la
from utility import load_graph
from graph_maker import export_graph
from map_creator import graph_to_UTM

def minimize_norm(id_vent):
    #W = np.load("graph_matrix.npy")
    W = np.load("graph_matrix_col_normalized.npy")
    norm = la.norm(W)

    X = np.zeros(W.shape[0])

    X [id_vent] = 1 #mettere id bocca nel grafo
    acc = X
    count = 0
    while norm > 0.0001:
        WX = np.dot(W, X)
        
        acc += WX
        X = WX
        norm = la.norm(X, ord = np.inf)
        count += 1
    
    np.savetxt("acc.txt", acc)
    G = norm_to_graph(acc)
    graph_to_UTM(G, "ASCII_grids/ASCII_norm_from_col_normalization.txt")

#normalizzo la matrice sulle colonne
def normalize_column():
    W = np.load("graph_matrix.npy")
    sums = np.zeros(W.shape[1])
    for j in range(0, W.shape[1]):
        for i in range(0, W.shape[0]):
            sums[j] += W[i][j]

    for j in range(0, W.shape[1]):
        for i in range(0, W.shape[0]):
            if not sums[j] == 0:
                W[i][j] = W[i][j]/ sums[j]

    np.save("graph_matrix_col_normalized.npy", W)

# assegno i valori del vettore risultante dal metodo minimize_norm ai nodi del grafo
def norm_to_graph(np_vect):
    G = load_graph()
    for u in G.nodes():
        G.node[u]["current_flow"] = np_vect.item(int(u))

    export_graph(G, "norm_from_col_normalization_graph.gexf", False)
    return G

    

print("normalizzo colonne\n\n\n")
normalize_column()
print("\n\n\nminimizzo la norma\n\n\n")
id_vent = 3383
minimize_norm(id_vent)
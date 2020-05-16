from glob import glob
import numpy as np
import conversion
import utility
import networkx as nx
import numpy as np 
import os
from scipy import sparse

# ottiene un vettore di cardinalità 5820 dalle simulazioni unificate di MAGFLOW
def vect_sim(id_vent):
    #matrice 91*75
    M = np.zeros((91, 75), dtype=int)
    # carico la lista dei file delle simulazioni
    filelist = glob("Data/simulations/NotN_vent_" + str(id_vent) + "_" + "*"  + ".txt")
    if len(filelist) == 0:
        return
    print("vent: ", id_vent)
    for vent_file in filelist:
        #apre ogni singolo file
        with open(vent_file, 'r') as in_file:
            # legge ogni riga del file
            for line in in_file:
                row, col = line.split(" ")
                row = int(row)
                col = int(col)
                #per ogni riga del file inserisce 1 nella matrice
                M[int(row / 25)][int(col / 25)] = 1

    #carica il grafo
    G = utility.load_graph()
    #istanzia il vettore di output
    vect = np.zeros((len(G.nodes)), dtype= int)
    #scorre i nodi del grafo
    for u in G.nodes():
        # si ottiene una lista di coordinate
        coords = G.nodes[u]['coord_regions'].split("|")
        for coord in coords:
            # ottiene il valore di riga e colonna
            row, col = conversion.cast_coord_attr(coord)
            # si riempie il vettore in posizione u con il valore di M(row, col)
            vect[int(u)] = M[row][col]
    filename = "Data/real_vectors/" + str(id_vent)
    # esporta il vettore
    np.save(filename, vect)

# inserisce i pesi ottenuti dall'allenamento nei nodi del grafo.
def set_new_G_weights():
    G = utility.load_graph()
    # carico i pesi da inserire in G
    W = sparse.load_npz("weights_relu.npz").toarray() #5820 x 5820

    min_W = np.min(W)
    max_W = np.max(W)
    for i in range(0, W.shape[0]):
        for j in range(0, W.shape[1]):
            W[i][j] = (W[i][j] - min_W) / (max_W - min_W)

    min_W = np.min(W)
    max_W = np.max(W)
    for u,v,data in G.edges(data=True):
        G.edges[u,v]["prop_weight"] = (W[int(u)][int(v)] - min_W) / (max_W - min_W)

    nx.write_gexf(G, "test_relu.gexf")

#set_new_G_weights()
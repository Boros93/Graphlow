from glob import glob
import numpy as np
import conversion
import utility
import networkx as nx
import numpy as np 
import os

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
    filename = "nn/test_set/" + str(conversion.get_node_from_idvent(id_vent))
    # esporta il vettore
    np.save(filename, vect)

# divide l'insieme di vettori delle simulazioni in test, train e validation set
def split_dataset():
    dataset_path = "nn/"
    train_set_path = "train_set/" # 70%
    test_set_path = "test_set/" # 30%

    file_list = glob(dataset_path + "*" + ".npy")
    np.random.seed(33)
    idx = np.random.permutation(len(file_list))
    train_size = int(len(file_list) * 0.7)
    
    for i in range(0, train_size):
        filename = file_list[idx[i]]
        # isola il nome del file
        filename = os.path.basename(filename)
        # sposta il file nella cartella del train_set
        os.rename(dataset_path + filename, dataset_path + train_set_path + filename)
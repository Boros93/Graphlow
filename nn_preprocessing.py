from glob import glob
import numpy as np
import conversion
import utility
import networkx as nx
import numpy as np 

def vect_sim(id_vent):
    #matrice 91*75
    M = np.zeros((91, 75), dtype=int)
    # carico la lista dei file delle simulazioni
    
    filelist = glob("Data/simulations/NotN_vent_" + str(id_vent) + "*"  + ".txt")
    
    for vent_file in filelist:
        with open(vent_file, 'r') as in_file:
            for line in in_file:
                row, col = line.split(" ")
                row = int(row)
                col = int(col)
                M[int(row / 25)][int(col / 25)] = 1

    G = utility.load_graph()
    vect = np.zeros((len(G.nodes)), dtype= int)
    for u in G.nodes():
        coords = G.node[u]['coord_regions'].split("|")
        for coord in coords:
            row, col = conversion.cast_coord_attr(coord)
            vect[int(u)] = M[row][col]
    filename = str(conversion.get_node_from_idvent(id_vent))
    np.save(filename, vect)

vect_sim(2233)
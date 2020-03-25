import networkx as nx
import utility
import numpy as np
import graph_algorithm as ga
from scipy import sparse

# ============================ HEADER =============================
# estremi coordinate nord e ovest della griglia DEM
NORTH = 4192500
SOUTH = 4147000
EAST = 520000
WEST = 482500
# Dimensioni della griglia: numero righe e colonne
ROWS = 91
COLS = 75

header = ["north: " + str(NORTH), "south: " + str(SOUTH),
            "east: " + str(EAST), "west: " + str(WEST), 
            "rows: " + str(ROWS), "cols: " + str(COLS)]
destination_path = "ASCII_grids/"

def graph_to_UTM(G, filename):
    utm_map = np.zeros((ROWS, COLS), dtype=float)

    for u, data in G.nodes(data = True):
        for coords in data["coord_regions"].split("|"):
            coord_x, coord_y = utility.cast_coord_attr(coords)
            utm_map[coord_x][coord_y] = data["current_flow"]
    # scrittura header
    with open(filename, 'w') as utmfile:
        for i in range(0, len(header)):
            utmfile.write(header[i] + "\n")

        for x in range(0, ROWS):
            for y in range(0, COLS):
                utmfile.write(str(utm_map[x][y]) + " ")
            utmfile.write("\n")

def matrix_to_UTM(sparse_matrix, id_vent, char):  #metodo che serve per convertire vettori sparsi in formato utm
                            #utilizzato per applicare le metriche di fitting
                            # sparse_matrix è un vettore sparso di uno
    print("\nExporting UTM file...")
    sparse_matrix = sparse.load_npz("sparse/sparse_sim_" + char + "_" + str(id_vent) + ".npz")
    M = sparse_matrix.toarray()


    utm_filename = "ASCII_grids/u" + char + "sim_" + str(id_vent) + ".txt"
    with open(utm_filename, 'w') as utmfile:
        for i in range(0, len(header)):
            utmfile.write(header[i] + "\n")
    
        for x in range(0, ROWS):
            for y in range(0, COLS):
                utmfile.write(str(M[x][y]) + " ")
            utmfile.write("\n")
    print("\nDone.\n")
    
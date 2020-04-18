import networkx as nx
import utility
import numpy as np
import graph_algorithm as ga
import conversion
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
            coord_x, coord_y = conversion.cast_coord_attr(coords)
            utm_map[coord_x][coord_y] = data["current_flow"]
    # scrittura header
    with open(filename, 'w') as utmfile:
        for i in range(0, len(header)):
            utmfile.write(header[i] + "\n")

        for x in range(0, ROWS):
            for y in range(0, COLS):
                utmfile.write(str(utm_map[x][y]) + " ")
            utmfile.write("\n")

# Metodo che crea il file ascii data una matrice sparsa
def ascii_creator(id_vent, propagation_method, sparse_matrix):
    utm_filename = "ASCII_grids/" + propagation_method + "_" + str(id_vent) + ".txt"
    M = sparse_matrix.toarray() 
    with open(utm_filename, 'w') as utmfile:
        # Scrittura dell'header del file (northing...)
        for i in range(0, len(header)):
            utmfile.write(header[i] + "\n")
        # Scrittura valori nel DEM
        for x in range(0, ROWS):
            for y in range(0, COLS):
                if M[x][y] == 0:
                    utmfile.write("0" + " ")
                else:
                    utmfile.write(str(M[x][y]) + " ")
            utmfile.write("\n")
    
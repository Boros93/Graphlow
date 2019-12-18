import networkx as nx
import utility
import numpy as np
import graph_algorithm as ga

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
destination_path = "ASCII_grids\\"

def graph_to_UTM(G, filename):
    utm_map = np.zeros((ROWS, COLS), dtype=int)

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


# real simulation
sim_filename = "NotN_vent_3248_6.txt"
G_original = nx.read_gexf("graph_gexf\\scaled_map91x75.gexf")
G = ga.sim_to_graph(G_original, sim_filename)
graph_to_UTM(G, destination_path + "ASCII_grid_" + sim_filename[10:])

# eruption
'''graph_filename = "eruption3248.gexf"
G = nx.read_gexf("graph_gexf\\" + graph_filename)
graph_to_UTM(G, destination_path + "ASCII_grid_" + graph_filename[:-4] + "txt")'''



import networkx as nx
import utility

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
destination_path = "Extra\\"

def graph_to_UTM(G, filename):
    # scrittura header
    with open(filename, 'a') as utmfile:
        for i in range(0, len(header)):
            utmfile.write(header[i] + "\n")

        for x in range(0, ROWS):
            for y in range(0, COLS):
                for u, data in G.nodes(data = True):
                    for coords in data["coord_regions"].split("|"):
                        coord_x, coord_y = utility.cast_coord_attr(coords)
                        if coord_x == x and coord_y == y:
                            if not data["current_flow"] == 0:   
                                utmfile.write(str(data["current_flow"]) + " ")
                            else:
                                utmfile.write("*" + " ")
            
            utmfile.write("\n")

G = nx.read_gexf("graph_gexf\\eruption2233_vol100000_d10.gexf")

graph_to_UTM(G, destination_path +"provaprova.txt")
import networkx as nx
import utility
import numpy as np
import graph_algorithm as ga
import conversion
from scipy import sparse
from xml.dom import minidom

# ============================ HEADER =============================
# estremi coordinate nord e ovest della griglia DEM
NORTH = 4192500
SOUTH = 4147000
EAST = 520000
WEST = 482500
# Dimensioni della griglia: numero righe e colonne
ROWS = 91
COLS = 75
ROWS_DEM = 2275
COLS_DEM = 1875

header = ["north: " + str(NORTH), "south: " + str(SOUTH),
            "east: " + str(EAST), "west: " + str(WEST), 
            "rows: " + str(ROWS), "cols: " + str(COLS),
            "null: 0"]
destination_path = "ASCII_grids/"

def graph_to_UTM(G, filename):
    utm_map = np.zeros((ROWS, COLS), dtype=float)

    for u, data in G.nodes(data = True):
        for coords in data["coord_regions"].split("|"):
            coord_x, coord_y = conversion.cast_coord_attr(coords)
            utm_map[coord_x][coord_y] = data["is_city"]
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
    
# legge il file paesi-etnei.gml e ritorna una matrice nelle cui celle vi è 
# 1 se quella rappresenta un paese/città, zero altrimenti.
# inoltre ritorna una matrice di nomi delle città: 
# M(x, y) = ["Zafferana", "Bronte"]
def create_city_map():
    doc = minidom.parse("Data/urban_zones/paesi-etnei.gml")
    # Inizializzazione matrice "presenza città" e "nome città"
    cities_matrix = np.zeros((ROWS, COLS), dtype=float)
    cities_names_matrix = np.zeros((ROWS, COLS), dtype=object)

    count=0
    # Count per l'id dell'edificato
    ed_count = 0
    for featureMember in doc.getElementsByTagName("gml:featureMember"):
        # estrazione nome città dal file gml
        try:
            city_name = featureMember.getElementsByTagName("ogr:NOME")[0].childNodes[0].data
        except:
            city_name = "Edificato" + str(ed_count)
            ed_count += 1
        print("city_name", city_name)
        #estrazione lista coordinate UTM dal file gml. formato: x,y x,y x,y
        coord_line = featureMember.getElementsByTagName("gml:coordinates")[0].childNodes[0].data
        #elimino gli spazi inter-coordinate
        coord_list = coord_line.split(" ")
        for coord in coord_list:
            #rimuovo virgola intra-coordinate
            x_utm, y_utm = coord.split(",")
            # 0 < x < 91, 0 < y < 75
            # Conversione da utm di paesi-etnei.gml in coordinate DEM
            x, y = conversion.utm_to_matrix(x_utm, y_utm)
            # Downscaling
            x = int(x/25)
            y = int(y/25)
            #inserisco il valore 1 in cities per identificare che in x, y vi è una città/paese
            cities_matrix[x][y] = 1
            #inserisco il nome del paese/città in city_name_matrix per identificare che in x, y vi è il paese/ città city_name
            if cities_names_matrix[x][y] == 0:
                cities_names_matrix[x][y] = city_name + ","
            else:
                if not city_name in cities_names_matrix[x][y]:
                    cities_names_matrix[x][y] += city_name + ","
        count += 1
    print("Sono stati estratti ", count, "edificati.")
    
    return cities_matrix, cities_names_matrix

    

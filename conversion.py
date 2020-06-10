import utility
import csv

# numero di righe della griglia dei vent
ROWS_VENT = 73
# ampiezza in metri quadrati di ogni cella della griglia vent
STEP_VENT = 500
# estremi coordinate nord e ovest della griglia dei vent
EASTING_MIN_VENT = 482490
NORTHING_MAX_VENT = 4191990

# estremi coordinate nord e ovest della griglia DEM
NORTHING_MAX_DEM = 4192500
NORTHING_MIN_DEM = 4147000
EASTING_MIN_DEM = 482500
EASTING_MAX_DEM = 520000

# ampiezza in metri quadrati di ogni cella della griglia DEM
STEP_DEM = 20

def get_node_from_idvent(id_vent: str):
    filename = "Data/node_vent_csv.csv"
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[0] == id_vent:
                return row[1]

def get_vent_from_idnode(id_node: str):
    filename = "Data/node_vent_csv.csv"
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[1] == id_node:
                return row[0]

# Restituisce l'id del nodo, dato un id di un vent controllando le coordinate all'interno del grafo
def get_node_from_idvent_in_graph(id_vent):
    # La griglia dei vent parte da 1
    id_vent = int(id_vent) - 1
    # Ritorna le coordinate del vent nel DEM
    coord_vent = vent_in_dem(id_vent)
    G = utility.load_graph()
    # Date le coordinate del DEM, restituisce il nodo corrispondente
    node = get_id_from_coord(G, coord_vent)
    return node

# Conversion coordinate griglia vent in griglia DEM
def vent_in_dem(id_vent):
    # calcola coordinate della bocca nella griglia vent 
    #x_vent = (id_vent % ROWS_VENT) - 1
    x_vent = id_vent % ROWS_VENT
    y_vent = int(id_vent/ROWS_VENT)

    # calcola le coordinate nord e est della bocca
    northing_vent = NORTHING_MAX_VENT - (STEP_VENT * x_vent)
    easting_vent = EASTING_MIN_VENT + (STEP_VENT * y_vent)
    # calcola le coordinate della bocca nella griglia DEM
    x_dem = int((NORTHING_MAX_DEM - northing_vent) / STEP_DEM)
    y_dem =int((easting_vent - EASTING_MIN_DEM) / STEP_DEM)

    return (x_dem, y_dem)

def get_id_from_coord(G, coord):
    for u, data in G.nodes(data=True):
        for coords in data["coord_regions"].split("|"):
            coord_x, coord_y = cast_coord_attr(coords)
            if coord_x == int(coord[0]/25) and coord_y == int(coord[1]/25):
                return u

# casta le coordinate. "(row, col)" --> row col
def cast_coord_attr(coord):
    coord = coord.replace('(', '')
    coord = coord.replace(')', '')
    coord_x, coord_y = coord.split(',')
    coord_x = int(coord_x)
    coord_y = int(coord_y)
    return coord_x, coord_y

def id_from_not_n(not_n_filename):
    id_vent = int(not_n_filename[10: -6])
    return id_vent

# cast delle coordinate northing e easting in coordinate di una matrice (nel nostro caso 2275 x 1975, che sono le celle del DEM)
def utm_to_matrix(x_utm, y_utm):
    x_utm = float(x_utm)
    y_utm = float(y_utm)
    if x_utm > EASTING_MIN_DEM and x_utm < EASTING_MAX_DEM and y_utm > NORTHING_MIN_DEM and y_utm < NORTHING_MAX_DEM:
        # ritorna 
        # 515092.859538545,4185142.66594326
        y_dem = int((x_utm - EASTING_MIN_DEM) / STEP_DEM)
        x_dem = int((NORTHING_MAX_DEM - y_utm) / STEP_DEM)
    else:
        return [-1, -1]

    return x_dem, y_dem
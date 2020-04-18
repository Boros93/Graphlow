import utility

# Restituisce l'id del nodo, dato un id di un vent
def get_node_from_idvent(id_vent):
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
    # numero di righe della griglia dei vent
    ROWS_VENT = 73
    # ampiezza in metri quadrati di ogni cella della griglia vent
    STEP_VENT = 500
    # estremi coordinate nord e ovest della griglia dei vent
    EASTING_MIN_VENT = 482490
    NORTHING_MAX_VENT = 4191990

    # estremi coordinate nord e ovest della griglia DEM
    NORTHING_MAX_DEM = 4192500
    EASTING_MIN_DEM = 482500
    # ampiezza in metri quadrati di ogni cella della griglia DEM
    STEP_DEM = 20

    # calcola coordinate della bocca nella griglia vent 
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
    id_vent = int(not_n_filename[10: -6])-1
    return id_vent
import numpy as np
from region import Region
import csv
import networkx as nx
import os
import graph_algorithm as ga
import graph_maker as gm
import map_creator as mc

from scipy import sparse
from scipy.stats import uniform


# Metodo per caricare una linked map da file CSV
def load_csv_map(shapes, map_filename):
    # Creo la struttura dati vuota
    linked_map = np.empty((shapes[0],shapes[1]), dtype=object)
    # Inizializzo le coordinate di ogni regione 
    for x in range(0, linked_map.shape[0]):
        for y in range(0, linked_map.shape[1]):
            linked_map[x][y] = Region(coord=(x,y))
    with open(map_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        i = 0
        j = 0
        # Per ogni riga del CSV, aggiunge le simulazioni alla struttura dati
        for row in csv_reader:
            linked_map[i][j].add_list_sim(row)
            j += 1
            if j >= shapes[1]:
                i += 1
                j = 0
            line_count += 1
            if line_count % 1000 == 0:
                print("Line ", line_count, " processed")
    print("Linked Map created")
    return linked_map

# Metodo per salvare una linked map in un file CSV
def write_in_csv(csv_filename, l_map):
    print("Writing csv...")
    line_count = 0
    with open(csv_filename, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        for x in range(0, l_map.shape[0]):
            for y in range(0, l_map.shape[1]):
                filewriter.writerow(l_map[x][y].create_csv_row())
                line_count += 1
                if line_count % 10000 == 0:
                    print("Line ", line_count, " processed")
    print("CSV written")

def id_from_not_n(not_n_filename):
    id_vent = int(not_n_filename[10: -6])-1
    return id_vent

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

def cast_coord_attr(coord):
    coord = coord.replace('(', '')
    coord = coord.replace(')', '')
    coord_x, coord_y = coord.split(',')
    coord_x = int(coord_x)
    coord_y = int(coord_y)
    return coord_x, coord_y
    
def load_graph():
    if os.path.exists("graph_gexf/weight_norm_graph.gexf"):
        G = nx.read_gexf("graph_gexf/weight_norm_graph.gexf")
        return G
    else:
        print("Graph does not exists.")
        return None


def get_node_from_idvent(id_vent):
    id_vent = int(id_vent)
    coord_vent = vent_in_dem(id_vent)
    G = load_graph()
    node = ga.get_id_from_coord(G, coord_vent)
    return node

# Metodo per esportare il grafo sottoforma di matrice di adiacenza
# Taglio gli archi (v, u) se (v, u).trasmit < (u, v). trasmit
def graph_to_matrix(G):
    G = load_graph()
    n_nodes = len(G.nodes())

    M = np.zeros((n_nodes, n_nodes), dtype = float)

    for i in G.nodes():
        for j in G.successors(i):
            if G.edges[j, i]["trasmittance"] > G.edges[i, j]["trasmittance"]:
                M[int(i)][int(j)] = G.edges[j, i]["trasmittance"]
            else:
                M[int(j)][int(i)] = G.edges[i, j]["trasmittance"]
    
    np.save("graph_matrix.npy", M)

# genera una matrice sparsa che rappresenta l'unione delle simulazioni MAGFLOW della bocca specificata
def unify_sims(id_vent, char):
    simspath = "Data/simulations/"
    filelist = os.listdir(simspath)
    current_vent_files = []
    
    for filename in filelist:
        if int(id_vent) == id_from_not_n(filename) + 1:
            current_vent_files.append(filename)
    print("unisco i seguenti file:", current_vent_files)
    
    lines_to_write = []
    for f in current_vent_files:
        print("processing file", f)
        with open(simspath + f, 'r') as infile:
            for line in infile:
                if not line in lines_to_write:
                    lines_to_write.append(line)

    flows = np.zeros((91, 75), dtype=float)
    count = 0
    for line in lines_to_write:  
##################### Mostro la percentuale di completamento ##############################################################
        percentage = (100 * count)/len(lines_to_write)
        mod = percentage % 5
        if mod == 0 and not int(percentage) == 0 and not mod < 1:
            print(str(percentage) + " %")
###########################################################################################################################

        row, col = line.split()
        row = int(int(row)/25)
        col = int(int(col)/25)
        if char == 'c': # unione con output continuo tra 0 e 1
            flows[row][col] += 1
        else:           # unione con output discreto: 0 o 1
            flows[row][col] = 1
        count += 1
    if char == 'c':
        for r in range(0, flows.shape[0]):
            for c in range(0, flows.shape[1]):
                if not flows[r][c] == 0:
                    flows[r][c] = flows[r][c] / 6
    sparse_matrix = sparse.csr_matrix(flows)
    sparse.save_npz("sparse_matrix_" + char + "_" + str(id_vent), sparse_matrix, compressed = True)
    return sparse_matrix
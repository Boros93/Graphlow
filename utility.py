import numpy as np
import csv
import networkx as nx
import os
import graph_algorithm as ga
import graph_maker as gm
import map_creator as mc
import conversion
import metrics
from region import Region
from scipy import sparse
from glob import glob

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

def load_graph(gexf_filename = "graphlow.gexf"):
    if os.path.exists("graph_gexf/" + gexf_filename):
        G = nx.read_gexf("graph_gexf/" + gexf_filename)
        return G
    else:
        print("Graph does not exists.")
        return None

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

# Genera una matrice sparsa che rappresenta l'unione delle simulazioni MAGFLOW della bocca specificata
def unify_sims(id_vents: list, char, neighbor):
    simspath = "Data/simulations/"

    all_flows = np.zeros((91, 75), dtype=float)
    all_norm = 0

    for id_vent in id_vents:
        current_vent_files = glob("{}/NotN_vent_{}_*.txt".format(simspath, id_vent))
        all_norm += len(current_vent_files)

        vent_flows = np.zeros((91, 75), dtype=float)

        for f in current_vent_files:
            this_flow = np.zeros((91, 75), dtype=float)
            with open(f, 'r') as infile:
                for line in infile:
                    row, col = line.split()
                    row = int(int(row)/25)
                    col = int(int(col)/25)
                    this_flow[row][col] = 1

            if char == 'c':
                # add this_flow to flows: +1 for each flow
                vent_flows += this_flow
                all_flows += this_flow
            else:
                # pick the maximum between this_flow and flows (1 if it was in _any_ flow)
                vent_flows = np.maximum(vent_flows, this_flow)
                all_flows = np.maximum(all_flows, this_flow)

        # normalize
        if char == 'c':
            for r in range(0, vent_flows.shape[0]):
                for c in range(0, vent_flows.shape[1]):
                    if not vent_flows[r][c] == 0:
                        vent_flows[r][c] = vent_flows[r][c] / 6
        sparse_matrix = sparse.csr_matrix(vent_flows)
        # sparse.save_npz("sparse/sparse_sim_" + char + "_" + str(id_vent) + ".npz", sparse_matrix, compressed = True)

    # normalize across all
    if char == 'c':
        for r in range(0, all_flows.shape[0]):
            for c in range(0, all_flows.shape[1]):
                if not all_flows[r][c] == 0:
                    all_flows[r][c] = all_flows[r][c] / all_norm
    sparse_matrix = sparse.csr_matrix(all_flows)
    sparse.save_npz("sparse/sparse_sim_" + char + neighbor + "_" + str(id_vents[0]) + ".npz", sparse_matrix)
    return sparse_matrix

def init_table(propagation_method):
    print("\n\n                                  " + propagation_method)
    metric_name_list = ["VENT  ", " PPV   ", " PPVC  ", " TPR   ", " TPRC  ", " HIT   ", " HITC  ", " F1    ", " F1C   ", " CITY  ", " RISK  "]
    for metric in metric_name_list:
        print("| " + metric, end = " ")
    print("|")

def create_row_table(metric_list, vent):
    vent = str(vent)
    print("| " + vent.ljust(7, " "), end="")
    for metric in metric_list:
        metric = format(metric, ".1e")
        print("| " + str(metric), end = " ")
    print("|")

# Dato l'id di un nodo, ritorna l'id del vent
def node_vent_csv():
    vent_list = []
    file_list = glob("Data/simulations/*")
    for f in file_list:
        id_vent = conversion.id_from_not_n(f[17:])
        if id_vent not in vent_list:
            vent_list.append(id_vent)
            
    out_file = "node_vent_csv.csv"
    with open(out_file, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(['id_vent', 'id_node'])
        for v in vent_list:
            # scrive la linea id_vent,id_node
            id_node = conversion.get_node_from_idvent_in_graph(v)
            filewriter.writerow([v, id_node])

def create_vent_dict():
    # Leggo il file csv
    # Creo il dizionario key:vent, value:node
    vent_node_dict = {}
    filename = "CSVMaps/node_vent_map.csv"
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for i, row in enumerate(csv_reader):
            if i != 0:
                vent_node_dict[row[0]] = row[1]
    return vent_node_dict

# Genera una scacchiera di nodi (vent) di dimensione = size e passo = step data una coordinata iniziale
def get_node_vent_chessboard(x, y, size, step):
    node_matrix = np.load("Data/node_matrix.npy")
    vent_matrix = np.load("Data/vent_matrix.npy")
    
    if (x + size) > node_matrix.shape[0]:
        print("Error: x + size exceed matrix number of rows!")
        return
    if (y + size) > node_matrix.shape[1]:
        print("Error: y + size exceed matrix number of cols!")
        return

    node_list = []
    vent_list = []
    for i in range(0, size):
        if i % 2 == 0:
            j_start = 0
        else:
            j_start = int(step/2)

        for j in range(j_start, size, step):
            vent = vent_matrix[x + i][y + j]
            if vent != 0:
                node_list.append(str(node_matrix[x + i][y + j]))
                vent_list.append(str(vent))
    
    return node_list, vent_list

def visualize_and_metrics(id_vents: list, propagation_method, neighbor, sparse_matrix, G, header):
    # Esportazione in ASCII Grid
    mc.ascii_creator(id_vents, propagation_method + neighbor, sparse_matrix)
    # Calcolo delle metriche
    metric_list = metrics.compute(id_vents, neighbor, sparse_matrix, G)
    # Intabellamento
    # Scrittura header tabella
    if not header == True:  
        init_table(propagation_method)
    create_row_table(metric_list, id_vents[0])
    
    return metric_list

# Calcolo del vicinato di moore o di neumann
def get_neighborhood(id_vent, neighbor_method, radius):
    radius = int(radius)
    id_vent = int(id_vent)
    id_vents = [id_vent]
    if neighbor_method == 'moore':
        for r in range(-radius, radius+1):
            for c in range(-radius, radius+1):
                if r != 0 and c !=0:
                    id_vents.append(id_vent + r*73 + c)
    else:
        for r in range(-radius, radius+1):
            for c in range(-radius, radius+1):
                if abs(r)+abs(c) <= radius:
                    if r != 0 and c !=0:
                        id_vents.append(id_vent + r*73 + c)

    return id_vents
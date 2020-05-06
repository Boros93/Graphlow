import numpy as np
from region import Region
import csv
import networkx as nx
import os
import graph_algorithm as ga
import graph_maker as gm
import map_creator as mc
import conversion
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

# genera una matrice sparsa che rappresenta l'unione delle simulazioni MAGFLOW della bocca specificata
def unify_sims(id_vents, char):
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
        sparse.save_npz("sparse/sparse_sim_" + char + "_" + str(id_vent) + ".npz", sparse_matrix, compressed = True)

    # normalize across all
    if char == 'c':
        for r in range(0, all_flows.shape[0]):
            for c in range(0, all_flows.shape[1]):
                if not all_flows[r][c] == 0:
                    all_flows[r][c] = all_flows[r][c] / all_norm
    sparse_matrix = sparse.csr_matrix(all_flows)

    return sparse_matrix

def init_table(propagation_method):
    print("\n\n                                  " + propagation_method)
    metric_name_list = ["VENT  ", " PPV   ", " PPVC  ", " TPR   ", " TPRC  ", " HIT   ", " HITC  ", " F1    ", " F1C   ", " CITY  ", " RISK  "]
    for metric in metric_name_list:
        print("| " + metric, end = " ")
    print("|")

def create_row_table(metric_list, vent):
    print("| " + vent.ljust(7, " "), end="")
    for metric in metric_list:
        metric = format(metric, ".1e")
        print("| " + str(metric), end = " ")
    print("|")

#dato l'id di un nodo, ritorna l'id del vent
def node_vent_csv():
    vent_list = []
    file_list = glob("Data/simulations/*")
    for file in file_list:
        id_vent = conversion.id_from_not_n(file[17:])
        if id_vent not in vent_list:
            vent_list.append(id_vent)
            
    out_file = "node_vent_csv.csv"
    count = 0
    with open(out_file, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        for v in vent_list:
            # scrive la linea id_vent,id_node
            id_node = conversion.get_node_from_idvent(v)
            print(id_node, v)
            filewriter.writerow([id_node, v])
            if count > 2:
                return
            count += 1

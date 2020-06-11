import map_creator as mc
import graph_algorithm as ga
import graph_maker as gm
import numpy as np 
import networkx as nx
import map_creator as mc
import utility
import random
import metrics
import conversion
import re
import math
import glob
import os
import seaborn as sns
import visualize
from scipy import sparse
from Propagation import Propagation
from Genetic_algorithm import Genetic_algorithm
from matplotlib import pyplot as plt

def realsim_cmd(id_vent: int, real_class: str, neighbor_method: str, radius: int):
    id_vent = str(id_vent - 1)
    propagation = Propagation()
    id_vents = [id_vent]
    neighbor = ""
    # Se la classe è 0 allora bisogna fare Unify
    if real_class == "0":
        if neighbor_method != None:
            if neighbor_method == "moore" or neighbor_method == "neumann":
                id_vents = utility.get_neighborhood(id_vent, neighbor_method, radius)
                neighbor = "_" + neighbor_method + str(radius)
            else:
                print("You must specify a valid neighbor method: moore / neumann.")
                return None  
        sparse_matrix_c, sparse_matrix_d = propagation.real(id_vents, real_class, neighbor)
        # Esportazione in ASCII Grid
        for i in range(len(id_vents)):
            id_vents[i] = int(id_vents[i]) + 1
        mc.ascii_creator(id_vents, "ucsim" + neighbor, sparse_matrix_c)
        mc.ascii_creator(id_vents, "udsim" + neighbor, sparse_matrix_d)
        return 
    else:
        if len(id_vents) > 1:
            raise ValueError("multiple vents not supported for class != 0")
        sparse_matrix = propagation.real(id_vents, real_class, neighbor)
        # Esportazione in ASCII Grid
        mc.ascii_creator([str(id_vent + 1)], neighbor + real_class, sparse_matrix)
        return

# Sistemare - per il mio amico Pavel. Se sono Pavel allora so già tutto!
def compare(*parameter_list):
    # Primo parametro corrisponde al fatto che il metodo sia random o scelto dall'utente
    vent_list, setting = [], []
    if parameter_list[0] == '-r':
        vent_list = random_vent() 
    elif parameter_list[0] == '-c':
        vent_list = select_vent()
    else:
        print(parameter_list[0], "non esiste come opzione. Selezionare -r o -c")
    
    # Secondo parametro (se esiste) indica che l'utente vuole scegliere i parametri per gli algoritmi
    if len(parameter_list) > 1 and parameter_list[1] == "-p":
        setting = choose_setting()
    else:
        # Si costruisce questa lista per dire ai comandi di prendere i valori di default
        setting = [-1, [-1,-1,-1], [-1, -1]]
    
    # ogni elemento di queste liste sarà una lista composta da (in ordine):
    # (precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1, f1_c)
    methods = ["TRIVECTOR", "ERUPTION", "PROBERUPTION"]
    for method in methods:
        utility.init_table(method)
        for vent in vent_list:
            if method == "TRIVECTOR":
                trivector_cmd(vent, setting[0], header=True)
            elif method == "ERUPTION":
                eruption_cmd(vent, *setting[1], header=True)
            elif method == "PROBERUPTION":
                montecarlo_cmd(vent, *setting[2], header=True)

def random_vent(*parameter_list):
    n_vents = int(input("Insert number of vents to compare:"))
    # Genera n vent casualmente
    vent_list = []
    for i in range(0, n_vents):
        x = random.randint(74, 4814)
        while str(x) in vent_list:
            x = str(random.randint(74, 4814))
        vent_list.append(str(x))
    return vent_list

def select_vent(*parameter_list):
    vents = input("Insert the list of vents to compare:")
    vent_list = vents.split(" ")
    return vent_list

def choose_setting():
    setting_list = []
    # Trivector parametri
    threshold = input("Insert the parameter of Trivector's Algorithm (threshold):")
    if threshold == "":
        threshold = 0.001
    setting_list.append(threshold)

    # Eruption parametri
    volume = input("Insert volume of Eruption:")
    if volume == "":
        volume = 1000
    n_days = input("Insert number of days of Eruption:")
    if n_days == "":
        n_days = 7
    threshold = input("Insert the threshold of Eruption:")
    if threshold == "":
        threshold = 0.15
    setting_list.append([volume, n_days, threshold])

    # Proberuption parametri
    epoch = input("Insert the number of epoch for Montecarlo")
    if epoch == "":
        epoch = 100
    second_chance = input("Insert the probability for the second chance in Montecarlo")
    if second_chance == "":
        second_chance = 0
    setting_list.append([epoch, second_chance])

    return setting_list
# Fine argomenti tesina amico Pavel.

def trivector_cmd(id_vent: str, neighbor_method: str, radius: int, threshold: float, graph: str, header = False):
    propagation = Propagation()
    # Setta i parametri
    if os.path.isfile("graph_gexf/"+graph):
        propagation.set_Graph(utility.load_graph(graph))
    else:
        print("Graph doesn't exist, default are loaded")
    propagation.set_trivector(threshold)
    id_vents = []
    propagation_method = "trivector"
    neighbor = ""
    if neighbor_method != None:
        if neighbor_method == "moore" or neighbor_method == "neumann":
            id_vents = utility.get_neighborhood(id_vent, neighbor_method, radius)
            neighbor += "_" + neighbor_method + str(radius)
        else:
            print("You must specify a valid neighbor method: moore / neumann.")
            return None
    else:
        id_vents = [id_vent]
    
    # Esecuzione algoritmo 
    sparse_matrix = propagation.trivector(id_vents)
    # Esportazione in ASCII e calcolo metriche
    G = propagation.get_Graph()
    utility.visualize_and_metrics(id_vents, propagation_method, neighbor, sparse_matrix, G, header)

def eruption_cmd(id_vent, volume = -1, n_days = -1, threshold = -1, header = False):
    if id_vent == 0:
        return
    propagation = Propagation()
    # Setta i parametri
    propagation.set_eruption(volume, n_days, threshold)
    # Esecuzione algoritmo 
    sparse_matrix = propagation.eruption(id_vent)
    # Esportazione in ASCII e calcolo metriche
    G = propagation.get_Graph()
    utility.visualize_and_metrics(id_vent, "eruption", sparse_matrix, G, header)

def montecarlo_cmd(id_vent, n_epochs = -1, second_chance = -1, header = False):
    if id_vent == 0:
        return
    propagation = Propagation()
    # Setta i parametri
    propagation.set_montecarlo(n_epochs, second_chance)
    # Esecuzione algoritmo 
    sparse_matrix = propagation.trivector(id_vent)
    # Esportazione in ASCII e calcolo metriche
    G = propagation.get_Graph()
    utility.visualize_and_metrics(id_vent, "montecarlo", sparse_matrix, G, header)

def test(id_vent, distance = 4):
    propagation = Propagation()
    propagation.trivector([id_vent])
    G = propagation.get_Graph()

    # Conversione vent
    id_node = conversion.get_node_from_idvent(int(id_vent))

    # Estrazione sottografo
    for i in range(len(G.nodes)):
        if G.nodes[str(i)]['current_flow'] == 0:
            G.remove_node(str(i))

    # Cambio pesi
    for u, v, data in G.edges(data=True):
        if data['trasmittance'] == 0:
            G.edges[u, v]['trasmittance'] = math.inf
        else:
            G.edges[u, v]['trasmittance'] = -math.log(data['trasmittance'])

    # Lista nodi città
    city_nodes = []
    for n in G.nodes:
        if G.nodes[n]['priority'] > 0:
            city_nodes.append(n)

    # Shortest paths
    shortest_paths = {}
    for n in city_nodes:
        shortest_paths[n] = nx.shortest_path(G, id_node, n, weight='trasmittance')
    
    cutted_edges = {}
    for n in shortest_paths:
        path = shortest_paths[n]
        for i in range(distance, len(path)-distance):
            edge_id = (path[i-1], path[i])
            if edge_id not in cutted_edges:
                propagation.set_Graph(utility.load_graph())
                propagation.cut_edges([[path[i-1], path[i]]])
                sparse_matrix = propagation.trivector([id_vent])
                G = propagation.get_Graph()
                risk = metrics.compute([id_vent], 'trivector', sparse_matrix, G)[-1]
                cutted_edges[edge_id] = risk
                print(edge_id, risk)

    min_risk = min(cutted_edges, key=cutted_edges.get)
    print(min_risk)

def autocut_cmd(id_vent: str, distance: int, neighbor_method: str, radius: int, dimension: int, mode: str):
    propagation = Propagation()
    id_vents = []
    propagation_method = "trivector"
    neighbor = ""
    if neighbor_method != None:
        if neighbor_method == "moore" or neighbor_method == "neumann":
            id_vents = utility.get_neighborhood(id_vent, neighbor_method, radius)
            neighbor += "_" + neighbor_method + str(radius)
        else:
            print("You must specify a valid neighbor method: moore / neumann.")
            return None
    else:
        id_vents = [id_vent]
    
    # Esecuzione algoritmo prima di tagliare
    no_cutted_sparse = propagation.trivector(id_vents)
    G = propagation.get_Graph()
    # Decommentare se si vuole stampare le metriche del trivector senza taglio 
    # utility.visualize_and_metrics(id_vents, propagation_method, no_cutted_sparse, G, False)

    # selezione degli archi da tagliare
    list_edges = ga.get_edges_to_cut(G, id_vents, distance, dimension, mode)

    propagation.set_Graph(utility.load_graph())
    # taglio archi selezionati
    propagation.cut_edges(list_edges)

    # esecuzione trivector dopo il taglio degli archi
    cutted_sparse = propagation.trivector(id_vents)
    G = propagation.get_Graph()
    utility.visualize_and_metrics(id_vents, propagation_method, neighbor, cutted_sparse, G, False)
    mc.ascii_barrier(id_vent, propagation_method + neighbor, list_edges)

def cut_cmd(id_vent, list_edges: list, neighbor_method, radius):
    edges_to_cut = []
    for edges in list_edges:
        edges_to_cut.append(edges.split(','))
    propagation = Propagation()
    id_vents = []
    propagation_method = "trivector"
    neighbor = ""
    if neighbor_method != None:
        if neighbor_method == "moore" or neighbor_method == "neumann":
            id_vents = utility.get_neighborhood(id_vent, neighbor_method, radius)
            neighbor += "_" + neighbor_method + str(radius)
        else:
            print("You must specify a valid neighbor method: moore / neumann.")
            return None
    else:
        id_vents = [id_vent]

    propagation.cut_edges(edges_to_cut)
    # Esportazione in ASCII e calcolo metriche
    sparse_matrix = propagation.trivector(id_vents)
    G = propagation.get_Graph()
    utility.visualize_and_metrics(id_vents, propagation_method, neighbor, sparse_matrix, G, False)
    mc.ascii_barrier(id_vent, propagation_method + neighbor, edges_to_cut)

def genetic_train_cmd(id_vent: int, size: int, step: int, population_len: int, rho: int, epochs: int):
    # Lista vents/nodes del sottografo
    id_nodes, id_vents = utility.get_node_vent_chessboard(id_vent, size, step)

    print("Calcolo chessboard terminato!")

    filename = "graph_gexf/subgraphs/sg_" + str(id_vent) + "_" + str(size) + "_" + str(step) + ".gexf"
    if os.path.isfile(filename):
        G = nx.read_gexf("graph_gexf/genetic_graph.gexf")
        SG = nx.read_gexf(filename)
        for u,v in SG.edges:
            SG.edges[u,v]['prop_weight'] = G.edges[u,v]['prop_weight']
    else:
        # Creazione del vettore dei real vect
        real_vect_list = []
        for vent in id_vents:
            real_vect_list.append(np.load("Data/real_vectors/" + str(vent) + ".npy"))
        # Creazione del vettore dei trivector
        p = Propagation()
        tri_vect_list = []
        for node in id_nodes:
            tri_vect_list.append(p.trivector_train(node))

        # Real vect e tri vect unificati
        real_vect = np.zeros(5820)
        tri_vect = np.zeros(5820)
        for i in range(5820):
            for vect in tri_vect_list:
                if vect[i] > 0:
                    tri_vect[i] = 1
                    break
            for vect in real_vect_list:
                if vect[i] > 0:
                    real_vect[i] = 1
                    break

        # Creazione del sottografo
        SG = ga.get_trivector_subgraph(tri_vect, real_vect)
        nx.write_gexf(SG, filename)
        
    print("Init Genetic Algorithm")
    # Algoritmo genetico
    gen = Genetic_algorithm(id_vents, id_nodes, SG.edges, population_len, rho)
    gen.start(epochs)

def plot_train_result_cmd(metric: str, id_vent: int, size: int, step: int):
    # Load dei grafi
    original_graph = utility.load_graph()
    genetic_graph = utility.load_graph(gexf_filename="genetic_graph.gexf")

    if metric == "precision":
        filename = "plot/" + str(id_vent) + "_" + str(size) + "_" + str(step) + "_precision.plt"
        if os.path.isfile(filename):
            id_vents, original_list, trained_list = visualize.load_plot2D_from_file(filename)
        else:
            # Lista vents/nodes del sottografo
            _, id_vents = utility.get_node_vent_chessboard(id_vent, size, step)
            for i in range(len(id_vents)):
                id_vents[i] = str(int(id_vents[i]) + 1)
            # Lista precision su grafo originale
            original_list = metrics.get_ppv_list(original_graph, id_vents)
            # Lista precision su grafo modificato
            trained_list = metrics.get_ppv_list(genetic_graph, id_vents)
            # Salvataggio dei risultati del trivector PRIMA l'addestramento
            visualize.save_plot2D_on_file(id_vents, original_list, trained_list, "plot/" + str(id_vent) + "_" + str(size) + "_" + str(step) + "_precision.plt")

    elif metric == "recall":
        filename = "plot/" + str(id_vent) + "_" + str(size) + "_" + str(step) + "_recall.plt"
        if os.path.isfile(filename):
            id_vents, original_list, trained_list = visualize.load_plot2D_from_file(filename)
        else:
            # Lista vents/nodes del sottografo
            _, id_vents = utility.get_node_vent_chessboard(id_vent, size, step)
            for i in range(len(id_vents)):
                id_vents[i] = str(int(id_vents[i]) + 1)
            # Lista recall su grafo originale
            original_list = metrics.get_tpr_list(original_graph, id_vents)
            # Lista recall su grafo modificato
            trained_list = metrics.get_tpr_list(genetic_graph, id_vents)
            # Salvataggio dei risultati del trivector PRIMA l'addestramento
            visualize.save_plot2D_on_file(id_vents, original_list, trained_list, "plot/" + str(id_vent) + "_" + str(size) + "_" + str(step) + "_recall.plt")

    sns.lineplot(id_vents, original_list, label="original")
    sns.lineplot(id_vents, trained_list, label="trained")
    plt.show()
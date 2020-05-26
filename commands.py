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
from utility import graph_to_matrix
from utility import load_graph
from scipy import sparse
from Propagation import Propagation

# AGGIUNGERE I NUOVI COMANDI
# FIXARE LE INTERFACCE
def man():
    print(r"""
    - exit: is used to quit the program. Just type 'exit' in command line.
    - eruption: is used to launch a real time simulation. To begin an eruption it needs some parameters, in this order:
            id vent(int)    <- integer between 4 and 4814 which indicates the id of vent.
                               You can find it in 'Data/simulations/' after 'NotN_vent_' string.
            volume(int)     <- this is the amount of magma of your eruption, default 1000.
            n_days(int)     <- this parameter indicate the eruption duration(in days), default 7.
            alpha(float)    <- parameter to fix magma forwarding, default 0.125
            threshold(int)  <- another parameter to fix magma forwarding, default 1
                               example of usage:  eruption 2233 1000 7 0.11 10

    - showsim: is used to show a simulation from MAGFLOW. It needs the follow parameters:
            id vent(int)    <- integer between 4 and 4814 which indicates the id of vent. 
                               You can find it in 'Data/simulations/' after 'NotN_vent_' string.
            class(int)      <- integer in range 1 to 6 that indicates the eruption class. 
                               An eruption class is a combination of volume and duration of eruption. default 1
                               example of usage: showsim 2233 6
    """)

def show_sim(spec=None, real_class = 1):
    if spec is None:
        raise ValueError("must specify an id_vent")

    id_vents = set()
    propagation = Propagation()

    # accept a comma-separated list of specifications
    # each vent specification can be either a single vent, or a vent neighborhod specification
    # moore(vent[,r]) specifies the Moore neighborhood of radius r
    # neumann(vent[,r]) specifies the von Neumann neighborhood of radius r
    # default value for r is 1
    while spec:
        # match groups:
        # an optional initial comma, with surrounding space
        # moore( or neumann(, storing moore or neumann in the neib group
        # digitis (vent id)
        # a comma, optional whitespace, the radius (optionally) and the closing ) (obligatoy), if neib was specified
        match = re.match("(?:\s*,\s*)?(?:(?P<neib>moore|neumann)\()?(?P<id>\d+)(?(neib)(?:,\s*(?P<radius>\d+))?\))", spec)
        if not match:
            raise ValueError("invalid vent spec '{}'".format(spec))
        neib = match.group('neib')
        radius = int(match.group('radius') or 1)
        vent = int(match.group('id'))
        # TODO FIXME neighbor computations aren't valid at the edge of the vent grid
        if neib is None:
            id_vents.add(vent)
        elif neib == 'moore':
            for r in range(-radius, radius+1):
                for c in range(-radius, radius+1):
                    id_vents.add(vent + r*73 + c)
        elif neib == 'neumann':
            for r in range(-radius, radius+1):
                for c in range(-radius, radius+1):
                    if abs(r)+abs(c) <= radius:
                        id_vents.add(vent + r*73 + c)
        # match next
        spec = spec[match.end():]

    id_vents = [ str(v) for v in id_vents ]
    id_vents.sort()
    print(id_vents)

    if real_class == "0":
        # Qui si unificano le simulazioni, si esportano come matrici sparse e si creano gli ASCII
        sparse_matrix_c, sparse_matrix_d = propagation.real(id_vents, real_class)
        ascii_vents = "_".join(id_vents)
        mc.ascii_creator(ascii_vents, "ucsim", sparse_matrix_c)
        mc.ascii_creator(ascii_vents, "udsim", sparse_matrix_d)
        return

    # Esecuzione simulazione --single vent only
    if len(id_vents) != 1:
        raise ValueError("multiple vents not supported for class != 0")
    id_vent = id_vents[0]
    sparse_matrix = propagation.real(id_vent, real_class)
    # Esportazione in ASCII Grid
    mc.ascii_creator(id_vent, "real_" + real_class, sparse_matrix)

def realsim_cmd(id_vent: str, real_class: str, neighbor_method: str, radius: int):
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
        mc.ascii_creator(id_vents, "ucsim" + neighbor, sparse_matrix_c)
        mc.ascii_creator(id_vents, "udsim" + neighbor, sparse_matrix_d)
        return 
    else:
        if len(id_vents) > 1:
            raise ValueError("multiple vents not supported for class != 0")
        sparse_matrix = propagation.real(id_vents, real_class, neighbor)
        # Esportazione in ASCII Grid
        mc.ascii_creator(id_vents, neighbor + real_class, sparse_matrix)
        return

def node_from_idvent(id_vent):
    node = conversion.get_node_from_idvent(id_vent)
    print(node)

# Sistemare
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

# il comando esegue il metodo di propagazione trivector. supporta l'esecuzione su una sola bocca
# oppure su più bocche.
# per eseguire il comando a bocca singola specificare id_vent, threshold (se si desidera specificarne una) 
# ESEMPIO DI UTILIZZO: trivector 2233
# per eseguire il comando a bocca multipla specificare un id_vent, un metodo di determinazione del vicinato 
# e un raggio.
# ESEMPIO DI UTILIZZO: trivector 2233 moore 2
def trivector_cmd(id_vent: str, neighbor_method: str, radius: int, threshold: float, header = False):
    propagation = Propagation()
    # Setta i parametri
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
    visualize_and_metrics(id_vents, propagation_method, neighbor, sparse_matrix, G, header)

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
    visualize_and_metrics(id_vent, "eruption", sparse_matrix, G, header)

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
    visualize_and_metrics(id_vent, "montecarlo", sparse_matrix, G, header)

def visualize_and_metrics(id_vents: list, propagation_method, neighbor, sparse_matrix, G, header):
    # Esportazione in ASCII Grid
    mc.ascii_creator(id_vents, propagation_method + neighbor, sparse_matrix)
    # Calcolo delle metriche
    metric_list = metrics.compute(id_vents, neighbor, sparse_matrix, G)
    # Intabellamento
    # Scrittura header tabella
    if not header == True:  
        utility.init_table(propagation_method)
    utility.create_row_table(metric_list, id_vents[0])
    
    return metric_list

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
        if G.nodes[n]['is_city'] > 0:
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
                propagation.set_Graph(load_graph())
                propagation.cut_edges([[path[i-1], path[i]]])
                sparse_matrix = propagation.trivector([id_vent])
                G = propagation.get_Graph()
                risk = metrics.compute([id_vent], 'trivector', sparse_matrix, G)[-1]
                cutted_edges[edge_id] = risk
                print(edge_id, risk)

    min_risk = min(cutted_edges, key=cutted_edges.get)
    print(min_risk)

def autocut_cmd(id_vent: str, distance: int, neighbor_method: str, radius: int, dimension: int, mode: str, measure: str):
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
    # visualize_and_metrics(id_vents, propagation_method, no_cutted_sparse, G, False)

    # selezione degli archi da tagliare
    list_edges = ga.get_edges_to_cut(G, id_vents, distance, dimension, mode, measure)

    propagation.set_Graph(load_graph())
    # taglio archi selezionati
    propagation.cut_edges(list_edges)

    # esecuzione trivector dopo il taglio degli archi
    cutted_sparse = propagation.trivector(id_vents)
    G = propagation.get_Graph()
    visualize_and_metrics(id_vents, propagation_method, neighbor, cutted_sparse, G, False)
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
    visualize_and_metrics(id_vents, propagation_method, neighbor, sparse_matrix, G, False)
    mc.ascii_barrier(id_vent, propagation_method + neighbor, edges_to_cut)

def weight_adjustment():
    # Lista di vents
    vents = []
    file_list = glob.glob("Data/real_vectors/*")
    for f in file_list:
        vents.append(f[18:-4])
    
    # Dizionario vent, node
    vent_node_dict = utility.create_vent_dict()

    p = Propagation()
    if os.path.exists("graph_gexf/trained_graphlow.gexf"):
        p.set_Graph(load_graph('trained_graphlow.gexf'))

    for e in range(100):
        print("Epoca: ", e)
        global_error = np.zeros((5820,))
        idx = np.random.permutation(len(vents))
        for i in idx[:500]:
            print(vents[i])
            node = vent_node_dict[vents[i]]
            out = p.trivector_train(node)
            y = np.load("Data/real_vectors/" + vents[i] + ".npy")
            error = out - y
            global_error += error
        mean_error = global_error / len(vents)

        # Calcolo dei nuovi pesi
        G = p.get_Graph()
        for id_node, err in enumerate(mean_error):
            pre = list(G.predecessors(str(id_node)))
            succ = list(G.successors(str(id_node)))

            delta = float(err) / (len(pre) + len(succ))

            for v in pre:
                G.edges[v, str(id_node)]['prop_weight'] += delta
            for v in succ:
                G.edges[str(id_node), v]['prop_weight'] += delta
        
        # Normalizzazione pesi tra 0 e 1
        #prop_weights = []
        #for u, v, data in G.edges(data=True):
        #    prop_weights.append(data['prop_weight'])
        #min_weight = min(prop_weights)
        #max_weight = max(prop_weights)

        #for u, v, data in G.edges(data=True):
        #    G.edges[u, v]['prop_weight'] = (data['prop_weight'] - min_weight) / (max_weight - min_weight) 

        #G = gm.normalize_prop_weight(G)
        p.set_Graph(G)

        # Export del grafo
        p.export_graph('trained_graphlow.gexf')

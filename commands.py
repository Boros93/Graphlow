import map_creator as mc
import graph_algorithm as ga
import graph_maker as gm
import os
import networkx as nx
import map_creator as mc
import probabilistic_algorithm
from utility import graph_to_matrix
from utility import load_graph
import utility
from scipy import sparse
import random
from Propagation import Propagation
import metrics
import conversion

# AGGIUNGERE I NUOVI COMANDI
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
def show_sim(id_vent = 0, real_class = 1):
    if id_vent == 0:
        print("WARNING! Insert an id_vent")
        return
    propagation = Propagation()
    if real_class == "0":
        # Qui si unificano le simulazioni, si esportano come matrici sparse e si creano gli ASCII
        sparse_matrix_c, sparse_matrix_d = propagation.real(id_vent, real_class)
        mc.ascii_creator(id_vent, "ucsim_", sparse_matrix_c)
        mc.ascii_creator(id_vent, "udsim_", sparse_matrix_d)
        return
    # Esecuzione simulazione
    sparse_matrix = propagation.real(id_vent, real_class)
    # Esportazione in ASCII Grid
    mc.ascii_creator(id_vent, "real_" + real_class, sparse_matrix)
    
def norm_weight():
    G = nx.read_gexf("graph_gexf/scaled_map91x75_normalized.gexf")
    G = gm.normalize_weight(G)
    gm.export_graph(G, "weight_norm_graph.gexf", False)

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

def trivector_cmd(id_vent, threshold = -1, header = False):
    if id_vent == 0:
        return
    propagation = Propagation()
    # Setta i parametri
    propagation.set_trivector(threshold)
    # Esecuzione algoritmo 
    sparse_matrix = propagation.trivector(id_vent)
    # Esportazione in ASCII e calcolo metriche
    visualize_and_metrics(id_vent, "trivector", sparse_matrix, header)

# Da sistemare lunedì
def batch_trivector(*parameter_list):
    # Primo parametro corrisponde al fatto che il metodo sia random o scelto dall'utente
    vent_list, setting = [], []
    if parameter_list[0] == '-r':
        vent_list = random_vent() 
    elif parameter_list[0] == '-c':
        vent_list = select_vent()
    else:
        print(parameter_list[0], "non esiste come opzione. Selezionare -r o -c")



def eruption_cmd(id_vent, volume = -1, n_days = -1, threshold = -1, header = False):
    if id_vent == 0:
        return
    propagation = Propagation()
    # Setta i parametri
    propagation.set_eruption(volume, n_days, threshold)
    # Esecuzione algoritmo 
    sparse_matrix = propagation.eruption(id_vent)
    # Esportazione in ASCII e calcolo metriche
    visualize_and_metrics(id_vent, "eruption", sparse_matrix, header)

def montecarlo_cmd(id_vent, n_epochs = -1, second_chance = -1, header = False):
    if id_vent == 0:
        return
    propagation = Propagation()
    # Setta i parametri
    propagation.set_montecarlo(n_epochs, second_chance)
    # Esecuzione algoritmo 
    sparse_matrix = propagation.trivector(id_vent)
    # Esportazione in ASCII e calcolo metriche
    visualize_and_metrics(id_vent, "montecarlo", sparse_matrix, header)


def visualize_and_metrics(id_vent, propagation_method, sparse_matrix, header):
    # Esportazione in ASCII Grid
    mc.ascii_creator(id_vent, propagation_method, sparse_matrix)
    # Calcolo delle metriche
    metric_list = metrics.compute(id_vent, propagation_method, sparse_matrix)
    # Intabellamento
    # Scrittura header tabella
    if not header == True:  
        utility.init_table(propagation_method)
    utility.create_row_table(metric_list, id_vent)
    
    return metric_list

def test():
    return
    

    

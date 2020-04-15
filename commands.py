import map_creator as mc
import graph_algorithm as ga
import graph_maker as gm
import os
import networkx as nx
import map_creator as mc
import probabilistic_algorithm
from utility import graph_to_matrix
from utility import vent_in_dem
from utility import get_node_from_idvent
from graph_algorithm import get_id_from_coord
from utility import load_graph
from utility import unify_sims
import utility
from scipy import sparse
import random

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

def prob_eruption_(id_vent = 0, epoch = 100, second_chance = 0):
    G = load_graph()
    if id_vent == 0:
        return
    G_ = ga.prob_eruption(G, int(id_vent), int(epoch), float(second_chance))
    gm.export_graph(G_, "proberuption_" + str(id_vent) + ".gexf", is_first_time = False)
    
    #############################################
    # propagation_method = 1 ---> trivector     #
    #                    = 2 ---> eruption      #
    #                    = 3 ---> proberuption  #
    #############################################
    utility.vect_to_matrix(id_vent, 3)
    
    sparse_matrix = sparse.load_npz("sparse/M_proberuption_" + str(id_vent) + ".npz")
    mc.matrix_to_UTM(sparse_matrix, id_vent, eruption_method=3)
       
    #calcolo metriche
    precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1, f1_c = utility.compute_metrics(id_vent, 3)
    return [precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1, f1_c]


def eruption1(id_vent = 0, volume = 1000, n_days = 7, threshold = 0.15):
    
    if id_vent == 0:
        return
    G = load_graph()
    G_ = ga.eruption1(G, int(id_vent), int(volume), int(n_days), float(threshold))
    gm.export_graph(G_, "eruption_" + str(id_vent) + ".gexf", is_first_time = False)
    
    #############################################
    # propagation_method = 1 ---> trivector     #
    #                    = 2 ---> eruption      #
    #                    = 3 ---> proberuption  #
    #############################################
    utility.vect_to_matrix(id_vent, 2)

    sparse_matrix = sparse.load_npz("sparse/M_eruption_" + str(id_vent) + ".npz")
    mc.matrix_to_UTM(sparse_matrix, id_vent, eruption_method=2)

   
    #calcolo metriche
    precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1, f1_c = utility.compute_metrics(id_vent, 2)
    return [precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1, f1_c]


def trivector(id_vent = 0, threshold = 0.001): 
    if id_vent == 0:
        return
    G = load_graph()
    G_ = probabilistic_algorithm.eruption_trivector(G, id_vent, float(threshold))
    gm.export_graph(G_, "trivector_" + str(id_vent) + ".gexf", is_first_time = False)
    utility.vect_to_matrix(id_vent, 1)
    sparse_matrix = sparse.load_npz("sparse/M_trivector_" + str(id_vent) + ".npz")
    mc.matrix_to_UTM(sparse_matrix, id_vent, eruption_method=1)

    #############################################
    # propagation_method = 1 ---> trivector     #
    #                    = 2 ---> eruption      #
    #                    = 3 ---> proberuption  #
    #############################################
    #calcolo metriche
    precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1, f1_c = utility.compute_metrics(id_vent, 1)
    return [precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1, f1_c]


def show_sim(id_vent = 0, class_ = 1):
    if id_vent == 0:
        print("WARNING! Insert an id_vent")
        return
    sim_filename = "NotN_vent_" +id_vent + "_" + class_ + ".txt"
    G_original = nx.read_gexf("graph_gexf/scaled_map91x75.gexf")
    G = ga.sim_to_graph(G_original, sim_filename)
    print("Exporting ASCII grid...")
    mc.graph_to_UTM(G, "ASCII_grids/" + "ASCII_grid_simulation_" + sim_filename[10:])
    print("...done.")
    
def norm_weight():
    G = nx.read_gexf("graph_gexf/scaled_map91x75_normalized.gexf")
    G = gm.normalize_weight(G)
    gm.export_graph(G, "weight_norm_graph.gexf", False)

def node_from_idvent(id_vent):
    node = get_node_from_idvent(id_vent)
    print(node)

def unify(id_vent, char = 'c'):
    sparse_matrix = unify_sims(id_vent, char)    
    mc.matrix_to_UTM(sparse_matrix, id_vent, char)

def MAE_metric(id_vent, unify_type):
    utility.MAE_metric(id_vent, unify_type)

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
        setting = [0.001, [1000,7,0.15], [100, 0]]
    
    # ogni elemento di queste liste sarà una lista composta da (in ordine):
    # (precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1, f1_c)
    methods = ["TRIVECTOR", "ERUPTION", "PROBERUPTION"]
    for method in methods:
        utility.init_table(method)
        for vent in vent_list:
            if method == "TRIVECTOR":
                utility.create_row_table(trivector(vent, setting[0]), vent)
            elif method == "ERUPTION":
                utility.create_row_table(eruption1(vent, *setting[1]), vent)
            elif method == "PROBERUPTION":
                utility.create_row_table(prob_eruption_(vent, *setting[2]), vent)

def random_vent(*parameter_list):
    n_vents = int(input("Insert number of vents to compare:"))
    # Genera n vent casualmente
    vent_list = []
    for i in range(0, n_vents):
        x = random.randint(4, 4814)
        while str(x) in vent_list:
            x = str(random.randint(4, 4814))
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


    

    

    

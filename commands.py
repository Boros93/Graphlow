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

def prob_eruption_(id_vent = 0, epoch = 100):
    G = load_graph()
    if id_vent == 0:
        return
    G_ = ga.prob_eruption(G, int(id_vent), epoch)
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
    precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1 = utility.compute_metrics(id_vent, 3)
    return [precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1]


def eruption1(id_vent = 0, volume = 1000, n_days = 7, alpha = 1/8):
    
    if id_vent == 0:
        return
    G = load_graph()
    G_ = ga.eruption1(G, int(id_vent), int(volume), int(n_days), float(alpha))
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
    precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1 = utility.compute_metrics(id_vent, 2)
    return [precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1]


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
    precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1 = utility.compute_metrics(id_vent, 1)
    return [precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1]


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

def test(id_vent = 0, volume = 1000, n_days = 7, alpha = 1/8, threshold = 1):
    #test per esportare nuovi grafi
    '''G = load_graph()
    G = gm.sigmoid_norm_tr_rank(G)
    gm.export_graph(G, "scaled_map91x75_sigmoid_normalized.gexf", is_first_time = False)'''
    
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

def compare_eruption(id_vent): #capire come poter passare bene i parametri di tutti e tre i metodi
    # avvia i metodi di propagazione e mette a confronto le metriche.

    #parametri trivector
    threshold = input("Insert threshold for trivector > ")
    if threshold == "":
        threshold = 0.001
    else:
        threshold = float(threshold)

    #parametri eruption
    volume = input("Insert volume for eruption > ")
    if volume == "":
        volume = 1000
    else:
        volume = int(volume)

    n_days = input("Insert #days for eruption > ")
    if n_days == "":
        n_days = 7
    else:
        n_days = int(n_days)

    alpha = input("Insert alpha for eruption > ")
    if alpha == "":
        alpha = 0.125
    else:
        alpha = float(alpha)
    #parametri proberuption
    epoch = input("Insert epoch for proberuption > ")
    if epoch == "":
        epoch = 100
    else:
        epoch = int(epoch)
    
    #############################################
    # propagation_method = 1 ---> trivector     #
    #                    = 2 ---> eruption      #
    #                    = 3 ---> proberuption  #
    #############################################
    trivector(id_vent, threshold)
    tri_precision, tri_precision_c, tri_tpr, tri_tpr_c, tri_acc, tri_hit, tri_hit_c, tri_mae_d, tri_mae_c, tri_f1 = utility.compute_metrics(id_vent, 1)

    eruption1(id_vent, volume, n_days, alpha)
    eru_precision, eru_precision_c, eru_tpr, eru_tpr_c, eru_acc, eru_hit, eru_hit_c, eru_mae_d, eru_mae_c, eru_f1 = utility.compute_metrics(id_vent, 2)
    
    prob_eruption_(id_vent, epoch)
    pr_eru_precision, pr_eru_precision_c, pr_eru_tpr, pr_eru_tpr_c, pr_eru_acc, pr_eru_hit, pr_eru_hit_c, pr_eru_mae_d, pr_eru_mae_c, pr_eru_f1 = utility.compute_metrics(id_vent, 3)

    print("\nIn order: trivector, eruption, proberuption")
    print("PRECISION:\n", tri_precision, "\n", eru_precision, "\n", pr_eru_precision,"\n")
    print("PRECISION_C:\n", tri_precision_c, "\n", eru_precision_c, "\n", pr_eru_precision_c,"\n")
    print("\nTPR:\n", tri_tpr,"\n", eru_tpr,"\n", pr_eru_tpr,"\n")
    print("\nTPR_C:\n", tri_tpr_c,"\n", eru_tpr_c,"\n", pr_eru_tpr_c,"\n")
    print("\nACC\n", tri_acc,"\n", eru_acc,"\n", pr_eru_acc,"\n")
    print("\nHIT:\n", tri_hit,"\n", eru_hit,"\n", pr_eru_hit,"\n")
    print("\nHIT_C:\n", tri_hit_c,"\n", eru_hit_c,"\n", pr_eru_hit_c,"\n")
    print("\nMAE_D:\n", tri_mae_d,"\n", eru_mae_d,"\n", pr_eru_mae_d,"\n")
    print("\nMAE_C:\n", tri_mae_c,"\n", eru_mae_c,"\n", pr_eru_mae_c,"\n")
    print("\nF1:\n", tri_f1,"\n", eru_f1,"\n", pr_eru_f1,"\n")

def multicompare(*parameter_list, rng = True):
    vent_list = []
    # acquisisco la lista di bocche da comparare
    if rng == True:
        print("Random")
        n = int(parameter_list[0])
        for i in range(0, n):
            x = random.randint(4, 4814)
            while str(x) in vent_list:
                x = str(random.randint(4, 4814))
            vent_list.append(str(x))
        print("vent to compare:", vent_list)
    else:
        for p in parameter_list:
            vent_list.append(p)
    
    # ogni elemento di queste liste sarà una lista composta da (in ordine):
    # (precision, precision_c, tpr, tpr_c, acc, hit, hit_c, mae_d, mae_c, f1)
    methods = ["TRIVECTOR", "ERUPTION", "PROBERUPTION"]
    for method in methods:
        utility.init_table(method)
        for vent in vent_list:
            if method == "TRIVECTOR":
                utility.create_row_table(trivector(vent), vent)
            elif method == "ERUPTION":
                utility.create_row_table(eruption1(vent), vent)
            elif method == "PROBERUPTION":
                utility.create_row_table(prob_eruption_(vent), vent)
    

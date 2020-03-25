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

def begin_eruption(id_vent = 0, volume = 1000, n_days = 7, alpha = 1/8, threshold = 1):
    if os.path.exists("graph_gexf/weight_norm_graph.gexf"):
        G = nx.read_gexf("graph_gexf/weight_norm_graph.gexf")
    else:
        print("Graph does not exists.")
        return
    
    if id_vent == 0:
        print("\nWARNING! Insert an id_vent\n")
        return
    
    #G_ = ga.eruption(G, int(id_vent), int(volume), int(n_days), float(alpha), int(threshold))
    #G_ = ga.eruption_prob(G, int(id_vent), 100)
    G_ = ga.eruption1(G, int(id_vent), int(volume), int(n_days), float(alpha), int(threshold))
    print("\nExporting graph...")
    gm.export_graph(G_, "no_h_control_eruption_" + str(id_vent) + ".gexf", is_first_time = False)
    #gm.export_graph(G_, "no_h_eruption_" + str(id_vent) + ".gexf", is_first_time = False)
    print("...done.")
    print("\n\nNow you can check 'graph_gexf' folder and open", "eruption_" + str(id_vent) + ".gexf in GEPHI.")
    print("\n\nExporting ASCII grid...")
    mc.graph_to_UTM(G_, "ASCII_grids/" + "ASCII_grid_eruption_" + str(id_vent) + ".txt")
    print("...done.")
    print("\n\nNow you can check 'ASCII_grids' folder and open", "ASCII_grid_eruption_" + str(id_vent) + ".txt in QGIS.")

def prob_algorithm(id_vent):
    G = load_graph()
    G_ = probabilistic_algorithm.eruption_trivector(G, id_vent)
    gm.export_graph(G_, "prob_eruption_" + str(id_vent) + ".gexf", is_first_time = False)
    #gm.export_graph(G_, "no_h_eruption_" + str(id_vent) + ".gexf", is_first_time = False)
    print("...done.")
    print("\n\nNow you can check 'graph_gexf' folder and open", "eruption_" + str(id_vent) + ".gexf in GEPHI.")
    print("\n\nExporting ASCII grid...")
    mc.graph_to_UTM(G_, "ASCII_grids/" + "ASCII_grid_eruption_" + str(id_vent) + ".txt")
    print("...done.")
    print("\n\nNow you can check 'ASCII_grids' folder and open", "ASCII_grid_eruption_" + str(id_vent) + ".txt in QGIS.")

    print("Exporting sparse matrix...")
    utility.vect_to_matrix(id_vent)
    print("done.\n")

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

def test():
    utility.hit_metric(666)
    return
    
def norm_weight():
    G = nx.read_gexf("graph_gexf/scaled_map91x75_normalized.gexf")
    G = gm.normalize_weight(G)
    gm.export_graph(G, "weight_norm_graph.gexf", False)

def node_from_idvent(id_vent):
    node = get_node_from_idvent(id_vent)
    print(node)

def unify(id_vent, char):
    sparse_matrix = unify_sims(id_vent, char)    
    mc.matrix_to_UTM(sparse_matrix, id_vent, char)

def MAE_metric(id_vent):
    utility.MAE_metric(id_vent)

def hit_metric(id_vent):
    utility.hit_metric(id_vent)
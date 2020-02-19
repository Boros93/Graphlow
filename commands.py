import map_creator as mc
import graph_algorithm as ga
import graph_maker as gm
import os
import networkx as nx
import map_creator as mc
from utility import graph_to_matrix


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
                               example of usage:  eruption 50000 100 2233 0.11 10

    - showsim: is used to show a simulation from MAGFLOW. It needs the follow parameters:
            id vent(int)    <- integer between 4 and 4814 which indicates the id of vent. 
                               You can find it in 'Data/simulations/' after 'NotN_vent_' string.
            class(int)      <- integer in range 1 to 6 that indicates the eruption class. 
                               An eruption class is a combination of volume and duration of eruption. default 1
                               example of usage: showsim 2233 6
    """)

def begin_eruption(id_vent = 0, volume = 1000, n_days = 7, alpha = 1/8, threshold = 1):
    if os.path.exists("graph_gexf/scaled_map91x75_normalized.gexf"):
        G = nx.read_gexf("graph_gexf/scaled_map91x75_normalized.gexf")
    else:
        print("Graph does not exists.")
        return
    
    if id_vent == 0:
        print("\nWARNING! Insert an id_vent\n")
        return
    
    G_ = ga.eruption(G, int(id_vent), int(volume), int(n_days), float(alpha), int(threshold))
    print("Exporting graph...")
    gm.export_graph(G_, "eruption_" + str(id_vent) + ".gexf", is_first_time = False)
    print("...done.")
    print("Now you can check 'graph_gexf' folder and open", "eruption_" + str(id_vent) + ".gexf in GEPHI.")
    print("Exporting ASCII grid...")
    mc.graph_to_UTM(G_, "ASCII_grids/" + "ASCII_grid_eruption_" + str(id_vent) + ".txt")
    print("...done.")
    print("Now you can check 'ASCII_grids' folder and open", "ASCII_grid_eruption_" + str(id_vent) + ".txt in QGIS.")


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
    G = nx.read_gexf("graph_gexf/weight_norm_graph.gexf")
    graph_to_matrix(G)

def norm_weight():
    G = nx.read_gexf("graph_gexf/scaled_map91x75_normalized.gexf")
    G = gm.normalize_weight(G)
    gm.export_graph(G, "weight_norm_graph.gexf", False)
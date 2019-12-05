import graph_maker as gm
import utility
import graph_algorithm as ga
import os
import networkx as nx
import glob
# Set parameters
x_shape = 91
y_shape = 75
filename = "scaled_map25x25" # set shape to x=91, y=75
#csv_filename = "graph_test.csv" # set shape to x=5, y=4

# cariga il grafo se esiste, altrimenti lo crea. 
if os.path.exists("graph_gexf\\scaled_map25x25.gexf"):
    G = nx.read_gexf("graph_gexf\\scaled_map25x25.gexf")
else: 
    # Carica la linked map csv
    our_map = utility.load_csv_map(shapes=[x_shape, y_shape], map_filename = ".\\CSVMaps\\"+ filename + ".csv")
    G = gm.create_graph(our_map)
    # e lo esporta
    G = gm.export_graph(G, filename + ".gexf", is_first_time = True)

i = 0
for sim in os.listdir(("Data\\simulations\\")):
    if i < 1:
        print ("processo ", sim)
        G = ga.set_node_rank(G, sim)
        os.rename("Data\\simulations\\"+sim, "Data\\sim_processed\\" + sim)
        i +=1

# aggiungere export del grafo
gm.export_graph(G, filename + "transmit.gexf", is_first_time = False)
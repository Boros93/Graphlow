import graph_maker as gm
import utility
import graph_algorithm as ga
import os
import networkx as nx
import glob
import processing as prx
# Set parameters
scale_factor = 25
x_shape = int(2275/scale_factor)
y_shape = int(1875/scale_factor)
filename = "graphlow"

# cariga il grafo se esiste, altrimenti lo crea. 
if os.path.exists("graph_gexf/"+filename+".gexf"):
    G = nx.read_gexf("graph_gexf/"+filename+".gexf")
else: 
    # Carica la linked map csv
    if os.path.exists("./CSVMaps/" + filename + ".csv"):    
        our_map = utility.load_csv_map(shapes=[x_shape, y_shape], map_filename = "./CSVMaps/"+ filename + ".csv")
    else: 
        our_map = prx.downsampling_map(scale_factor, filename='CSVMaps/scaled_map91x75.csv')
        utility.write_in_csv(filename + ".csv", our_map)
    G = gm.create_graph(our_map)
    # set di trasmit_rank dei nodi
    i = 0
    for sim in os.listdir(("Data/simulations/")):
        if i%1000 == 0 or i ==4999:
            print ("processo ", sim)
        G = ga.set_node_rank(G, sim)
        i +=1
    # normalizzo trasmit_rank
    G = gm.normalize_trasmittance(G)
    #esporto il grafo
    gm.export_graph(G, filename + ".gexf", is_first_time = True)


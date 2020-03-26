import graph_maker as gm
import utility
import graph_algorithm as ga
import os
import networkx as nx
import glob
import processing as prx
import visualize as vi
# Set parameters
scale_factor = 25
x_shape = int(2275/scale_factor)
y_shape = int(1875/scale_factor)
filename = "scaled_map"+str(x_shape)+"x"+str(y_shape)

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
    # e la esporta
    G = gm.export_graph(G, filename + ".gexf", is_first_time = True)



if os.path.exists("graph_gexf/"+filename+"_normalized.gexf"):
    G = nx.read_gexf("graph_gexf/"+filename+"_normalized.gexf") 
else: 
    i = 0
    for sim in os.listdir(("Data/simulations/")):
        if i%1000 == 0 or i ==4999:
            print ("processo ", sim)
        G = ga.set_node_rank(G, sim)
        i +=1
    G = gm.normalize_trasmittance(G)
    #gm.export_graph(G, filename + "_normalized.gexf", is_first_time = False)
    gm.export_graph(G, "no_max_map.gexf", is_first_time = False)


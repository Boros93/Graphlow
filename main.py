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
filename = "scaled_map"+str(x_shape)+"x"+str(y_shape)

# cariga il grafo se esiste, altrimenti lo crea. 
if os.path.exists("graph_gexf\\"+filename+".gexf"):
    G = nx.read_gexf("graph_gexf\\"+filename+".gexf")
else: 
    # Carica la linked map csv
    if os.path.exists(filename+".csv"):    
        our_map = utility.load_csv_map(shapes=[x_shape, y_shape], map_filename = ".\\CSVMaps\\"+ filename + ".csv")
    else: 
        our_map = prx.downsampling_map(scale_factor, filename='CSVMaps\\linked_map.csv')
        utility.write_in_csv(filename + ".csv", our_map)
    G = gm.create_graph(our_map)
    # e la esporta
    G = gm.export_graph(G, filename + ".gexf", is_first_time = True)

i = 0
for sim in os.listdir(("Data\\simulations\\")):
    if i%1000 == 0 or i ==4999:
        print ("processo ", sim)
    G = ga.set_node_rank(G, sim)
    os.rename("Data\\simulations\\"+sim, "Data\\sim_processed\\" + sim)
    i +=1

gm.export_graph(G, filename + "transmit.gexf", is_first_time = False)
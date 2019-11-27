import graph_maker as gm
import utility
# Set parameters
x_shape = 91
y_shape = 75
filename = "scaled_map25x25" # set shape to x=91, y=75
#csv_filename = "graph_test.csv" # set shape to x=5, y=4
# Carica la linked map csv
our_map = utility.load_csv_map(shapes=[x_shape, y_shape], map_filename = ".\\CSVMaps\\"+ filename + ".csv")
# Crea il grafo 
G = gm.create_graph(our_map)
# e lo esporta
gm.export_graph(G, filename + ".gexf")
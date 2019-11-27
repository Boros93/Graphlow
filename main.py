import networkx as nx
import processing as prx
import utility

# inters(a,b)/union(a,b)
def get_jaccard_index(set_a, set_b):
    set_a = next(iter(set_a)).sim
    set_b = next(iter(set_b)).sim
    inters = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    jaccard_index = inters/union

    return jaccard_index

# set parameters
x_shape = 91
y_shape = 75
csv_filename = "scaled_map25x25.csv" # set shape to x=91, y=75
#csv_filename = "graph_test.csv" # set shape to x=5, y=4

print("Creating Graph...")
G = nx.Graph()
print("Done.")
our_map = utility.load_csv_map(shapes=[x_shape, y_shape], map_filename = ".\\CSVMaps\\"+csv_filename)
list_node = prx.aggregate(our_map)

print("Adding nodes...")
id_node = 0
for node in list_node:
    list_region = set(node[0])
    list_neighbors = set(node[1])
    G.add_node(id_node, list_region = list_region, list_neighbors = list_neighbors)
    id_node += 1
print("Done.")

print("Creating edges...")
n_edges = 0
for u in G.nodes():
    for v in G.nodes():
        if u != v:
            if len(G.node[u]["list_region"].intersection(G.node[v]["list_neighbors"])) >= 1:
                weight = get_jaccard_index(G.node[u]["list_region"], G.node[v]["list_region"])
                G.add_edge(u,v, weight=weight)
                n_edges += 1

    if (n_edges % 5000 == 0 and n_edges != 0):
        print("Created ", n_edges, " edges.")

G_copy = nx.Graph()
for u in G.nodes():
    list_region = repr((next(iter(G.node[u]["list_region"])).sim))
    G_copy.add_node(u, label= list_region)
    
for node1,node2,data in G.edges(data=True):
    G_copy.add_edge(node1, node2, weight = data['weight'])
print("fatto.")
print("Writing gexf...")

gexf_filename=csv_filename[0:-3]+"gexf"
print("Writed in" ,gexf_filename)
nx.write_gexf(G_copy, ".\\graph_gexf\\"+gexf_filename)
print("Done.")
print("Results: ", G_copy.number_of_nodes(), " nodes, ", G_copy.number_of_edges(), " edges.")



#print(G.node(0))
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

print("Creating Graph...")
G = nx.Graph()
print("Done.")
our_map = utility.load_csv_map(shapes=[x_shape, y_shape], map_filename=".\\CSVMaps\\scaled_map25x25.csv")
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
for u in G.nodes():
    for v in G.nodes():
        if u != v:
            if len(G.node[u]["list_region"].intersection(G.node[v]["list_neighbors"])) >= 1:
                weight = get_jaccard_index(G.node[u]["list_region"], G.node[v]["list_region"])
                G.add_edge(u,v, weight=weight)
    if u % 1000 == 0:
        print("processed ", u, " edges.")

G_copy = nx.Graph()
print("copio nodi")
for u in G.nodes():
    G_copy.add_node(u)
print("fatto. copio edges")
for e in G.edges():
    G_copy.add_edge(e[0], e[1])
print("fatto.")
print("Writing gexf...")
nx.write_gexf(G_copy, "Etna_graph.gexf")
print("Done.")



#print(G.node(0))
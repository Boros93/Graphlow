import networkx as nx 
import processing as prx
import utility 
import init_map 
import math
from statistics import median
import os


def create_graph(l_map):
    G = nx.DiGraph()
    ''' Aggrega le regioni, restituendo una lista formata da altre due liste di tipo Region:
    - region_list, lista delle regioni che formano il nodo (sim tutte uguali)
    - near_node_list, lista delle regioni visitate durante l'aggregazione (vicinato) '''
    list_node = prx.aggregate(l_map)
    create_nodes(G, list_node)
    create_edges(G)
    print("N. nodes: ", G.number_of_nodes())
    print("N. edges: ", G.number_of_edges())
    return G

def create_nodes(G, list_node):
    print("Adding nodes...")

    # carico il file DEM per la determinazione dell'altezza del nodo.
    scaled_hmap = init_map.create_scaled_hmap(25)

    id_node = 0
    for node in list_node:
        # Si estraggono le due liste per ogni nodo
        region_list = node[0]
        near_node_list = node[1]
        # Se la regione non ha nemmeno una sim, non viene creato il nodo
        if len(region_list[0].sim) != 0:
            # Creazione attributi da inserire nel grafo
            # Numero simulazioni per nodo
            n_sim = len(region_list[0].sim)
            # Numero di regioni aggregate
            n_region = len(region_list)
            # Coordinate dei baricentri dei nodi per layout
            x,y = get_median_position(region_list)
            coord_regions = ""
            for r in region_list:
                coord_regions += (str(r.coord)) + "|"
            #per eliminare l'ultimo delimitatore.
            coord_regions = coord_regions[0:-1]
            # Casting in set delle liste, computazionalmente efficienti
            region_list = set(region_list)
            near_node_list = set(near_node_list)
            # calcolo l'altezza del nodo.
            height = float(get_height(scaled_hmap, coord_regions))


            G.add_node(id_node, region_list = region_list, near_node_list = near_node_list, n_region = n_region,
                    n_sim = n_sim, x = x, y = y, coord_regions = coord_regions, rank = -1, is_vent = 0,
                    height = height, current_flow = 0.0, awash = False)
            id_node += 1
    print("Done.")

def create_edges(G):
    print("Creating edges...")
    n_edges = 0
    for u in G.nodes():
        for v in G.nodes():
            if u != v:
                # Se ci sono elementi in comune tra la lista delle regioni di u e i vicini di v, allora viene creato l'edge
                if len(G.node[u]['region_list'].intersection(G.node[v]['near_node_list'])) >= 1:
                    # Calcolo pesi degli edge
                    weight_uv = get_weight(G.node[u]['region_list'], G.node[v]['region_list'])
                    weight_vu = get_weight(G.node[v]['region_list'], G.node[u]['region_list'])

                    #calcolo la pendenza dell'arco (u, v)
                    slope_uv = compute_slope(G, u, v)
                    slope_vu = -slope_uv
                    # Viene creato l'edge solo se il peso è maggiore di 0
                    if weight_uv != 0:
                        G.add_edge(u, v, weight=weight_uv, transmit_rank = 0, slope = slope_uv, forwarding_flow = 0.0, trasmittance = 0.0)
                        G.add_edge(v, u, weight=weight_vu, transmit_rank = 0, slope = slope_vu, forwarding_flow = 0.0, trasmittance = 0.0)
                        n_edges += 2
                    if n_edges % 5000 == 0 and n_edges != 0:
                        print("Created", n_edges, " edges")
                        
    print("Done.")

# Metodo per esportare il grafo in formato .gexf (per visualizzare)
def export_graph(G, filename, is_first_time):
    print("Writing gexf file...")
    # Crea una copia del grafo per esportarlo con gli attributi 
    G_copy = nx.DiGraph()
    for u, data in G.nodes(data=True):
        # Fa il cast da set a stringa per darlo come attributo (gephi non accetta set),
                # solo se il grafo non è stato importato.
        if is_first_time: 
            region_list = repr((next(iter(G.node[u]["region_list"])).sim))
            G_copy.add_node(u, region_list = region_list, n_region = data['n_region'], n_sim = data['n_sim'],
                            x = - int(data['x']), y = int(data['y']), coord_regions = data["coord_regions"], 
                            rank = data["rank"], is_vent = data["is_vent"], height = data["height"], 
                            current_flow = data["current_flow"], awash = data["awash"])
        else:
            region_list = data["region_list"]
            G_copy.add_node(u, region_list = region_list, n_region = data['n_region'], n_sim = data['n_sim'],
                            x = int(data['x']), y = int(data['y']), coord_regions = data["coord_regions"], 
                            rank = data["rank"], is_vent = data["is_vent"], height = data["height"],
                            current_flow = data["current_flow"], awash = data["awash"])
        
    for node1, node2, data in G.edges(data=True):
        G_copy.add_edge(node1, node2, weight = data['weight'], transmit_rank = data["transmit_rank"], slope = data["slope"],
                        forwarding_flow = data["forwarding_flow"], trasmittance = data["trasmittance"])

    nx.write_gexf(G_copy, "./graph_gexf/"+filename)
    print("Writed in ", filename)
    return G_copy

# Metodo per calcolare un eventuale peso: inters(a,b)/union(a,b)
def get_jaccard_index(set_a, set_b):
    set_a = next(iter(set_a)).sim
    set_b = next(iter(set_b)).sim
    inters = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    jaccard_index = inters/union

    return jaccard_index

# Metodo per calcolare il peso: inters(a,b)/len(a)
def get_weight(set_a, set_b):
    set_a = next(iter(set_a)).sim
    set_b = next(iter(set_b)).sim
    inters = len(set_a.intersection(set_b))
    weight = inters/len(set_a)
    return weight

# Metodo per calcolare il baricentro di una regione
def get_median_position(list_region):
    list_x = []
    list_y = []
    for reg in list_region:
        list_x.append(reg.coord[0])
        list_y.append(reg.coord[1])
    median_x = median(list_x)
    median_y = median(list_y)
    return median_x, median_y

def get_height(scaled_hmap, coord_regions):
    coord_regions = coord_regions.split("|")
    median_list = []
    for coord in coord_regions:    
        coord = utility.cast_coord_attr(coord)
        median_list.append(scaled_hmap[coord[0]][coord[1]])
    med = median(median_list)
    return med

def node_distance(G, u, v):
    delta_x = abs(G.node[u]["x"] - G.node[v]["x"])
    delta_y = abs(G.node[u]["y"] - G.node[v]["y"])
    distance = math.sqrt(delta_x**2 + delta_y**2)
    return distance
    
def compute_slope(G, u, v):
    delta_h = G.node[u]["height"] - G.node[v]["height"]
    delta_uv = node_distance(G, u, v)
    slope = delta_h/delta_uv
    return slope

def normalize_trasmittance(G):
    for u in G.nodes():
        max_trasm = 0
        sum_trasm = 0
        for v in G.successors(u):
            u_v_trasm = G.edges[u, v]["transmit_rank"]
            sum_trasm += u_v_trasm
            if max_trasm < u_v_trasm:
                max_trasm = u_v_trasm
        if max_trasm > 0:
            denominator = sum_trasm + max_trasm
            for v in G.successors(u):
                G.edges[u, v]["trasmittance"] =  G.edges[u, v]["transmit_rank"] / denominator
    return G


            
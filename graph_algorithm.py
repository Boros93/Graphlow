import utility
import queue


def set_node_rank(G, not_n_filename):
    rank = 0
    coord_vent = utility.vent_in_dem(not_n_filename)
    # ricerca del nodo che contiene la coordinata della bocca selezionata.
    for u, data in G.nodes(data=True):
        for coords in data["coord_regions"].split("|"):
            coord_x, coord_y = utility.cast_coord_attr(coords)
            if coord_x == int(coord_vent[0]/25) and coord_y == int(coord_vent[1]/25):
                root = u 
                break
        else: 
            continue
        break
    G.node[root]['rank'] = 0
    
    G.node[root]["marked"] = 1
    
    next_queue = queue.Queue()
    id_sim =  not_n_filename[10:-4].split('_')[0] + not_n_filename[10:-4].split('_')[1]

    for u in get_neighbors(G, root, id_sim):
        next_queue.put(u)
    current_queue = queue.Queue()

    while not next_queue.empty():
        rank += 1
        print("rank= ", rank)
        current_queue = next_to_current(current_queue, next_queue)
        next_queue = queue.Queue()
        while not current_queue.empty():
            n = current_queue.get()
            if "marked" not in G.node[n]:
                G.node[n]["marked"] = 1
                print("marked: ", n)
                G.node[n]["rank"] = rank
                assign_transmit_rank(G, n, rank)
                for u in get_neighbors(G, n, id_sim):
                    next_queue.put(u)
    return G

def assign_transmit_rank(G, u, rank):
    for v in G.predecessors(u):
        if G.node[v]["rank"] == (rank-1):
            G.edges[v, u]["transmit_rank"] += 1

def get_neighbors(G, u, id_sim):
    list_neighbors = []
    for n in G.successors(u):
        region_list = G.node[n]["region_list"][1:-1]
        region_list = region_list.split(', ')
        if id_sim in region_list and "marked" not in G.node[n]:
            list_neighbors.append(n)
    return list_neighbors
        
def next_to_current(current_queue, next_queue):
    while not next_queue.empty():
        current_queue.put(next_queue.get())
    return current_queue
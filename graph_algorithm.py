import utility
import queue
import math
import random
from scipy import sparse
import numpy as np

def set_node_rank(G, not_n_filename):
    # inserisco nella lista il nodo per poter azzerarne il rango alla fine.
    not_n_nodes = []
    rank = 0
    id_vent = utility.id_from_not_n(not_n_filename)
    coord_vent = utility.vent_in_dem(id_vent)
    # ricerca del nodo che contiene la coordinata della bocca selezionata.
    root = get_id_from_coord(G, coord_vent)
    G.node[root]['rank'] = 0
    G.node[root]["marked"] = 1
    G.node[root]["is_vent"] = 1
    # inserisco nella lista il nodo per poter azzerarne il rango alla fine.
    not_n_nodes.append(root)
    next_queue = queue.Queue()
    id_sim =  not_n_filename[10:-4].split('_')[0] + not_n_filename[10:-4].split('_')[1]

    for u in get_neighbors(G, root, id_sim):
        next_queue.put(u)
    current_queue = queue.Queue()

    while not next_queue.empty():
        rank += 1
        current_queue = next_to_current(current_queue, next_queue)
        next_queue = queue.Queue()
        while not current_queue.empty():
            n = current_queue.get()
            if "marked" not in G.node[n]:
                G.node[n]["marked"] = 1
                G.node[n]["rank"] = rank
                # inserisco nella lista il nodo per poter azzerarne il rango alla fine.
                not_n_nodes.append(n)
                assign_transmit_rank(G, n, rank)
                for u in get_neighbors(G, n, id_sim):
                    next_queue.put(u)
    # azzero il rango e resetto marked
    for n in not_n_nodes:
        G.node[n]["rank"] = -1
        del G.node[n]["marked"]
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

def get_id_from_coord(G, coord):
    for u, data in G.nodes(data=True):
        for coords in data["coord_regions"].split("|"):
            coord_x, coord_y = utility.cast_coord_attr(coords)
            if coord_x == int(coord[0]/25) and coord_y == int(coord[1]/25):
                return u

'''def eruption(G, id_vent, volume, n_days, alpha, threshold):
    volume_per_day = int(volume/n_days)
    volume_remaining = volume
    node_to_visit=[]
    coord_vent = utility.vent_in_dem(id_vent)
    root = get_id_from_coord(G, coord_vent)
    node_to_visit.append(root)
    G.node[root]["current_flow"] = volume_per_day
    volume_remaining -= volume_per_day

    day_count = 1
    while not len(node_to_visit) == 0:
        temp_list = []
        if volume_remaining > 0:
            print("giorno", day_count)
            G.node[root]["current_flow"] += volume_per_day
            volume_remaining -= volume_per_day
            day_count += 1
        for u in node_to_visit:
            for v in G.successors(u):
                #print("delta_h:", delta_h)
                u_flow = G.node[u]["current_flow"]
                v_flow = G.node[v]["current_flow"]
                u_height = G.node[u]["height"]
                v_height = G.node[v]["height"]
                delta_h = u_flow - v_flow
                if delta_h > threshold:
                    if u_flow + u_height > v_flow + v_height:
                        temp = (u_flow + u_height)/(v_flow + v_height)
                        G.edges[u, v]["forwarding_flow"] = G.edges[u, v]["trasmittance"] * alpha * delta_h * (1/ (1 + math.exp(-temp)))
                        if u not in temp_list and G.edges[u, v]["forwarding_flow"] > 0.1:
                            #print("forwarding flow",G.edges[u, v]["forwarding_flow"], "from", u,"to",v)
                            temp_list.append(u)
        if len(temp_list) > 0:
            for u in node_to_visit:
                for v in G.successors(u):
                    if G.edges[u, v]["forwarding_flow"] > 0:
                        G.node[v]["current_flow"] += G.edges[u, v]["forwarding_flow"]
                        G.node[u]["current_flow"] -= G.edges[u, v]["forwarding_flow"]
                        #print("passo", G.edges[u, v]["forwarding_flow"],"lava da", u,"a", v)
                        G.edges[u, v]["forwarding_flow"] = 0.0
                        if v not in temp_list:
                            temp_list.append(v)
                #print("flow nel nodo", G.node[u]["current_flow"])
        #print("flusso nel nodo root", G.node[root]["current_flow"])
        node_to_visit = []
        node_to_visit = temp_list
    return G'''

# eruption con controlli su transmitrank e senza controlli su altezze
# transmit_rank(u, v) - transmit_rank(v, u) > epsilon 
# LAVA TRASMESSA TUTTA PRIMA DI EMETTERLA DI NUOVO
def eruption1(G, id_vent, volume, n_days, alpha):
    volume_per_day = int(volume/n_days)
    volume_remaining = volume
    node_to_visit=[]
    coord_vent = utility.vent_in_dem(id_vent - 1)
    root = get_id_from_coord(G, coord_vent)
    node_to_visit.append(root)
    G.node[root]["current_flow"] = volume_per_day
    volume_remaining -= volume_per_day

    epsilon = 0.15
    day_count = 1
    while volume_remaining > 0:
        G.node[root]["current_flow"] += volume_per_day
        volume_remaining -= volume_per_day
        day_count += 1
        while not len(node_to_visit) == 0:
            temp_list = []
            for u in node_to_visit:
                for v in G.successors(u):
                    #print("delta_h:", delta_h)
                    u_flow = G.node[u]["current_flow"]
                    v_flow = G.node[v]["current_flow"]
                    u_height = G.node[u]["height"]
                    v_height = G.node[v]["height"]
                    delta_h = (u_flow + u_height) - (v_flow + v_height)
                    if delta_h < 0:
                        continue
                    delta_h = min(delta_h, u_flow)
                    temp = (u_flow + u_height)/(v_flow + v_height) - 1
                    if  G.edges[u, v]["trasmittance"] - G.edges[v, u]["trasmittance"] > epsilon:
                        G.edges[u, v]["forwarding_flow"] = G.edges[u, v]["trasmittance"] * alpha * delta_h * (1/ (1 + math.exp(-temp)))
                        if u not in temp_list and G.edges[u, v]["forwarding_flow"] > 0.1:
                            temp_list.append(u)
            if len(temp_list) > 0:
                for u in node_to_visit:
                    for v in G.successors(u):
                        if G.edges[u, v]["forwarding_flow"] > 0:
                            G.node[v]["current_flow"] += G.edges[u, v]["forwarding_flow"]
                            G.node[u]["current_flow"] -= G.edges[u, v]["forwarding_flow"]
                            G.edges[u, v]["forwarding_flow"] = 0.0
                            if v not in temp_list:
                                temp_list.append(v)
                    
            node_to_visit = []
            node_to_visit = temp_list
    # esporta l'output come vettore per poi ottenere la matrice sparsa
    #        necessaria per il calcolo delle metriche
    vect = np.zeros(len(G.nodes()))
    max_cf = 0 

    for u in G.nodes():
        if G.node[u]["current_flow"] > max_cf:
            max_cf = G.node[u]["current_flow"]
    for u in G.nodes(): 
        
        val = (G.node[u]["current_flow"] - 1.e-7) / (max_cf - 1.e-7)
        vect[int(u)] = val
        if vect[int(u)] < 1.e-7:
            vect[int(u)] = 0
    
    sparse_vect = sparse.csr_matrix(vect)
    sparse.save_npz("sparse/eruption_" + str(id_vent) + ".npz", sparse_vect, compressed = True)
    return G

# eruption con controlli su transmitrank e senza controlli su altezze
# transmit_rank(u, v) - transmit_rank(v, u) > epsilon 
def eruption1_old(G, id_vent, volume, n_days, alpha):
    volume_per_day = int(volume/n_days)
    volume_remaining = volume
    node_to_visit=[]
    coord_vent = utility.vent_in_dem(id_vent - 1)
    root = get_id_from_coord(G, coord_vent)
    node_to_visit.append(root)
    G.node[root]["current_flow"] = volume_per_day
    volume_remaining -= volume_per_day

    epsilon = 0.15
    day_count = 1
    while not len(node_to_visit) == 0:
        temp_list = []
        if volume_remaining > 0:
            G.node[root]["current_flow"] += volume_per_day
            volume_remaining -= volume_per_day
            day_count += 1
        for u in node_to_visit:
            for v in G.successors(u):
                #print("delta_h:", delta_h)
                u_flow = G.node[u]["current_flow"]
                v_flow = G.node[v]["current_flow"]
                u_height = G.node[u]["height"]
                v_height = G.node[v]["height"]
                delta_h = (u_flow + u_height) - (v_flow + v_height)
                if delta_h < 0:
                    continue
                delta_h = min(delta_h, u_flow)
                temp = (u_flow + u_height)/(v_flow + v_height) - 1
                if  G.edges[u, v]["trasmittance"] - G.edges[v, u]["trasmittance"] > epsilon:
                    G.edges[u, v]["forwarding_flow"] = G.edges[u, v]["trasmittance"] * alpha * delta_h * (1/ (1 + math.exp(-temp)))
                    if u not in temp_list and G.edges[u, v]["forwarding_flow"] > 0.1:
                        temp_list.append(u)
        if len(temp_list) > 0:
            for u in node_to_visit:
                for v in G.successors(u):
                    if G.edges[u, v]["forwarding_flow"] > 0:
                        G.node[v]["current_flow"] += G.edges[u, v]["forwarding_flow"]
                        G.node[u]["current_flow"] -= G.edges[u, v]["forwarding_flow"]
                        G.edges[u, v]["forwarding_flow"] = 0.0
                        if v not in temp_list:
                            temp_list.append(v)
                
        node_to_visit = []
        node_to_visit = temp_list
    # esporta l'output come vettore per poi ottenere la matrice sparsa
    #        necessaria per il calcolo delle metriche
    vect = np.zeros(len(G.nodes()))
    max_cf = 0 

    for u in G.nodes():
        if G.node[u]["current_flow"] > max_cf:
            max_cf = G.node[u]["current_flow"]
    for u in G.nodes(): 
        
        val = (G.node[u]["current_flow"] - 1.e-7) / (max_cf - 1.e-7)
        vect[int(u)] = val
        if vect[int(u)] < 1.e-7:
            vect[int(u)] = 0
        if G.node[u]["current_flow"] == max_cf:
            print(vect[int(u)])
    
    sparse_vect = sparse.csr_matrix(vect)
    sparse.save_npz("sparse/eruption_" + str(id_vent) + ".npz", sparse_vect, compressed = True)
    return G

'''def eruption_new(G, id_vent, threshold):
    print(threshold)
    coord_vent = utility.vent_in_dem(id_vent)
    root = get_id_from_coord(G, coord_vent)
    print(root)
    G.node[root]['current_flow'] = 1
    G.node[root]['awash'] = True
    node_to_visit = queue.Queue()
    node_to_visit.put(root)
    while not node_to_visit.empty():
        #print("node to visit size:", node_to_visit.qsize())
        current_node = node_to_visit.get()
        # print(current_node)
        for v in G.successors(current_node):
            if(not G.node[v]['awash']):
                node_to_visit.put(v)
                flow = G.node[current_node]['current_flow'] * G.edges[current_node, v]["weight"]
                if flow > threshold:
                    G.node[v]['current_flow'] += flow 
                    G.node[current_node]['current_flow'] -= flow
                    print(G.node[current_node]['current_flow'])
                G.node[v]['awash'] = True
    return G'''


def prob_eruption(G, id_vent, epoch):
    coord_vent = utility.vent_in_dem(id_vent - 1)
    root = get_id_from_coord(G, coord_vent)
    node_to_restart = []
    for ep in range(0, epoch):
        G.node[root]['awash'] = True
        node_to_visit = queue.Queue()
        node_to_visit.put(root)
        while not node_to_visit.empty():
            current_node = node_to_visit.get()
            awashed = 0
            max_prob = 0
            id_max_prob = 0
            for v in G.successors(current_node):
                if(not G.node[v]['awash']):
                    rand_value = random.uniform(0, 1)
                    if rand_value < G.edges[current_node, v]["trasmittance"]:
                        awashed += 1
                        G.node[v]['awash'] = True
                        G.node[v]['current_flow'] += 1
                        node_to_restart.append(v)
                        node_to_visit.put(v)
                if G.edges[current_node, v]["trasmittance"] > max_prob:
                    max_prob = G.edges[current_node, v]["trasmittance"]
                    id_max_prob = v

            if id_max_prob != 0:
                if awashed == 0:
                    if(not G.node[id_max_prob]['awash']):
                        rand_value = random.uniform(0,1)
                        if rand_value < 0.5:
                            G.node[id_max_prob]['awash'] = True
                            node_to_restart.append(id_max_prob)
                            G.node[id_max_prob]['current_flow'] += 1
                            node_to_visit.put(v)
                            #print(v, "Awashed dopo")
        for node in node_to_restart:
            G.node[node]['awash'] = False


    # esporta l'output come vettore per poi ottenere la matrice sparsa
    #        necessaria per il calcolo delle metriche
    vect = np.zeros(len(G.nodes()))
    for u in G.nodes():
        G.node[u]['current_flow'] = G.node[u]['current_flow'] / epoch
        vect[int(u)] = G.node[u]["current_flow"] / epoch
    sparse_vect = sparse.csr_matrix(vect)
    sparse.save_npz("sparse/proberuption_" + str(id_vent) + ".npz", sparse_vect, compressed = True)
    return G

#seconda implementazione del metodo eruption
'''def eruption(G, volume, id_vent):
    coord_vent = utility.vent_in_dem(id_vent)
    root = get_id_from_coord(G, coord_vent)
    G.node[root]["current_flow"] = volume
    next_queue = queue.Queue()
    next_queue.put(root)
    while not next_queue.empty():
        current_node = next_queue.get()
        print("sono nel nodo: ", current_node)
        print("current_flow", G.node[current_node]["current_flow"])
        if not G.node[current_node]["awash"]:
            G.node[current_node]["awash"] = True
            sum_transmit_rank, max_transmit_rank = 0, 0
            for v in G.successors(current_node):
                u_v_transmit_rank = G.edges[current_node, v]["transmit_rank"]
                sum_transmit_rank += u_v_transmit_rank
                if max_transmit_rank < u_v_transmit_rank:
                    max_transmit_rank = u_v_transmit_rank
            denominator = sum_transmit_rank + max_transmit_rank
            sum_flow = 0
            tau = G.node[current_node]["current_flow"]/denominator
            for v in G.successors(current_node):
                out_flow = int(G.edges[current_node, v]["transmit_rank"] * tau)
                if out_flow > 0 and not G.node[v]["awash"]:
                    G.node[v]["current_flow"] = out_flow
                    next_queue.put(v)
                    print("metto in coda il nodo:", v)
                    print("arco= ", current_node, " - ", v, "transmit rank= ",  G.edges[current_node, v]["transmit_rank"])
                    sum_flow += out_flow
            G.node[current_node]["current_flow"] = G.node[current_node]["current_flow"] - sum_flow
            print("current flow after forwarding:", G.node[current_node]["current_flow"])'''

# prima implementazione del metodo eruption
'''def eruption_old(G, volume, capacity, id_vent):
    coord_vent = utility.vent_in_dem(id_vent)
    root = get_id_from_coord(G, coord_vent)
    G.node[root]["current_flow"] = volume
    G.node[root]["marked"] = True
    next_queue = queue.Queue()
    next_queue.put(root)

    while not next_queue.empty():
        current_node = next_queue.get()
        if G.node[current_node]["current_flow"] > capacity:
            print("sono nel nodo: ", current_node)
            G.node[current_node]["marked"] = True
            if G.node[current_node]["current_flow"] > capacity:
                out_flow = G.node[current_node]["current_flow"] - capacity
            else: 
                out_flow=0
            print("current_flow", G.node[current_node]["current_flow"]," out_flow:", out_flow)
            if out_flow > capacity:
                G.node[current_node]["current_flow"] = capacity
            else:
                G.node[current_node]["current_flow"] = out_flow
            
            neighbors = G.successors(current_node)
            tot_transmit = 0
            for neigh in neighbors:
                if "marked" not in G.node[neigh]:
                    print("arco= ", current_node, " - ", neigh, "transmit rank= ",  G.edges[current_node, neigh]["transmit_rank"])
                    tot_transmit += G.edges[current_node, neigh]["transmit_rank"]
            print("tot_transmit:",tot_transmit)
            if not tot_transmit == 0:
                unit_flow = out_flow/tot_transmit
                neighbors = G.successors(current_node)
                for neigh in neighbors:
                    if "marked" not in G.node[neigh]:    
                        G.node[neigh]["current_flow"] += int(unit_flow * G.edges[current_node, neigh]["transmit_rank"])
                        if  G.node[neigh]["current_flow"] > capacity:
                            print("metto in coda il nodo:", neigh)
                            G.node[current_node]["marked"] = True
                            next_queue.put(neigh)'''
            
def sim_to_graph(G_original, not_n_filename):
    G = set_node_rank(G_original, not_n_filename)
    for u, v, data in G.edges(data = True):
        if not data["transmit_rank"] == 0:
            G.node[u]["current_flow"] = 1
            G.node[v]["current_flow"] = 1
    
    return G
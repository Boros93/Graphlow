import os
import utility
import map_creator as mc
from scipy import sparse
from Propagation import Propagation

# Tabella della verità 
#    | eruption | real  |
# TP |     V    |   V   |
# TN |     X    |   X   |
# FP |     V    |   X   |
# FN |     X    |   V   |
def compute(id_vents: list, neighbor, sparse_matrix, G):
    M_graphlow = sparse_matrix.toarray()
    # Caricamento simulazioni MAGFLOW da confrontare
    # real[row][col] = 0 o 1
    udsim_sparse_file = "sparse/sparse_sim_d" + neighbor + "_" + str(id_vents[0]) + ".npz"
    # real[row][col] = TRA 0 e 1
    ucsim_sparse_file = "sparse/sparse_sim_c" + neighbor + "_" + str(id_vents[0]) + ".npz"
    
    # Se non esiste in memoria la matrice sparsa della simulazione, le crea e esporta anche l'ascii grid
    if not os.path.isfile(udsim_sparse_file):
        sparse_matrix = utility.unify_sims(id_vents, 'd', neighbor)
        mc.ascii_creator(id_vents, "udsim" + neighbor, sparse_matrix)
    if not os.path.isfile(ucsim_sparse_file):
        sparse_matrix = utility.unify_sims(id_vents, 'c', neighbor)
        mc.ascii_creator(id_vents, "ucsim" + neighbor, sparse_matrix)
        
    M_real_d = sparse.load_npz(udsim_sparse_file).toarray()
    M_real_c = sparse.load_npz(ucsim_sparse_file).toarray()
    

    fp = 0      # Contatore di fp booleano
    tp = 0      # Contatore di tp booleano
    tn = 0      # Contatore di tn booleano
    fn = 0      # Contatore di fn booleano
    
    tp_c = 0    # ACCUMULATORE tp
    tn_c = 0    # ACCUMULATORE tn
    fp_c = 0    # ACCUMULATORE fp
    fn_c = 0    # ACCUMULATORE fn

    #variabili che servono a calcolare TPR e precision entrambi nel caso continuo
    sum_real = 0
    sum_graphlow = 0

    maxes = 0

    for row in range(0, M_graphlow.shape[0]):
        for col in range(0, M_graphlow.shape[1]):
            if M_graphlow[row][col] > 0 and M_real_d[row][col] > 0:     # tp
                tp += 1
            if M_graphlow[row][col] > 0 and M_real_d[row][col] == 0:    # fp
                fp += 1
            if M_graphlow[row][col] == 0 and M_real_d[row][col] == 0:   # tn
                tn += 1
            if M_graphlow[row][col] == 0 and M_real_d[row][col] > 0:   # fn 
                fn += 1

            tp_c += min(M_real_c[row][col], M_graphlow[row][col])
            tn_c += min(1 - M_real_c[row][col], 1 - M_graphlow[row][col])
            fp_c += min(1 - M_real_c[row][col], M_graphlow[row][col])
            fn_c += min(M_real_c[row][col], 1 - M_graphlow[row][col])

            sum_graphlow += M_graphlow[row][col]
            sum_real += M_real_c[row][col]

            maxes += max(M_real_c[row][col], M_graphlow[row][col])

    #################### calcolo le metriche ########################
    precision = ppv(tp, fp)
    precision_c = tp_c / sum_graphlow
    tpr = tp_rate(tp, fn)
    tpr_c = tp_c / sum_real
    hit = hit_rate(tp, fp, fn)
    # maxes = sum(max(real, graphlow))
    hit_c = tp_c / maxes
    F1 = f1(precision,tpr)
    F1_c = f1(precision_c, tpr_c)
    n_invaded_cities, risk = count_invaded_cities(G)
    #################################################################

    return [precision, precision_c, tpr, tpr_c, hit, hit_c, F1, F1_c, n_invaded_cities, risk]

# precision = PPV = tp/(tp + fp)
def ppv(tp, fp):
    if not tp + fp == 0:
        precision = tp/ (tp + fp)
    else:
        precision = 0
    return precision

# TPR = RECALL = tp/(tp + fn)
def tp_rate(tp, fn):
    if not tp + fn == 0:
        tpr = tp/ (tp + fn)
    else:
        tpr = 0
    return tpr

# hit_rate = tp / (fp + fn + tp)
def hit_rate(tp, fp, fn):
    if not fp + fn + tp == 0:
        hit = tp / (fp + fn + tp)
    else:
        hit = 0
    return hit

def f1(precision, tpr):
    if not precision == 0 and not tpr == 0:
        f1 = 2 * precision * tpr / (precision + tpr)
    else:
        f1 = 0
    return f1

def count_invaded_cities(G): 
    n_invaded_cities = 0
    risk = 0
    for u in G.nodes():
        if G.nodes[u]['is_city'] > 0 and G.nodes[u]['current_flow'] > 0:
            n_invaded_cities += 1
            risk += G.nodes[u]['current_flow'] * G.nodes[u]['is_city']
    return n_invaded_cities, risk

def get_ppv_list(G, vent_list):
    p = Propagation()
    p.set_Graph(G)

    ppv_list = []
    for vent in vent_list:
        sparse_matrix = p.trivector([vent])
        ppv = compute([vent], "", sparse_matrix, G)[0]
        ppv_list.append(ppv)

    return ppv_list

def get_tpr_list(G, vent_list):
    p = Propagation()
    p.set_Graph(G)

    tpr_list = []
    for vent in vent_list:
        sparse_matrix = p.trivector([vent])
        tpr = compute([vent], "", sparse_matrix, G)[2]
        tpr_list.append(tpr)

    return tpr_list
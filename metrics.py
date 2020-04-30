import os
import utility
import map_creator as mc
from scipy import sparse
# Tabella della verità 
#    | eruption | real  |
# TP |     V    |   V   |
# TN |     X    |   X   |
# FP |     V    |   X   |
# FN |     X    |   V   |
def compute(id_vent, propagation_method, sparse_matrix):
    M_graphlow = sparse_matrix.toarray()
    # Caricamento simulazioni MAGFLOW da confrontare
    # real[row][col] = 0 o 1
    udsim_sparse_file = "sparse/sparse_sim_d_" + str(id_vent) + ".npz"
    # real[row][col] = TRA 0 e 1
    ucsim_sparse_file = "sparse/sparse_sim_c_" + str(id_vent) + ".npz"
    
    # Se non esiste in memoria la matrice sparsa della simulazione, le crea e esporta anche l'ascii grid
    if not os.path.isfile(udsim_sparse_file):
        sparse_matrix = utility.unify_sims(id_vent, 'd')
        mc.ascii_creator(id_vent, "udsim", sparse_matrix)
    if not os.path.isfile(ucsim_sparse_file):
        sparse_matrix = utility.unify_sims(id_vent, 'c')
        mc.ascii_creator(id_vent, "ucsim", sparse_matrix)
        
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
    n_invaded_cities = count_invaded_cities(n_invaded_cities)
    #################################################################

    return [precision, precision_c, tpr, tpr_c, hit, hit_c, F1, F1_c]

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

def count_invaded_cities(n_invaded_cities):
    return n_invaded_cities
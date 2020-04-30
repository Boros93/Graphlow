import utility
import conversion
import numpy as np
import queue
from scipy import sparse
import math
import random
import metrics

class Propagation:
    def __init__(self):
        # --- Parametri default ---
        # Trivector:
        self.tri_threshold = 0.001

        # Eruption:
        self.eru_volume = 1000
        self.eru_n_days = 7
        self.eru_threshold = 0.15

        # Montecarlo:
        self.prob_epoch = 100
        self.prob_second_chance = 0

        self.G = utility.load_graph()

    def trivector(self, id_vent):
        root = conversion.get_node_from_idvent(int(id_vent))
        # Inizializzazione dei tre vettori temporali
        vect1 = np.zeros(len(self.G.nodes()))
        vect2 = np.zeros(len(self.G.nodes()))
        vect3 = np.zeros(len(self.G.nodes()))
        # Inizializzazione della root
        vect2[int(root)] = 1
        vect3[int(root)] = 1
        # Creazione di due code, la prima per il ciclo interno e la seconda per quello esterno
        node_to_visit = queue.Queue()
        support_queue = queue.Queue()

        #definisce la chiave da controllare 
        key_to_control = "trasmittance" 

        # Iniziamo mettendo i vicini della root nella coda esterna
        for v in self.G.successors(root):
            support_queue.put(v)
        
        # Inizio ciclo esterno, cicla fin quando non abbiamo più nodi da esplorare
        while not support_queue.empty():
            
            # Trasferisco i nuovi vicini alla coda interna per poterli calcolare
            while not support_queue.empty():
                node_to_visit.put(support_queue.get())
            # Inizio ciclo interno
            while not node_to_visit.empty():
                # Estraggo il nodo di cui aggiornare la probabilità
                j_node = node_to_visit.get()
                # Estraggo i predecessori di j per calcolarmi gli incrementi
                pred = []
                # Li appendo in lista, castandoli ad int
                for v in self.G.predecessors(j_node):
                    pred.append(int(v))
                # Inizio formula
                increment = 0
                for alpha in range(0, len(pred)):
                    # Inizializzazione delle due produttorie interne (si possono eliminare)
                    product1 = 1
                    product2 = 1
                    for beta in range(0, len(pred)):
                    # memorizzo il valore della trasmittanza dell'arco (beta, j)
                        a = self.G.edges[str(pred[beta]), j_node][key_to_control]
                        # prima produttoria
                        if beta < alpha:
                            product1 *= 1 - (a * vect2[pred[beta]])
                        else:
                            product2 *= 1 - a * vect1[pred[beta]]
                    partial = product1 * product2
                    partial *= (vect2[pred[alpha]] - vect1[pred[alpha]])
                    increment += (partial * self.G.edges[str(pred[alpha]), j_node][key_to_control])
                
                # Soglia dell'incremento
                if increment > self.tri_threshold:
                    vect3[int(j_node)] = vect2[int(j_node)] + increment
                    # Inserisco in coda i successori di j in modo che verranno esplorati al prossimo ciclo
                
                support_queue_list = list(support_queue.queue)
                if increment > 1.e-7:
                    for v in self.G.successors(j_node):
                        if True: #G.edges[j_node, v][key_to_control] - G.edges[v, j_node][key_to_control] > 0:
                            if v not in support_queue_list:
                                support_queue.put(v)
            # Shift dei vettori temporali
            vect1 = vect2.copy()
            vect2 = vect3.copy()
            # vect3 resta uguale
        # Inserisco i flow calcolati nei nodi 
        for index in range(0, len(vect3)):
            value = float(vect3[index])
            self.G.nodes[str(index)]['current_flow'] = value
        # Esportazione in matrice sparsa
        sparse_matrix = self.export_sparse(vect3, id_vent, "trivector")
        return sparse_matrix

    def eruption(self, id_vent):
        alpha = 1/8
        # Suddivisione del volume nei giorni 
        volume_per_day = int(self.eru_volume/self.eru_n_days)
        volume_remaining = self.eru_volume
        node_to_visit=[]
        # Inizializzazione root
        root = conversion.get_node_from_idvent(int(id_vent))
        node_to_visit.append(root)
        self.G.nodes[root]["current_flow"] = volume_per_day
        volume_remaining -= volume_per_day
        day_count = 1

        key_to_control = "prop_weight"
        while volume_remaining > 0:
            # Ciclo esterno che gestisce il flusso giornaliero nella root
            self.G.nodes[root]["current_flow"] += volume_per_day
            volume_remaining -= volume_per_day
            day_count += 1
            while not len(node_to_visit) == 0:
                temp_list = []
                for u in node_to_visit:
                    for v in self.G.successors(u):
                        u_flow = self.G.nodes[u]["current_flow"]
                        v_flow = self.G.nodes[v]["current_flow"]
                        u_height = self.G.nodes[u]["height"]
                        v_height = self.G.nodes[v]["height"]
                        # Controllo delle altezze
                        delta_h = (u_flow + u_height) - (v_flow + v_height)
                        # Se la differenza delle altezze effettive è minore di 0, allora non propaga 
                        if delta_h < 0:
                            continue
                        delta_h = min(delta_h, u_flow)
                        temp = (u_flow + u_height)/(v_flow + v_height) - 1
                        # Se la differenza tra la trasmittanza ad uscire e quella ad entrare è minore di una soglia
                        if  self.G.edges[u, v][key_to_control] - self.G.edges[v, u][key_to_control] > self.eru_threshold:
                            # Allora propago
                            self.G.edges[u, v]["forwarding_flow"] = self.G.edges[u, v][key_to_control] * alpha * delta_h * (1/ (1 + math.exp(-temp)))
                            # Minimo flusso che si può trasmettere (minimo 0.1)
                            if u not in temp_list and self.G.edges[u, v]["forwarding_flow"] > 0.1:
                                temp_list.append(u)
                # Distribuisce il flusso che c'è negli archi sui nodi
                if len(temp_list) > 0:
                    for u in node_to_visit:
                        for v in self.G.successors(u):
                            if self.G.edges[u, v]["forwarding_flow"] > 0:
                                self.G.nodes[v]["current_flow"] += self.G.edges[u, v]["forwarding_flow"]
                                self.G.nodes[u]["current_flow"] -= self.G.edges[u, v]["forwarding_flow"]
                                self.G.edges[u, v]["forwarding_flow"] = 0.0
                                if v not in temp_list:
                                    temp_list.append(v)
                        
                node_to_visit = []
                node_to_visit = temp_list
        # esporta l'output come vettore per poi ottenere la matrice sparsa
        #        necessaria per il calcolo delle metriche
        vect = np.zeros(len(self.G.nodes()))
        max_cf = 0 

        for u in self.G.nodes():
            if self.G.nodes[u]["current_flow"] > max_cf:
                max_cf = self.G.nodes[u]["current_flow"]
        for u in self.G.nodes(): 
            # Qui vengono normalizzati i flussi tra 0 e 1
            val = (self.G.nodes[u]["current_flow"] - 1.e-7) / (max_cf - 1.e-7)
            vect[int(u)] = val
            if vect[int(u)] < 1.e-7:
                vect[int(u)] = 0
        # Esportazione in matrice sparsa
        sparse_matrix = self.export_sparse(vect, id_vent, "eruption")
        return sparse_matrix

    def montecarlo(self, id_vent):
        root = conversion.get_node_from_idvent(int(id_vent))
        # Si tiene conto dei nodi invasi, così da resettarli all'inizio della nuova epoca
        node_to_restart = []
        for ep in range(0, self.prob_epoch):
            self.G.nodes[root]['awash'] = True
            node_to_visit = queue.Queue()
            node_to_visit.put(root)
            while not node_to_visit.empty():
                current_node = node_to_visit.get()
                awashed = 0
                max_prob = 0
                id_max_prob = 0
                for v in self.G.successors(current_node):
                    if(not self.G.nodes[v]['awash']):
                        rand_value = random.uniform(0, 1)
                        if rand_value < self.G.edges[current_node, v]["trasmittance"]:
                            awashed += 1
                            self.G.nodes[v]['awash'] = True
                            self.G.nodes[v]['current_flow'] += 1
                            node_to_restart.append(v)
                            node_to_visit.put(v)
                    if self.G.edges[current_node, v]["trasmittance"] > max_prob:
                        max_prob = self.G.edges[current_node, v]["trasmittance"]
                        id_max_prob = v

                if id_max_prob != 0:
                    if awashed == 0:
                        if(not self.G.nodes[id_max_prob]['awash']):
                            rand_value = random.uniform(0,1)
                            if rand_value < self.prob_second_chance:
                                self.G.nodes[id_max_prob]['awash'] = True
                                node_to_restart.append(id_max_prob)
                                self.G.nodes[id_max_prob]['current_flow'] += 1
                                node_to_visit.put(v)
            for node in node_to_restart:
                self.G.nodes[node]['awash'] = False


        # esporta l'output come vettore per poi ottenere la matrice sparsa
        #        necessaria per il calcolo delle metriche
        vect = np.zeros(len(self.G.nodes()))

        for u in self.G.nodes():
            self.G.nodes[u]['current_flow'] = self.G.nodes[u]['current_flow'] / self.prob_epoch
            vect[int(u)] = self.G.nodes[u]["current_flow"] / self.prob_epoch
        
        # Esportazione in matrice sparsa
        sparse_matrix = self.export_sparse(vect, id_vent, "proberuption")
        return sparse_matrix

    def real(self, id_vent, real_class):
        if not real_class == "0":
            filename = "Data/simulations/NotN_vent_" + str(id_vent) + "_" + str(real_class) + ".txt"
        else:
            sparse_M_c = utility.unify_sims(id_vent, "c")
            sparse_M_d = utility.unify_sims(id_vent, "d")
            return sparse_M_c, sparse_M_d
        # Lettura file
        with open(filename) as file:
            lines = file.readlines()

        # Lista di coordinate [[x,y], [x,y]]
        coords = []
        for line in lines:
            coords.append(line.split(" "))
        M = np.zeros((91,75), dtype=float)

        # Inserimento nella matrice
        for coord in coords:
            row = int(int(coord[0])/25)
            col = int(int(coord[1])/25)
            M[row][col] = 1

        # Trasformazione in matrice sparsa
        sparse_M = sparse.csr_matrix(M)
        return sparse_M

    def export_sparse(self, vect, id_vent, propagation_method):
        M = np.zeros((91, 75), dtype=float)
        for u in self.G.nodes():
            regions = self.G.nodes[u]["coord_regions"].split("|")
            for reg in regions:
                reg_row, reg_col = conversion.cast_coord_attr(reg)
                M[reg_row][reg_col] = vect[int(u)]
        sparse_M = sparse.csr_matrix(M)
        # Decommentare se serve esportare in un file la matrice sparsa
        # sparse.save_npz("sparse/M_" + propagation_method + "_" + id_vent + ".npz", sparse_M)
        return sparse_M

    def set_trivector(self, tri_threshold):
        if not tri_threshold == -1:
            self.tri_threshold = float(tri_threshold)
    
    def set_eruption(self, eru_volume, eru_n_days, eru_threshold):
        if not eru_volume == -1: 
            self.eru_volume = int(eru_volume)
        if not eru_n_days == -1: 
            self.eru_n_days = int(eru_n_days)
        if not eru_threshold == -1: 
            self.eru_threshold = float(eru_threshold)

    def set_montecarlo(self, prob_epoch, prob_second_chance):
        if not prob_epoch == -1:
            self.prob_epoch = int(prob_epoch)
        if not prob_second_chance == -1:
            self.prob_second_chance = float(prob_second_chance)

    def set_Graph(self, G):
        self.G = G 

    def get_Graph(self):
        return self.G


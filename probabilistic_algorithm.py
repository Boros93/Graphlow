import utility 
import queue
import networkx as nx 
import numpy as np
def eruption_trivector(G, id_vent):
    root = utility.get_node_from_idvent(id_vent)
    # Inizializzazione dei tre vettori temporali
    vect1 = np.zeros(len(G.nodes()))
    vect2 = np.zeros(len(G.nodes()))
    vect3 = np.zeros(len(G.nodes()))
    # Inizializzazione della root
    vect2[int(root)] = 1
    vect3[int(root)] = 1
    # Creazione di due code, la prima per il ciclo interno e la seconda per quello esterno
    node_to_visit = queue.Queue()
    support_queue = queue.Queue()
    # Iniziamo mettendo i vicini della root nella coda esterna
    for v in G.successors(root):
        support_queue.put(v)
    # Inizio ciclo esterno, cicla fin quando non abbiamo più nodi da esplorare
    while not support_queue.empty():
        print("Nodi da visitare", support_queue.qsize())
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
            for v in G.predecessors(j_node):
                pred.append(int(v))
            # Inizio formula
            increment = 0
            for alpha in range(0, len(pred)):
                # Inizializzazione delle due produttorie interne (si possono eliminare)
                product1 = 0
                product2 = 0
                for beta in range(0, len(pred)):
                # memorizzo il valore della trasmittanza dell'arco (beta, j)
                    a = G.edges[str(pred[beta]), j_node]["trasmittance"]
                    if beta < alpha:
                        product1 *= 1 - (a * vect2[pred[beta]])
                    else:
                        product2 *= 1 - a * vect1[pred[beta]]
                partial = product1 * product2
                partial *= (vect2[pred[alpha]] - vect1[pred[alpha]])
                increment += (partial * G.edges[str(pred[alpha]), j_node]["trasmittance"])
            # Soglia dell'incremento
            if increment > 0.01:
                vect3[int(j_node)] = vect2[int(j_node)] + increment
                # Inserisco in coda i successori di j in modo che verranno esplorati al prossimo ciclo
            else:
                vect3[int(j_node)] = vect2[int(j_node)]
            
            for v in G.successors(j_node):
                if G.edges[j_node, v]['trasmittance'] > G.edges[v, j_node]['trasmittance']:
                    support_queue.put(v)
        # Shift dei vettori temporali
        vect1 = vect2.copy()
        vect2 = vect3.copy()
        # vect3 resta uguale
    # Inserisco i flow calcolati nei nodi 
    for index in range(0, len(vect3)):
        G.node[str(index)]['current_flow'] = vect3[index]
    
    return G

            

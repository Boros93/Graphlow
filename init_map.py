# File contenente i metodi per creare le mappe
import numpy as np
import glob
import threading
import time
from region import Region
# Crea un array 1:1 con le altezze 
def create_hmap():
    array = []
    # Apre il file con le altezze
    with open("Data\\DEM_CT.txt") as in_file:
        content = in_file.readlines()
    # Per ogni riga del file, salta le prime 6 righe e splitta le righe estraendo le altezze, saltando l'ultimo carattere \n 
    for row in content[6:]:
        array.append(np.float_(row.split(" ")[:-1]))

    array = np.array(array, dtype="float64")
    return array
hmap = create_hmap()

# Crea una mappa sottocampionata di un fattore scale_factor
def create_scaled_hmap(scale_factor):
    hmap = create_hmap()
    s = int(scale_factor)
    # Inizializza un array con la grandezza finale
    scaled_hmap = np.zeros((int(hmap.shape[0]/s), int(hmap.shape[1]/s)), dtype="float64")
    # Inserisce negli elementi dell'array, la media dell'intorno
    for i in range(scaled_hmap.shape[0]):
        for j in range(scaled_hmap.shape[1]):
            scaled_hmap[i][j] = np.average(hmap[s*i:s*i+s, s*j:s*j+s])
    return scaled_hmap

# Crea una mappa con il numero di invasioni in ogni cella
def create_hazard_map(n_threads):
    h_map = np.zeros((2275, 1875), dtype="float16")
    # Estrae i paths delle simulazioni
    sims = glob.glob("Data\\simulations\\*.txt")
    # Calcola la dimensione del batch di ogni thread
    batch_size = int(len(sims)/n_threads)

    i = 0
    threads = []

    # Inizializzazione thread
    for n in range(n_threads):
        thread = threading.Thread(target=executeThread, args=(i,sims, h_map, batch_size))
        threads.append(thread)
        thread.start()
        # Calcola l'inizio del thread successivo
        i = i + batch_size

    for i in threads:
        i.join()
    # Salva la mappa sul disco
    np.save('h_map.npy', h_map)

def create_linked_map():
    linked_map = np.empty((2275,1875), dtype=object)
    for x in range(0, 2275):
        for y in range(0, 1875):
            linked_map[x][y] = Region(coord=(x,y))
    return linked_map

# Cosa esegue ogni thread
def executeThread(i, sims, h_map, batch_size):
    # print("Parte thread", i)
    # Esegue le simulazioni del proprio batch
    for s in sims[i:i+batch_size]:
        # print("Thread", i, "esegue ", s)
        with open(s) as in_file:
            content = in_file.readlines()
        
        for c in content:
            x = np.int(c.split(" ")[0])
            y = np.int(c.split(" ")[1])

            h_map[x][y] += 1

# --- Main ---
t0 = time.time()
l_map = create_linked_map()
print("Shape:", l_map.shape)
t1 = time.time()
total_time = t1 - t0
print("Total time:",total_time)
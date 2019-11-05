import numpy as np
from region import Region
import csv

def down_sampling(scale_factor):
    s = int(scale_factor)
    print("Inizio ad inizializzzare")
    # Inizializza un array con la grandezza finale e lo inizializzo
    scaled_lmap = np.empty((int(linked_map.shape[0]/s), int(linked_map.shape[1]/s)), dtype=object)
    for x in range(0, scaled_lmap.shape[0]):
        for y in range(0, scaled_lmap.shape[1]):
            scaled_lmap[x][y] = Region(coord=(x,y))
    print("Inizializzazione finita ",scaled_lmap.shape)
    # Inserisce negli elementi dell'array, la media dell'intorno
    for i in range(scaled_lmap.shape[0]):
        for j in range(scaled_lmap.shape[1]):
            for k in range(s):
                for l in range(s):
                    # print("PRIMA", i," ", j, ": ",scaled_lmap[i][j].sim)
                    # print("Da aggiungere", linked_map[i+k][j+l].sim)
                    scaled_lmap[i][j].sim = scaled_lmap[i][j].sim.union(linked_map[i+k][j+l].sim)
                    # print("DOPO", i," ", j, ": ",scaled_lmap[i][j].sim)
        print("Row", i, "processed")
 
        
    return scaled_lmap

def load_csvmap(filename):
    # Inizializzazione linked map
    linked_map = np.empty((2275,1875), dtype=object)
    # Aggiunge una region vuota per ogni cella
    for x in range(0, linked_map.shape[0]):
        for y in range(0, linked_map.shape[1]):
            linked_map[x][y] = Region(coord=(x,y))
    # Apre il file csv
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # Prende le prime due word (sono le coord x e y)
            coord_x = int(row[0])
            coord_y = int(row[1])
            # Per ogni cella x e y aggiunte il set (il rimanente della riga)
            linked_map[coord_x][coord_y].add_list_sim(row[2:])
            line_count+=1
            # Debug
            if line_count % 500000 == 0:
                print("Line ", line_count, " processed")
                break
                
    return linked_map

def down_sampling_map(scale_factor, filename):
    scaled_map = np.empty((2275/scale_factor , 1875/scale_factor), dtype=object)

    with open filename as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # Prende le prime due word (sono le coord x e y)
            coord_x = int(row[0]/scale_factor)
            coord_y = int(row[1]/scale_factor)

            scaled_map[coord_x][coord_y].add_list_sim(row[2:])
            line_count+=1
            if line_count % 100000 == 0 :
                print("line count = " , line_count)



linked_map= load_csvmap('linked_map.csv')
print("Coord=", linked_map[496][1308].coord, " | ", len(linked_map[496][1308].sim))
scaled_map = down_sampling(5)
print("shape",scaled_map.shape)
print("Coord=", scaled_map[100][261].coord, " | ", len(scaled_map[100][261].sim))

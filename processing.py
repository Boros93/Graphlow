import numpy as np
from region import Region
import csv
import utility
import queue


def downsampling_map(scale_factor, filename):
    # Inizializzazione scaled map vuota
    scaled_map = np.empty((int(2275/scale_factor) , int(1875/scale_factor)), dtype=object)
    for x in range(0, scaled_map.shape[0]):
        for y in range(0, scaled_map.shape[1]):
            scaled_map[x][y] = Region(coord=(x,y))
    # Bisogna sostituirlo con load_csv_map (attenzione coord)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # Prende le prime due word (sono le coord x e y)
            coord_x = int(int(row[0])/scale_factor)
            coord_y = int(int(row[1])/scale_factor)

            scaled_map[coord_x][coord_y].add_list_sim(row[2:])
            line_count+=1
            if line_count % 10000 == 0 :
                print("line count = " , line_count)

    return scaled_map


def aggregate(scaled_map):
    red = queue.Queue()
    green = queue.Queue()
    # lista dei nodi creati
    node_list = [] 
    red.put(scaled_map[0][0])
    while red.empty() == False :
        # lista degli oggetti di tipo regione che costituisce ogni nodo
        region_list = []
        current_el = red.get()
        if current_el.marked == False:
            green.put(current_el)
            while green.empty() != True:
                current_el = green.get()
                if current_el.marked == False:
                    current_el.marked = True
                    region_list.append(current_el)
                    neighbors = get_neighbors(current_el.coord, scaled_map.shape[0], scaled_map.shape[1])
                    for neighbor_coord in neighbors:
                        neighbor_el=scaled_map[neighbor_coord[0]][neighbor_coord[1]]
                        if neighbor_el.marked == False:
                            if is_mergeable(current_el, neighbor_el) == True:
                                green.put(neighbor_el)
                            else:
                                red.put(neighbor_el)                        
            node_list.append(region_list)
    return node_list


def is_mergeable(reg_a, reg_b):
    if reg_a.sim == reg_b.sim:
        return True
    return False


def get_neighbors(coord, scaled_map_x, scaled_map_y):
    neighbors = []

    for x in range(-1, 2):
        for y in range(-1, 2):
            if not(x == 0 and y == 0):
                if coord[0] + x in range(0, scaled_map_x) and coord[1] + y in range(0, scaled_map_y):
                    neighbors.append([coord[0] + x, coord[1] + y])
    return neighbors

our_map = utility.load_csv_map(shapes=[455, 375], map_filename="scaled_map.csv")
our_list_node = aggregate(our_map)
count=0
for node in our_list_node:
    count += 1
print(our_list_node[0][0].sim, our_list_node[0][1].sim)
print("numero di nodi",count)
print("Finish")


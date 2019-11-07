import numpy as np
from region import Region
import csv
import utility

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

scaled_map = downsampling_map(5,"linked_map.csv")
print("Coord=", scaled_map[100][261].coord, " | ", len(scaled_map[100][261].sim))
utility.write_in_csv("scaled_map.csv", scaled_map)
print("Finish")


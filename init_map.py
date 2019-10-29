# File contenente i metodi per creare la mappa
import numpy as np

def create_hmap():
    array = []

    with open("Data\\DEM_CT.txt") as in_file:
        content = in_file.readlines()

    for row in content[6:]:
        array.append(np.float_(row.split(" ")[:-1]))

    array = np.array(array, dtype="float64")
    return array

hmap = create_hmap()
print(hmap.shape)
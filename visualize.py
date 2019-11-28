import numpy as np
import utility
from PIL import Image
# Visualizza la numerosità delle colate in ogni cella
def create_image_from_map(l_map):
    img = np.zeros([l_map.shape[0], l_map.shape[1]], dtype=np.uint8)
    # Cerca il massimo numero di inondazioni in una cella
    max_val = 0
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            if max_val < len(l_map[i][j].sim):
                max_val = len(l_map[i][j].sim)
                print("Max val: ", max_val)
    print("Max val trovato. \nProcesso l'immagine...")

    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            n = len(l_map[i][j].sim)
            img[i][j] =int( np.log(1 + n / max_val)*255)
    print("Fatto.")
    photo = Image.fromarray(img)

    photo.save("Map.png")

def create_image_from_npy(npyfilename, imgfilename):
    np_map = np.array(np.load(npyfilename))
    img = np.zeros([np_map.shape[0], np_map.shape[1]], dtype=np.uint8)
    max_value = np.max(np_map)
    min_value = np.min(np_map)
    for x in range(np_map.shape[0]):
        for y in range(np_map.shape[1]):
            img[x][y] = int((np_map[x][y] - min_value) * (255 / (max_value - min_value)))
            # print(np_map[x][y])
    image = Image.fromarray(img)
    image.save(imgfilename)

#l_map = utility.load_csv_map([91,75], ".\\CSVMaps\\scaled_map25x25.csv")
print("Saving map...")
#create_image_from_map(l_map)
create_image_from_npy("Extra\\hazard_map.npy", "hazard_map.png")
print("Saved.")
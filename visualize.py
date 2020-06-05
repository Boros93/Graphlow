import numpy as np
import utility
import conversion
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

def print_notn(notN_filename):
    coord_vent = conversion.vent_in_dem(notN_filename)
    img_filename = "Extra/not_n/" + notN_filename
    notN_filename = "Data/simulations/" + notN_filename
    dem_map= np.zeros((2275, 1875), dtype=np.uint8)
    with open(notN_filename) as in_file:
        content = in_file.readlines()
        # Per ogni riga di una simulazione, mette il nome della simulazione nella lista della regione 
        for c in content:
            x = np.int(c.split(" ")[0])
            y = np.int(c.split(" ")[1])
            dem_map[x][y] = 75
    dem_map [coord_vent[0]][coord_vent[1]]=255
    image = Image.fromarray(dem_map)
    image.save(img_filename[:-3] + "png")
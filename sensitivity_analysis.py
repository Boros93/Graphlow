import commands
import random
from Propagation import Propagation
import statistics
import pandas as pd
import metrics
import os
def batch_analysis(n_vents):
    # Genera n vent casualmente
    vent_list = []
    # Seleziona tra le simulazioni salvate
    for sim in os.listdir(("sparse/")):
        if "sparse_sim_c" in sim:
            vent_list.append(sim[13:-4])
    vent_list = random.sample(vent_list, n_vents)
    metrics_matrix = []
    print("Vent to analyze:", vent_list)
    for vent in vent_list:
        propagation = Propagation()
        # Esecuzione algoritmo 
        sparse_matrix = propagation.trivector(vent)
        # Esportazione in ASCII e calcolo metriche
        metrics_list = metrics.compute(vent, "trivector", sparse_matrix)
        metrics_matrix.append(metrics_list)
        print("vent:", vent, " analyzed")

    dataframe = pd.DataFrame(metrics_matrix, columns=["PPV", "PPVF", "TPR", "TPRF", "F1", "F1F", "THREAT", "THREATF"])
    print(dataframe)
    print("\n")
    print(dataframe.describe())

def parameter_analysis(id_vent):
    print("Vent to analyze:", id_vent)
    metrics_matrix = []
    parameter_list = [0.001, 0.0001, 0.01]
    # Algoritmo eseguito con i parametri di default
    for parameter in parameter_list:
        propagation = Propagation()
        # Setta i parametri
        propagation.set_trivector(parameter)
        # Esecuzione algoritmo 
        sparse_matrix = propagation.trivector(id_vent)
        # Esportazione in ASCII e calcolo metriche
        metrics_list = metrics.compute(id_vent, "trivector", sparse_matrix)
        metrics_matrix.append(metrics_list)

    dataframe = pd.DataFrame(metrics_matrix, columns=["PPV", "PPVF", "TPR", "TPRF", "F1", "F1F", "THREAT", "THREATF"])
    print(dataframe)
    print("\n")

#batch_analysis(2)
# Seleziona tra le simulazioni salvate
vent_list = []
for sim in os.listdir(("sparse/")):
    if "sparse_sim_c" in sim:
        vent_list.append(sim[13:-4])
vent_list = random.sample(vent_list, 3)
for vent in vent_list:
    parameter_analysis(vent)
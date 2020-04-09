from utility import unify_sims
from utility import id_from_not_n
import os

filelist = os.listdir("Data/simulations/1/")
filelist.sort()

current_vent = 0
for f in filelist:
    tmp = id_from_not_n(f) + 1
    if not current_vent == tmp:
        current_vent = tmp
        print("unify_sim", current_vent)
        unify_sims(current_vent, 'd')
        unify_sims(current_vent, 'c')

from scipy import sparse
import numpy as np
import utility
import conversion
import map_creator
G = utility.load_graph()
vect = sparse.load_npz("gnn_test.npz")
vect = vect.toarray()
M = np.zeros((91, 75), dtype=float)
for u in G.nodes():
    regions = G.node[u]["coord_regions"].split("|")
    for reg in regions:
        reg_row, reg_col = conversion.cast_coord_attr(reg)
        M[reg_row][reg_col] = vect[0][int(u)]
sparse_M = sparse.csr_matrix(M)
map_creator.ascii_creator(2233, "NN", sparse_M)

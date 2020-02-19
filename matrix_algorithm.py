import numpy as np
from numpy import linalg as la

def minimize_norm():
    W = np.load("graph_matrix.npy")

    norm = la.norm(W)
    print("####", norm)

    X = np.zeros(W.shape[0])
    X [5] = 1
    acc = X
    count = 0
    while norm > 0.0001:
        WX = np.dot(W, X)
        
        acc += WX
        X = WX
        norm = la.norm(X, ord = np.inf)
        count += 1
        print(norm)
    np.savetxt("acc.txt", acc)
    print(np.sum(X))

minimize_norm()
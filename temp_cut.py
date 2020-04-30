def cut_edges(G, edges_list):
    for u, v in G.edges():
        if [u,v] in edges_list:
            G.edges[u,v]["prop_weight"] = 0
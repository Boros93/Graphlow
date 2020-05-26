from Genetic_solution import Genetic_solution
from copy import copy

import numpy as np 

class Genetic_algorithm:
    def __init__(self, id_node: str, edges: dict, population_len = 5, rho = 6):
        
        # Preso dal csv
        self.id_vent = '2233'
        # Real vector
        self.real_vect = np.load("Data/real_vectors/" + self.id_vent + ".npy")

        self.id_node = id_node
        # Dizionario che mantiene la struttura degli archi key = (u, v) e value = trasmittance
        self.edges_dict = edges
        # Estraggo i valori degli edges
        self.edges = []
        for u, v, data in self.edges_dict(data=True):
            self.edges.append(data['trasmittance'])

        # Parametro per l'hypermutation: più è alto meno mutazioni si fanno
        self.rho = rho
        # Lunghezza della popolazione
        self.population_len = population_len
        # Genero n soluzioni uguali
        self.population = [Genetic_solution(self.id_node, self.edges, self.real_vect) for _ in range(population_len)]

        # Popolazione clonata
        self.population_cloned = []
        # Popolazione figli
        self.population_cross = []

        # Calcolo la fitness del patriarca
        self.population[0].compute_fitness(self.edges_dict)
        # Setto la fitness delle altre soluzioni e applico le mutazioni(in base alla fitness)
        for i in range(1, self.population_len):
            self.population[i].set_fitness(self.population[0].fitness)
            self.population[i].hypermutation(self.rho)
            self.population[i].compute_fitness(self.edges_dict)

    def __clone(self):
        self.population_cloned = []
        for i in range(self.population_len):
            tmp = copy(self.population[i])
            tmp.set_random_age()
            self.population_cloned.append(tmp)

    def __hypermutation(self):
        for i in range(len(self.population_cloned)):
            self.population_cloned[i].hypermutation(self.rho)
            self.population_cloned[i].compute_fitness(self.edges_dict)

    def __crossover(self):
        self.population_cross = []
        temp_population = self.population + self.population_cloned
        
        idx = np.random.permutation(len(temp_population))
        sol_len = len(self.population[0].edges)

        for i in range(0, len(idx), 2):
            # Scelgo il punto di taglio a random
            cut = np.random.randint(1, sol_len-2)
            # Inizializzo i figli
            child1_edges = np.concatenate((temp_population[idx[i]].edges[:cut], temp_population[idx[i+1]].edges[cut:]))
            child2_edges = np.concatenate((temp_population[idx[i+1]].edges[:cut], temp_population[idx[i]].edges[cut:]))

            # Creo le soluzioni figli
            child1_sol = Genetic_solution(self.id_node, child1_edges, self.real_vect)
            child1_sol.compute_fitness(self.edges_dict)
            self.population_cross.append(child1_sol)

            child2_sol = Genetic_solution(self.id_node, child2_edges, self.real_vect)
            child2_sol.compute_fitness(self.edges_dict)
            self.population_cross.append(child2_sol)

    def __increment_age(self):
        for i in range(len(self.population)):
            self.population[i].increment_age()

    def __selection(self):
        # Seleziono le population_len soluzioni migliori
        temp_population = self.population + self.population_cloned + self.population_cross
        # Ordinamento array
        temp_population.sort(key = lambda s : s.fitness, reverse=True)

        # Aggiorno la popolazione
        self.population = temp_population[:self.population_len]

        #self.population = [temp_population[0]]
        #max_age = temp_population[0].max_age
        #i = 1
        #while(len(self.population) < self.population_len):
        #    if temp_population[i].age < max_age:
        #        self.population.append(temp_population[i])
        #    i += 1
    
    def start(self, epochs):
        for e in range(epochs):
            print("Epoch:", e)
            # Incremento età delle soluzioni
            print("Aging...")
            #self.__increment_age()
            # Cloning (lista 2 volte population_len)
            print("Cloning...")
            self.__clone()
            # Hypermutation sulla popolazione clonata
            print("Hypermutation...")
            self.__hypermutation()
            # Crossover su entrambe le popolazioni
            print("Crossover...")
            self.__crossover()
            # Selezione nuova popolazione
            print("Selection...")
            self.__selection()
            # Stampa le best fitness
            print("Printing...")
            for p in self.population:
                print(p.fitness)

        G = self.population[0].propagation.export_graph('genetic_graph2233.gexf')
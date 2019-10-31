class Region: 

    def __init__(self, coord):
        self.coord = coord
        self.sim = []
    
    def add_sim(self, name_sim):
        self.sim.append(name_sim)

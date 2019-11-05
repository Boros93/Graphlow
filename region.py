class Region: 

    def __init__(self, coord):
        self.coord = coord
        self.sim = set()

    # Aggiunge una simulazione nel set
    def add_sim(self, name_sim):
        final_name = name_sim[20:-4]
        self.sim.add(final_name)

    # Aggiunge una lista di simulazioni al set
    def add_list_sim(self, list_sim):
        self.sim = set(list_sim)

    # Crea la riga da aggiungere al CSV
    def create_csv_row(self):
        row = []
        row.append(self.coord[0])
        row.append(self.coord[1])
        for s in self.sim:
            row.append(s)
        return row
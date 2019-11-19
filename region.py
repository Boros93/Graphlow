class Region: 

    def __init__(self, coord):
        self.coord = coord
        self.sim = set()
        self.marked = False

    # Aggiunge una simulazione nel set
    def add_sim(self, name_sim):
        final_name = name_sim[27:-4]
        first_part, second_part = final_name.split("_")
        final_name = first_part + second_part
        self.sim.add(final_name)

    # Aggiunge una lista di simulazioni al set
    def add_list_sim(self, list_sim):
        for s in list_sim:
            s = [int(s)]
            self.sim = self.sim.union(s)

    # Crea la riga da aggiungere al CSV
    def create_csv_row(self):
        row = []
        # Decommentare se si vogliono salvare anche le coordinate
        #row.append(self.coord[0])
        #row.append(self.coord[1])
        for s in self.sim:
            row.append(s)
        return row
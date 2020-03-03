import numpy as np

# • Devise genetic representation
# • Build a population
# • Design a fitness function
# • Choose selection method
# • Choose crossover & mutation
# • Choose data analysis method
class Population:
    def __init__(self, pop_size, eval_func, min_val=-2, max_val=2):
        self.pop_size = pop_size
        self.eval_func = eval_func
        self.min_val = min_val
        self.max_val= max_val
        
        self.__generate_population__()
        
    def select(self, percentile):
        cutoff = np.percentile([i["fitness"] for i in self.individuals], percentile)
        self.individuals = [i for i in self.individuals if i["fitness"] < cutoff]
        
    def crossover(self):
        """
            swap some genes around by mixing distribution parameters
        """
        for i, p in enumerate(self.individuals):
            if np.random.uniform(0, 1) > 0.90:
                i1 = self.individuals[np.random.randint(0, len(self.individuals))]
                i2 = self.individuals[np.random.randint(0, len(self.individuals))]
                if i % 2 == 0:
                    i1["a1"], i2["a1"] = i2["a1"], i1["a1"]
                    i1["a2"], i2["a2"] = i2["a2"], i1["a2"]
                else:
                    i1["b1"], i2["b1"] = i2["b1"], i1["b1"]
                    i1["b2"], i2["b2"] = i2["b2"], i1["b2"]
                    
    def mutate(self):
        """
            mutate some random genomes
        """
        for i, p in enumerate(self.individuals):
            if np.random.uniform(0, 1) > 0.90:
                param = np.random.choice(["a1", "b1", "a2", "b2"])
                diff = np.random.randn() * 0.01
                p[param] += diff
                
    def reproduce(self):
        new_pop = []
        counter = 0
        while len(new_pop) < self.pop_size:
            # chosen = np.random.randint(0, len(survivors))
            chosen = counter % len(self.individuals)
            counter += 1
            parent = self.individuals[chosen]
            ind = self.__generate_child__(parent["a1"], parent["b1"], parent["a2"], parent["b2"])
            new_pop.append(ind)
        
        self.individuals = new_pop
        
    def __generate_population__(self):
        """
            @param min_val: min_val bound for a1 and a2
            @param max_val: max_val bound for b1 and b2
            @param fit_func: fitness function
        """
        self.individuals = []
        for i in range(self.pop_size):
            a1 = np.random.uniform(self.min_val, self.max_val)
            b1 = np.random.uniform(self.min_val, self.max_val)
            a2 = np.random.uniform(self.min_val, self.max_val)
            b2 = np.random.uniform(self.min_val, self.max_val)
            ind = self.__generate_child__(a1, b1, a2, b2)
            self.individuals.append(ind)
            
    def __generate_child__(self, a1, b1, a2, b2):
        """
        @param a1: 1st bound on x1 phonotype
        @param b1: 2nd bound on x1 phonotype
        @param a2: 1st bound on x2 phonotype
        @param b2: 2nd bound on x2 phonotype
        x1: x1 value of position
        x2: x2 value of position
        """
        x1 = np.random.uniform(a1, b1)
        x2 = np.random.uniform(a2, b2)
        fitness = self.eval_func([x1, x2])
        ind = {
            "a1": a1,
            "b1": b1,
            "a2": a2,
            "b2": b2,
            "pos": [x1, x2],
            "fitness": fitness
        }
        return ind
import numpy as np
from copy import deepcopy

# • Devise genetic representation
# • Build a population
# • Design a fitness function
# • Choose selection method
# • Choose crossover & mutation
# • Choose data analysis method
class Population:
    def __init__(self, pop_size, eval_func, min_val=-2, max_val=2, crossover_rate=0.75, mutation_rate=0.1):
        self.pop_size = pop_size
        self.eval_func = eval_func
        self.min_val = min_val
        self.max_val= max_val
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.__generate_population__()
        
    def select(self, percentile):
        cutoff = np.percentile([i["fitness"] for i in self.individuals], percentile)
        if len([i for i in self.individuals if i["fitness"] < cutoff]) == 0:
            return # quickfix find a better selection method
        self.individuals = [i for i in self.individuals if i["fitness"] < cutoff]
        
    def regenerate(self):
        """
            Generates random genomes until the population is full
        """
        for _ in range(self.pop_size - len(self.individuals)):
            self.individuals.append(self.__generate_child__(self.min_val, self.max_val, self.min_val, self.max_val))
        
    def crossover(self):
        """
            swap some genes around by mixing distribution parameters
        """
        num_crossovers = (self.pop_size - len(self.individuals)) // 2
        for _ in range(num_crossovers):
            if np.random.rand() < self.crossover_rate:
                i1 = self.individuals[np.random.randint(0, len(self.individuals))]
                i2 = self.individuals[np.random.randint(0, len(self.individuals))]
                c1 = deepcopy(i1)
                c2 = deepcopy(i2)
                
                c1["pos"][0], c2["pos"][0] = c2["pos"][0], c1["pos"][0]
                c1["pos"][1], c2["pos"][1] = c2["pos"][1], c1["pos"][1]
                    
                c1["fitness"] = self.eval_func(c1["pos"])
                c2["fitness"] = self.eval_func(c2["pos"])
                self.individuals.append(c1)
                self.individuals.append(c2)
                    
    def mutate(self):
        """
            mutate some random genomes
        """
        for i, p in enumerate(self.individuals):
            if np.random.uniform(0, 1) < self.mutation_rate:
                param = np.random.choice([0, 1])
                diff = np.random.randn() * 0.1
                p["pos"][param] += diff
                p["fitness"] = self.eval_func(p["pos"])
        
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
            "pos": [x1, x2],
            "fitness": fitness
        }
        return ind
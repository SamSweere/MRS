import numpy as np
from copy import deepcopy

# • Devise genetic representation
# • Build a population
# • Design a fitness function
# • Choose selection method
# • Choose crossover & mutation
# • Choose data analysis method
class Population:
    def __init__(self, pop_size, genome_size, eval_func, min_val=-2, max_val=2, crossover_rate=0.75, mutation_rate=0.1):
        self.pop_size = pop_size
        self.genome_size = genome_size
        self.eval_func = eval_func
        self.min_val = min_val
        self.max_val= max_val
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        self.__generate_population__()
        
    def select(self, percentage):
        sorted_individuals = sorted(self.individuals, key=lambda x: x["fitness"])
        total_rank_sum = (len(self.individuals) * (len(self.individuals) + 1)) / 2
        propabilities = [(i+1)/total_rank_sum for i, p in enumerate(sorted_individuals)]
        
        num = int(len(sorted_individuals) * percentage)
        self.individuals = np.random.choice(sorted_individuals, num, p=propabilities).tolist()
        
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
                p1 = self.individuals[np.random.randint(0, len(self.individuals))]
                p2 = self.individuals[np.random.randint(0, len(self.individuals))]
                
                crossover_point = np.random.randint(1, self.genome_size)
                c1_genome = [*p1["pos"][:crossover_point],*p2["pos"][crossover_point:]]
                c2_genome = [*p2["pos"][:crossover_point],*p1["pos"][crossover_point:]]
                c1 = {
                    "pos": c1_genome,
                    "fitness": self.eval_func(c1_genome)
                }
                c2 = {
                    "pos": c2_genome,
                    "fitness": self.eval_func(c2_genome)
                }
                
                self.individuals.append(c1)
                self.individuals.append(c2)
                    
    def mutate(self):
        """
            mutate some random genomes
        """
        for i, p in enumerate(self.individuals):
            if np.random.uniform(0, 1) < self.mutation_rate:
                param = np.random.choice([0, 1])
                diff = np.random.randn() * 0.15
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
            ind = self.__generate_child__()
            self.individuals.append(ind)
            
    def __generate_child__(self):
        x = np.random.uniform(low=self.min_val, high=self.max_val, size=self.genome_size)
        fitness = self.eval_func(x)
        ind = {
            "pos": x,
            "fitness": fitness
        }
        return ind
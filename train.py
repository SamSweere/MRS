from genetic.ANN import ANN
from genetic.population import Population
from world_creator import WorldCreator

import numpy as np

class ANNCoverageEvaluator:
    def __init__(self, input_dims, output_dims, hidden_dims):
        self.input_dims = input_dims
        self.output_dims = output_dims
        self.hidden_dims = hidden_dims
        
    def evaluate(self, genome):
        ann = self.__to_ann__(genome)
        
        inp = np.ones(self.input_dims).reshape(-1, 1)
        return ann.predict(inp)[-1][0][0]
        
    def get_genome_size(self):
        genome_size = 0
        
        prev_dim = self.input_dims
        for hidden_dim in self.hidden_dims:
            genome_size += hidden_dim * (prev_dim + 1)
            prev_dim = hidden_dim
        
        genome_size += self.output_dims * (prev_dim+1)
        return genome_size
        
    def __to_ann__(self, genome):
        prev_dim = self.input_dims
        prev_index = 0
        
        weight_matrices = []
        for hidden_dim in self.hidden_dims:
            num_units = hidden_dim * (prev_dim + 1)
            
            # Generate the matrix based on the weights in the genome
            matrix = genome[prev_index:prev_index+num_units]
            matrix = matrix.reshape((hidden_dim, prev_dim+1))
            weight_matrices.append(matrix)
            
            prev_dim = hidden_dim
            prev_index = prev_index + num_units
            
        # Generate the matrix for the output
        matrix = genome[prev_index:]
        matrix = matrix.reshape((self.output_dims, prev_dim+1))
        weight_matrices.append(matrix)
        
        # Generate the ANN
        ann = ANN(self.input_dims,self.output_dims, self.hidden_dims)
        ann.weight_matrices = weight_matrices
        return ann
    
if __name__ == "__main__":
    WIDTH = 1000
    HEIGHT = 650
    POP_SIZE = 100
    
    robot_args = {
        "n_sensors": 12,
        "max_sensor_length": 100
    }
    
    generator = WorldCreator(WIDTH, HEIGHT, **robot_args)
    evaluator = ANNCoverageEvaluator(4, 3, [3,2])
    population = Population(POP_SIZE, evaluator.get_genome_size(), evaluator.evaluate, min_val=-1, max_val=1)
    
    for i in range(100):
        population.select(0.90)
        population.crossover()
        population.mutate()
        
        fittest_genome = max(population.individuals, key=lambda x: x["fitness"])
        print(f"{i}: {evaluator.evaluate(fittest_genome['pos'])}")
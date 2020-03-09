from genetic.ANN import ANN
from genetic.population import Population
from world_generator import WorldGenerator
from gui.ann_controller import apply_action, exponential_decay
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class ANNCoverageEvaluator:
    def __init__(self, generator, input_dims, output_dims, hidden_dims,
        eval_seconds=20, step_size_ms=270):
        self.generator = generator
        self.input_dims = input_dims
        self.output_dims = output_dims
        self.hidden_dims = hidden_dims
        self.eval_seconds = eval_seconds
        # According to the internetz humans have a reaction time of 200ms to 300ms
        self.step_size_ms = step_size_ms
        
    def evaluate(self, genome):
        """
            Evaluate fitness of current genome (ANN weights)
        """
        ann = self.to_ann(genome)
        world, robot = self.generator.create_rect_world(random_robot=False)
        # TODO: is this legit?
        # Dirty Hack - Do an update to let the robot collect sensor data
        world.update(0)
        
        # We round up so that we'd rather overestimate evaluation time
        steps = int((self.eval_seconds * 1000) / self.step_size_ms) + 1
        delta_time = self.step_size_ms / 1000
        distance_sums = []
        for _ in range(steps):
            apply_action(robot, ann)
            world.update(delta_time)
            
            sensors = exponential_decay([dist for hit, dist in robot.sensor_data])
            distance_sums.append(np.sum(sensors))
            
        return world.dustgrid.cleaned_cells - np.sum(distance_sums) * 10
        
    def get_genome_size(self):
        genome_size = 0
        
        prev_dim = self.input_dims
        for hidden_dim in self.hidden_dims:
            genome_size += hidden_dim * (prev_dim + 1)
            prev_dim = hidden_dim
        
        genome_size += self.output_dims * (prev_dim+1)
        return genome_size
        
    def to_ann(self, genome):
        """
            Initialize ANN with genome weights
            @param genome: flattened ANN weights
        """
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

def train(iterations, generator, evaluator, population):
    max_fitness = []
    avg_fitness = []
    diversity = []
    for i in range(iterations):
        population.select(0.90)
        population.crossover()
        population.mutate()
        
        # Collect some data
        fittest_genome = population.get_fittest_genome()
        max_fitness.append(population.get_max_fitness())
        avg_fitness.append(population.get_average_fitness())
        diversity.append(population.get_average_diversity())
        # Early Stopping
        if diversity[-1] < 0.08:
            # Save the best genome
            ann = evaluator.to_ann(fittest_genome['pos'])
            ann.save(f'./checkpoints/model_{i}.p')
            
            print("Early stopping due to low diversity")
            break
        
        # Print iteration data
        print(f"{i} - fitness:\t {evaluator.evaluate(fittest_genome['pos'])}")
        print("diversity:\t", population.get_average_diversity())
        if (i % 20 == 0) or (i == iterations - 1):
            # Save the best genome
            ann = evaluator.to_ann(fittest_genome['pos'])
            ann.save(f'./checkpoints/model_{i}.p')

    history = pd.DataFrame({
        "max_fitness": max_fitness,
        "avg_fitness": avg_fitness,
        "diversity": diversity,
        "iteration": [i for i in range(len(max_fitness))]
    })
    return ann, history


def show_history(history):
    long_df = history.melt(
        value_vars=["max_fitness", "avg_fitness", "diversity"],
        id_vars=["iteration"]
    )
    g = sns.FacetGrid(long_df, row="variable", sharey=False)
    g.map(plt.plot, "iteration", "value").add_legend()
    plt.show()

    
if __name__ == "__main__":
    # Create folder for saving models
    from pathlib import Path
    Path("./checkpoints").mkdir(parents=True, exist_ok=True)

    # TODO: main thing missing seems to be feedback about own motion!
    # TODO: make sure we evaluate our ANN for a sensible amount of time!
    
    # Initialization
    WIDTH = 500
    HEIGHT = 325
    POP_SIZE = 100
    
    robot_args = {
        "n_sensors": 6,
        "max_sensor_length": 100
    }
    
    generator = WorldGenerator(WIDTH, HEIGHT, 20, robot_args)
    evaluator = ANNCoverageEvaluator(generator, robot_args["n_sensors"], 2, [16, 8])
    population = Population(
        POP_SIZE,
        evaluator.get_genome_size(),
        evaluator.evaluate,
        init_func=np.random.uniform,
        mutation_rate=0.1,
        mutation_scale=0.1
    )
    
    # Train
    iterations = 1000
    ann, history = train(iterations, generator, evaluator, population)
    show_history(history)

    ann.show()

    # # let's look into our ANN
    # a = evaluator.to_ann(population.individuals[0]["pos"])
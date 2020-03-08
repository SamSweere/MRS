from genetic.ANN import ANN
from genetic.population import Population
from world_generator import WorldGenerator
from gui.ann_controller import apply_action, exponential_decay
import matplotlib.pyplot as plt
import numpy as np


class ANNCoverageEvaluator:
    def __init__(self, generator, input_dims, output_dims, hidden_dims, eval_seconds=20, step_size_ms=270):
        self.generator = generator
        self.input_dims = input_dims
        self.output_dims = output_dims
        self.hidden_dims = hidden_dims
        self.eval_seconds = eval_seconds
        # According to the internetz humans have a reaction time of somewhat 200ms to 300ms
        self.step_size_ms = step_size_ms
        
    def evaluate(self, genome):
        """
            Let the ANN perform an action and collect sensor data
        """
        ann = self.to_ann(genome)
        world, robot = self.generator.create_random_world()
        # TODO: is this legit?
        # Dirty Hack - Do an update to let the robot collect sensor data
        world.update(0)
        
        # We round up so that we'd rather overestimate evaluation time
        steps = int((self.eval_seconds * 1000) / self.step_size_ms) + 1
        delta_time = self.step_size_ms / 1000
        distance_sums = []
        for i in range(steps):
            apply_action(robot, ann)
            world.update(delta_time)
            
            sensors = exponential_decay([dist for hit, dist in robot.sensor_data])
            distance_sums.append(np.sum(sensors))
        
        return -np.sum(distance_sums) * 100
        
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
        print(f"{i}: {evaluator.evaluate(fittest_genome['pos'])}")
        print(population.get_average_diversity())
        if i % 20 == 0 or i == iterations - 1:
            # Save the best genome
            ann = evaluator.to_ann(fittest_genome['pos'])
            ann.save(f'./checkpoints/model_{i}.p')
    history = {
        "max_fitness": max_fitness,
        "avg_fitness": avg_fitness,
        "diversity": diversity
    }
    return ann, history


def show_history(history):
    # Fitness plot
    plt.figure()
    plt.title("Fitness")
    plt.xlabel("Epoch")
    plt.ylabel("Fitness")
    plt.plot(history["max_fitness"], label="Maximum")
    plt.plot(history["avg_fitness"], label="Average")
    plt.legend()
    plt.show()
    
    # Diversity plot
    plt.figure()
    plt.title("Diversity")
    plt.xlabel("Epoch")
    plt.ylabel("Diversity")
    plt.plot(history["diversity"])
    
if __name__ == "__main__":
    # Create folder for saving models
    from pathlib import Path
    Path("./checkpoints").mkdir(parents=True, exist_ok=True)
    
    # Initialization
    WIDTH = 1000
    HEIGHT = 650
    POP_SIZE = 100
    
    robot_args = {
        "n_sensors": 12,
        "max_sensor_length": 100
    }
    
    generator = WorldGenerator(WIDTH, HEIGHT, **robot_args)
    evaluator = ANNCoverageEvaluator(generator, robot_args["n_sensors"], 2, [32,16])
    population = Population(POP_SIZE, evaluator.get_genome_size(), evaluator.evaluate, init_func=np.random.normal)
    
    # Train
    iterations = 100

    ann, history = train(iterations, generator, evaluator, population)
    show_history(history)


            
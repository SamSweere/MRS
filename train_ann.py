from genetic.ANN import ANN
from genetic.population import Population
from simulation.world_generator import WorldGenerator
from gui.ann_controller import apply_action, exponential_decay
import _experiments.visualize as visualize
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from datetime import datetime
import subprocess
from pathlib import Path
# import multiprocessing as mp
# from itertools import repeat


class ANNCoverageEvaluator:
    def __init__(self, generator, input_dims, output_dims, hidden_dims,
                 feedback, eval_seconds, step_size_ms, feedback_time):
        self.generator = generator
        self.input_dims = input_dims
        self.output_dims = output_dims
        self.hidden_dims = hidden_dims
        self.eval_seconds = eval_seconds
        # According to the internetz humans have a reaction time of 200ms to 300ms, why does this matter?
        self.step_size_ms = step_size_ms
        self.feedback = feedback
        self.feedback_time = feedback_time

    def generate_evaluate(self, genome, random_robot):
        world, robot = self.generator.create_rect_world(random_robot=random_robot)
        return self.evaluate_in_world(world, robot, genome)

    def evaluate(self, genome):
        scores = []

        for step in range(10):
            scores.append(self.generate_evaluate(genome, True))

        return np.mean(scores)

        # Interesting result, not pooling is faster
        # setup multitreath poolling
        # threads = mp.cpu_count()
        # self.pool = mp.Pool(threads)
        #
        # scores = [self.pool.apply(self.generate_evaluate, args=(genome, True)) for step in range(10)]
        # print(scores)
        # pool.close()


    def evaluate_in_world(self, world, robot, genome):
        """
            Evaluate fitness of current genome (ANN weights)
        """
        ann = self.to_ann(genome)
        # Dirty Hack - Do an update to let the robot collect sensor data
        world.update(0)

        # We round up so that we'd rather overestimate evaluation time
        steps = int((self.eval_seconds * 1000) / self.step_size_ms) + 1
        delta_time = self.step_size_ms / 1000
        distance_sums = []
        for _ in range(steps):
            apply_action(robot, ann, self.feedback)
            world.update(delta_time)

            sensors = exponential_decay([dist for hit, dist in robot.sensor_data])
            distance_sums.append(np.sum(sensors))

        return world.dustgrid.cleaned_cells - np.sum(distance_sums)*20 #100

    def get_genome_size(self):
        genome_size = 0

        prev_dim = self.input_dims
        for i, hidden_dim in enumerate(self.hidden_dims):
            # for the last layer, add the weights for feedback
            if self.feedback:
                if i == len(self.hidden_dims) - 1:
                    genome_size += hidden_dim * hidden_dim
            genome_size += hidden_dim * (prev_dim + 1)
            prev_dim = hidden_dim

        genome_size += self.output_dims * (prev_dim + 1)
        return genome_size

    def to_ann(self, genome):
        """
            Initialize ANN manually with genome weights
            @param genome: flattened ANN weights
        """
        prev_dim = self.input_dims
        prev_index = 0

        weight_matrices = []
        for i, hidden_dim in enumerate(self.hidden_dims):

            # Generate weight matrix based on genome
            if i == (len(self.hidden_dims) - 1):  # feedback layer
                num_units = hidden_dim * (hidden_dim + prev_dim + 1)
                matrix = genome[prev_index:(prev_index + num_units)]
                matrix = matrix.reshape((hidden_dim, hidden_dim + prev_dim + 1))
                # TODO: we need to put feedback in genome!
            else:  # any other layer
                num_units = hidden_dim * (prev_dim + 1)
                # Generate the matrix based on the weights in the genome
                matrix = genome[prev_index:prev_index + num_units]
                matrix = matrix.reshape((hidden_dim, prev_dim + 1))

            weight_matrices.append(matrix)
            prev_dim = hidden_dim
            prev_index = prev_index + num_units

        # Generate the matrix for the output
        matrix = genome[prev_index:]
        matrix = matrix.reshape((self.output_dims, prev_dim + 1))
        weight_matrices.append(matrix)

        # Generate the ANN
        ann = ANN(self.input_dims, self.output_dims, self.hidden_dims, self.step_size_ms,
                  self.feedback_time)
        ann.weight_matrices = weight_matrices
        return ann


def train(iterations, generator, evaluator, population, save_modulo=20, experiment=""):
    max_fitness = []
    avg_fitness = []
    diversity = []
    if experiment == "":
        experiment = f"{datetime.now():%Y-%m-%d_%H-%S-%f}"
    experiment = os.path.join("_experiments", experiment) 
    if not os.path.isdir(experiment):
        os.mkdir(experiment)
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
        if diversity[-1] < 0.02: #0.08
            # Save the best genome
            ann = evaluator.to_ann(fittest_genome['pos'])
            ann.save(f'./_checkpoints/model_{i}.p')

            print("Early stopping due to low diversity")
            break

        # Print iteration data
        print(f"{i} - fitness:\t {evaluator.evaluate(fittest_genome['pos'])}")
        print("diversity:\t", population.get_average_diversity())
        if (i % save_modulo == 0) or (i == iterations - 1):
            # Save the best genome
            ann = evaluator.to_ann(fittest_genome['pos'])
            model_name = f"model_{i}"
            ann.save(os.path.join("_checkpoints", f"{model_name}.p"))
            # Take a snapshot of what robot outcomes look like
            subprocess.call(["python", "main.py", "--snapshot",
                "--snapshot_dir", f"{experiment}/{model_name}.png",
                "--model_name", f"{model_name}.p"])

    history = pd.DataFrame({
        "max_fitness": max_fitness,
        "avg_fitness": avg_fitness,
        "diversity": diversity,
        "iteration": [i for i in range(len(max_fitness))]
    })
    save_history(history, experiment)
    return ann, history


def save_history(history, experiment):
    timestamp = f"{datetime.now():%Y-%m-%d_%H-%S-%f}"
    file_name = os.path.join(experiment, f"{timestamp}.csv")
    history.to_csv(file_name)


if __name__ == "__main__":
    # Create folder for saving models
    Path("_checkpoints").mkdir(parents=True, exist_ok=True)

    # TODO: main thing missing seems to be feedback about own motion!
    # TODO: make sure we evaluate our ANN for a sensible amount of time!

    # Initialization
    WIDTH = 500
    HEIGHT = 325
    POP_SIZE = 100
    FEEDBACK = True

    robot_args = {
        "n_sensors": 12,
        "max_sensor_length": 100
    }

    generator = WorldGenerator(WIDTH, HEIGHT, 20, robot_args)
    evaluator = ANNCoverageEvaluator(
        generator,
        robot_args["n_sensors"],
        output_dims=2,
        hidden_dims= [16, 4],
        feedback=FEEDBACK,
        eval_seconds=20,
        step_size_ms=100, #270
        feedback_time=100 #540
    )
    population = Population(
        POP_SIZE,
        evaluator.get_genome_size(),
        evaluator.evaluate,
        init_func=np.random.normal,
        mutation_rate=0.1,
        mutation_scale=0.1
    )

    # Train
    iterations = 100
    ann, history = train(iterations, generator, evaluator, population)
    visualize.show_history(history)

    ann.show()

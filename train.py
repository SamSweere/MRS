from genetic.ANN import ANN
from genetic.population import Population
from world_creator import WorldCreator
from gui.ann_controller import apply_action

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
        ann = self.to_ann(genome)
        world, robot = self.generator.create_random_world()
        # Dirty Hack - Do an update to let the robot collect sensor data
        world.update(0)
        
        # We round up so that we are above the evaluation time, instead of below
        steps = int((self.eval_seconds * 1000) / self.step_size_ms) + 1
        delta_time = self.step_size_ms / 1000
        for i in range(steps):
            apply_action(robot, ann)
            world.update(delta_time)
        
        return world.dustgrid.cleaned_cells
        
    def get_genome_size(self):
        genome_size = 0
        
        prev_dim = self.input_dims
        for hidden_dim in self.hidden_dims:
            genome_size += hidden_dim * (prev_dim + 1)
            prev_dim = hidden_dim
        
        genome_size += self.output_dims * (prev_dim+1)
        return genome_size
        
    def to_ann(self, genome):
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
    
    generator = WorldCreator(WIDTH, HEIGHT, **robot_args)
    evaluator = ANNCoverageEvaluator(generator, robot_args["n_sensors"], 2, [32,16])
    population = Population(POP_SIZE, evaluator.get_genome_size(), evaluator.evaluate, min_val=-1, max_val=1)
    
    # Train
    train_steps = 100
    for i in range(train_steps):
        population.select(0.90)
        population.crossover()
        population.mutate()
        
        fittest_genome = population.get_fittest_genome()
        print(f"{i}: {evaluator.evaluate(fittest_genome['pos'])}")
        
        if i % 20 == 0 or i == train_steps - 1:
            # Save the best genome
            ann = evaluator.to_ann(fittest_genome['pos'])
            ann.save(f'./checkpoints/model_{i}.p')
    
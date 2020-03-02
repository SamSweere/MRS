import numpy as np
from functions import rastrigin, rosenbrock
from copy import deepcopy
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import PSO.plots as plots
import os

# • Devise genetic representation
# • Build a population
# • Design a fitness function
# • Choose selection method
# • Choose crossover & mutation
# • Choose data analysis method


def generate_pop(pop_size, min_val, max_val, fit_func):
    """
    @param min_val: min_val bound for a1 and a2
    @param max_val: max_val bound for b1 and b2
    @param fit_func: fitness function
    """
    individuals = []
    for i in range(pop_size):
        a1 = np.random.uniform(min_val, max_val)
        b1 = np.random.uniform(min_val, max_val)
        a2 = np.random.uniform(min_val, max_val)
        b2 = np.random.uniform(min_val, max_val)
        ind = generate_child(a1, b1, a2, b2, fit_func)
        individuals.append(ind)
    return individuals


def generate_child(a1, b1, a2, b2, fit_func):
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
    fitness = fit_func([x1, x2])
    ind = {
        "a1": a1,
        "b1": b1,
        "a2": a2,
        "b2": b2,
        "pos": [x1, x2],
        "fitness": fitness
    }
    return ind


def select(pop, percentile):
    cutoff = np.percentile([i["fitness"] for i in pop], percentile)
    return [i for i in pop if i["fitness"] < cutoff]


def reproduce(survivors, pop_size, fit_func):
    new_pop = []
    counter = 0
    while len(new_pop) < pop_size:
        # chosen = np.random.randint(0, len(survivors))
        chosen = counter % len(survivors)
        counter += 1
        parent = survivors[chosen]
        ind = generate_child(parent["a1"], parent["b1"], parent["a2"],
            parent["b2"], fit_func)
        new_pop.append(ind)
    return new_pop


def crossover(pop):
    """
    swap some genes around by mixing distribution parameters
    """
    for i, p in enumerate(pop):
        if np.random.uniform(0, 1) > 0.90:
            idx1 = np.random.randint(0, len(pop))
            idx2 = np.random.randint(0, len(pop))
            if i % 2 == 0:
                pop[idx1]["a1"], pop[idx2]["a1"] = pop[idx2]["a1"], pop[idx1]["a1"]
                pop[idx1]["a2"], pop[idx2]["a2"] = pop[idx2]["a2"], pop[idx1]["a2"]
            else:
                pop[idx1]["b1"], pop[idx2]["b1"] = pop[idx2]["b1"], pop[idx1]["b1"]
                pop[idx1]["b2"], pop[idx2]["b2"] = pop[idx2]["b2"], pop[idx1]["b2"]
    return pop


def mutate(pop):
    """
    mutate a gene at a time
    """
    for i, p in enumerate(pop):
        if np.random.uniform(0, 1) > 0.90:
            param = np.random.choice(["a1", "b1", "a2", "b2"])
            diff = np.random.randn() * 0.01
            p[param] += diff
            # print(f"MUTATION: {param} {diff}")
    return pop


def check(pop):
    """
    remove individuals with invalid genes
    """
    # TODO: maybe just swap?
    new_pop = []
    for p in pop:
        if (p["a1"] < p["b1"]) and (p["a2"] < p["b2"]):
            new_pop.append(p)
    return new_pop


def show(pop):
    for j, i in enumerate(pop):
        if j % 10 == 0:
            a1 = i["a1"]
            b1 = i["b1"]
            a2 = i["a2"]
            b2 = i["b2"]
            x1 = i["pos"][0]
            x2 = i["pos"][1]
            fitness = i["fitness"]
            print(f"{a1:.1f} {b1:.2f} {a2:.1f} {b2:.2f}\t{x1:.2f} {x2:.2f}\tfit {fitness:.2f}")
    avg_fitness = np.mean([i["fitness"] for i in pop])
    print(f"average fitness: {avg_fitness}\n")


def evolve(n, pop, pop_size, min_val, max_val):
    """train function"""
    history = []
    for i in range(n):
        survivors = select(pop, 75)
        pop = crossover(pop)
        pop = mutate(pop)
        # pop = check(pop)
        pop = reproduce(survivors, pop_size, rosenbrock)
        history.append(deepcopy(pop))
        if i % 100 == 0:
            show(pop)
    return pop, history


def process_history(history):
    """create a df from history for plotting"""
    fitness = []
    diversity = []
    for pop in history:
        fitness.append(np.mean([i["fitness"] for i in pop]))
        x1_diversity = np.var([i["pos"][0] for i in pop])
        x2_diversity = np.var([i["pos"][1] for i in pop])
        div = np.linalg.norm([x1_diversity, x2_diversity])
        diversity.append(div)

    df = pd.DataFrame({
        "fitness": fitness,
        "diversity": diversity
    })
    df["Generation"] = df.index
    df = pd.melt(df, id_vars=['Generation'],
        value_vars=["fitness", "diversity"])
    return df


if __name__ == "__main__":
    pop_size = 100
    min_val = -2
    max_val = 2
    functions = [rosenbrock, rastrigin]
    function_num = 1 # 0: rosenbrock, 1: rastrigin
    fn = functions[function_num]


    pop = generate_pop(pop_size, min_val, max_val, fn)
    new_pop, history = evolve(1000, pop, pop_size, min_val,
        max_val)

    df = process_history(history)
    g = sns.FacetGrid(data=df, row="variable", height=3, sharey="row")
    g = g.map(plt.plot, "Generation", "value")
    # sns.lineplot(data=df, x="Generation", y="value", hue="variable")
    plt.show()


    extent = [-2, 2, -2, 2]
    file_name = "ae"
    img_dir = ""
    if(function_num == 0):
        file_name = "ae_rosenbrock"
    elif(function_num == 1):
        file_name = "ae_rastrigin"
    plots.visualize_heatmap(fn, history, extent, trail_lenght=5,
        fname=os.path.join(img_dir, file_name+".gif"), output="step")


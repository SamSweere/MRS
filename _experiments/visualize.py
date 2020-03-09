import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def show_history(history):
    long_df = history.melt(
        value_vars=["max_fitness", "avg_fitness", "diversity"],
        id_vars=["iteration"]
    )
    g = sns.FacetGrid(long_df, row="variable", sharey=False)
    g.map(plt.plot, "iteration", "value").add_legend()
    plt.show()

if __name__ == "__main__":
    # TODO: load a file from history
    pass
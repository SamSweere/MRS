import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def show_history(history, path=""):
    long_df = history.melt(
        value_vars=["Max_Fitness", "Avg_Fitness", "Diversity"],
        id_vars=["Iteration"], var_name="variable", value_name="value"
    )
    g = sns.FacetGrid(long_df, row="variable", sharey=False, height=2, aspect=3)
    g.map(plt.plot, "Iteration", "value").add_legend()
    if path != "":
        g.savefig(path)
    return g


if __name__ == "__main__":
    # TODO: load a file from history
    experiment = os.path.join("_experiments", "2020-03-09_22-27-846488")
    file_name = os.path.join(experiment, "2020-03-09_22-27-515527.csv")
    history = pd.read_csv(file_name)
    g = show_history(history)
    g.savefig(
        os.path.join(experiment, "ev_algo.png")
    )
    plt.show()
    pass
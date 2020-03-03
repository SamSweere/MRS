
import numpy as np
from copy import deepcopy
import plots
import utils
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
import imageio
from scipy import optimize
from importlib import reload
reload(plots)
reload(utils)


def gradient_descent(fn, fn_grad, pos, fname="particles.png"):
    """perform a couple rounds of grad desc with some adaptive learning rates"""
    scale = 5
    extent = [-scale, scale, -scale, scale]
    pos_history = [deepcopy(pos)]
    for i in range(100000):
        # grad = GRAD_FUNC(fn, pos, 1, 1)
        grad = fn_grad(pos)
        pos -= 1e-7 * i * grad
        pos_history.append(deepcopy(pos))
    fig = plt.figure()
    X = np.arange(extent[0], extent[1], 0.1)
    Y = np.arange(extent[2], extent[3], 0.1)
    X_grid, Y_grid = np.meshgrid(X, Y)
    Z = fn([X_grid, Y_grid])
    plt.imshow(Z, extent=extent, cmap='hot')
    pos_x = [i[0] for i in pos_history]
    pos_y = [i[1] for i in pos_history]
    sns.scatterplot(pos_x, pos_y)
    plt.savefig(fname)
    plt.show()


def visualize_grad_desc():
    initial_pos = np.array([3.8, 3.8])

    fn = utils.rastrigin
    fn_grad = utils.rastrigin_grad
    gradient_descent(fn, fn_grad, initial_pos, "gifs_to_keep/grad_desc_rastrigin")

    fn = utils.rosenbrock
    fn_grad = utils.rosenbrock_grad
    gradient_descent(fn, fn_grad, initial_pos, "gifs_to_keep/grad_desc_rosenbrock")


if __name__ == "__main__":
    visualize_grad_desc()

    
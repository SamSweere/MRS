from scipy.optimize import minimize
import utils

def bla(x, y):
    return x**2

def rosenbrock(params, a=1, b=100):
    x1, x2 = params
    return (a - x1) ** 2 + b * (x2 - x1 ** 2) ** 2

utils.rastrigin(0, 0)

a = minimize(rosenbrock, [10, 10])


import matplotlib.pyplot as plt

x = [1,2,3,4,5,6]
y = [3,4,5,6,7,8]

plt.plot(x[1:], y[1:], 'ro')
plt.plot(x[0], y[0], 'g*')

fig= plt.figure()
ax = plt.axes()
bla, = ax.plot(x[0], y[0], 'g*')

bla.set_data(1, 3)
plt.show()
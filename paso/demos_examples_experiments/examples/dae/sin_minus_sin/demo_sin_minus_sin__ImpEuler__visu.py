import numpy as np

from paso.demos_examples_experiments.examples.dae.sin_minus_sin.demo_sin_minus_sin__ImpEuler__integ import sol

import matplotlib.pyplot as plt


print('load solution')
Ts = np.load('results_dump/Ts_ImpEuler_sin_minus_sin.npy')
Xs = np.load('results_dump/Xs_ImpEuler_sin_minus_sin.npy')
print('load completed')


plt.figure()

plt.plot(Ts, Xs)
plt.plot(Ts, Xs, 'ro')

plt.title('numerical integration')


plt.figure()

plt.plot(Ts, [sol(ti) for ti in Ts])

plt.title('exact solution')


plt.figure()

plt.plot(Ts, [Xs[i] - sol(ti) for i, ti in enumerate(Ts)])

plt.title('difference')


plt.show()

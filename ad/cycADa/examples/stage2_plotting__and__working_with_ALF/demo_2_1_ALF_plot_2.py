from ad.cycADa import *
import numpy as np
from scipy.sparse import csr_matrix


def func(v, more = False):
    x,y = v[0], v[1]

    product = x*y
    product_equivalent = exp(log(x) + log(y))

    out = product - product_equivalent

    if more:
        return out, product, product_equivalent
    return out # bar - foo # x*y - exp(log(x) + log(y))


'''
    overload
    --------
'''
t = tape(1)

x_ad = adFloat(t)
y_ad = adFloat(t)

v_ad = np.array([x_ad, y_ad])

f_ad, bar_ad, foo_ad = func(v_ad, more = True)

f_ad.dependent = True

'''
    differentiate
    -------------
'''
v_mid = np.array([3.0, 3.0])
v_rad = np.array([0.3, -0.2])

t.allocJac(False)
t.D(v_mid, v_rad)

'''
    gather derivative results
    -------------------------
'''
ALF = csr_matrix((t.data, abs(t.indices), t.indptr), shape = (t.s + t.m, t.n + t.s))
cb = np.zeros(shape = (t.s + t.m,))
z_check = np.zeros(shape = (t.s,))
z_hat = np.zeros(shape = (t.s,))

for idx, z in enumerate(t.swVars):
    cb[idx] = z.mid
    z_check[idx] = z.mid - z.rad
    z_hat[idx] = z.mid + z.rad
cb[-1] = f_ad.mid # because m == 1 for this example
print(cb)
# raise Exception

def evaluate_ALF(n, s, m, cb, ALF, v):
    z = np.zeros(shape = (s,))
    for i in range(s):
        z[i] = cb[i] + ALF[i, :n].dot(v - v_mid) + ALF[i, n:].dot(abs(z) - (abs(z_check) + abs(z_hat))/2.0)

    return cb[s:] + ALF[s:, :n].dot(v - v_mid) + ALF[s:, n:].dot(abs(z) - (abs(z_check) + abs(z_hat))/2.0)

print(ALF.toarray())

'''
    plotting
    --------
'''
from mpl_toolkits.mplot3d import Axes3D

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np


print('This script demonstrates on one hand the plotting of an ALF but also')
print('that secant expansions are unique to an evaluation procedure (aka algorithm) BUT NOT necessarily')
print('to a function (in a math sense).\t') 
print('Example: product of two non-negative floating point numbers (i.e. x, y > 0):')
print("\t\tg1(x, y) := x*y  '=='  exp(log(x) + log(y)) =: g2(x, y)")
print("\t\tf(x, y)  := g1(x, y) - g2(x, y)  '=='  0")

fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1, projection = '3d')
ax2 = fig.add_subplot(1, 2, 2, projection = '3d')

for axi, title in zip([ax1, ax2], ['$F(x_0, x_1)$', '$PL_F(x_0, x_1)$']):
    axi.set_xlim(0.9, 4.1)
    axi.set_ylim(0.9, 4.1)
    axi.set_xlabel('$x_0$')
    axi.set_ylabel('$x_1$')
    axi.set_zlabel(title)
    axi.view_init(45, 220)

X = np.arange(1.0, 4.0, 0.05)
Y = np.arange(1.0, 4.0, 0.05)

len_x = len(X)
len_y = len(Y)

X, Y = np.meshgrid(X, Y)

Z = np.zeros(shape = X.shape)
Z2 = np.zeros(shape = X.shape)

for i in range(len_x):
    for j in range(len_y):
        Z[i, j] = func([X[i, j], Y[i, j]])
        Z2[i, j] = evaluate_ALF(t.n, t.s, t.m, cb, ALF, np.array([X[i, j], Y[i, j]]))

surf = ax1.plot_surface(X, Y, Z, cmap = cm.viridis, linewidth = 10.0, antialiased = True)
surf2 = ax2.plot_surface(X, Y, Z2, cmap = cm.viridis, linewidth = 10.0, antialiased = True)

for axi in [ax1, ax2]:
    axi.plot([(v_mid + v_rad)[0]], [(v_mid + v_rad)[1]], [0.0], 'o', c='grey')
    axi.plot([(v_mid - v_rad)[0]], [(v_mid - v_rad)[1]], [0.0], 'o', c='grey')
    axi.plot([(v_mid + v_rad)[0], (v_mid + v_rad)[0]],
            [(v_mid + v_rad)[1], (v_mid + v_rad)[1]],
            [0.0, func(v_mid + v_rad)], c='grey', linestyle='--')
    axi.plot([(v_mid - v_rad)[0], (v_mid - v_rad)[0]],
            [(v_mid - v_rad)[1], (v_mid - v_rad)[1]],
            [0.0, func(v_mid - v_rad)], c='grey', linestyle='--')
    axi.plot([(v_mid + v_rad)[0]], [(v_mid + v_rad)[1]], [func(v_mid + v_rad)], 'o', c='red')
    axi.plot([(v_mid - v_rad)[0]], [(v_mid - v_rad)[1]], [func(v_mid - v_rad)], 'o', c='red')

plt.show()


print('script finished.')

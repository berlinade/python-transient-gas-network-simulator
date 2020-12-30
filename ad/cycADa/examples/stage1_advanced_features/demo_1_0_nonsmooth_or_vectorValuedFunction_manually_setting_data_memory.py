import numpy as np

from ad.cycADa import *
# from ad.cycADa import tape, adFloat, sin, cos, exp, log, inv


num_of_scopes = 3 # scopes

t = tape(num_of_scopes, True)

xad = adFloat(t, (True, True, False)) #, ID = 4) # defines a variable
yad = adFloat(t, [1, 0, 1])#, ID = 9)
# zad = adFloat(t) # is equal to zad = adFloat(t, [1, 1, 1])
three = adFloat(t, 3.0) # defines a constant

print("No. of tape scopes : {}".format(t.num_of_scopes))
print("current tape scope : {}".format(t.scope))

from numpy import array, pi
 
valX = array([1.1, -3.1415, 0.4])
midX = array([1.1, -3.1415, 0.4])
radX = array([0.0, 0.0, 0.2])
 
# setting values of variables
# ===========================
xad.val = valX[0]
xad.mid = midX[0]
xad.rad = radX[0]
 
yad.val = valX[1]
yad.mid = midX[1]
yad.rad = radX[1]

print("xad | val, mid, rad : {}, {}, {}".format(xad.val, xad.mid, xad.rad))
print("yad | val, mid, rad : {}, {}, {}\n".format(yad.val, yad.mid, yad.rad))


def f(x, y):
    zx = x
    zy = y

    wx = abs(zx) # involves x
    wy = abs(zy) # involves y

    w1 = abs(wx-22.0) # involves x
    w2 = abs(sin(x) + y + w1) # involves x and y

    c = 3.0

    out = np.array([c, wx, (-((w2*3.0) - 17.0))*2.0 + y, wy, c + x])

    return out # np.array([tthree + x + y, tthree, tthree, tthree])

def divDiff(f, x, y, hx = 0.1, hy = 0.0):
    return (f(x + hx, y + hy) - f(x, y))/(hx + hy)


Fad = f(xad, yad)
fad = Fad[1]

t.declare_dependent(Fad)
for fad_i in Fad:
    print(fad_i, fad_i.dependent)

print("(n : {} | s : {} | m : {})" .format(t.n, t.s, t.m))


t.scope = 0

print("evaluate Jacobian of scope {} ...".format(t.scope))

# t.allocJac(False)

len_z = t.s
len_y = t.m
# if USys:
#     len_z += self.s
local_data_out = np.zeros(shape = (len_z + len_y,))
t.set_grad_pointer(local_data_out, False)

t.D(midX, radX)

# t.scope = 1
#
# print("evaluate Jacobian of scope {} ...".format(t.scope))
# t.allocJac(False)
# t.D(midX, radX)
#
# t.scope = 2
#
# print("evaluate Jacobian of scope {} ...".format(t.scope))
# t.allocJac(False)
# t.D(midX, radX)


t.scope = 0

print("div Diff:")
print(np.transpose(np.array([divDiff(f, xad.mid, yad.mid, 0.000001, 0.0),
                             divDiff(f, xad.mid, yad.mid, 0.0, 0.000001)])))
print("")


from scipy.sparse import csr_matrix

print("Jacobian of scope {} : ".format(t.scope))
jac = csr_matrix((t.data, abs(t.indices), t.indptr), shape = (t.s+t.m, t.n+t.s))#t.jac_spa_row(midX, radX)[0])
print(jac.todense())

# t.scope = 1
# print("Jacobian of scope {} : ".format(t.scope))
#
# jac = csr_matrix((t.data, abs(t.indices), t.indptr), shape = (t.s+t.m, t.n+t.s))#t.jac_spa_row(midX, radX)[0])
# print(jac.todense())


len_z = t.s
len_y = t.m
# if USys:
#     len_z += self.s
local_data_out = np.zeros(shape = (len_z + len_y,))
t.set_grad_pointer(local_data_out, False)

t.D(midX, radX)

print("Jacobian of scope {} : ".format(t.scope))
jac2 = csr_matrix((t.data, abs(t.indices), t.indptr), shape = (t.s+t.m, t.n+t.s))#t.jac_spa_row(midX, radX)[0])
print(jac2.todense())

jac2.data[0] = 99.99

print("compare")
print(jac.todense())
print(jac2.todense())


print("script finished.")

import numpy as np

from ad.cycADa import *
# from ad.cycADa import tape, adFloat, sin, cos, exp, log, inv


'''
    meaning of scopes in cycADa. First of all: This is not about differentiation scopes.
    But assume there is a function F: IR^n x IR^k --> IR^m
    
        F(x, y)
        
    now assume you need the following partial derivative matrices: 
      A = d/(dv) F(v), were v = (x, y)
      B = d/(dx) F(x, y)
      C = d/(dy) F(x, y)
    and you need to be in able to update them indepently from each other.
    E.g. B need to be updated but not A and C and no copies.
    Furthermore slicing is difficult since A, B and C are row-wise sparse matrices.
    
    So 3 distinct tapes would be required for each matrix.
    Instead cycADa offers scopes which are called scopes.
    Within each scope any variable can be active (i.e. to differentiate for) 
    or passive (i.e. not to differentiate for).
    
    See line 39 for further details at the variable initialisation.
'''
num_of_scopes = 1 # scopes

t = tape(num_of_scopes, False)

print("No. of tape scopes : {}".format(t.num_of_scopes))
print("current tape scope : {}".format(t.scope))

xad = adFloat(t)
yad = adFloat(t)

print("xad | val, mid, rad : {}, {}, {}".format(xad.val, xad.mid, xad.rad))
print("yad | val, mid, rad : {}, {}, {}\n".format(yad.val, yad.mid, yad.rad))


def f(x, y):
    b = x > y
    b2 = True
    b3 = logical_and(b, b2)
    # print("===>", b, b2, b3, type(b3))
    z = cond_assign(b3, x, y)

    return z, [b, b3]

Fad, Bad = f(xad, yad) #pow(-(((yad + sin(xad))*three) - 17.0), 2.0)*inv(yad) # <= continue tracing

t.declare_dependent(Fad)
print(Fad.dependent)
# for fad_i in Fad:
#     print(fad_i, fad_i.dependent)

print("(n : {} | s : {} | m : {})" .format(t.n, t.s, t.m))
print("Fad vars : {}".format(Fad.variables)) # <= all variables are enumerated and this yields the numbers of variables fad depends on
print("xad.idx = {}; or xad is the first entry on the tape ...".format(xad.idx))
print("Fad.idx = {}; or Fad is the {}th entry on the tape ...".format(Fad.idx, 1 + Fad.idx))

# setting values of variables
# ===========================
valX = np.array([1.0, -2.0])
midX = np.array([1.0, -2.0])
radX = np.array([0.0, 0.0])

t(valX)
print("================")
print("{} == {}".format(Fad.val, f(xad.val, yad.val)[0]))

t.scope = 0

print("evaluate Jacobian of scope {} ...".format(t.scope))
t.allocJac(False)
t.D(midX, radX)

 
print("")
print("fad - mid, rad, grad:")
print("{}, {}".format(Fad.mid, Fad.rad))
print(Fad.grad)
print(Fad.indices)


print('script finished.')

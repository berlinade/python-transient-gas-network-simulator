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
num_of_scopes = 3 # scopes

t = tape(num_of_scopes, False)

'''
    Here the (True, True, False) defines the role of x within each scope (aka scope) corresponding to the example above.
    As well as as [1, 0, 1] does the same job for y. In other words True, False and integers 0, 1 can be used.
    So in the first scope (or scope) f will be differentiated for x and y to achieve matrix A.
    In the second scope f will be differentiatited for x only to acieve B.
    In the third scope f will be differentiatited for y only to acieve C.
'''
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

# def f(x, y):
#     if isinstance(x, float):
#         tthree = 3.0
#     else:
#         tthree = three
#     return np.array([tthree, (-((abs(sin(x)+y)*3.0) - 17.0))**2.0/y])

def f(x, y):
    # if isinstance(x, float) and isinstance(y, float):
    #     tthree = three.val
    # else:
    #     tthree = three

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
 
# sinXad = sin(xad)
# t() #  <=  t.__call__()
# print("{} == {} == {}".format(npSin(xad.val), sin(xad.val), sinXad.val))
 
Fad = f(xad, yad) #pow(-(((yad + sin(xad))*three) - 17.0), 2.0)*inv(yad) # <= continue tracing
fad = Fad[1]
print("nonsense value : {}".format(fad.val)) #  <=  should yield nonsense, because 't' wasn't evaluated up to this state
 
print("fad is dependent : {}".format(fad.dependent))
print("switching dependent state of fad ...")
fad.dependent = True
print("fad is dependent : {}\n".format(fad.dependent))
# turning the rest of the output variables into dependent
t.declare_dependent(Fad)
for fad_i in Fad:
    print(fad_i, fad_i.dependent)

print("(n : {} | s : {} | m : {})" .format(t.n, t.s, t.m))
print("fad vars : {}".format(fad.variables)) # <= all variables are enumerated and this yields the numbers of variables fad depends on
print("xad.idx = {}; or xad is the first entry on the tape ...".format(xad.idx))
print("fad.idx = {}; or fad is the {}th entry on the tape ...".format(fad.idx, 1+fad.idx))
 
t(valX)
print("{} == {}".format(fad.val, f(xad.val, yad.val)))

t.scope = 0

print("evaluate Jacobian of scope {} ...".format(t.scope))
t.allocJac(False)
t.D(midX, radX)

t.scope = 1

print("evaluate Jacobian of scope {} ...".format(t.scope))
t.allocJac(False)
t.D(midX, radX)

t.scope = 2

print("evaluate Jacobian of scope {} ...".format(t.scope))
t.allocJac(False)
t.D(midX, radX)

t.scope = 0
 
print("")
print("fad - mid, rad, grad:")
print("{}, {}".format(fad.mid, fad.rad))
print(fad.grad)
 
# xad.rad = 0.02
# yad.rad = 0.021
 
print("div Diff:")
print(np.transpose(np.array([divDiff(f, xad.mid, yad.mid, 0.000001, 0.0),
                             divDiff(f, xad.mid, yad.mid, 0.0, 0.000001)])))
print("")
 
t.D(midX, radX)
print(fad.mid)
print(fad.rad)
print(fad.grad) # <= re-evalutions of the tape will change the grad, because the numpy-ndarray and the gradient (c++ vector) of fad share the same mem location 

print("bla")

# for x in t.vars:
#     print(x.idx)
# print("")
for z in t.swVars:
    print(z.idx)
print("")
# for y in t.depends:
#     print(y.idx)

print("data, indices, indptr")
print("data    : {}".format(t.data))
print("indices : {}".format(t.indices))
print("indptr  : {}".format(t.indptr))
print("end of printing data, indices, indptr")

from scipy.sparse import csr_matrix

print("Jacobian of scope {} : ".format(t.scope))
jac = csr_matrix((t.data, abs(t.indices), t.indptr), shape = (t.s+t.m, t.n+t.s))#t.jac_spa_row(midX, radX)[0])
print(jac.todense())

t.scope = 1
print("Jacobian of scope {} : ".format(t.scope))

jac = csr_matrix((t.data, abs(t.indices), t.indptr), shape = (t.s+t.m, t.n+t.s))#t.jac_spa_row(midX, radX)[0])
print(jac.todense())


print("="*15)
print("new feature: forward mode (fwd)")

for scope in range(t.num_of_scopes):
    t.scope = scope
    print("\n" + "t.scope = {} | n = {}, s = {}, m = {}".format(t.scope, t.n, t.s, t.m))
    t.allocFwdVec()
    t.fwd(midX, radX, np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    print(t.fwd_vec)
    t.fwd(midX, radX, np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0]))
    print(t.fwd_vec)
    t.fwd(midX, radX, np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0]))
    print(t.fwd_vec)
    t.fwd(midX, radX, np.array([0.0, 0.0, 0.0, 1.0, 0.0, 0.0]))
    print(t.fwd_vec)
    t.fwd(midX, radX, np.array([0.0, 0.0, 0.0, 0.0, 1.0, 0.0]))
    print(t.fwd_vec)
    t.fwd(midX, radX, np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0]))
    print(t.fwd_vec)

print("="*15)
print("new feature: reverse mode (rev)")

for scope in range(t.num_of_scopes):
    t.scope = scope
    print("\n" + "t.scope = {} | n = {}, s = {}, m = {}".format(t.scope, t.n, t.s, t.m))
    t.allocRevVec()
    t.rev(midX, radX, np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    print(t.rev_vec)
    t.rev(midX, radX, np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    print(t.rev_vec)
    t.rev(midX, radX, np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    print(t.rev_vec)
    t.rev(midX, radX, np.array([0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    print(t.rev_vec)
    t.rev(midX, radX, np.array([0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]))
    print(t.rev_vec)
    t.rev(midX, radX, np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]))
    print(t.rev_vec)
    t.rev(midX, radX, np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]))
    print(t.rev_vec)
    t.rev(midX, radX, np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]))
    print(t.rev_vec)
    t.rev(midX, radX, np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]))
    print(t.rev_vec)

print("="*15)
print("new feature: get identifiers of adFloat")

print("xad identifier: {}".format(xad.identifier))
print("fad identifier: {}".format(fad.identifier))

print("xad operation type: {}".format(xad.operation_type))
print("xad operation type: {}".format(fad.operation_type))

print("="*15)
print("new feature: get dependencies of adFloat as adFloats")
print("Fad[2] operation type: {}".format(Fad[2].operation_type))
print("Fad[2] arg1 operation type: {}".format(Fad[2].depends_on[0].operation_type))
print("Fad[2] arg2 operation type: {}".format(Fad[2].depends_on[1].operation_type))
print("")
print("Fad[2] arg1 successor operation type: {} ".format(Fad[2].depends_on[0].dependency_of[0].operation_type) +
      "(should be the same as Fad[2] operation type)")
print("Fad[2] arg1 successor is dependent: {}".format(Fad[2].depends_on[0].dependency_of[0].dependent))

print("Fad[2] successor (there should be none -or- empty list): {}".format(Fad[2].dependency_of))
print("xad dependencies (there should be none -or- empty list): {}".format(xad.depends_on))

print("="*15)
print("new feature: adFloats have prints")
print(Fad[2])
print(xad)
print(Fad[0])
print([Fad[2], xad, Fad[0].depends_on[0]])

print("BIG WARNING: Operations involving adFloats that have been declared dependent already may lead " +
      "to undefined behaviour! Dependent declarations should happen after tracing all operations!")

print("finished")

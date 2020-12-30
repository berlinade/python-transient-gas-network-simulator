'''
    properties/data class for functions
    required for operator overloading
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
import numpy as np

from typing import Union, List, Tuple

from paso.util.basics import export #, force_array, shape_t


@export
def clipped_func(a : float, x : float, b : float): return (a + b + abs(a - x) - abs(b - x)) / 2.0

@export
def relu(x : float): return (x + abs(x))/2.0


class create_ufunc_handler(object):

    def __init__(self):
        self.sin_func = np.sin
        self.cos_func = np.cos
        self.tan_fun = np.tan

        self.arctan_func = np.arctan

        self.sinh_func = np.sinh
        self.cosh_func = np.cosh
        self.arctanh_func = np.arctanh

        self.exp_func = np.exp
        self.log_func = np.log

    def sinc_func(self, x):  # return np.pi*np.sinc(x/np.pi)
        if x == 0.0: return 1.0
        return self.sin_func(x)/x

    def sinhc_func(self, x):  # makeshift definition of sinhc (defined by: x * sinhc(x) = sinh(x))
        if x == 0.0: return 1.0
        return self.sinh_func(x)/x

    def arctanhc_func(self, x):  # makeshift definition of arctanhc (defined by: x * arctanhc(x) = arctanh(x))
        if x == 0.0: return 1.0
        return self.arctanh_func(x)/x

    def max_2_func(self, u, w): return max_2(u, w)

    def min_2_func(self, u, w): return min_2(u, w)

    @export
    def maximum_func(self, *args): return maximum(*args)

    @export
    def minimum_func(self, *args): return minimum(*args)

def max_2(u, w):
    return (u + w + abs(w - u))/2.0

def min_2(u, w):
    return (u + w - abs(w - u))/2.0

@export
def maximum(*args):
    if len(args) == 0: return None
    if len(args) == 1: return args[0]
    if len(args) == 2: return max_2(*args)
    if len(args) % 2 == 1: return max_2(args[0], maximum(*args[1:]))
    return maximum(*[max_2(args[2*i], args[2*i + 1]) for i in range(len(args)//2)])

@export
def minimum(*args):
    if len(args) == 0: return None
    if len(args) == 1: return args[0]
    if len(args) == 2: return min_2(*args)
    if len(args) % 2 == 1: return min_2(args[0], minimum(*args[1:]))
    return minimum(*[min_2(args[2*i], args[2*i + 1]) for i in range(len(args)//2)])

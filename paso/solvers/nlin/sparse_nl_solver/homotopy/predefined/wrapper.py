'''
    prepared homotopy functions
    ===========================
'''

__author__ = ('Sascha Baumanns', 'Tom Streubel', 'Christian Strohm', 'Caren Tischendorf') # alphabetical order of surnames
__credits__ = ('Lennart Jansen',) # alphabetical order of surnames


'''
    imports
    =======
'''
import numpy as np

from paso.util.types_and_errors import Vec_t, CsMatrix_t

from typing import Union, Callable


'''
    body
    ====
'''
def create_nav(fun : Callable[[Vec_t], Vec_t], jac : Callable[[Vec_t], CsMatrix_t],
               mu : float, x_current : Vec_t):
    '''
        f_nav is a homotopy function for the naive homotopy.

        :param fun:
        :param jac:
        :param mu:
        :param x_current:
        :return:
    '''

    def fun_nav(x : Vec_t) -> Vec_t: return fun(x) - (1.0 - mu)*fun(x_current)
    def jac_nav(x : Vec_t) -> CsMatrix_t: return jac(x)
    return fun_nav, jac_nav

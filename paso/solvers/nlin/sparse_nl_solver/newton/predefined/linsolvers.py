'''
    prepared, convenient wrapper for scipy sparse linear solvers
    ============================================================

    It is highly recommended to provide your own linear solver for newton, but here are some defaults
'''

__author__ = ('Sascha Baumanns', 'Tom Streubel', 'Christian Strohm', 'Caren Tischendorf') # alphabetical order of surnames
__credits__ = ('Lennart Jansen',) # alphabetical order of surnames


'''
    imports
    =======
'''
from scipy.sparse.linalg import spsolve, splu, spilu

from paso.util.types_and_errors import Vec_t, CsMatrix_t, LinSolveError

from typing import Union


'''
    body
    ====
'''
class linsolver_template(object):

    def __init__(self, name : str): self.name = name

    def __call__(self, A : CsMatrix_t, b : Vec_t, A_did_change : bool = True) -> Vec_t: raise NotImplementedError

    def __str__(self): return f'Linsolver: {self.name}'

    def __repr__(self): return self.__str__()


class spsolve_simple_wrapper(linsolver_template):

    def __init__(self): super().__init__(name = 'scipy.sparse.linalg.spsolve')

    def __call__(self,
                 A : CsMatrix_t,
                 b : Vec_t,
                 A_did_change : bool = True) -> Vec_t:
        '''
            :param A: CSR -or- sparse system matrix of a linear system of equations: A*x = b
            :param b: right-hand-side (RHS) vector of a linear system of equations: A*x = b
            :param A_did_change: boolean flag whether the system matrix has changed since last call
            :return: solution x as vector of A*x = b
        '''
        try: return spsolve(A, b)
        except: raise LinSolveError('spsolve failed!')


class splu_simple_wrapper(linsolver_template):

    def __init__(self):
        super().__init__(name = 'scipy.sparse.linalg.splu')
        self.Mat : Union[None, CsMatrix_t] = None

    def __call__(self, A : CsMatrix_t,
                 b : Vec_t,
                 A_did_change : bool = True) -> Vec_t:
        '''
            :param A: CSR -or- sparse system matrix of a linear system of equations: A*x = b
            :param b: right-hand-side (RHS) vector of a linear system of equations: A*x = b
            :param A_did_change: boolean flag whether the system matrix has changed since last call
            :return: solution x as vector of A*x = b
        '''
        try:
            if self.Mat is None: A_did_change = True
            if A_did_change: self.Mat = splu(A.tocsc(copy = False)) # if A is CSR then numpy ignores copy = False, since copying is inevitable
            return self.Mat.solve(b)
        except: LinSolveError('splu failed!')


class spilu_simple_wrapper(linsolver_template):

    def __init__(self):
        super().__init__(name = 'scipy.sparse.linalg.spilu')
        self.Mat : Union[None, CsMatrix_t] = None

    def __call__(self, A : CsMatrix_t,
                 b : Vec_t,
                 A_did_change : bool = True) -> Vec_t:
        '''
            :param A: CSR -or- sparse system matrix of a linear system of equations: A*x = b
            :param b: right-hand-side (RHS) vector of a linear system of equations: A*x = b
            :param A_did_change: boolean flag whether the system matrix has changed since last call
            :return: solution x as vector of A*x = b
        '''
        try:
            if self.Mat is None: A_did_change = True
            if A_did_change: self.Mat = spilu(A.tocsc(copy = False)) # if A is CSR then numpy ignores copy = False, since copying is inevitable
            return self.Mat.solve(b)
        except: LinSolveError('spilu failed!')

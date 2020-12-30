'''
    types and error classes
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
import numpy as np
from scipy.sparse import csr_matrix, csc_matrix
from scipy.optimize.optimize import OptimizeResult

from typing import Union, Callable, Tuple, Sequence, List, Any, Optional, Iterable


''' 
    Type declarations
    =================
'''

''' int related '''
Vec_int_t = Union[Sequence[int], np.ndarray]
Shape_t = Vec_int_t # alias


''' float '''
Vec_float_t = Union[Sequence[float], np.ndarray]
Vec_t = Vec_float_t

Nes_t = Union[float, Vec_float_t, 'Nes_t', Sequence['Nes_t']] # nested structures/arrays/array of arrays

# matrix
Matrix_t = Union[Sequence[Vec_float_t], np.ndarray]

# sparse matrix
CsrMatrix_plain_t = Tuple[str, Vec_t, Vec_int_t, Vec_int_t, Shape_t] # 'csr', data, indices, indptr, shape
CscMatrix_plain_t = Tuple[str, Vec_t, Vec_int_t, Vec_int_t, Shape_t] # 'csc', data, indices, indptr, shape
CsMatrix_plain_t = Union[CsrMatrix_plain_t, CscMatrix_plain_t]

CsrMatrix_scipy_t = csr_matrix
CscMatrix_scipy_t = csc_matrix
CsMatrix_scipy_t = Union[CsrMatrix_scipy_t, CscMatrix_scipy_t]

CsrMatrix_t = Union[CsrMatrix_plain_t, CsrMatrix_scipy_t]
CscMatrix_t = Union[CscMatrix_plain_t, CscMatrix_scipy_t]
CsMatrix_t = Union[CsrMatrix_t, CscMatrix_t]


''' solver related functions'''
Callback_t = Callable[[Any], None] # type of callback function

LinSolve_t = Callable[[CsMatrix_t, Vec_t, bool], Vec_t] # general type for Linsolver for Newton

NLinSolve_t = Callable[[Any], OptimizeResult]


''' AD related functions '''
Elemental_1_to_1_t = Callable[[Any], float]
Elemental_2_to_1_t = Callable[[Any, Any], float]
Elemental_t = Union[Elemental_1_to_1_t, Elemental_2_to_1_t]


''' 
    Error-type declarations
    =======================
'''
class LinSolveError(Exception): pass # in case linear solver failed to converge

class NLinSolveError(Exception): pass # in case non-linear solver failed to converge

'''
    a class to organize jacobians of vector valued functions that provides finite differencing in case no exact
    derivatives are available!
'''

__author__ = ('Sascha Baumanns', 'Tom Streubel', 'Christian Strohm', 'Caren Tischendorf') # alphabetical order of surnames
__credits__ = ('Lennart Jansen',) # alphabetical order of surnames


'''
    imports
    =======
'''
import numpy as np
from scipy.sparse import csr_matrix

from paso.util.types_and_errors import Vec_t, CsrMatrix_t

from typing import Callable, Optional, List, Tuple, Set, Union, Sequence


'''
    body
    ====
'''
Sparsity_pattern_t = Sequence[Sequence[int]] # list of lists, where the i-th list consists of all variable-indices on which f_i actually depeds on; see example below

CS_pattern_t = Sequence[Vec_t] # i.e. (indices, indptr) in the sense of scipy.sparse.csr_matrix or csc_matrix


class jac_csr(object):

    def __init__(self,
                 fun : Callable[[Vec_t], Vec_t],
                 shape : Tuple[int, int],
                 dfun : Optional[Callable[[Vec_t], Vec_t]] = None,
                 indices : Optional[Vec_t] = None,
                 indptr : Optional[Vec_t] = None,
                 always_to_scipy : Optional[bool] = True):
        self.fun : Callable[[Vec_t], Vec_t] = fun
        self.dfun : Optional[Callable[[Vec_t], Vec_t]] = dfun # assuming that self.fun(x0) updates self.dfun, too

        self.precision : float = 1.0e-8

        self.shape : Tuple[int, int] = shape

        self.indices : Optional[Vec_t] = indices
        self.indptr : Optional[Vec_t] = indptr
        self.data : Optional[Vec_t] = None

        self.dirs : List[Vec_t] = []

        self.always_to_scipy : bool = always_to_scipy

        if not ((self.indices is None) or (self.indptr is None)): self.update_directions()

    def assign_sparsity_pattern(self, sparsity_pattern : Optional[Sparsity_pattern_t] = None):
        if sparsity_pattern is None:
            self.indices = np.array([j for _ in range(self.dim_f) for j in range(self.dim_x)])

            indptr : List[int] = [0]
            for i in range(self.dim_f): indptr.append(indptr[-1] + self.dim_x)
            self.indptr = np.array(indptr)
        else:
            self.indices = np.array([entry for row in sparsity_pattern for entry in row])

            indptr : List[int] = [0]
            for row in sparsity_pattern: indptr.append(indptr[-1] + len(row))
            self.indptr = np.array(indptr)

        self.update_directions()

    @property
    def dim_f(self): return self.shape[0]

    @property
    def dim_x(self): return self.shape[1]

    def f_depends_on_x(self, i : int): return self.indices[self.indptr[i]:self.indptr[i + 1]]

    def row_indices(self, i : int): return self.f_depends_on_x(i = i)

    def row(self, i : int): return self.data[self.indptr[i]:self.indptr[i + 1]]

    def _get_input_to_output_relation(self) -> List[Set[int]]:
        x_contributes_to_f : List[Set[int]] = [set() for j in range(self.dim_x)]

        for i in range(self.dim_f):
            for j in self.f_depends_on_x(i): x_contributes_to_f[j].add(i)

        return x_contributes_to_f

    def update_directions(self):
        x_contributes_to_f : List[Union[None, Set[int]]] = self._get_input_to_output_relation()

        i_of_dirs : List[Set[int]] = []
        j_of_dirs : List[Set[int]] = []
        for j in range(self.dim_x):
            for idx_dir, i_of_dir in enumerate(i_of_dirs):
                if len(x_contributes_to_f[j].intersection(i_of_dir)) == 0:
                    i_of_dirs[idx_dir] = i_of_dir.union(x_contributes_to_f[j]) # disjunctive union
                    j_of_dirs[idx_dir].add(j)
                    break
            else:
                i_of_dirs.append(x_contributes_to_f[j])
                j_of_dirs.append({j})
            x_contributes_to_f[j] = None # free memory
        del x_contributes_to_f # free memory
        del i_of_dirs # free memory

        self.dirs = []
        for idx_dir, j_of_dir in enumerate(j_of_dirs):
            dir_new = np.zeros(shape = (self.dim_x,))
            for j in j_of_dir: dir_new[j] = 1.0
            self.dirs.append(dir_new)
        del j_of_dirs # free memory

        self.data = np.zeros(shape = (self.indptr[-1],))

    @staticmethod
    def finite_diff(fun : Callable[[Vec_t], Vec_t],
                    x0 : Vec_t,
                    direction : Vec_t,
                    h : float = 1.0e-8,
                    f0 : Optional[Vec_t] = None) -> Tuple[Vec_t, Vec_t]:
        if f0 is None: f0 = fun(x0)
        return (fun(x0 + h*direction) - f0)/h, f0

    def __call__(self, x0 : Vec_t) -> CsrMatrix_t:
        f0 = self.fun(x0)
        for idx_dir, direction in enumerate(self.dirs):
            if self.dfun is None: directional_derivative, _ = self.finite_diff(fun = self.fun, x0 = x0,
                                                                               direction = direction,
                                                                               h = self.precision, f0 = f0)
            else: directional_derivative = self.dfun(direction)
            for i in range(self.dim_f):
                for idx_j, j in enumerate(self.f_depends_on_x(i)):
                    if direction[j] != 0.0: self.row(i)[idx_j] = directional_derivative[i]

        if self.always_to_scipy: return csr_matrix((self.data, self.indices, self.indptr), shape = self.shape)
        return ('csr', self.data, self.indices, self.indptr, self.shape)


if __name__ == '__main__':

    test = jac_csr(lambda x: np.array([x[0] + x[1] + x[6],
                                       x[1] + x[2] + x[6],
                                       x[2] + x[3] + x[5],
                                       x[3] + x[4] + x[5],
                                       x[4] + x[5] + x[6]]),
                          shape = (5, 7)) #,
                          # indices = np.array([0, 1, 6,
                          #                     1, 2, 6,
                          #                     2, 3, 5,
                          #                     3, 4, 5,
                          #                     4, 5, 6]),
                          # indptr = np.array([0, 3, 6, 9, 12, 15]))

    test.assign_sparsity_pattern([[0, 1, 6], [1, 2, 6], [2, 3, 5], [3, 4, 5], [4, 5, 6]])

    test.precision = 1.0e-11
    print(test.dirs)
    print(test(np.ones(7)).todense())

    test.always_to_scipy = False
    print(test(np.ones(7)))

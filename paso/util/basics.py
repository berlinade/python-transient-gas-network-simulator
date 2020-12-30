'''
    some basics
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
import sys, os

import numpy as np

from paso.util.types_and_errors import Vec_t, Nes_t

from typing import Union, Callable, Tuple, Sequence, List, Any, Optional, Iterable


def export(fn):
    '''
    common export function

    :param fn: a function or class to decorate
    :return: the function or class unchanged but added to __all__ of this file
    '''
    mod = sys.modules[fn.__module__]
    if hasattr(mod, '__all__'):
        if (fn_name := fn.__name__) not in (mod_all := mod.__all__): mod_all.append(fn_name)
    else: mod.__all__ = [fn.__name__]
    return fn


@export
def iter_window(to_iterate : Iterable, n : int, default : Optional[Any] = None):
    '''
    a generator that iterates through a list element-wise but 'memorizing' the last 'n' preceeding values from that list

    >> for (ai, bi, ci) in iter_window(list(range(6)), n = 3):
    >>     print(ai, bi, ci)
    will yield:
    >> 0 1 2
    >> 1 2 3
    >> 2 3 4
    >> 3 4 5

    :param to_iterate: an Iterable
    :param n: size of groups
    :param default: default return for the first n iterations, if to_iterate offers less then n items
    :return: generator
    '''
    if n == 0: raise IndexError(f'n: {n} > 0!')

    iter_inst = iter(to_iterate)
    args = [next(iter_inst, default) for _ in range(n)]
    yield args
    for entry in iter_inst:
        args.pop(0)
        args.append(entry)
        yield args


def clear_folder(dump_folder) -> None:
    '''
    deletes everything inside a folde except '.gitkeep' and '.gitignore'

    :param dump_folder: path to and including name of the folder do free of content
    :return: None
    '''

    for the_file in os.listdir(dump_folder):
        file_path = os.path.join(dump_folder, the_file)
        try:
            if os.path.isfile(file_path) and ((not ('.gitkeep' in file_path)) and (not ('.gitignore' in file_path))):
                print(f" ==> delete: \'{file_path}\'")
                os.unlink(file_path)
            else: print(f'[skip]: \'{file_path}\'')
        except Exception as e: print(e)


@export
def force_array(x : Nes_t, force_1D : bool = False) -> Vec_t:
    '''
    forces an input of type list, tuple, array and/or nested all od these to become an np.ndarray
    of 'force_1D' is True then the return is a one-dimensional array, i.e. with shape (-1,)

    :param x: object ot 'array-fy'
    :param force_1D: if True (default: False) the output is an one-dimensional or flat array
    :return: np.ndarray
    '''
    def _flatten_nesting(x_in : Nes_t, return_array : bool = False) -> Union[List[float], np.ndarray]:
        if isinstance(x_in, np.ndarray):
            if return_array: return x_in.reshape((-1,))
            out = list(x_in.reshape((-1,)))
        else:
            out = []
            if isinstance(x_in, (tuple, list)):
                for x_in_i in x_in: out.extend(_flatten_nesting(x_in = x_in_i))
            else: out.append(float(x_in))
        if return_array: return np.array(out)
        return out

    if force_1D: return _flatten_nesting(x_in = x, return_array = True)
    elif not isinstance(x, np.ndarray):
        if isinstance(x, (float, int)): x = [float(x)]
        return np.array(x, copy = False)
    return x


@export
def fuse(list_o_data : List[float], min_dist : float = 1.0e-7) -> List[float]:
    '''
    takes a list of float 'list_o_data' and merge/fuse entries that are closer then 'min_dist' apart.

    e.g.
        >> taus = [0.0, 0.1, 0.1 + 4.0e-8, 0.1 + 1.0e-7, 0.2, 0.2, 0.2 + 1.0e-8, 0.2 + 2.0e-8, 0.7 - 1.0e-8, 0.7, 1.0]
        >> print(fuse(taus))
        >> print(taus)
        will yield: [0.0, 0.10000006, 0.20000000750000002, 0.699999995, 1.0]

    :param list_o_data: list of floats
    :param min_dist: minimum distance entries should have (default: 1.0e-7)
    :return: new list of merged entries (see example above)
    '''
    dat : List[Union[float, None]] = sorted(list_o_data)

    for tries in range(10):
        mergers : bool = False

        for idx, entry in enumerate(dat):
            if entry is None: continue
            for j, entry_succ in enumerate(dat[idx + 1:], start = 1):
                if abs(entry - entry_succ) < min_dist:
                    dat[idx] = (entry := (j*dat[idx] + entry_succ)/(j + 1))
                    dat[idx + j] = None
                    mergers = True
                else: continue
        if mergers: dat = [entry_i for entry_i in dat if (not (entry_i is None))]

        if not mergers: break
    else: raise RuntimeError('tried to often -> did not converge!')

    return dat

'''
    some helpful tools for printing and matrix analysis
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
import sys

import numpy as np

from paso.util.basics import export
from paso.util.types_and_errors import CsMatrix_scipy_t

from typing import List, Tuple, Union, Optional, Callable, Any


'''
    body
    ====
'''
@export
def matrix_sparsity_pattern_plot(Mat : CsMatrix_scipy_t, draw_or_show : Union[None, str] = 'draw'):
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    fig, ax = plt.subplots()

    # plt.spy(J_n1.todense(), precision = 0.1, markersize = 5) # <== neat, but not enough information displayed
    m = Mat.todense()
    m_range = max(abs(np.max(Mat)), abs(np.min(Mat)))
    plt.imshow(m, norm = mcolors.Normalize(vmin = -m_range,
                                           vmax = m_range), interpolation = 'none', cmap = 'RdGy')
    plt.colorbar()
    if (not (draw_or_show is None)) and ('draw' in draw_or_show): plt.draw()
    else: plt.show()


@export
class table_print(object):

    def __init__(self,
                 header_signature : Optional[List[Tuple[str, type, int]]] = None,
                 file_path_and_name : Optional[str] = None):
        self.sep_first = '| '
        self.sep_mid = ' | '
        self._sep_last = ' |'

        self.float_offset : int = 10

        self.header_signature : List[Tuple[str, type, int]] = header_signature
        self.num_cols : int = 0
        self.map_column : dict = {}
        self.total_width : int = 0

        self.printed_rows : int = 0

        self.file_path_and_name: Optional[str] = file_path_and_name
        self._file = None
        if self.file_path_and_name:
            with open(self.file_path_and_name, mode = 'w'): pass # clear out log file if existent

    @property
    def sep_last(self): return self._sep_last + '\n'

    @sep_last.setter
    def sep_last(self, new_sep_last : str): self._sep_last = new_sep_last

    @property
    def file(self):
        if self.file_path_and_name:
            if self._file is None: self._file = open(self.file_path_and_name, mode = 'a')
            return self._file
        else: return sys.stdout

    def file_close(self): # to avoid accidentally closing sys.stdout aka. the console (and yes that is possible)
        if not (self._file is None):
            self._file.close()
            self._file = None

    def parse(self):
        self.num_cols = len(self.header_signature)
        self.map_column = {}
        self.total_width : int = len(self.sep_first) + len(self._sep_last) + max(0, self.num_cols - 1)*len(self.sep_mid)
        for idx, (header_field, sub_type, width) in enumerate(self.header_signature):
            self.total_width += width
            if sub_type == float: self.total_width += self.float_offset
            self.map_column[header_field] = idx

    def print_out(self, msg : str, end = ''):
        try:
            print(msg, end = end, file = self.file)
            self.file_close()
        except: self.file_close()

    def create_line(self, char = '-', print_out : bool = False):
        out = char*self.total_width + '\n'
        if print_out: self.print_out(out)
        return out

    def create_table_header(self, print_out : bool = True):
        self.printed_rows = 0 # reset

        out : str = self.create_line('=')
        out += self.sep_first
        for idx, (header_field, sub_type, width) in enumerate(self.header_signature):
            if sub_type == float: width += self.float_offset
            out += f'{header_field:^{width}s}'
            if idx + 1 < len(self.header_signature): out += self.sep_mid
            else: out += self.sep_last
        out += self.create_line()

        if print_out: self.print_out(out)
        return out

    def create_row(self, *args, print_out : bool = True, last_row : bool = False, **kwargs):
        out_row = [None for _ in range(len(self.header_signature))]
        for idx, arg in enumerate(args): out_row[idx] = arg
        for key, value in kwargs.items(): out_row[self.map_column[key]] = value

        if last_row and (self.printed_rows > 0):
            out : str = self.create_line()
            out += self.sep_first
        else: out = self.sep_first
        for idx, (_, sub_type, width) in enumerate(self.header_signature):
            if sub_type == int:
                if out_row[idx] is None: out += ' '*width
                else: out += f'{out_row[idx]:>{width}d}'
            elif sub_type == float:
                if out_row[idx] is None: out += ' '*(width + self.float_offset)
                else: out += f'{out_row[idx]:>{width + self.float_offset}.{width}e}'
            else:
                if out_row[idx] is None: out += ' '*width
                else: out += f'{str(out_row[idx]):^{width}s}'
            if idx + 1 < len(self.header_signature): out += self.sep_mid
            else: out += self.sep_last
        if last_row: out += self.create_line('=')

        self.printed_rows += 1

        if print_out: self.print_out(out)
        return out


if __name__ == '__main__':

    table_print_instance = table_print(header_signature = None)
    table_print_instance.header_signature = [('test', int, 10),
                                             ('test2', float, 5),
                                             ('test3', str, 30)]
    table_print_instance.parse()
    table_print_instance.create_table_header()
    table_print_instance.create_row(99, 1.1, "you will see me!")
    table_print_instance.create_row(98, 2.2, "you won't see me!", test3 = 'but you will see me!')
    table_print_instance.create_row(97, 3.3, test3 = 'and me!')
    table_print_instance.create_row(96, test3 = 'and MEE!')
    table_print_instance.create_row(105, -1.1, "you will see me!", last_row = True)


    print('script finished')

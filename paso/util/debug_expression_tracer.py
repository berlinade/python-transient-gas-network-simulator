'''
    simple overloading class for textual representation of functions
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from paso.util.basics import export


@export
class debug_cls(object):

    def __init__(self, msg, left = '(', right = ')'):
        '''
        can be used to overload functions and anaylyse math operations applied.
        Get a somewhat symbolic representation of a function, mostly for debug purposes.

        :param msg:
        :param left:
        :param right:
        '''
        self.msg = f'{left}{msg}{right}'

    def __pos__(self): return debug_cls(f"+{self.msg}")

    def __add__(self, other):
        if isinstance(other, debug_cls): return debug_cls(f"{self.msg}+{other.msg}")
        return debug_cls(f"{self.msg}+{other}")

    def __radd__(self, other): return debug_cls(f"{(other)}+{self.msg}")

    def __neg__(self): return debug_cls(f"-{self.msg}")

    def __sub__(self, other):
        if isinstance(other, debug_cls): return debug_cls(f"{self.msg}-{other.msg}")
        return debug_cls(f"{self.msg}-{other}")

    def __rsub__(self, other): return debug_cls(f"{(other)}-{self.msg}")

    def __mul__(self, other):
        if isinstance(other, debug_cls): return debug_cls(f"{self.msg}*{other.msg}", left = '[', right = ']')
        return debug_cls(f"{self.msg}*{other}", left = '[', right = ']')

    def __rmul__(self, other): return debug_cls(f"{(other)}*{self.msg}", left = '[', right = ']')

    def __truediv__(self, other):
        if isinstance(other, debug_cls): return debug_cls(f"{self.msg}/{other.msg}", left = '[', right = ']')
        return debug_cls(f"{self.msg}/{other}", left = '[', right = ']')

    def __rtruediv__(self, other): return debug_cls(f"{(other)}/{self.msg}", left = '[', right = ']')

    def __pow__(self, other):
        if isinstance(other, debug_cls): return debug_cls(f"{self.msg}**{other.msg}", left = '<', right = '>')
        return debug_cls(f"{self.msg}**{other}", left = '<', right = '>')

    def __rpow__(self, other): return debug_cls(f"{(other)}**{self.msg}", left = '<', right = '>')

    def __abs__(self): return debug_cls(f"abs({self.msg})", left = '', right = '')

    def __str__(self): return self.__repr__()

    def __repr__(self): return f"'{self.msg}'"

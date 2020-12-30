'''
    this is a utils script
'''

__author__ = ('Sascha Baumanns', 'Tom Streubel', 'Christian Strohm', 'Caren Tischendorf') # alphabetical order of surnames
__credits__ = ('Lennart Jansen',) # alphabetical order of surnames


'''
    imports
    =======
'''
from paso.util.types_and_errors import Vec_t

from typing import List, Tuple, Union, Optional, Callable, Any


'''
    body
    ====
'''
def tolfunc_default(x : Vec_t) -> Vec_t: return x


def callback_default(*args, **kwargs) -> None: return None


class call_counter(object):

    def __init__(self, fun : Callable):
        self.calls : int = 0
        self.fun = fun

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.fun(*args, **kwargs)

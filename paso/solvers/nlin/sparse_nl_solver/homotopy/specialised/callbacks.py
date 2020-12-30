'''
    specialised callback functions/examples
    =======================================
'''

__author__ = tuple() # alphabetical order of surnames
__credits__ = tuple() # alphabetical order of surnames


'''
    imports
    =======
'''
import sys

import numpy as np

from paso.util.types_and_errors import Vec_t, CsMatrix_t, Callback_t

from paso.solvers.nlin.sparse_nl_solver.util.general import call_counter
from paso.solvers.nlin.sparse_nl_solver.homotopy.core import homotopy_options, homotopy_results, nlin_solver_cookie

from paso.util.analysis import table_print

from typing import Tuple, List, Optional, Callable



'''
    body
    ====
'''
# paste your callback functions/classes in here. Structually you should follow the examples provided in 'predefined/callbacks'!

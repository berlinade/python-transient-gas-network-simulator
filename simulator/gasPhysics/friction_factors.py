'''
    models for friction of gas with the wall of pipeline
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
import numpy as np
from typing import Callable, Union, Tuple


fModel_image_t = float
fModel_t = Callable[[float, float], fModel_image_t]


def friction_factor_PKN(r : float, D : float):
    '''
        PKN - formula of Prandtl, Kármán and Nikuradse

    :param r: roughness of pipe wall in meter
    :param D: diameter of pipe in meter
    :return:
    '''
    return (-2.0*np.log10(r/(D*3.7065)))**(-2.0)


fric_register = {'pkn' : friction_factor_PKN}

'''
    models for real gas factor  -aka-  z-model
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.gasPhysics.mixtures import gas_mixture
from typing import Callable, Union, Tuple, Optional


zModel_image_t = Union[float, Tuple[float, float]]

_zModel_a_t = Callable[[float, bool], zModel_image_t]
_zModel_b_t = Callable[[float], zModel_image_t]
_zModel_c_t = Callable[[], zModel_image_t]
zModel_t = Union[_zModel_a_t, _zModel_b_t, _zModel_c_t]


def create_scaled_aga_bracketAga(gasMix : gas_mixture):
    '''
        realizes AGA and the bracket term for AGA. Both can be scaled by some factor kappa:

        AGA     := (1 + alpha*p)
                    _                    _
                   |         z**2         |
        bracket := | -------------------- | == z**2 (since z - p \partial_p z == 1)
                   |_ z - p \partial_p z _|

        note on [bar] <-> [pascal] conversion/transformation: p in alpha*p is normalized by pc within alpha

        :param gasMix: a data structure representing a mixture of gas
        :type gasMix: src_tinySim.gasPhysics.mixtures.gas_mix
        :return: aga formula to compute z(p) i.e. the gas factor to a given pressure p
        :rtype: callable
    '''

    alpha = (0.257/gasMix.pc)*(1.0 - (0.533/0.257)*(gasMix.Tc/gasMix.T))

    def aga_bracketAga(p : float, bracket_eval : Optional[bool] = True) -> zModel_image_t:
        '''
            :param p: pressure to take z(p) from
            :type p: bool
            :param bracket_eval: (default: True) if True the function provides 2 instead of 1 return arguments.
                                 The new one will be the bracket term
            :type bracket_eval: bool
            :return aga: value of z(p) w.r.t. to the aga formula
            :rtype aga: float
            :return bracket: bracket term w.r.t. to the aga formula
            :rtype bracket: float
        '''

        aga = 1.0 + alpha*p

        if bracket_eval:
            return aga, aga**2.0
        return aga

    return aga_bracketAga


def create_c_bracketC(gasMix : gas_mixture):
    '''
        realizes a constant z via speed of sound c and the bracket term for it. Both can be scaled by some factor A:

        c_term  := z0 = c^2/A
                    _                    _
                   |         z**2         |
        bracket := | -------------------- | == z0 (since z const => \partial_p z = 0)
                   |_ z - p \partial_p z _|

        :param gasMix: a data structure representing a mixture of gas
        :type gasMix: src_tinySim.gasPhysics.mixtures.gas_mix
        :return: realize constant model for evaluation of z(p) from p
        :rtype callable:
    '''

    z_c = (340.0**2.0)/(gasMix.Rs * gasMix.T) # 340**2 is roughly speed of sound in [m/s]

    def c_bracketC(*args, bracket_eval : Optional[bool] = True) -> zModel_image_t:
        '''
            :param args: (optional) internally unused placeholder for any values, typically pressures p as floats
            :type args: any
            :param bracket_eval: (default: True) if True the function provides 2 instead of 1 return arguments.
                                 The new one will be the bracket term
            :type bracket_eval: bool
            :return z_c: value of z(p) w.r.t. to the constant model
            :rtype z_c: float
            :return bracket: bracket term w.r.t. to the constant model
            :rtype bracket: float
        '''
        '''
            args:
                *args        - doesn't need arguments; thus can be left empty
                bracket_eval - (default: True) if True returns both results otherwise just the first

            returns:
                340**2/(R_s*T)
                340**2/(R_s*T) (as evaluation of the bracket term, but only if bracket_eval is True)
        '''
        if bracket_eval:
            return z_c, z_c
        return z_c

    return c_bracketC


z_register = {'aga' : create_scaled_aga_bracketAga,
              'speedOfSound' : create_c_bracketC}

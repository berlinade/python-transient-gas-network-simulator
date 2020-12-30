'''
    property class for the description and management of (mostly natural) gas mixtures
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.resources.units import pressure_to_bar, temperature_to_kelvin, \
                                      molMass_to_kgPerMol, density_to_kilogramm_per_m_cube, validate_unit, \
                                      universal_gas_constant_to_kg_m2_per_s2_mol_Kelvin
from typing import Optional, Tuple


class gas_mixture(object):

    def __init__(self,
                 pc : Optional[float] = None, pc_unit : Optional[str] = None,
                 Tc : Optional[float] = None, Tc_unit : Optional[str] = None,
                 molMass : Optional[float] = None, molMass_unit : Optional[str] = None,
                 T : Optional[float] = None, T_unit : Optional[str] = None,
                 rho_0 : Optional[float] = None, rho_0_unit : Optional[str] = None):
        '''
            Encapsules all relevant physical constants of the gas mixture.

            args
                - pc      : pseudo-critical pressure in [bar]
                - Tc      : pseudo-critical temperature in [K] (i.e. [Kelvin])
                - molMass : molar mass in [kg/mol]
                - T       : Temperature in [Kelvin]
                - rho_0   : norm density in [kg/m^3]

            properties
                - R       : universal gas constant in [kg m^2/(s^2 mol K)] == 1000.0 [g m^2/(s^2 mol K)]
                - pc      : pseudo-critical pressure in [bar]
                - Tc      : pseudo-critical temperature in [K]
                - molMass : molar mass in [kg/mol] == 1000.0 [kg/kmol] == 1000.0 [g/mol]
                - T       : Temperature in [K]
                - Rs      : specific gas constant in [m^2/(s^2 K)]
                - rho_0   : norm density in [kg/m^3]
        '''
        self._pc, self.pc_unit = None, None
        self._Tc, self.Tc_unit = None, None
        self._molMass, self.molMass_unit = None, None
        self._T, self.T_unit = None, None
        self._Rs, self.Rs_unit = None, None
        self._rho_0, self.rho_0_unit = None, None

        if not (pc is None): self.pc = (pc, pc_unit)
        if not (Tc is None): self.Tc = (Tc, Tc_unit)
        if not (molMass is None): self.molMass = (molMass, molMass_unit)
        if not (T is None): self.T = (T, T_unit)
        if not (rho_0 is None): self.rho_0 = (rho_0, rho_0_unit)

    @property
    def pc(self):
        return self._pc

    @pc.setter
    def pc(self, pc_tuple : Tuple[float, str]):
        self._pc = pressure_to_bar(*pc_tuple)
        self.pc_unit = validate_unit('bar', 'pressure')

    @property
    def Tc(self):
        return self._Tc

    @Tc.setter
    def Tc(self, Tc_tuple : Tuple[float, str]):
        self._Tc = temperature_to_kelvin(*Tc_tuple)
        self.Tc_unit = validate_unit('K', 'temperature')

    @property
    def T(self):
        return self._T

    @T.setter
    def T(self, T_tuple : Tuple[float, str]):
        self._T = temperature_to_kelvin(*T_tuple)
        self.T_unit = validate_unit('K', 'temperature')

    @property
    def R(self):
        return universal_gas_constant_to_kg_m2_per_s2_mol_Kelvin(8.31446261815324, 'kg_m2/s2_mol_k')

    @property
    def R_unit(self):
        return validate_unit('kg_m2/s2_mol_k', 'universal_gas_constant')

    @property
    def molMass(self):
        return self._molMass

    @molMass.setter
    def molMass(self, molMass_tuple : Tuple[float, str]):
        self._molMass = molMass_to_kgPerMol(*molMass_tuple)
        self._Rs = self.R/self.molMass
        self.molMass_unit = validate_unit('kg/mol', 'molMass')
        self.Rs_unit = validate_unit('m^2/s^2_kelvin', 'specific_gas_constant')

    @property
    def Rs(self):
        return self._Rs

    @property
    def rho_0(self):
        return self._rho_0

    @rho_0.setter
    def rho_0(self, rho_0_tuple : Tuple[float, str]):
        self._rho_0 = density_to_kilogramm_per_m_cube(*rho_0_tuple)
        self.rho_0_unit = validate_unit('kg/m^3', 'density')


testMix = gas_mixture(pc = 46.66135406, pc_unit = 'bar',
                      Tc = 202.7179718,  Tc_unit = 'K',
                      molMass = 0.0181674369592, molMass_unit = 'kg/mol',
                      T = 283.2, T_unit = 'K',
                      rho_0 = 0.82, rho_0_unit = 'kg/m^3')


if __name__ == "__main__":
    print(testMix.pc, testMix.pc_unit)
    print(testMix.Rs, testMix.Rs_unit)
    print(testMix.R, testMix.R_unit)
    print(testMix.rho_0, testMix.rho_0_unit)

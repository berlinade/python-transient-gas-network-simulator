'''
    unit management of gas network simulator
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from datetime import timedelta
import yaml
from simulator.resources.auxiliary import UnitError
from typing import Union, Optional, Callable
import os


"""
    [NOTE]
    all known units for conversion is collected within "units.register.yaml"
    Hence for adding new unit conversion ==> take a look there first!
"""

'''
    the next functions, objects and classes are used to read in known units and conversion rules from 
    external yaml: "units.register.yaml"
'''
def advanced_cast(str_in : str, cast_type : type = float):
    if "//" in str_in:
        counter, denominator = str_in.split("//")

        return cast_type(counter)/cast_type(denominator)

    if "/" in str_in:
        counter, denominator = str_in.split("/")

        return cast_type(counter)/cast_type(denominator)

    if "**" in str_in:
        base, exponent = str_in.split("**")

        return cast_type(base)**cast_type(exponent)

    if "*" in str_in:
        factor0, factor1 = str_in.split("*")

        return cast_type(factor0)*cast_type(factor1)

    return cast_type(str_in)

with open(os.path.dirname(__file__) + "/units.register.yaml", mode = "r") as units_reg_yaml:
    units_reg = yaml.load(units_reg_yaml, Loader = yaml.SafeLoader)

    conversion_dicts, alias_dicts = [], []

    for key, val in units_reg.items():
        if "conversion_factors" in key:
            for sub_key, sub_val in val.items():
                if isinstance(sub_val, (tuple, list)):
                    if isinstance(sub_val[0], str):
                        sub_val[0] = advanced_cast(sub_val[0]) # float(eval(sub_val[0])) # plain eval would be unsafe
                else:
                    if isinstance(sub_val, str):
                        val[sub_key] = advanced_cast(sub_val) # float(eval(sub_val)) # plain eval would be unsafe

            conversion_dicts.append(val)
        else:
            alias_dicts.append(val)

    for conv_dict, alias_dict in zip(conversion_dicts, alias_dicts):
        conv_keys = conv_dict.keys()
        alias_dict.update(dict(zip(conv_keys, conv_keys)))

class _units_reg_view(object):

    def __init__(self, in_units_reg : dict, suffix : str = ''):
        self.reg = in_units_reg
        self.suffix = suffix

    def __getitem__(self, item : str):
        return self.reg[item + "_" + self.suffix]

    def items(self):
        return self.reg.items()

conversion_factors = _units_reg_view(in_units_reg = units_reg, suffix = "conversion_factors")
alias_dictionary = _units_reg_view(in_units_reg = units_reg, suffix = "alias_dictionary")


'''
    the following functions can be used to check/validate whether a unit as string is known to the units.reg.yaml
'''
def _unit_unify(unit : str) -> str:
    if not isinstance(unit, str):
        raise TypeError("unit : {} has to be of type str!".format(unit))
    if (unit[0] == '[') and (unit[-1] == ']'):
        unit = unit[1:-1]
    if not (len(unit) > 0):
        raise UnitError("a unit has string length 0 which is impossible!")

    unit = unit.lower()

    unit = '/'.join(unit.split('_per_'))
    unit = '^2'.join(unit.split('_square'))
    unit = '^3'.join(unit.split('_cube'))

    prepos = -1
    preletter = None
    repeat = True
    while repeat:
        for pos, letter in enumerate(unit):
            if (letter in ["2", "3"]) and (prepos >= 0) and (not (preletter in ["_", "^"])):
                unit = unit[:pos] + "^" + unit[pos:]
                break
            prepos = pos
            preletter = letter
        else:
            repeat = False

    groups = unit.split('/')
    for i, group in enumerate(groups):
        if "_" in group:
            groups[i] = '_'.join(sorted(group.split('_')))
    unit = '/'.join(groups)

    return unit

def validate_unit(unit : str, spec : Optional[str] = None) -> str:
    oringinal_unit = unit
    unit = _unit_unify(unit)

    for key, item in alias_dictionary.items():
        if (spec is None) or (spec in key):
            for sub_key in item.keys():
                if unit == sub_key:
                    return unit

    if spec is None:
        raise UnitError("the unit: '{}' (normalized: '{}') is unknown!".format(oringinal_unit, unit))
    raise UnitError("the unit: '{}' (normalized: '{}') is unknown within spec: {}!".format(oringinal_unit, unit, spec))


short_unit_func_t = Callable[[float, str], float]
long_unit_func_t = Callable[[float, str, Optional[float], Optional[str]], float]
unit_function_t = Union[short_unit_func_t, long_unit_func_t]

def conversion_decorator_factory(spec : str):
    def conversion_decorator(func : unit_function_t) -> unit_function_t:
        def wrapper(value : float, unit : str,
                    density : Optional[float] = None, density_unit : Optional[str] = None) -> float:
            """ empty docstring """

            ''' arg 0 - value '''
            if isinstance(value, str):
                value = float(value)

            ''' arg1 - unit '''
            unit = validate_unit(unit, spec = spec)

            if density is None:
                return func(value, unit)
            return func(value, unit, density, density_unit)
        return wrapper
    return conversion_decorator


"""
    the next functions actually realize the unit conversions
    ========================================================
"""
@conversion_decorator_factory(spec = 'time')
def relative_time_to_sec(value : float, unit : str) -> float:
    '''
        converts a time offset provided in seconds, minutes, hours into seconds

        :param value:
        :param unit:
        :return:
    '''
    unit = alias_dictionary['time_to_s'][unit]

    return value*conversion_factors['time_to_s'][unit]

def relative_date_to_sec(days : float, hours : float, minutes : float, seconds : float) -> float:
    '''
        converts a time offset given in terms of 4 integer representing days, hours, minute, seconds into seconds

        :param days:
        :param hours:
        :param minutes:
        :param seconds:
        :return:
    '''
    return timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds).total_seconds()


@conversion_decorator_factory(spec = 'length')
def length_to_meter(value : float, unit : str) -> float:
    unit = alias_dictionary['length_to_m'][unit]

    return value*conversion_factors['length_to_m'][unit]


@conversion_decorator_factory(spec = 'speed')
def speed_to_meter_per_second(value : float, unit : str) -> float:
    unit = alias_dictionary['speed_to_m_per_s'][unit]

    return value*conversion_factors['speed_to_m_per_s'][unit]


@conversion_decorator_factory(spec = 'acceleration')
def acceleration_to_m_per_s_2(value : float, unit : str) -> float:
    unit = alias_dictionary['acceleration_to_m_per_s_2'][unit]

    return value*conversion_factors['acceleration_to_m_per_s_2'][unit]


@conversion_decorator_factory(spec = 'flow')
def flow_to_kilogramm_per_second(value : float, unit : str,
                                 density : Optional[float] = None, density_unit : Optional[str] = None) -> float:
    unit = alias_dictionary['flow_to_kg_per_s'][unit]
    factor, needs_density = conversion_factors['flow_to_kg_per_s'][unit]

    if not needs_density:
        return value*factor
    return density_to_kilogramm_per_m_cube(density, density_unit)*value*factor

@conversion_decorator_factory(spec = 'flow')
def flow_to_1000NormCubicMeter_per_hour(value : float, unit : str,
                                        density : Optional[float] = None, density_unit : Optional[str] = None) -> float:
    unit = alias_dictionary['flow_to_thousand_Nm3_per_h'][unit]
    factor, needs_density = conversion_factors['flow_to_thousand_Nm3_per_h'][unit]

    if not needs_density:
        return value*factor
    return (value*factor)/density_to_kilogramm_per_m_cube(density, density_unit)


@conversion_decorator_factory(spec = 'pressure')
def pressure_to_pascal(value : float, unit : str) -> float:
    unit = alias_dictionary['pressure_to_Pa'][unit]
    factor, offset = conversion_factors['pressure_to_Pa'][unit]

    return (offset + value)*factor

@conversion_decorator_factory(spec = 'pressure')
def pressure_to_bar(value : float, unit : str) -> float:
    unit = alias_dictionary['pressure_to_Bar'][unit]
    factor, offset = conversion_factors['pressure_to_Bar'][unit]

    return (offset + value)*factor

@conversion_decorator_factory(spec = 'pressure')
def pressure_to_barg(value : float, unit : str) -> float:
    unit = alias_dictionary['pressure_to_BarG'][unit]
    factor, offset = conversion_factors['pressure_to_BarG'][unit]

    return (offset + value)*factor


@conversion_decorator_factory(spec = 'density')
def density_to_kilogramm_per_m_cube(value : float, unit : str) -> float:
    unit = alias_dictionary['density'][unit]
    factor, offset = conversion_factors['density'][unit]

    return (offset + value)*factor


@conversion_decorator_factory(spec = 'temperature')
def temperature_to_kelvin(value : float, unit : str) -> float:
    unit = alias_dictionary['temperature_to_K'][unit]
    factor, offset = conversion_factors['temperature_to_K'][unit]

    return (offset + value)*factor


@conversion_decorator_factory(spec = 'molMass')
def molMass_to_kgPerMol(value : float, unit : str) -> float:
    unit = alias_dictionary['molMass_to_kg_per_mol'][unit]

    return value*conversion_factors['molMass_to_kg_per_mol'][unit]


@conversion_decorator_factory(spec = 'specific_gas_constant')
def specific_gas_constant_to_m2_per_s2_Kelvin(value : float, unit : str) -> float:
    unit = alias_dictionary['specific_gas_constant_to_m2_per_s2_Kelvin'][unit]

    return value*conversion_factors['specific_gas_constant_to_m2_per_s2_Kelvin'][unit]

@conversion_decorator_factory(spec = 'universal_gas_constant')
def universal_gas_constant_to_kg_m2_per_s2_mol_Kelvin(value : float, unit : str) -> float:
    unit = alias_dictionary['universal_gas_constant_to_kg_m2_per_s2_mol_Kelvin'][unit]

    return value*conversion_factors['universal_gas_constant_to_kg_m2_per_s2_mol_Kelvin'][unit]


"""
    typical units are prepared here!
    ================================
"""
second = 1.0
minute = relative_time_to_sec(1.0, 'min')
hour   = relative_time_to_sec(1.0, 'h')

mm    = length_to_meter(1.0, 'mm')
meter = 1.0
km    = length_to_meter(1.0, 'km')


"""
    for DEBUG, demonstrations and Tests
    ===================================
"""
if __name__ == "__main__":

    val_in_bar = 33.0
    val_in_barg = pressure_to_barg(val_in_bar, 'bar')

    print("bar  (from bar):", val_in_bar)
    print("barg (from bar):", val_in_barg)

    val_in_Pa = val_in_bar*1.0e5
    print("bar  (from Pa) :", pressure_to_bar(val_in_Pa, 'Pa'))
    print("barg (from Pa) :", pressure_to_barg(val_in_Pa, 'Pa'))

    print("bar (from barg):", pressure_to_bar(val_in_barg, 'barg'))


    val_norm_density = 0.789

    val_flow_in_kg_per_sec = 200.0
    val_flow_in_1000NormCubicMeter_per_hour = flow_to_1000NormCubicMeter_per_hour(val_flow_in_kg_per_sec,
                                                                                  "kg/s",
                                                                                  val_norm_density,
                                                                                  "kg_per_m3")
    val_flow_in_kg_per_sec_2 = flow_to_kilogramm_per_second(val_flow_in_1000NormCubicMeter_per_hour,
                                                            "1000nm3/h",
                                                            val_norm_density,
                                                            "kg_per_m3")

    print("kg/s        (from kg/s)  :", val_flow_in_kg_per_sec)
    print("1000 Nm^3/h (from kg/s)  :", val_flow_in_1000NormCubicMeter_per_hour)
    print("kg/s        (1000 Nm^3/h):", val_flow_in_kg_per_sec_2)

    print("check whether '[BAR]' is a known unit:")
    print("  --> after normalization and check: {}".format(validate_unit('[BAR]')))
    print("check '[BAR]' specifically as unit of pressure:")
    print("  --> after normalization and check: {}".format(validate_unit('[BAR]', spec = 'pressure')))
    print("check '[BAR]' specifically as unit of temperature:")
    try:
        print("  --> after normalization and check: {}".format(validate_unit('[BAR]', spec = 'temperature')))
    except UnitError as e:
        print("  --> last check failed with following error message: {}".format(e))

    print("thanks to the _unit_unify function obfuscated units such as '[M2_per_s_square_k]' can be validated:")
    print("'[M2_per_s_square_k]' get recognized as: {}".format(validate_unit('[M2_per_s_square_k]')))

    print('thanks to advanced decorators a validation will always be applied before conversion.')
    print("assume you try to convert 30 'km' to 'bar'")
    try:
        print("30.0 'km' in bar are: {}".format(pressure_to_bar(30.0, 'km')))
    except UnitError as e:
        print("The conversion did not pass the validaton that aborts with Error: {}".format(e))
        print("... where as 30.0 'km' in 'm' are: {}".format(length_to_meter(30.0, 'km')))

    print('script finished!')

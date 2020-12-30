'''
    structures for options and results of various solver
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from typing import Optional, List

from paso.util.basics import export

from scipy.optimize.optimize import OptimizeResult

from typing import Any


'''
    configuration/option base class
'''
@export
class options_base(object):
    '''
        docu
    '''
    __field_keys : List['str'] = ['name'] # key list of options recognized by the class description

    def __init_subclass__(cls, **kwargs):
        '''
            completes self defined init of subclasses with additional post init processes.
            More specifically it will add user defined values and overwrite default values (which have
            been defined in inheriting class-init's)

            :param kwargs:
            :return:
        '''
        cls.__hidden__original_init = cls.__init__

        def modified_init(*args, **kwargs): # old style decorator without @
            cls.__hidden__original_init(*args, **kwargs)

            ''' fill in user specified values! '''
            self = args[0]
            for key, val in kwargs.items():
                if key in self.keys(): self.__setattr__(key, val)
                else: raise AttributeError(f'unknown field name: \'{key}\'')

        cls.__init__ = modified_init

    def __init__(self, name : str, additional_keys : Optional[List[str]] = None):
        '''
            docu

            :param name:
            :param additional_keys:
        '''

        for key in (additional_keys or []):
            if not (key in self.keys()):
                if key in self.__dict__: raise AttributeError(f'forbidden key: {key}!')
                self.__class__.__field_keys.append(key)

        self.overrides : dict = {}

        self.name : str = name # set first as well as always present default!

    def __setattr__(self, key : str, val : Any) -> None:
        if key in self.keys():
            if key in self.__dict__:
                if self.__dict__[key] != val: # this if will record changes to __field_keys values!
                    if key in self.overrides: self.overrides[key]['former values'].append(self.__dict__[key])
                    else: self.overrides[key] = {'default' : self.__dict__[key], 'former values' : []}
        super().__setattr__(key, val)

    def __setitem__(self, key, value):
        if key in self.keys(): return self.__setattr__(key, value)
        else: raise AttributeError(f'unknown field name: {key}')

    def __getitem__(self, key):
        if key in self.keys(): return self.__getattribute__(key)
        else: raise AttributeError(f'unknown field name: {key}')

    def keys(self): return self.__class__.__field_keys # to make "dict(self)" or "{**self}" available

    def __dir__(self): return list(self.keys())

    def todict(self) -> dict: return {**self} # alias for {**self} or dict(self)

    def asdict(self) -> dict: return self.todict() # alias

    def __repr__(self) -> str:
        out = f"name: {self.name}\n" + "="*(6 + len(self.name))
        for key in self.keys():
            if key == 'name': continue
            out += "\n" + f"{key}: {self.__dict__[key]}"
            if key in self.overrides:
                out += "\n\t" + f"default: {self.overrides[key]['default']}"
                if len(self.overrides[key]['former values']) > 0:
                    out += " | " + f"former values: {self.overrides[key]['former values']}"
        return out

    def __str__(self) -> str: return self.__repr__()


@export
class integration_options(options_base):

    def __init__(self, name : str, **kwargs):
        additional_keys : List['str'] = ['h_min', 'h_max', 'h_grid', 'grid_offset',
                                         'custom_time_points',
                                         'atol_dom', 'rtol_dom',
                                         'atol_range', 'rtol_range',
                                         'one_step']

        if 'additional_keys' in self.__dict__: # this handles deriving classes wanting to add more additional keys
            additional_keys.extend(self.additional_keys)
            del self.additional_keys

        super().__init__(name = name, additional_keys = set(additional_keys))

        ''' define Defaults! '''
        self.h_min : Optional[float] = 0.0 # minimal step size <= h_max
        self.h_max : Optional[float] = None # maximum step size <= h_grid
        self.h_grid : Optional[float] = None # grid width (e.g. T-t0 or (T - t0/100)) creates an outer grid of timepoints/can be utilized for constant time step integrations
        self.grid_offset : Optional[float] = 0.0

        self.custom_time_points : List[float] = []

        self.atol_dom : float = 1.0e-8
        self.rtol_dom : float = 1.0e-6

        self.atol_range : float = 1.0e-8
        self.rtol_range : float = 1.0e-6

        self.one_step : bool = False


'''
    report/result base class
'''
@export
class results_base(OptimizeResult): pass


''' the return of any dae integrator/solver should be an instance of this (preferable) or a derived class! '''
@export
class integration_report(results_base):

    def __init__(self, *args, **kwargs):
        # typical attributes should be appended here as new class properties
        # special attributes shall be appended to instances 'on the fly' only!
        self.msg = None

        self.Ts = None
        self.Hs = None

        self.Xs = None
        self.dXs = None

        self.Ys = None
        self.dYs = None

        self.Errs_predicted = None

        self.num_of_ops = None

        super().__init__(*args, **kwargs)


if __name__ == '__main__':
    test_instance = integration_report(Hs = 'barFoo')
    test_instance['fooBar'] = 99
    test_instance.bella = 'donna'
    print(test_instance)

    print('\n')

    out = integration_options(name = 'example options instance')
    out.h_min = 22
    out['h_min'] = 99
    out.h_min = 0.99
    out.rtol_dom = 0.001
    out.order = 98
    out.order = 99
    print(out)


    print('\n')


    out_param = dict(out)
    out_param['name'] = '2nd example instance'

    out2 = integration_options(**out_param)

    print('')
    print(out2)


    class int_opts_test(integration_options):

        def __init__(self, name : str):
            self.additional_keys = ['bar', 'foo']
            super().__init__(name = name)

            self.bar = 1
            self.foo = -1

    out3 = int_opts_test(name = 'test')

    print('')
    print(out3)


    print("script finished")

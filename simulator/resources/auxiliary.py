'''
    various auxiliary functionalities
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
import sys, os


'''
    Error types & common Errors
    ===========================
'''

''' Error classes '''
class ModellingError(Exception): pass

class UnitError(Exception): pass

class ConfigDescriptionError(Exception): pass

class NetDescriptionError(Exception): pass

class SceneDescriptionError(Exception): pass

class DimensionError(Exception): pass


''' error caused by missing objects '''
def obligatory_function(name : str, meta : str = None):
    def missing_function(*args, **kwargs):
        if meta is None: raise ModellingError(f'{name} wasn\'t set or defined!')
        raise ModellingError(f'{meta} {name} wasn\'t set or defined!')
    return missing_function


''' empty logger -or- no logger as fallback if the user does not provide a proper one! '''
class no_logger(object):

    _fields = ['debug', 'info', 'warning', 'error', 'critical'] #, 'warn', 'exception' #, 'newline', 'linebreak']

    def __init__(self): pass

    def __getattr__(self, item : str):
        if item.lower() in self.__class__._fields:
            print(f'[{item.upper()}]: ', end = '')
            return print

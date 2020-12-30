'''
    setup.py script for compiling cycADa
'''

__author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
__credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
               'Oliver Kunst', 'Lutz Lehmann',
               'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames


'''
    imports
    =======
'''
from distutils.core import setup, Extension
from Cython.Build import cythonize
from setup_configuration_script import annotate_cython

import numpy as np

import os, sys, shutil


os.environ["CC"] = "g++" 
os.environ["CXX"] = "g++"


'''
    evaluate annotate option #1
    ---------------------------
'''
if annotate_cython: cythonize_flags = {'language_level' : 3, 'build_dir' : "build", 'annotate' : True}
else: cythonize_flags = {'language_level' : 3, 'build_dir' : "build"}


'''
    execute setup script
    ====================
'''
setup(ext_modules = cythonize(Extension('cycADa_interface',
                                        sources = ['src_cython/cycADa_interface.pyx',
                                                   'src_cpp/cycADa_adouble.cpp',
                                                   'src_cpp/cycADa_tape.cpp',
                                                   'src_cpp/cycADa_elemOp.cpp'],
                                        language = 'c++',
                                        include_dirs = [np.get_include()],
                                        library_dirs = [],
                                        libraries = [],
                                        extra_compile_args = ['-std=c++11'],
                                        extra_link_args = []), 
                              **cythonize_flags))


'''
    evaluate annotate option #2
    ---------------------------
'''
if (not annotate_cython):
    try: shutil.rmtree("./build/")
    except: pass

for _file in  os.listdir():
    if (_file[-3:] == ".so") and (_file[:6] == "cycADa"): shutil.move(_file, "bin/" + _file)

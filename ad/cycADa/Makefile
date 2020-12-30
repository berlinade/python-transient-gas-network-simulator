# Makefile script for compiling cycADa
#
# __author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
# __credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
#                'Oliver Kunst', 'Lutz Lehmann',
#                'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames


## user choosable flags
## ====================

# change python 3 interpreter here
PYINTERPRETER ?= python3
# name of script to compile
SCRIPT ?= demo_cycADa

CPP_OBJ  = obj/$(SCRIPT).o obj/cycADa_elemOp.o obj/cycADa_tape.o obj/cycADa_adouble.o


.PHONY: all build_py build_cpp clean


all:
	@(echo "Usage: make build_py                       - compile cython interface and cpp backend with $(PYINTERPRETER)")
	@(echo "Usage: make build_py PYINTERPRETER=python3 - compile cython interface and cpp backend with 'PYINTERPRETER'")
	@(echo "Usage: make build_cpp                      - compile cpp backend & $(SCRIPT).cpp for cpp usage of cycADa")
	@(echo "Usage: make build_cpp SCRIPT=demo_cycADa   - compile cpp backend & 'SCRIPT'.cpp for cpp usage of cycADa")
	@(echo "Usage: make clean                          - delete all compiled and generated files done by make")


build_py: src_cython/cycADa_interface.pyx
	@(echo PYINTERPRETER is [$(PYINTERPRETER)])
	$(PYINTERPRETER) setup.py build_ext --inplace


build_cpp: bin/$(SCRIPT)

bin/$(SCRIPT): $(CPP_OBJ)
	mkdir -p bin
	$(info CPP_OBJ is [$(CPP_OBJ)])
	g++ -std=c++11 -o $@ $^

obj:
	mkdir -p obj
obj/%.o: src_cpp/%.cpp | obj
	g++ -fPIC -std=c++11 -c -o $@ $<
obj/%.o: examples/stage4_using_the_cpp_interface/%.cpp | obj
	g++ -fPIC -std=c++11 -c -o $@ $<


clean: remove
	rm -f src_cython/cycADa_interface.cpp

remove: remove_py remove_cpp remove_test

remove_py:
	rm -f src_cython/*.pxd
	rm -f bin/*.pxd
	rm -f bin/*.so

remove_cpp:
	rm -f obj/*.o
	
remove_test:
	rm -f bin/demo_cycADa
	rm -f bin/cycADa_interface.*

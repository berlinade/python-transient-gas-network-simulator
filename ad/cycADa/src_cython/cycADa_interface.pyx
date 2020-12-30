'''
    this is the 2nd hearth-piece of cycADa namely its sole cython interface
'''

__author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
__credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
               'Oliver Kunst', 'Lutz Lehmann',
               'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames


'''
    imports
    =======
'''
# from builtins import int

from libcpp.string cimport string
from libcpp cimport bool as bool_cpp
from libcpp.vector cimport vector

import numpy as np
cimport numpy as np
np.import_array()

# from libc.stdint cimport uintptr_t

cdef extern from "../src_cpp/cycADa_elemOp.hpp" namespace "core":
    
    cdef cppclass ElemOp:
        
        size_t id
        vector[ElemOp*] precs, succs

    cdef cppclass boolOp:

        vector[ElemOp*] precs
        vector[boolOp*] bool_precs

        bool_cpp val;
        bool_cpp mid;
    
cdef extern from "../src_cpp/cycADa_tape.hpp" namespace "core":
    
    cdef cppclass cpp_tape "core::Tape":
        
        cpp_tape(size_t) except +
        
        long int read_var_id(size_t)
        void set_var_id(size_t, long int)
        
        size_t get_num_of_sets()
        size_t get_num_of_vars_and_params()
        size_t get_n(size_t)
        size_t get_s(size_t)
        size_t get_m()
        size_t get_len()
        
        void assign_val(vector[double])
        void assign_mid_rad(vector[double], vector[double])
        void assign_fwd_incr(size_t, vector[double])
        void assign_bar(size_t, vector[double])
        
        void zero_order_evaluation()
        void first_order_evaluation()
        void sparse_grad(size_t)
        void fwd(size_t)
        void rev(size_t)
        
        long int get_id_of_var(size_t, size_t)
        long int get_id_of_swVar(size_t, size_t)
        long int get_id_of_depend(size_t)


        size_t get_grad_size_inters(size_t)
        void set_grad_inters(size_t, double*)
        
        size_t get_grad_size_swVars(size_t)
        void set_grad_swVars(size_t, double*)
        
        size_t get_grad_size_depends(size_t)
        void set_grad_depends(size_t, double*)


        size_t get_fwd_vec_size_inters(size_t)
        void set_fwd_vec_inters(size_t, double*)

        size_t get_fwd_vec_size_swVars_and_depends(size_t )
        void set_fwd_vec_swVars_and_depends(size_t, double*)


        size_t get_rev_vec_size_inters(size_t)
        void set_rev_vec_inters(size_t, double*)

        size_t get_rev_vec_size_roots_and_swVars(size_t )
        void set_rev_vec_roots_and_swVars(size_t, double*)

cdef extern from "../src_cpp/cycADa_adouble.hpp" namespace "core":

    cdef cppclass cyAdbool "core::Adbool":

        boolOp *b

        cyAdbool()except +
        cyAdbool(bool_cpp in_b) except +
        cyAdbool(boolOp *in_b) except +

    cdef cppclass adouble "core::Adouble":

        ElemOp *ptr

        adouble() except +                                          # default constructor
        adouble(cpp_tape*, vector[bool_cpp]) except +                   # variable/param ini
        adouble(cpp_tape*, vector[bool_cpp], vector[long int]) except + # variable/param ini with preset IDs
        adouble(cpp_tape*, double) except +                         # constant ini
        adouble(cpp_tape*, ElemOp*) except +                        # create from ElemOp
        adouble(cpp_tape*, size_t, bool_cpp) except +                   # recreate Adouble from tape_entry
        
        size_t get_id()
        vector[ElemOp*] depends_on()
        vector[ElemOp*] dependency_of()
        
        size_t get_grad_len(size_t)
        double* get_grad_ptr(size_t)
        void set_grad_ptr(size_t, double*)
        
        size_t get_vars_len(size_t)
        long int* get_vars_ptr(size_t)
        
        void set_dependent_status(bool_cpp)
        bool_cpp is_root()
        bool_cpp is_swVar_node()
        bool_cpp is_active_swVar(size_t)
        bool_cpp is_active(size_t)
        bool_cpp is_abs_node()
        bool_cpp is_active_abs(size_t)
        bool_cpp is_dependent()
        bool_cpp is_const()
        
        void set_val(double)
        double get_val()
        void set_mid(double)
        double get_mid()
        void set_rad(double)
        double get_rad()

        int get_identifier()
        int get_subidentifier()
        
        adouble cyPos "operator+" ()
        adouble cySum "operator+" (adouble)
        adouble cyIncr "operator+" (double)
        
        adouble cyNeg "operator-" ()
        adouble cySub "operator-" (adouble)
        adouble cyDecr "operator-" (double)
        
        adouble cyMul "operator*" (adouble)
        adouble cyMul "operator*" (double)
        
        adouble cyDiv "operator/" (adouble)
        adouble cyDiv "operator/" (double)
        adouble cyInv "inv" ()

        cyAdbool cyEq "operator==" (adouble)
        cyAdbool cyEq "operator==" (double)

        cyAdbool cyNe "operator!=" (adouble)
        cyAdbool cyNe "operator!=" (double)

        cyAdbool cyLq "operator<=" (adouble)
        cyAdbool cyLq "operator<=" (double)

        cyAdbool cyLt "operator<" (adouble)
        cyAdbool cyLt "operator<" (double)

        cyAdbool cyGq "operator>=" (adouble)
        cyAdbool cyGq "operator>=" (double)

        cyAdbool cyGt "operator>" (adouble)
        cyAdbool cyGt "operator>" (double)
        
    adouble cyRIncr "operator+" (double, adouble)
    adouble cyRDecr "operator-" (double, adouble)
    adouble cyRMul "operator*" (double, adouble)
    adouble cyRDiv "operator/" (double, adouble)

    cyAdbool cyREq "operator==" (double, adouble)
    cyAdbool cyRNe "operator!=" (double, adouble)
    cyAdbool cyRLq "operator<=" (double, adouble)
    cyAdbool cyRLt "operator<" (double, adouble)
    cyAdbool cyRGq "operator>=" (double, adouble)
    cyAdbool cyRGt "operator>" (double, adouble)

    cyAdbool cyLogical_and "logical_and" (cyAdbool u, cyAdbool w)
    cyAdbool cyLogical_and "logical_and" (cyAdbool u, bool_cpp w)
    cyAdbool cyLogical_and "logical_and" (bool_cpp u, cyAdbool w)
    cyAdbool cyLogical_or "logical_or" (cyAdbool u, cyAdbool w)
    cyAdbool cyLogical_or "logical_or" (cyAdbool u, bool_cpp w)
    cyAdbool cyLogical_or "logical_or" (bool_cpp u, cyAdbool w)

    adouble cySin "sin" (adouble)
    adouble cyCos "cos" (adouble)

    adouble cyExp "exp" (adouble)
    adouble cyLog "log" (adouble)
    
    adouble cyAtan "atan" (adouble)
    
    adouble cySignSquare "signSquare" (adouble)
    
    adouble cyPow "pow" (adouble, adouble)
    adouble cyPow "pow" (adouble, double)
    adouble cyPow "pow" (adouble, int)
    adouble cyRPow "pow" (double, adouble)
    
    adouble cyAbs "abs" (adouble)
    adouble cyAbs2 "abs2" (adouble)

    adouble cyCondAssign "cond_assign" (cyAdbool b, adouble u, adouble w)
    adouble cyCondAssign "cond_assign" (cyAdbool b, adouble u, double w)
    adouble cyCondAssign "cond_assign" (cyAdbool b, double u, adouble w)
    adouble cyCondAssign "cond_assign" (bool_cpp b, adouble u, adouble w)
    adouble cyCondAssign "cond_assign" (bool_cpp b, adouble u, double w)
    adouble cyCondAssign "cond_assign" (bool_cpp b, double u, adouble w)
    double cyCondAssign "cond_assign" (bool_cpp b, double u, double w)

cdef extern from "cmath" namespace "std":

    double mathSin  "sin"  (double)
    double mathCos  "cos"  (double)
    double mathExp  "exp"  (double)
    double mathLog  "log"  (double)
    double mathAtan "atan" (double)


cdef class tape:
    
    cdef:
        size_t set_idx
        cpp_tape *t
#         np.ndarray indices, indptr, data, _data_4_intermediate_vars
        list indices_sets, indptr_sets, data_sets, data_fwd_sets, data_bar_sets
        list _data_4_intermediate_vars_sets, _data_4_fwd_intermediate_vars_sets, _data_4_bar_intermediate_vars_sets
        np.ndarray csr_len_sets
        int i_deps
        list USys, _in_rad_zeros
        
        bool_cpp ignore_kinks

    property scope:
        def __get__(self):
            return self.set_idx
        def __set__(self, new_set_idx):
            if new_set_idx >= self.num_of_scopes:
                raise Exception("scope out of bounds: scope has to be in [0, 1, ... num_of_scopes[!")
            self.set_idx = new_set_idx
        
    property mode:
        def __get__(self):
            print('use of <tape>.mode is deprecated. Use <tape>.scope instead.')
            return self.scope
        def __set__(self, new_set_idx):
            print('use of <tape>.mode is deprecated. Use <tape>.scope instead.')
            self.scope = new_set_idx
            
    property idx:
        def __get__(self):
            return self.t.read_var_id(self.set_idx)
        def __set__(self, new_idx):
            if new_idx >= 0:
                self.t.set_var_id(self.set_idx, new_idx)
            else:
                self.t.set_var_id(self.set_idx, -new_idx)              
    
    property num_of_scopes:
        def __get__(self):
            return self.t.get_num_of_sets()

    property num_of_modes:
        def __get__(self):
            print('use of <tape>.mode is deprecated. Use <tape>.scope instead.')
            return self.num_of_scopes
    
    property dom_dim:
        def __get__(self):
            return self.t.get_num_of_vars_and_params()
    
    property n:  
        def __get__(self):
            return self.t.get_n(self.set_idx)
        
    property s:
        def __get__(self):
            return self.t.get_s(self.set_idx)
        
    property m:
        def __get__(self):
            return self.t.get_m()

    def __len__(self):
        return self.t.get_len()
        
    def __cinit__(self, size_t num_of_sets = 1, bool_cpp ignore_kinks = False):
        self.set_idx = 0
        
        self.t = new cpp_tape(num_of_sets)
        
        self.indices_sets = [None for i in range(num_of_sets)]
        self.indptr_sets = [None for i in range(num_of_sets)]
        self.data_sets = [None for i in range(num_of_sets)]
        self.data_fwd_sets = [None for i in range(num_of_sets)]
        self.data_bar_sets = [None for i in range(num_of_sets)]

        self._data_4_intermediate_vars_sets = [None for i in range(num_of_sets)]
        self._data_4_fwd_intermediate_vars_sets = [None for i in range(num_of_sets)]
        self._data_4_bar_intermediate_vars_sets = [None for i in range(num_of_sets)]

        self.USys = [None for i in range(num_of_sets)]
        self._in_rad_zeros = [None for i in range(num_of_sets)]
        
        self.csr_len_sets = np.zeros(shape = (num_of_sets, ), dtype = np.int)
        
        self.i_deps = 0
        
        self.ignore_kinks = ignore_kinks

    property in_rad_zeros:
        def __get__(self):
            if (self._in_rad_zeros[self.set_idx] is None) or (len(self._in_rad_zeros[self.set_idx]) != self.dom_dim):
                self._in_rad_zeros[self.set_idx] = np.zeros(shape = (self.dom_dim,))
            return self._in_rad_zeros[self.set_idx]

    def __dealloc__(self):
        del self.t
        
    def __getitem__(self, size_t idx):
        return _adFloat_from_tape(self, idx)
        
    property variables:
        def __get__(self):
            for i in range(self.n):
                yield self[self.t.get_id_of_var(self.set_idx, i)]

    property vars:
        def __get__(self):
            return self.variables
        
    property swVars:
        def __get__(self):
            for i in range(self.s):
                yield self[self.t.get_id_of_swVar(self.set_idx, i)]
        
    property depends:
        def __get__(self):
            for i in range(self.m):
                yield self[self.t.get_id_of_depend(i)]

    property deps:
        def __get__(self):
            return self.depends

    def _flatten_nesting(self, x_in, return_array = False):
        if isinstance(x_in, np.ndarray):
            if return_array: return x_in.reshape((-1,))
            out = list(x_in.reshape((-1,)))
        else:
            out = []
            if isinstance(x_in, (tuple, list)):
                for x_in_i in x_in: out.extend(self._flatten_nesting(x_in = x_in_i))
            else: out.append(float(x_in))
        if return_array: return np.array(out)
        return out

    def _ensure_flat_array(self, in_arr): return self._flatten_nesting(in_arr, return_array = True)
        
    def __call__(self, *in_val):
        if len(in_val) == 0: self._call2()
        else: self._call(self._ensure_flat_array(in_val))

    cdef void _call(self, vector[double] in_val):
        self.t.assign_val(in_val)
        self.t.zero_order_evaluation()

    cdef void _call2(self):
        self.t.zero_order_evaluation()

    def D(self, in_mid = None, in_rad = None):
        if in_mid is None: self._D2()
        else:
            if in_rad is None: in_rad = self.in_rad_zeros
            else: in_rad = self._ensure_flat_array(in_rad)

            self._D(self._ensure_flat_array(in_mid), in_rad)
        
    cdef void _D(self, vector[double] in_mid, vector[double] in_rad):
        self.t.assign_mid_rad(in_mid, in_rad)
        self.t.first_order_evaluation()
        self.t.sparse_grad(self.set_idx)

    cdef void _D2(self):
        self.t.first_order_evaluation()
        self.t.sparse_grad(self.set_idx)

    def fwd(self, in_mid, in_rad_or_in_incr, in_incr = None):
        in_mid = self._ensure_flat_array(in_mid)
        in_rad_or_in_incr = self._ensure_flat_array(in_rad_or_in_incr)

        if in_incr is None:
            in_rad = self.in_rad_zeros
            in_incr = in_rad_or_in_incr
        else:
            in_rad = in_rad_or_in_incr
            in_incr = self._ensure_flat_array(in_incr)

        self._fwd(in_mid, in_rad, in_incr)

    cdef void _fwd(self, vector[double] in_mid, vector[double] in_rad, vector[double] in_incr):
        self.t.assign_mid_rad(in_mid, in_rad)
        self.t.first_order_evaluation()
        self.t.assign_fwd_incr(self.set_idx, in_incr)
        self.t.fwd(self.set_idx)

    def rev(self, in_mid, in_rad_or_in_bar, in_bar = None):
        in_mid = self._ensure_flat_array(in_mid)
        in_rad_or_in_bar = self._ensure_flat_array(in_rad_or_in_bar)

        if in_bar is None:
            in_rad = self.in_rad_zeros
            in_bar = in_rad_or_in_bar
        else:
            in_rad = in_rad_or_in_bar
            in_bar = self._ensure_flat_array(in_bar)

        self._rev(in_mid, in_rad, in_bar)

    cdef void _rev(self, vector[double] in_mid, vector[double] in_rad, vector[double] in_bar):
        self.t.assign_mid_rad(in_mid, in_rad)
        self.t.first_order_evaluation()
        self.t.assign_bar(self.set_idx, in_bar)
        self.t.rev(self.set_idx)
    
    def set_grad_pointer(self, np.ndarray[double, mode="c", ndim=1] local_data_out, USys = False):
        cdef: 
            np.ndarray[double, mode="c", ndim=1] local_data_inters # since z are new outputs, they are grouped with actual output variables
            np.ndarray[np.int_t, mode="c", ndim=1] local_indices
            np.ndarray[np.int_t, mode="c", ndim=1] local_indptr
            int len_v, len_z, len_y
            adFloat z
            size_t set_idx
            
        set_idx = self.set_idx
        
        n = self.n
        s = self.s
        m = self.m
        
        len_v = self.t.get_grad_size_inters(set_idx)
        len_z = self.t.get_grad_size_swVars(set_idx)
        len_y = self.t.get_grad_size_depends(set_idx)
        
        if USys: len_z += s
        
        local_data_inters = np.zeros(shape = (len_v, ))
        
        self._data_4_intermediate_vars_sets[set_idx] = local_data_inters
        self.data_sets[set_idx] = local_data_out
        
        self.t.set_grad_inters(set_idx, &local_data_inters[0])
        if USys:
            len_z = 0
            for z in self.swVars:
                z.ptr.set_grad_ptr(set_idx, &local_data_out[len_z])
                len_z += z.grad_len + 1 # the +1 is for UPL mode where any z needs its own idx in the sparsity structure
        else:
            self.t.set_grad_swVars(set_idx, &local_data_out[0])
        self.t.set_grad_depends(set_idx, &local_data_out[len_z])
        
        local_indices = np.zeros(shape = (len_z + len_y, ), dtype = np.int64)
        local_indptr  = np.zeros(shape = (s + m + 1, ), dtype = np.int64)
        
        self.indices_sets[set_idx] = local_indices
        self.indptr_sets[set_idx] = local_indptr
        
        for i, z in enumerate(self.swVars):            
            zlen = z.grad_len
            local_indptr[i+1] = local_indptr[i] + zlen
            local_indices[local_indptr[i]:local_indptr[i+1]] = z.variables # abs(z.variables)
            if USys:
                local_indices[local_indptr[i+1]] = n+i
                local_data_out[local_indptr[i+1]] = -1.0
                local_indptr[i+1] += 1
        for i, y in enumerate(self.depends):
            ylen = y.grad_len
            local_indptr[s+i+1] = local_indptr[s+i] + ylen
            local_indices[local_indptr[s+i]:local_indptr[s+i+1]] = y.variables # abs(y.variables)
        
    def allocJac(self, USys = False):
        cdef:
            np.ndarray[double, mode="c", ndim=1] local_data_out # since z are new outputs, they are grouped with actual output variables
            int len_z, len_y
            size_t set_idx
            
        set_idx = self.set_idx
        
        len_z = self.t.get_grad_size_swVars(set_idx)
        len_y = self.t.get_grad_size_depends(set_idx)
        
        if USys: len_z += self.s
        
        local_data_out = np.zeros(shape = (len_z + len_y,))
        
        self.set_grad_pointer(local_data_out, USys)

    def set_fwd_pointer(self, np.ndarray[double, mode="c", ndim=1] local_data_out):
        cdef:
            np.ndarray[double, mode="c", ndim=1] local_data_inters # since z are new outputs, they are grouped with actual output variables
            int len_v
            size_t set_idx

        set_idx = self.set_idx

        len_v = self.t.get_fwd_vec_size_inters(set_idx)

        local_data_inters = np.zeros(shape = (len_v,))

        self._data_4_fwd_intermediate_vars_sets[set_idx] = local_data_inters
        self.data_fwd_sets[set_idx] = local_data_out

        self.t.set_fwd_vec_inters(set_idx, &local_data_inters[0])
        self.t.set_fwd_vec_swVars_and_depends(set_idx, &local_data_out[0])

    def allocFwdVec(self):
        cdef:
            np.ndarray[double, mode="c", ndim=1] local_data_out # since z are new outputs, they are grouped with actual output variables
            int len_z_and_y
            size_t set_idx

        set_idx = self.set_idx

        len_z_and_y = self.t.get_fwd_vec_size_swVars_and_depends(set_idx)

        local_data_out = np.zeros(shape = (len_z_and_y,))

        self.set_fwd_pointer(local_data_out)

    def set_rev_pointer(self, np.ndarray[double, mode="c", ndim=1] local_data_out):
        cdef:
            np.ndarray[double, mode="c", ndim=1] local_data_inters # since z are new outputs, they are grouped with actual output variables
            int len_v
            size_t set_idx

        set_idx = self.set_idx

        len_v = self.t.get_rev_vec_size_inters(set_idx)

        local_data_inters = np.zeros(shape = (len_v,))

        self._data_4_bar_intermediate_vars_sets[set_idx] = local_data_inters
        self.data_bar_sets[set_idx] = local_data_out

        self.t.set_rev_vec_inters(set_idx, &local_data_inters[0])
        self.t.set_rev_vec_roots_and_swVars(set_idx, &local_data_out[0])

    def allocRevVec(self):
        cdef:
            np.ndarray[double, mode="c", ndim=1] local_data_out # since z are new outputs, they are grouped with actual output variables
            int len_x_and_z
            size_t set_idx

        set_idx = self.set_idx

        len_x_and_z = self.t.get_rev_vec_size_roots_and_swVars(set_idx)

        local_data_out = np.zeros(shape = (len_x_and_z,))
        self.set_rev_pointer(local_data_out)
        
    property data:
        def __get__(self):
            return self.data_sets[self.set_idx]
    
    property indices: 
        def __get__(self):
            return self.indices_sets[self.set_idx]
    
    property indptr:
        def __get__(self):
            return self.indptr_sets[self.set_idx]

    property fwd_vec:
        def __get__(self):
            return self.data_fwd_sets[self.set_idx]

    property rev_vec:
        def __get__(self):
            return self.data_bar_sets[self.set_idx]

    def declare_dependent(self, in_obj, _parent = None, _parent_idx = None):
        try:
            in_obj_iterator = iter(in_obj)
        except TypeError:
            if isinstance(in_obj, adFloat):
                in_obj.dependent = True
            elif isinstance(in_obj, (float, int)):
                if _parent is None:
                    in_obj = adFloat(self, in_obj)
                    in_obj.dependent = True
                    return in_obj
                else:
                    _parent[_parent_idx] = adFloat(self, in_obj)
                    _parent[_parent_idx].dependent = True
            else:
                raise AssertionError('cannot interpret in_obj!')
        else:
            for idx, sub_obj in enumerate(in_obj_iterator):
                self.declare_dependent(sub_obj, in_obj, idx)


cdef class adBool:

    cdef:
        cyAdbool ptr
        int _op_idx
        str repr_str
        str repr_str2

    def __cinit__(self, val = None, argLeft = None, argRight = None):
        cdef:
            bool_cpp _tr = True
            bool_cpp _fl = False

        self._op_idx = -1
        self.repr_str = "[ {}".format(argLeft) + " {} " + "{} ]".format(argRight)
        self.repr_str2 = self.repr_str

        if not (val is None):
            if val:
                self.ptr = cyAdbool(_tr)
                self.op_idx = 8
            else:
                self.ptr = cyAdbool(_fl)
                self.op_idx = 9

    property val:
        def __get__(self):
            if self.ptr.b.val:
                return True
            return False

    property mid:
        def __get__(self):
            if self.ptr.b.mid:
                return True
            return False

    property op_idx:
        def __get__(self):
            return self._op_idx

        def __set__(self, new_op_idx):
            self._op_idx = new_op_idx
            if new_op_idx == 0:
                self.repr_str2 = self.repr_str.format("'=='")
            elif new_op_idx == 1:
                self.repr_str2 = self.repr_str.format("'!='")
            elif new_op_idx == 2:
                self.repr_str2 = self.repr_str.format("'<='")
            elif new_op_idx == 3:
                self.repr_str2 = self.repr_str.format("'<'")
            elif new_op_idx == 4:
                self.repr_str2 = self.repr_str.format("'>='")
            elif new_op_idx == 5:
                self.repr_str2 = self.repr_str.format("'>'")
            elif new_op_idx == 6:
                self.repr_str2 = self.repr_str.format("'and'")
            elif new_op_idx == 7:
                self.repr_str2 = self.repr_str.format("'or'")
            elif new_op_idx == 8:
                self.repr_str2 = "[ True ]"
            elif new_op_idx == 9:
                self.repr_str2 = "[ False ]"

    def __bool__(self):
        raise Exception("adBools are tracing objects. Their boolean value is determined later.")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.repr_str2


cpdef adFloat _pos_ad(adFloat u):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cyPos()
    v.t = u.t
    
    return v    

cpdef adFloat _sum_ad_ad(adFloat u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cySum(w.ptr)
    v.t = u.t
    
    return v

cpdef adFloat _sum_ad_d(adFloat u, double w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cyIncr(w)
    v.t = u.t
    
    return v

cpdef adFloat _sum_d_ad(double u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = cyRIncr(u, w.ptr)
    v.t = w.t
    
    return v


cpdef adFloat _neg_ad(adFloat u):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cyNeg()
    v.t = u.t
    
    return v 

cpdef adFloat _sub_ad_ad(adFloat u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cySub(w.ptr)
    v.t = u.t
    
    return v

cpdef adFloat _sub_ad_d(adFloat u, double w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cyDecr(w)
    v.t = u.t
    
    return v

cpdef adFloat _sub_d_ad(double u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = cyRDecr(u, w.ptr)
    v.t = w.t
    
    return v


cpdef adFloat _mul_ad_ad(adFloat u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cyMul(w.ptr)
    v.t = u.t
    
    return v

cpdef adFloat _mul_ad_d(adFloat u, double w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cyMul(w)
    v.t = u.t
    
    return v

cpdef adFloat _mul_d_ad(double u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = cyRMul(u, w.ptr)
    v.t = w.t
    
    return v


cpdef adFloat _div_ad_ad(adFloat u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cyDiv(w.ptr)
    v.t = u.t
    
    return v

cpdef adFloat _div_ad_d(adFloat u, double w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cyDiv(w)
    v.t = u.t
    
    return v

cpdef adFloat _div_d_ad(double u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = cyRDiv(u, w.ptr)
    v.t = w.t
    
    return v

cpdef adFloat _inv_ad(adFloat u):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = u.ptr.cyInv()
    v.t = u.t
    
    return v


cpdef adFloat _sin_ad(adFloat u):
    cdef:
        adFloat v
         
    v = adFloat()
    v.ptr = cySin(u.ptr)
    v.t = u.t
    
    return v

cpdef adFloat _cos_ad(adFloat u):
    cdef:
        adFloat v
         
    v = adFloat()
    v.ptr = cyCos(u.ptr)
    v.t = u.t
    
    return v


cpdef adFloat _exp_ad(adFloat u):
    cdef:
        adFloat v
         
    v = adFloat()
    v.ptr = cyExp(u.ptr)
    v.t = u.t
    
    return v

cpdef adFloat _log_ad(adFloat u):
    cdef:
        adFloat v
         
    v = adFloat()
    v.ptr = cyLog(u.ptr)
    v.t = u.t
    
    return v


cpdef adFloat _atan_ad(adFloat u):
    cdef:
        adFloat v
         
    v = adFloat()
    v.ptr = cyAtan(u.ptr)
    v.t = u.t
    
    return v


cpdef adFloat _signSquare_ad(adFloat u):
    cdef:
        adFloat v
         
    v = adFloat()
    v.ptr = cySignSquare(u.ptr)
    v.t = u.t
    
    return v


cpdef adFloat _pow_ad_ad(adFloat u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = cyPow(u.ptr, w.ptr) #u.ptr.cyPow(w.ptr)
    v.t = u.t
    
    return v

cpdef adFloat _pow_ad_d(adFloat u, double w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = cyPow(u.ptr, w) #u.ptr.cyPow(w)
    v.t = u.t
    
    return v

cpdef adFloat _pow_ad_int(adFloat u, int w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = cyPow(u.ptr, w) #u.ptr.cyPow(w)
    v.t = u.t
    
    return v

cpdef adFloat _pow_d_ad(double u, adFloat w):
    cdef:
        adFloat v
        
    v = adFloat()
    v.ptr = cyRPow(u, w.ptr) #w.ptr.cyRPow(u)
    v.t = w.t
    
    return v


cpdef adFloat _abs_ad(adFloat u):
    cdef:
        adFloat v
         
    v = adFloat()
    v.ptr = cyAbs(u.ptr) #u.ptr.cyAbs()
    v.t = u.t
    
    return v

cpdef adFloat _abs2_ad(adFloat u):
    cdef:
        adFloat v
         
    v = adFloat()
    v.ptr = cyAbs2(u.ptr)
    v.t = u.t
    
    return v


cpdef adBool _bool_ad_ad(int op_idx, adFloat u, adFloat w):
    cdef:
        adBool v

    v = adBool(argLeft = u, argRight = w)

    if op_idx == 0: # "=="
        v.ptr = (u.ptr.cyEq(w.ptr))
        v.op_idx = 0
    elif op_idx == 1: # "!="
        v.ptr = (u.ptr.cyNe(w.ptr))
        v.op_idx = 1
    elif op_idx == 2: # "<="
        v.ptr = (u.ptr.cyLq(w.ptr))
        v.op_idx = 2
    elif op_idx == 3: # "<"
        v.ptr = (u.ptr.cyLt(w.ptr))
        v.op_idx = 3
    elif op_idx == 4: # ">="
        v.ptr = (u.ptr.cyGq(w.ptr))
        v.op_idx = 4
    elif op_idx == 5: # ">"
        v.ptr = (u.ptr.cyGt(w.ptr))
        v.op_idx = 5
    else:
        raise Exception("logic operation unknown!")

    return v

cpdef adBool _bool_ad_d(int op_idx, adFloat u, double w):
    cdef:
        adBool v

    v = adBool(argLeft = u, argRight = w)

    if op_idx == 0: # "=="
        v.ptr = (u.ptr.cyEq(w))
        v.op_idx = 0
    elif op_idx == 1: # "!="
        v.ptr = (u.ptr.cyNe(w))
        v.op_idx = 1
    elif op_idx == 2: # "<="
        v.ptr = (u.ptr.cyLq(w))
        v.op_idx = 2
    elif op_idx == 3: # "<"
        v.ptr = (u.ptr.cyLt(w))
        v.op_idx = 3
    elif op_idx == 4: # ">="
        v.ptr = (u.ptr.cyGq(w))
        v.op_idx = 4
    elif op_idx == 5: # ">"
        v.ptr = (u.ptr.cyGt(w))
        v.op_idx = 5
    else:
        raise Exception("logic operation unknown!")

    return v

cpdef adBool _bool_d_ad(int op_idx, double u, adFloat w):
    cdef:
        adBool v

    v = adBool(argLeft = u, argRight = w)

    if op_idx == 0: # "=="
        v.ptr = cyREq(u, w.ptr)
        v.op_idx = 0
    elif op_idx == 1: # "!="
        v.ptr = cyRNe(u, w.ptr)
        v.op_idx = 1
    elif op_idx == 2: # "<="
        v.ptr = cyRLq(u, w.ptr)
        v.op_idx = 2
    elif op_idx == 3: # "<"
        v.ptr = cyRLt(u, w.ptr)
        v.op_idx = 3
    elif op_idx == 4: # ">="
        v.ptr = cyRGq(u, w.ptr)
        v.op_idx = 4
    elif op_idx == 5: # ">"
        v.ptr = cyRGt(u, w.ptr)
        v.op_idx = 5
    else:
        raise Exception("logic operation unknown!")

    return v

cpdef adBool _and_ab_ab(adBool u, adBool w):
    cdef:
        adBool v

    v = adBool(argLeft = u, argRight = w)
    v.ptr = cyLogical_and(u.ptr, w.ptr)
    v.op_idx = 6

    return v

cpdef adBool _and_ab_b(adBool u, bool_cpp w):
    cdef:
        adBool v

    v = adBool(argLeft = u, argRight = w)
    v.ptr = cyLogical_and(u.ptr, w)
    v.op_idx = 6

    return v

cpdef adBool _and_b_ab(bool_cpp u, adBool w):
    cdef:
        adBool v

    v = adBool(argLeft = u, argRight = w)
    v.ptr = cyLogical_and(u, w.ptr)
    v.op_idx = 6

    return v

cpdef adBool _or_ab_ab(adBool u, adBool w):
    cdef:
        adBool v

    v = adBool(argLeft = u, argRight = w)
    v.ptr = cyLogical_or(u.ptr, w.ptr)
    v.op_idx = 7

    return v

cpdef adBool _or_ab_b(adBool u, bool_cpp w):
    cdef:
        adBool v

    v = adBool(argLeft = u, argRight = w)
    v.ptr = cyLogical_or(u.ptr, w)
    v.op_idx = 7

    return v

cpdef adBool _or_b_ab(bool_cpp u, adBool w):
    cdef:
        adBool v

    v = adBool(argLeft = u, argRight = w)
    v.ptr = cyLogical_or(u, w.ptr)
    v.op_idx = 7

    return v


cpdef adFloat _cond_assign_ab_ad_ad(adBool b, adFloat u, adFloat w):
    cdef:
        adFloat v

    v = adFloat()
    v.ptr = cyCondAssign(b.ptr, u.ptr, w.ptr)
    v.t = u.t

    return v

cpdef adFloat _cond_assign_ab_ad_d(adBool b, adFloat u, double w):
    cdef:
        adFloat v

    v = adFloat()
    v.ptr = cyCondAssign(b.ptr, u.ptr, w)
    v.t = u.t

    return v

cpdef adFloat _cond_assign_ab_d_ad(adBool b, double u, adFloat w):
    cdef:
        adFloat v

    v = adFloat()
    v.ptr = cyCondAssign(b.ptr, u, w.ptr)
    v.t = u.t

    return v

cpdef adFloat _cond_assign_b_ad_ad(bool_cpp b, adFloat u, adFloat w):
    cdef:
        adFloat v

    v = adFloat()
    v.ptr = cyCondAssign(b, u.ptr, w.ptr)
    v.t = u.t

    return v

cpdef adFloat _cond_assign_b_ad_d(bool_cpp b, adFloat u, double w):
    cdef:
        adFloat v

    v = adFloat()
    v.ptr = cyCondAssign(b, u.ptr, w)
    v.t = u.t

    return v

cpdef adFloat _cond_assign_b_d_ad(bool_cpp b, double u, adFloat w):
    cdef:
        adFloat v

    v = adFloat()
    v.ptr = cyCondAssign(b, u, w.ptr)
    v.t = u.t

    return v


cpdef adFloat _adFloat_from_tape(tape in_tape, const size_t &idx):
    cdef:
        adFloat v

    v = adFloat()
    v.ptr = adouble(in_tape.t, idx, True)
    v.t = in_tape

    return v

cpdef list _adFloat_precs_from_adFloat(tape in_tape, adFloat arg):
    cdef:
        vector[ElemOp*] precs

    out = []
    precs = arg.ptr.depends_on()

    for elemOperation in precs:
        out.append(_adFloat_from_tape(in_tape, elemOperation.id))

    return out

cpdef list _adFloat_succs_from_adFloat(tape in_tape, adFloat arg):
    cdef:
        vector[ElemOp*] succs

    out = []
    succs = arg.ptr.dependency_of()

    for elemOperation in succs:
        out.append(_adFloat_from_tape(in_tape, elemOperation.id))

    return out


def check_adFloat(u):
    if isinstance(u, np.ndarray):
        if len(u.shape) == 0:
            u = u[tuple()]
        elif (len(u.shape) == 1) and (u.shape[0] == 1):
            u = u[0]
        else:
            raise Exception("arg should not be an array!")

    if isinstance(u, adBool):
        raise Exception("arg cannot be adBool here!")

    uIsAD = isinstance(u, adFloat)

    return u, uIsAD


def check_adBool(u):
    if isinstance(u, np.ndarray):
        if len(u.shape) == 0:
            u = u[tuple()]
        elif (len(u.shape) == 1) and (u.shape[0] == 1):
            u = u[0]
        else:
            raise Exception("arg should not be an array!")

    if isinstance(u, adFloat):
        raise Exception("arg cannot be adFloat here!")

    uIsAB = isinstance(u, adBool)

    return u, uIsAB


def adFloat_array(in_tape, shape, scalar_or_bool_set = None):
    if len(shape) == 0: return None
    length = 1
    for s_i in shape: length *= s_i
    if length == 0: return None

    out = np.array([adFloat(in_tape, scalar_or_bool_set) for _ in range(length)])

    return out.reshape(shape)


cdef class adFloat:

    cdef:
        adouble ptr
        tape    t
    
    property set_idx:
        def __get__(self): return self.t.set_idx
        
    def __cinit__(self, tape in_tape = None, scalar_or_bool_set = None, ID = None):
        cdef:
            vector[bool_cpp] boolList
            vector[long int] preSetIDs
            double           in_c
            
        if isinstance(ID, (list, tuple, np.ndarray)):
            for idx in ID: preSetIDs.push_back(idx)
        elif ID is None: pass
        else:
            for _ in range(in_tape.num_of_scopes): preSetIDs.push_back(ID)
        
        if not (in_tape is None):
            if scalar_or_bool_set is None:
                for i in range(in_tape.num_of_scopes): boolList.push_back(True)
                if ID is None: self.ptr = adouble(in_tape.t, boolList)
                else: self.ptr = adouble(in_tape.t, boolList, preSetIDs)
            else:
                if isinstance(scalar_or_bool_set, (list, tuple, np.ndarray)):
#                     boolList = scalar_or_bool_set
                    for boolEntry in scalar_or_bool_set: boolList.push_back(boolEntry)
                    if ID is None: self.ptr = adouble(in_tape.t, boolList)
                    else: self.ptr = adouble(in_tape.t, boolList, preSetIDs)
                else:
                    in_c = scalar_or_bool_set
                    self.ptr = adouble(in_tape.t, in_c)
            self.t = in_tape

    property depends_on:
        def __get__(self): return _adFloat_precs_from_adFloat(self.t, self)

    property dependency_of:
        def __get__(self): return _adFloat_succs_from_adFloat(self.t, self)
                
    property idx:
        def __get__(self): return self.ptr.get_id()
         
    property var_idx:
        def __get__(self):
            if (self.ptr.is_active(self.set_idx) and self.ptr.is_root()) or self.ptr.is_active_abs(self.set_idx):
                return self.variables[0]
            return None                 
    
    def __pos__(u):
        u, _ = check_adFloat(u)
        return _pos_ad(u)
            
    def __add__(u, w):
#        uIsAD = isinstance(u, adFloat)
#        wIsAD = isinstance(w, adFloat)
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)

        if uIsAD and wIsAD: return _sum_ad_ad(u, w)
        elif uIsAD: return _sum_ad_d(u, w)
        return _sum_d_ad(u, w) # strange bug: cython should use __radd__ if uIsAD is False, but it doesn't
    
    def __neg__(u):
        u, _ = check_adFloat(u)
        return _neg_ad(u)
            
    def __sub__(u, w):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)
        
        if uIsAD and wIsAD: return _sub_ad_ad(u, w)
        elif uIsAD: return _sub_ad_d(u, w)
        return _sub_d_ad(u, w) # strange bug: cython should use __rsub__ if uIsAD is False, but it doesn't
            
    def __mul__(u, w):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)
        
        if uIsAD and wIsAD: return _mul_ad_ad(u, w)
        elif uIsAD: return _mul_ad_d(u, w)
        return _mul_d_ad(u, w) # strange bug: cython should use __rmul__ if uIsAD is False, but it doesn't
            
    def __truediv__(u, w):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)
        
        if uIsAD and wIsAD: return _div_ad_ad(u, w)
        elif uIsAD: return _div_ad_d(u, w)
        return _div_d_ad(u, w) # strange bug: cython should use __rdiv__ if uIsAD is False, but it doesn't
    
#    def __div__(u, w): # python 2 compatibility
#        return u.__truediv__(w)
    
    def __pow__(u, w, out):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)
        
        if uIsAD and wIsAD: return _pow_ad_ad(u, w)
        elif uIsAD:
            if w % 1 == 0: #np.issubdtype(w.__class__, np.integer):
                return _pow_ad_int(u, int(w))
            return _pow_ad_d(u, w)
        return _pow_d_ad(u, w) # strange bug: cython should use __rpow__ if uIsAD is False, but it doesn't
    
    def __abs__(u):
        u, uIsAD = check_adFloat(u)

        if u.t.ignore_kinks: return _abs2_ad(u)
        return _abs_ad(u)

    def inv(self): return inv(self)

    def sin(self): return sin(self)

    def cos(self): return cos(self)

    def arctan(self): return atan(self)

    def atan(self): return atan(self)

    def exp(self): return exp(self)

    def log(self): return log(self)

    def ln(self): return log(self)

    def signSquare(self): return signSquare(self)

    def max(self, other): return max(self, other)

    def min(self, other): return min(self, other)

    def __bool__(self): raise Exception("adFloats are tracing objects. Their boolean value is determined later.")

    def __eq__(u, w):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)

        if uIsAD and wIsAD: return _bool_ad_ad(0, u, w)
        elif uIsAD: return _bool_ad_d(0, u, w)
        return _bool_d_ad(0, u, w)

    def __ne__(u, w):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)

        if uIsAD and wIsAD: return _bool_ad_ad(1, u, w)
        elif uIsAD: return _bool_ad_d(1, u, w)
        return _bool_d_ad(1, u, w)

    def __le__(u, w):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)

        if uIsAD and wIsAD: return _bool_ad_ad(2, u, w)
        elif uIsAD: return _bool_ad_d(2, u, w)
        return _bool_d_ad(2, u, w)

    def __lt__(u, w):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)

        if uIsAD and wIsAD: return _bool_ad_ad(3, u, w)
        elif uIsAD: return _bool_ad_d(3, u, w)
        return _bool_d_ad(3, u, w)

    def __ge__(u, w):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)

        if uIsAD and wIsAD: return _bool_ad_ad(4, u, w)
        elif uIsAD: return _bool_ad_d(4, u, w)
        return _bool_d_ad(4, u, w)

    def __gt__(u, w):
        u, uIsAD = check_adFloat(u)
        w, wIsAD = check_adFloat(w)

        if uIsAD and wIsAD: return _bool_ad_ad(5, u, w)
        elif uIsAD: return _bool_ad_d(5, u, w)
        return _bool_d_ad(5, u, w)
    
    property t:
        def __get__(self): return self.t
    
    property tape:
        def __get__(self): return self.t

    property val:
        def __get__(self): return self.ptr.get_val()
        def __set__(self, double in_val): self.ptr.set_val(in_val)
        
    property mid:
        def __get__(self): return self.ptr.get_mid()
        def __set__(self, double in_mid): self.ptr.set_mid(in_mid)
        
    property rad:
        def __get__(self): return self.ptr.get_rad()
        def __set__(self, double in_rad): self.ptr.set_rad(in_rad)
            
    property const:
        def __get__(self):
            if self.ptr.is_const(): return self.val
            return None
        def __set__(self, in_c):
            if self.ptr.is_const():
                self.val = in_c
                self.mid = in_c
                self.rad = 0.0
    
    property dependent:
        def __get__(self): return self.ptr.is_dependent()
        def __set__(self, bool_cpp state): self.ptr.set_dependent_status(state)
    
    property grad_len:
        def __get__(self): return self.ptr.get_grad_len(self.set_idx)
    
    property grad:    
        def __get__(self):
            cdef:
                double *grad_ptr
                np.npy_intp shape[1]
                
            grad_ptr = self.ptr.get_grad_ptr(self.set_idx)
            shape[0] = self.grad_len
            
            ndarray = np.PyArray_SimpleNewFromData(1, shape, np.NPY_FLOAT64, grad_ptr)
            
            return np.array(ndarray, copy = False)

    property data:
        def __get__(self): return self.grad
    
    property variables:
        def __get__(self):
            cdef:
                long int *vars_ptr
                np.npy_intp shape[1]
                
            vars_ptr = self.ptr.get_vars_ptr(self.set_idx)
            shape[0] = self.ptr.get_vars_len(self.set_idx)
            ndarray = np.PyArray_SimpleNewFromData(1, shape, np.NPY_LONG, vars_ptr) #np.NPY_INT64
            
            return np.array(ndarray, copy = False)

    property indices:
        def __get__(self): return self.variables

    property identifier:
        def __get__(self): return [self.ptr.get_identifier(), self.ptr.get_subidentifier()]

    property operation_type:
        def __get__(self):
            idx, subidx = self.identifier

            unaries = ["pos", "neg",  "add", "radd",  "sub", "rsub",  "mul", "rmul",  "truediv", "rtruediv",
                       "sin", "cos", "exp", "log", "atan", "signPow2"]
            binaries = ["add", "sub", "mul", "truediv", "cond"]

            if idx == -1: return "var/param"
            if idx == -2: return "const"

            if idx == 1:
                if (subidx == -1) or (subidx == -2): return "u-abs"
                return "u-{}".format(unaries[subidx-1])

            if idx == 2: return "b-{}".format(binaries[subidx-1])

            return None

    def __str__(self):
        out = "adFloat <{}".format(self.operation_type)
        identifier = self.identifier[0]

        if identifier == -2: return out + " with value: {}>".format(self.val)
        elif identifier == 1: out += "> depends on ({})".format(self.depends_on[0].idx)
        elif identifier == 2:
            dep = self.depends_on
            out += "> depends on ({}, {})".format(dep[0].idx, dep[1].idx)
        else: out += ">"

        return out

    def __repr__(self):
        out = "<{}".format(self.operation_type)
        identifier = self.identifier[0]

        if identifier == -2: return out + ": {}>".format(self.val)
        elif identifier == 1: out += ">({})".format(self.depends_on[0].idx)
        elif identifier == 2:
            dep = self.depends_on
            out += ">({}, {})".format(dep[0].idx, dep[1].idx)
        else: out += ">"

        return out


def inv(u):
    u, uIsAD = check_adFloat(u)

    if uIsAD: return _inv_ad(u)
    return 1.0/u 


def sin(u):
    u, uIsAD = check_adFloat(u)

    if uIsAD: return _sin_ad(u)
    return mathSin(u)    
    
def cos(u):
    u, uIsAD = check_adFloat(u)

    if uIsAD: return _cos_ad(u)
    return mathCos(u)

def atan(u):
    u, uIsAD = check_adFloat(u)

    if uIsAD: return _atan_ad(u)
    return mathAtan(u)

def arctan(u):
    return atan(u)


def exp(u):
    u, uIsAD = check_adFloat(u)

    if uIsAD: return _exp_ad(u)
    return mathExp(u)
    
def log(u):
    u, uIsAD = check_adFloat(u)

    if uIsAD: return _log_ad(u)
    return mathLog(u)

def ln(u): return log(u)


def signSquare(u):
    u, uIsAD = check_adFloat(u)

    if uIsAD: return _signSquare_ad(u)
    return abs(u)*u


def cy_max_min_2(u, w):
    left = (u + w)/2.0
    right = abs(u - w)/2.0
    return left + right, left - right

def cy_max_2(u, w): return (u + w + abs(u - w))/2.0

def cy_min_2(u, w): return (u + w - abs(u - w))/2.0

def cy_max(*args):
    if len(args) == 0: return None
    if len(args) == 1: return args[0]
    if len(args) == 2: return cy_max_2(*args)
    if (len(args) % 2) == 0: return cy_max(*[cy_max_2(args[2*i], args[2*i + 1]) for i in range(len(args)//2)])
    return cy_max_2(args[0], cy_max(*args[1:]))

def cy_min(*args):
    if len(args) == 0: return None
    if len(args) == 1: return args[0]
    if len(args) == 2: return cy_min_2(*args)
    if (len(args) % 2) == 0: return cy_min(*[cy_min_2(args[2*i], args[2*i + 1]) for i in range(len(args)//2)])
    return cy_min_2(args[0], cy_min(*args[1:]))

# def max_min(u, w): return cy_max_min_2(u, w) # being in conflict with python's hardcoded keywords 'max' & 'min' this function is deprecated!

def cy_maximum(*args): return cy_max(*args) # alias

def cy_minimum(*args): return cy_min(*args) # alias

def maximum(*args): return cy_max(*args) # alias

def minimum(*args): return cy_min(*args) # alias

# def max(*args): # being in conflict with python's hardcoded keyword 'max' this function is deprecated!
#     return cy_max(*args)

# def min(*args): # being in conflict with python's hardcoded keyword 'min' this function is deprecated!
#     return cy_min(*args)


def abs2(u):
    u, uIsAD = check_adFloat(u)

    if uIsAD:
        return _abs2_ad(u)
    return abs(u)


def cond_assign(b, u, w, adBool_only = False):
    b, bIsAB = check_adBool(b)
    u, uIsAD = check_adFloat(u)
    w, wIsAD = check_adFloat(w)

    if not bIsAB:
        if adBool_only:
            raise Exception("adBool only mode active, but condition is not of type adBool!")

        if uIsAD:
            if wIsAD:
                return _cond_assign_b_ad_ad(b, u, w)
            else:
                return _cond_assign_b_ad_d(b, u, w)
        elif wIsAD:
            return _cond_assign_b_d_ad(b, u, w)
        else:
            if b:
                return u
            else:
                return w
    if uIsAD:
        if wIsAD:
            return _cond_assign_ab_ad_ad(b, u, w)
        return _cond_assign_ab_ad_d(b, u, w)

    if wIsAD:
        return _cond_assign_ab_d_ad(b, u, w)

    raise Exception("invalid use of cond_assign!")

def logical_and(u, w):
    u, uIsAB = check_adBool(u)
    w, wIsAB = check_adBool(w)

    if uIsAB:
        if wIsAB:
            return _and_ab_ab(u, w)
        return _and_ab_b(u, w)

    if wIsAB:
        return _and_b_ab(u, w)

    if (u and w):
        return True
    return False

def logical_or(u, w):
    u, uIsAB = check_adBool(u)
    w, wIsAB = check_adBool(w)

    if uIsAB:
        if wIsAB:
            return _or_ab_ab(u, w)
        return _or_ab_b(u, w)

    if wIsAB:
        return _or_b_ab(u, w)

    if (u or w):
        return True
    return False

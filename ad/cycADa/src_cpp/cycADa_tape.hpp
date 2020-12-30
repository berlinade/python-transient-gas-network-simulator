/*
 * part of the 1st hearth-piece of cycADa: the header for its tape structure
 *
 * __author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
 * __credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
 *                'Oliver Kunst', 'Lutz Lehmann',
 *                'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames
 */


#ifndef tape_h
#define tape_h tape_h

#include "cycADa_elemOp.hpp"

// #include <vector>
// #include <cmath>
// #include <numeric>
// #include <boost/math/special_functions/sinc.hpp>
// #include <boost/math/special_functions/sinhc.hpp>
// #include <boost/math/special_functions/atanh.hpp>

// makeshift definition of atanhc
// #include "atanhc.hpp"



namespace core{

    // vector of elementary operations
    class Tape{

    public:

        size_t elem_id;
        vector<long int> var_id_sets; // needs signs
        vector<ElemOp*> op_tape, tape_roots, tape_depends; //, abs_ops // when uncommenting this -> it may need to be instantiated w.r.t. var_id_sets
        vector<vector<ElemOp*>> tape_var_sets, tape_swVar_sets, tape_abs_sets;

        Tape(size_t num_of_sets);

        void add_op(ElemOp *v);

        void incr_var_id(size_t set_idx);
        long int read_var_id(size_t set_idx);
        void set_var_id(size_t set_idx, long int new_var_id);

        size_t get_num_of_sets();
        size_t get_num_of_vars_and_params();

        size_t get_n(size_t set_idx);
        size_t get_s(size_t set_idx);
        size_t get_m();
        size_t get_len();

        long int get_id_of_var(size_t set_idx, size_t pos);
        long int get_id_of_swVar(size_t set_idx, size_t pos);
        long int get_id_of_depend(size_t pos);

        void assign_val(vector<double> in_val);
        void zero_order_evaluation();

        void assign_mid_rad(vector<double> in_mid, vector<double> in_rad);
        void first_order_evaluation();
        void sparse_grad(size_t set_idx);

        void assign_fwd_incr(size_t set_idx, vector<double> in_incr);
        void fwd(size_t set_idx);

        void assign_bar(size_t set_idx, vector<double> in_bar);
        void rev(size_t set_idx);


        size_t get_grad_size_inters(size_t set_idx);
        void set_grad_inters(size_t set_idx, double *in_grad_ptr);

        size_t get_grad_size_swVars(size_t set_idx);
        void set_grad_swVars(size_t set_idx, double *in_grad_ptr);

        size_t get_grad_size_depends(size_t set_idx);
        void set_grad_depends(size_t set_idx, double *in_grad_ptr);


        size_t get_fwd_vec_size_inters(size_t set_idx);
        void set_fwd_vec_inters(size_t set_idx, double *in_fwd_vec_ptr);

        size_t get_fwd_vec_size_swVars_and_depends(size_t set_idx);
        void set_fwd_vec_swVars_and_depends(size_t set_idx, double *in_fwd_vec_ptr);


        size_t get_rev_vec_size_inters(size_t set_idx);
        void set_rev_vec_inters(size_t set_idx, double *in_bar_vec_ptr);

        size_t get_rev_vec_size_roots_and_swVars(size_t set_idx);
        void set_rev_vec_roots_and_swVars(size_t set_idx, double *in_bar_vec_ptr);


        ~Tape();
    };
}

#endif























































































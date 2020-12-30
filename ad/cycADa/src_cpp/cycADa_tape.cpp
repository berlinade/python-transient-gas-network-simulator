/*
 * part of the 1st hearth-piece of cycADa: the implementation of its tape structure
 *
 * __author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
 * __credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
 *                'Oliver Kunst', 'Lutz Lehmann',
 *                'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames
 */


#include "cycADa_tape.hpp"

// #include <vector>
// #include <cmath>
// #include <numeric>
// #include <boost/math/special_functions/sinc.hpp>
// #include <boost/math/special_functions/sinhc.hpp>
// #include <boost/math/special_functions/atanh.hpp>

// makeshift definition of atanhc
// #include "atanhc.hpp"



namespace core{

    Tape::Tape(size_t num_of_sets){
        elem_id = 0;
        var_id_sets.resize(num_of_sets, 0.0);
        tape_var_sets.resize(num_of_sets);
        tape_swVar_sets.resize(num_of_sets);
        tape_abs_sets.resize(num_of_sets);
    }

    void Tape::add_op(ElemOp *v){
        op_tape.push_back(v);
        v->id = elem_id;
        ++elem_id;
    }

    void Tape::incr_var_id(size_t set_idx){
        ++var_id_sets[set_idx];
    }

    long int Tape::read_var_id(size_t set_idx){
        return var_id_sets[set_idx];
    }

    void Tape::set_var_id(size_t set_idx, long int new_var_id){
        var_id_sets[set_idx] = new_var_id;
    }

    size_t Tape::get_num_of_sets(){
        return tape_var_sets.size();
    }

    size_t Tape::get_num_of_vars_and_params(){
        return tape_roots.size();
    }

    size_t Tape::get_n(size_t set_idx){
        return tape_var_sets[set_idx].size();
    }

    size_t Tape::get_s(size_t set_idx){
        return tape_swVar_sets[set_idx].size();
    }

    size_t Tape::get_m(){
        return tape_depends.size();
    }

    size_t Tape::get_len(){
        return op_tape.size();
    }

    long int Tape::get_id_of_var(size_t set_idx, size_t pos){
        return tape_var_sets[set_idx][pos]->id;
    }

    long int Tape::get_id_of_swVar(size_t set_idx, size_t pos){
        return tape_swVar_sets[set_idx][pos]->id;
    }

    long int Tape::get_id_of_depend(size_t pos){
        return tape_depends[pos]->id;
    }

    void Tape::assign_val(vector<double> in_val){
        for(size_t i = 0; i < tape_roots.size(); i++){
            tape_roots[i]->val = in_val[i];
        }
    }

    void Tape::zero_order_evaluation(){
        for(auto const& v: op_tape){
            v->zero_order_evaluation();
        }
    }

    void Tape::assign_mid_rad(vector<double> in_mid, vector<double> in_rad){
        for(size_t i = 0; i < tape_roots.size(); i++){
            tape_roots[i]->mid = in_mid[i];
            tape_roots[i]->rad = in_rad[i];
        }
    }

    void Tape::first_order_evaluation(){
        for(auto const& v: op_tape){
            v->first_order_evaluation();
        }
    }

    void Tape::sparse_grad(size_t set_idx){
        for(auto const& v: op_tape){
            v->sparse_grad(set_idx);
        }
    }

    void Tape::assign_fwd_incr(size_t set_idx, vector<double> in_incr){
        int idx = 0;

        for(size_t i = 0; i < tape_roots.size(); i++){
            if(tape_roots[i]->is_active(set_idx)){
                tape_roots[i]->fwd_ptr_sets[set_idx][0] = in_incr[idx];
                idx++;
            }else{
                tape_roots[i]->fwd_ptr_sets[set_idx][0] = 0.0;
            }
        }
        for(size_t i = 0; i < tape_abs_sets[set_idx].size(); i++){
            tape_abs_sets[set_idx][i]->fwd_ptr_sets[set_idx][0] = in_incr[idx];
            idx++;
        }
        // for(size_t i = 0; i < tape_swVar_sets[set_idx].size(); i++){ // old piece of code: but wrong because z might have more mappings than just |z|
        //     tape_swVar_sets[set_idx][i]->succs[0]->fwd_ptr_sets[set_idx][0] = in_incr[idx]; // old piece of code: but wrong because z might have more mappings than just |z|
        //     idx++;
        // }
    }

    void Tape::assign_bar(size_t set_idx, vector<double> in_bar){
        for(auto const& v: op_tape){
            v->bar_ptr_sets[set_idx][0] = 0.0; //necessary for reverse mode because of incremental updates
        }

        int idx = 0;
        for(size_t i = 0; i < tape_swVar_sets[set_idx].size(); i++){
            tape_swVar_sets[set_idx][i]->bar_ptr_sets[set_idx][0] = in_bar[idx];
            idx++;
        }
        for(size_t i = 0; i < tape_depends.size(); i++){
            tape_depends[i]->bar_ptr_sets[set_idx][0] = in_bar[idx];
            idx++;
        }
    }

    void Tape::fwd(size_t set_idx){
        for(auto const& v: op_tape){
            v->fwd(set_idx);
        }
    }

    void Tape::rev(size_t set_idx){
        for(size_t i = op_tape.size(); i >= 1; i--){
            op_tape[i-1]->rev(set_idx);
        }
    }

    size_t Tape::get_grad_size_inters(size_t set_idx){ // inters == intermediates
        size_t grad_len_inters = 0, tmp;

        for(auto const& v: op_tape){
            if(v->is_dependent == false && v->is_active_swVar(set_idx) == false){
                tmp = v->var_sets[set_idx].size();
                if(tmp < 1){
                    tmp = 1;
                }
                grad_len_inters += tmp;
//                if(v->is_root || v->is_const){
//                    ++grad_len_inters;
//                } else {
//                    grad_len_inters += max(v->var_sets[set_idx].size(), 1);
//                }
            }
        }

        return grad_len_inters;
    }

    void Tape::set_grad_inters(size_t set_idx, double *in_grad_ptr){
        size_t grad_len_inters = 0, tmp;

        for(auto const& v: op_tape){
            if(v->is_dependent == false && v->is_active_swVar(set_idx) == false){
                v->set_grad_ptr(set_idx, in_grad_ptr + grad_len_inters);

                tmp = v->var_sets[set_idx].size();
                if(tmp < 1){
                    tmp = 1;
                }
                grad_len_inters += tmp;
//                if(v->is_root || v->is_const){
//                    ++grad_len_inters;
//                } else {
//                    grad_len_inters += v->var_sets[set_idx].size();
//                }
            }
        }
    }

    size_t Tape::get_grad_size_swVars(size_t set_idx){
        size_t grad_len_swVars = 0, tmp;

        for(auto const& v: tape_swVar_sets[set_idx]){
            tmp = v->var_sets[set_idx].size();
//            if(tmp < 1){
//                tmp = 1;
//            }
            grad_len_swVars += tmp;
//            if(v->is_root || v->is_const){
//                ++grad_len_swVars;
//            } else {
//                grad_len_swVars += v->var_sets[set_idx].size();
//            }
        }

        return grad_len_swVars;
    }

    void Tape::set_grad_swVars(size_t set_idx, double *in_grad_ptr){
        size_t grad_len_swVars = 0, tmp;

        for(auto const& v: tape_swVar_sets[set_idx]){
            v->set_grad_ptr(set_idx, in_grad_ptr + grad_len_swVars);

            tmp = v->var_sets[set_idx].size();
//            if(tmp < 1){
//                tmp = 1;
//            }
            grad_len_swVars += tmp;
//            if(v->is_root || v->is_const){
//                ++grad_len_swVars;
//            } else {
//                grad_len_swVars += v->var_sets[set_idx].size();
//            }
        }
    }

    size_t Tape::get_grad_size_depends(size_t set_idx){
        size_t grad_len_depends = 0, tmp;
        ElemOp *v;

        for(size_t i = 0; i < tape_depends.size(); i++){
            v = tape_depends[i];

            tmp = v->var_sets[set_idx].size();
//            if(tmp < 1){
//                tmp = 1;
//            }
            grad_len_depends += tmp;

            //grad_len_depends += v->var_sets[set_idx].size();

            // declare as dependent has changed -> dependent cannot be root or const anymore
//            if(v->is_root || v->is_const){
//                ++grad_len_depends;
//            } else {
//                grad_len_depends += v->var_sets[set_idx].size();
//            }
        }

        return grad_len_depends;
    }

    void Tape::set_grad_depends(size_t set_idx, double *in_grad_ptr){
        size_t grad_len_depends = 0, tmp;
        ElemOp *v;

        for(size_t i = 0; i < tape_depends.size(); i++){
            v = tape_depends[i];
            v->set_grad_ptr(set_idx, in_grad_ptr + grad_len_depends);

            tmp = v->var_sets[set_idx].size();
//            if(tmp < 1){
//                tmp = 1;
//            }
            grad_len_depends += tmp;
//            if(v->is_root || v->is_const){
//                ++grad_len_depends;
//            } else {
//                grad_len_depends += v->var_sets[set_idx].size();
//            }
        }
    }

    size_t Tape::get_fwd_vec_size_inters(size_t set_idx){
        size_t fwd_vec_len_inters = 0;

        for(auto const& v: op_tape){
            if(v->is_dependent == false && v->is_active_swVar(set_idx) == false){
                ++fwd_vec_len_inters;
            }
        }

        return fwd_vec_len_inters;
    }

    void Tape::set_fwd_vec_inters(size_t set_idx, double *in_fwd_vec_ptr){
        size_t fwd_vec_len_inters = 0;

        for(auto const& v: op_tape){
            if(v->is_dependent == false && v->is_active_swVar(set_idx) == false){
                v->set_fwd_ptr(set_idx, in_fwd_vec_ptr + fwd_vec_len_inters);

                ++fwd_vec_len_inters;
            }
        }
    }

    size_t Tape::get_fwd_vec_size_swVars_and_depends(size_t set_idx){
        size_t fwd_vec_len_swVars_and_depends = 0;

        for(size_t i = 0; i < tape_swVar_sets[set_idx].size(); i++){
            ++fwd_vec_len_swVars_and_depends;
        }
        for(size_t i = 0; i < tape_depends.size(); i++){
            ++fwd_vec_len_swVars_and_depends;
        }

        return fwd_vec_len_swVars_and_depends;
    }

    void Tape::set_fwd_vec_swVars_and_depends(size_t set_idx, double *in_fwd_vec_ptr){
        size_t fwd_vec_len_swVars_and_depends = 0;

        for(auto const& v: tape_swVar_sets[set_idx]){
            v->set_fwd_ptr(set_idx, in_fwd_vec_ptr + fwd_vec_len_swVars_and_depends);

            ++fwd_vec_len_swVars_and_depends;
        }
        for(auto const& v: tape_depends){
            v->set_fwd_ptr(set_idx, in_fwd_vec_ptr + fwd_vec_len_swVars_and_depends);

            ++fwd_vec_len_swVars_and_depends;
        }
    }

    size_t Tape::get_rev_vec_size_inters(size_t set_idx){
        size_t bar_vec_len_inters = 0;

        for(auto const& v: op_tape){
            if(not((v->is_abs_node || v->is_root) && v->is_active(set_idx))){
                ++bar_vec_len_inters;
            }
        }

        return bar_vec_len_inters;
    }

    void Tape::set_rev_vec_inters(size_t set_idx, double *in_bar_vec_ptr){
        size_t bar_vec_len_inters = 0;

        for(auto const& v: op_tape){
            if(not((v->is_abs_node || v->is_root) && v->is_active(set_idx))){
                v->set_bar_ptr(set_idx, in_bar_vec_ptr + bar_vec_len_inters);

                ++bar_vec_len_inters;
            }
        }
    }

    size_t Tape::get_rev_vec_size_roots_and_swVars(size_t set_idx){
        size_t bar_vec_len_roots_and_swVars = 0;

        for(size_t i = 0; i < tape_var_sets[set_idx].size(); i++){
            ++bar_vec_len_roots_and_swVars;
        }
        for(size_t i = 0; i < tape_abs_sets[set_idx].size(); i++){
            ++bar_vec_len_roots_and_swVars;
        }

        return bar_vec_len_roots_and_swVars;
    }

    void Tape::set_rev_vec_roots_and_swVars(size_t set_idx, double *in_bar_vec_ptr){
        size_t bar_vec_len_roots_and_swVars = 0;

        for(auto const& v: tape_var_sets[set_idx]){
            v->set_bar_ptr(set_idx, in_bar_vec_ptr + bar_vec_len_roots_and_swVars);

            ++bar_vec_len_roots_and_swVars;
        }
        for(auto const& v: tape_abs_sets[set_idx]){
            v->set_bar_ptr(set_idx, in_bar_vec_ptr + bar_vec_len_roots_and_swVars);

            ++bar_vec_len_roots_and_swVars;
        }
    }

    Tape::~Tape(){
        for(size_t i = 0; i<op_tape.size(); i++){
            delete op_tape[i];
        }
    }
}























































































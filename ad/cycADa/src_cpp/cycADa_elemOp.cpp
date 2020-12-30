/*
 * part of the 1st hearth-piece of cycADa: the implementation of the tape elements
 *
 * __author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
 * __credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
 *                'Oliver Kunst', 'Lutz Lehmann',
 *                'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames
 */


#include "cycADa_elemOp.hpp"

// #include <vector>
// #include <cmath>
// #include <numeric>
#include <boost/math/special_functions/sinc.hpp>
#include <boost/math/special_functions/sinhc.hpp>
#include <boost/math/special_functions/atanh.hpp>

// makeshift definition of atanhc
#include "atanhc.hpp"



namespace core{

    using boost::math::sinc_pi;
    using boost::math::sinhc_pi;
    using boost::math::atanh;
    using boost::math::atanhc;


    /* [ABS] [C]o[MP]are
     * -----------------
     *
     *     compares IDs (of type 'long int') of 'ElemOp' instances.
     *
     *     It distinguishes user defined variables ('independent') from
     *     switching Variables ('swVars', which are defined by using abs function calls).
     *
     *     IDs of 'indipendent' are always considered as 'lower' as IDs of swVars
     *     (where the latter are negative: '-').
     */
    bool absCmp(size_t i, size_t j, const vector<long int> &vec){
        long int u = vec[i];
        long int w = vec[j];

        if(u*w < 0){
            if(u < 0){
                return false;
            }
        return true;
        }
        if(u < 0){
            if(u > w){
                return true;
            }
            return false;
        }
        if(u < w){
            return true;
        }
        return false;
    }

    vector<size_t> create_permutation_map(const vector<long int> &vec){
        vector<size_t> p(vec.size());
        iota(p.begin(), p.end(), 0);  // fills p with integers 0, 1, 2, 3, ...
        sort(p.begin(), p.end(), [&](size_t i, size_t j){ return absCmp(i, j, vec); }); // return vec[i] < vec[j]; });
        return p;
    }

    //template <typename T>
    //void apply_permutation_map(const vector<size_t>& p, vector<T>& vec){
    void apply_permutation_map(const vector<size_t>& p, vector<long int>& vec){
        vector<bool> done(vec.size(), false);
        size_t prev_j, j;

        for(size_t i = 0; i < vec.size(); ++i){
            if(done[i]){
                continue;
            }
            prev_j = i;
            j = p[i];
            while(i != j){
                swap(vec[prev_j], vec[j]);
                prev_j = j;
                j = p[j];
                done[prev_j] = true;
            }
            done[i] = true;
        }
    }


    // ElemOp - Klassen mit großen Buchstaben und CamelCase
    bool ElemOp::is_active_swVar(size_t set_idx){
        if(is_swVar_node && var_sets[set_idx].size() > 0){
            return true;
        }
        return false;
    }

    bool ElemOp::is_active(size_t set_idx){
        if(var_sets[set_idx].size() > 0){
            return true;
        }
        return false;
    }

    ElemOp::~ElemOp(){}


    // Operations with constructors
    // ============================
    UnaryOperation::UnaryOperation(){}

    UnaryOperation::UnaryOperation(ElemOp *u){ // constructor - evaluates precs and var_sets
        precs.push_back(u);
        u->succs.push_back(this);

        var_sets = u->var_sets;

        grad_ptr_sets.resize(u->grad_ptr_sets.size());
        fwd_ptr_sets.resize(u->grad_ptr_sets.size());
        bar_ptr_sets.resize(u->grad_ptr_sets.size());
    }

    void UnaryOperation::sparse_grad(size_t set_idx){
        ElemOp *u = precs[0];

        vector<long int> &vars = var_sets[set_idx];
        double *grad_ptr = grad_ptr_sets[set_idx], *u_grad_ptr = u->grad_ptr_sets[set_idx];


        for(size_t j=0; j < vars.size(); j++){
            grad_ptr[j] = cij[0] * u_grad_ptr[j];
        }
    }

    void UnaryOperation::fwd(size_t set_idx){
        ElemOp *u = precs[0];

        double *fwd_ptr = fwd_ptr_sets[set_idx], *u_fwd_ptr = u->fwd_ptr_sets[set_idx];

        fwd_ptr[0] = cij[0]*u_fwd_ptr[0];
    }

    void UnaryOperation::rev(size_t set_idx){
        ElemOp *u = precs[0];
        double *bar_ptr = bar_ptr_sets[set_idx], *u_bar_ptr = u->bar_ptr_sets[set_idx];

        u_bar_ptr[0] += cij[0]*bar_ptr[0];
    }

    void UnaryOperation::set_grad_ptr(size_t set_idx, double *in_grad_ptr){
        fill(in_grad_ptr, in_grad_ptr+var_sets[set_idx].size(), 0.0);
        grad_ptr_sets[set_idx] = in_grad_ptr;
    }

    void UnaryOperation::set_fwd_ptr(size_t set_idx, double *in_fwd_ptr){
        in_fwd_ptr[0] = 0.0;
        fwd_ptr_sets[set_idx] = in_fwd_ptr;
    }

    void UnaryOperation::set_bar_ptr(size_t set_idx, double *in_bar_ptr){
        in_bar_ptr[0] = 0.0;
        bar_ptr_sets[set_idx] = in_bar_ptr;
    }

    int UnaryOperation::identifier(){
        return 1;
    }

    int UnaryOperation::subidentifier(){
        return 0;
    }


    BinaryOperation::BinaryOperation(ElemOp *u, ElemOp *w){ // constructor - evaluates precs, var_sets and map_sets
        size_t pos;
        vector<size_t> permutation;

        map_sets.resize(u->grad_ptr_sets.size());

        // collect meta information from dependencies u (the 1st) and w (the 2nd)
        precs.push_back(u);
        precs.push_back(w);
        u->succs.push_back(this);
        w->succs.push_back(this);

        // evaluate dependency meta
        var_sets = u->var_sets;
        for(size_t set_idx = 0; set_idx < var_sets.size(); set_idx++){
            // set local alias -or- get current instance
            vector<long int> &vars = var_sets[set_idx];
            vector<size_t> &map = map_sets[set_idx];

            // u - 1st or left dependency of v = phi(u, w)
            map.resize(vars.size());
            iota(map.begin(), map.end(), 0); // fills map with integers 0, 1, 2, 3, ...

            // w - 2nd or right dependency of v = phi(u, w)
            for(auto const &x_id: w->var_sets[set_idx]){
                pos = find(vars.begin(), vars.end(), x_id) - vars.begin();
                if(pos >= vars.size()){
                    map.push_back(vars.size());
                    vars.push_back(x_id);
                }else{
                    map.push_back(pos);
                }
            }

            // sort of map by vars
            permutation = create_permutation_map(vars);
            apply_permutation_map(permutation, vars);

            for(size_t i=0; i < map.size(); i++){ // i was unsigned int
                map[i] = find(permutation.begin(), permutation.end(), map[i]) - permutation.begin();
            }
//
//            cout << "map : ";
//            _print_vec(map);
        }

        grad_ptr_sets.resize(u->grad_ptr_sets.size());
        fwd_ptr_sets.resize(u->grad_ptr_sets.size());
        bar_ptr_sets.resize(u->grad_ptr_sets.size());
    }

    void BinaryOperation::sparse_grad(size_t set_idx){
        ElemOp *u = precs[0], *w = precs[1];

        // set local alias -or- get current instance
        vector<long int> &u_vars = u->var_sets[set_idx], &w_vars = w->var_sets[set_idx];
        vector<size_t> &map = map_sets[set_idx];
        double *grad_ptr = grad_ptr_sets[set_idx],
                *u_grad_ptr = u->grad_ptr_sets[set_idx],
                *w_grad_ptr = w->grad_ptr_sets[set_idx];

        // actual grad operations
        size_t j, j2;
        fill(grad_ptr, grad_ptr+var_sets[set_idx].size(), 0.0); // clear grad

        for(j=0; j < u_vars.size(); j++){
            grad_ptr[map[j]] += cij[0] * u_grad_ptr[j];
        }
        for(j2 = 0; j2 < w_vars.size(); j2++){
            grad_ptr[map[j+j2]] += cij[1] * w_grad_ptr[j2];
        }
    }

    void BinaryOperation::fwd(size_t set_idx){
        ElemOp *u = precs[0], *w = precs[1];

        double *fwd_ptr = fwd_ptr_sets[set_idx],
               *u_fwd_ptr = u->fwd_ptr_sets[set_idx],
               *w_fwd_ptr = w->fwd_ptr_sets[set_idx];

        fwd_ptr[0] = cij[0]*u_fwd_ptr[0] + cij[1]*w_fwd_ptr[0];
    }

    void BinaryOperation::rev(size_t set_idx){
        ElemOp *u = precs[0], *w = precs[1];

        double *bar_ptr = bar_ptr_sets[set_idx],
               *u_bar_ptr = u->bar_ptr_sets[set_idx],
               *w_bar_ptr = w->bar_ptr_sets[set_idx];

        u_bar_ptr[0] += cij[0]*bar_ptr[0];
        w_bar_ptr[0] += cij[1]*bar_ptr[0];
    }

    void BinaryOperation::set_grad_ptr(size_t set_idx, double *in_grad_ptr){
        fill(in_grad_ptr, in_grad_ptr+var_sets[set_idx].size(), 0.0);
        grad_ptr_sets[set_idx] = in_grad_ptr;
    }

    void BinaryOperation::set_fwd_ptr(size_t set_idx, double *in_fwd_ptr){
        in_fwd_ptr[0] = 0.0;
        fwd_ptr_sets[set_idx] = in_fwd_ptr;
    }

    void BinaryOperation::set_bar_ptr(size_t set_idx, double *in_bar_ptr){
        in_bar_ptr[0] = 0.0;
        bar_ptr_sets[set_idx] = in_bar_ptr;
    }

    int BinaryOperation::identifier(){
        return 2;
    }

    int BinaryOperation::subidentifier(){
        return 0;
    }


    RootInit::RootInit(size_t num_of_sets){
        // initialize var_sets empty
        var_sets.resize(num_of_sets);
        is_independent.resize(num_of_sets, false);

        is_root = true;
        cij = {1.0};

        grad_ptr_sets.resize(num_of_sets);
        fwd_ptr_sets.resize(num_of_sets);
        bar_ptr_sets.resize(num_of_sets);
    }

    void RootInit::set_var_id(size_t set_idx, long int var_id){
        var_sets[set_idx] = {abs(var_id)};
        is_independent[set_idx] = true;
    }

    void RootInit::zero_order_evaluation(){}

    void RootInit::first_order_evaluation(){}

    void RootInit::sparse_grad(size_t set_idx){}

    void RootInit::fwd(size_t set_idx){}

    void RootInit::rev(size_t set_idx){}

    void RootInit::set_grad_ptr(size_t set_idx, double *in_grad_ptr){
        // preparation
        if(is_independent[set_idx]){
            in_grad_ptr[0] = 1.0;
        } else {
            in_grad_ptr[0] = 0.0;
        }

        grad_ptr_sets[set_idx] = in_grad_ptr;
    }

    void RootInit::set_fwd_ptr(size_t set_idx, double *in_fwd_ptr){
        in_fwd_ptr[0] = 0.0;
        fwd_ptr_sets[set_idx] = in_fwd_ptr;
    }

    void RootInit::set_bar_ptr(size_t set_idx, double *in_bar_ptr){
        in_bar_ptr[0] = 0.0;
        bar_ptr_sets[set_idx] = in_bar_ptr;
    }

    int RootInit::identifier(){
        return -1;
    }

    int RootInit::subidentifier(){
        return 0;
    }


    ConstInit::ConstInit(size_t num_of_sets){
        // initialize var_sets
        var_sets.resize(num_of_sets);

        is_const = true;
        cij = {};

        val = 0.0;
        mid = 0.0; rad = 0.0;

        grad_ptr_sets.resize(num_of_sets);
        fwd_ptr_sets.resize(num_of_sets);
        bar_ptr_sets.resize(num_of_sets);
    }

    ConstInit::ConstInit(size_t num_of_sets, double in_c){
        // initialize var_sets
        var_sets.resize(num_of_sets);

        is_const = true;
        cij = {};

        val = in_c;
        mid = in_c; rad = 0.0;

        grad_ptr_sets.resize(num_of_sets);
        fwd_ptr_sets.resize(num_of_sets);
        bar_ptr_sets.resize(num_of_sets);
    }

    void ConstInit::set_c(double in_c){
        val = in_c;
        mid = in_c; rad = 0.0;
    }

    void ConstInit::zero_order_evaluation(){}

    void ConstInit::first_order_evaluation(){}

    void ConstInit::sparse_grad(size_t set_idx){}

    void ConstInit::fwd(size_t set_idx){}

    void ConstInit::rev(size_t set_idx){}

    void ConstInit::set_grad_ptr(size_t set_idx, double *in_grad_ptr){
        in_grad_ptr[0] = 0.0;
        grad_ptr_sets[set_idx] = in_grad_ptr;
    }

    void ConstInit::set_fwd_ptr(size_t set_idx, double *in_fwd_ptr){
        in_fwd_ptr[0] = 0.0;
        fwd_ptr_sets[set_idx] = in_fwd_ptr;
    }

    void ConstInit::set_bar_ptr(size_t set_idx, double *in_bar_ptr){
        in_bar_ptr[0] = 0.0;
        bar_ptr_sets[set_idx] = in_bar_ptr;
    }

    int ConstInit::identifier(){
        return -2;
    }

    int ConstInit::subidentifier(){
        return 0;
    }


    abs_op::abs_op(ElemOp *u, size_t num_of_sets){
        var_sets.resize(num_of_sets);

        precs.push_back(u);
        u->succs.push_back(this);
        u->is_swVar_node = true;

        for(size_t set_idx = 0; set_idx < u->var_sets.size(); set_idx++){
            var_sets[set_idx] = {};
        }

        is_abs_node = true;
        cij = {1.0};

        grad_ptr_sets.resize(u->grad_ptr_sets.size());
        fwd_ptr_sets.resize(u->grad_ptr_sets.size());
        bar_ptr_sets.resize(u->grad_ptr_sets.size());
    }

    void abs_op::set_var_id(size_t set_idx, long int var_id){
        var_sets[set_idx] = {-abs(var_id)};
    }

    void abs_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = abs(u->val);
    }

    void abs_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        double check_v = abs(u->mid - u->rad), hat_v = abs(u->mid + u->rad);

        mid = 0.5*(hat_v + check_v);
        rad = 0.5*(hat_v - check_v);
    }

    void abs_op::sparse_grad(size_t set_idx){}

    void abs_op::fwd(size_t set_idx){
        // old code to compute increments rather then directional derivatives of G(x, w) from ANF representation
//        ElemOp *u = precs[0];
//
//        double *fwd_ptr = fwd_ptr_sets[set_idx], *u_fwd_ptr = u->fwd_ptr_sets[set_idx];
//
//        fwd_ptr[0] = abs(u->mid + u_fwd_ptr[0]) - mid;
        if(not (precs[0]->is_active_swVar(set_idx))){
            fwd_ptr_sets[set_idx][0] = 0.0;
        }
    }

    void abs_op::rev(size_t set_idx){
        ElemOp *u = precs[0];

        if(!(u->is_active_swVar(set_idx))){
            u->bar_ptr_sets[set_idx][0] = 0.0;
        }
    }

    void abs_op::set_grad_ptr(size_t set_idx, double *in_grad_ptr){
        if(precs[0]->is_active_swVar(set_idx)){
            in_grad_ptr[0] = 1.0;
        }else{
            in_grad_ptr[0] = 0.0;
        }
        grad_ptr_sets[set_idx] = in_grad_ptr;
    }

    void abs_op::set_fwd_ptr(size_t set_idx, double *in_fwd_ptr){
        in_fwd_ptr[0] = 0.0;
        fwd_ptr_sets[set_idx] = in_fwd_ptr;
    }

    void abs_op::set_bar_ptr(size_t set_idx, double *in_bar_ptr){
        in_bar_ptr[0] = 0.0;
        bar_ptr_sets[set_idx] = in_bar_ptr;
    }

    int abs_op::identifier(){
        return 1;
    }

    int abs_op::subidentifier(){
        return -1;
    }


    /*
     * recommended for experienced user only
     * recommended for tangent mode or e.g. in spline basis functions |x|*x^(n-1) for n > 1
     */
    void abs2_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = abs(u->val);
    }

    void abs2_op::first_order_evaluation(){
        ElemOp *u = precs[0];

        if(abs(u->rad) <= abs(u->mid)){
            mid = u->mid;
            rad = u->rad;
            if(u->mid >= 0.0){
                cij = {1.0};
            } else {
                mid *= -1.0;
                rad *= -1.0;
                cij = {-1.0};
            }
        } else { // |u->rad| >= |u->mid|  ==>  u->rad != 0.0
            double check_v = abs(u->mid - u->rad), hat_v = abs(u->mid + u->rad);

            mid = 0.5*(hat_v + check_v);
            rad = 0.5*(hat_v - check_v);
            cij = {rad/u->rad};
        }
    }

    int abs2_op::subidentifier(){
        return -2;
    }


    pos_op::pos_op(){}

    pos_op::pos_op(ElemOp *u){ // constructor
        precs.push_back(u);
        u->succs.push_back(this);

        var_sets = u->var_sets;

        cij = {1.0};

        grad_ptr_sets.resize(u->grad_ptr_sets.size());
        fwd_ptr_sets.resize(u->grad_ptr_sets.size());
        bar_ptr_sets.resize(u->grad_ptr_sets.size());
    }

    void pos_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = u->val;
    }

    void pos_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = u->mid;
        rad = u->rad;
    }

    int pos_op::subidentifier(){
        return 1;
    }


    neg_op::neg_op(){}

    neg_op::neg_op(ElemOp *u){ // constructor
        precs.push_back(u);
        u->succs.push_back(this);

        var_sets = u->var_sets;

        cij = {-1.0};

        grad_ptr_sets.resize(u->grad_ptr_sets.size());
        fwd_ptr_sets.resize(u->grad_ptr_sets.size());
        bar_ptr_sets.resize(u->grad_ptr_sets.size());
    }

    void neg_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = -u->val;
    }

    void neg_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = -u->mid;
        rad = -u->rad;
    }

    int neg_op::subidentifier(){
        return 2;
    }


    // Operations without constructor
    // ==============================
    void sum_op::zero_order_evaluation(){
        ElemOp *u = precs[0], *w = precs[1];
        val = u->val + w->val;
    }

    void sum_op::first_order_evaluation(){
        ElemOp *u = precs[0], *w = precs[1];
        mid = u->mid + w->mid;
        rad = u->rad + w->rad;
        cij = {1.0, 1.0};
    }

    int sum_op::subidentifier(){
        return 1;
    }


    void incr_op::set_c(double c_in){
        c = c_in;
        cij = {1.0};
    }

    void incr_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = u->val + c;
    }

    void incr_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = u->mid + c;
        rad = u->rad;
    }

    int incr_op::subidentifier(){
        return 3;
    }


    void incr_Rop::set_c(double c_in){
        c = c_in;
        cij = {1.0};
    }

    void incr_Rop::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = c + u->val;
    }

    void incr_Rop::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = c + u->mid;
        rad = u->rad;
    }

    int incr_Rop::subidentifier(){
        return 4;
    }


    void sub_op::zero_order_evaluation(){
        ElemOp *u = precs[0], *w = precs[1];
        val = u->val - w->val;
    }

    void sub_op::first_order_evaluation(){
        ElemOp *u = precs[0], *w = precs[1];
        mid = u->mid - w->mid;
        rad = u->rad - w->rad;
        cij = {1.0, -1.0};
    }

    int sub_op::subidentifier(){
        return 2;
    }


    void decr_op::set_c(double c_in){
        c = c_in;
        cij = {1.0};
    }

    void decr_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = u->val - c;
    }

    void decr_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = u->mid - c;
        rad = u->rad;
    }

    int decr_op::subidentifier(){
        return 5;
    }


    void decr_Rop::set_c(double c_in){
        c = c_in;
        cij = {-1.0};
    }

    void decr_Rop::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = c - u->val;
    }

    void decr_Rop::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = c - u->mid;
        rad = -u->rad;
    }

    int decr_Rop::subidentifier(){
        return 6;
    }


    void mul_op::zero_order_evaluation(){
        ElemOp *u = precs[0], *w = precs[1];
        val = u->val * w->val;
    }

    void mul_op::first_order_evaluation(){
        ElemOp *u = precs[0], *w = precs[1];
        mid = u->mid * w->mid + u->rad * w->rad;
        rad = u->rad * w->mid + u->mid * w->rad;
        cij = {w->mid, u->mid};
    }

    int mul_op::subidentifier(){
        return 3;
    }


    void scalmul_op::set_c(double c_in){
        c = c_in;
        cij = {c};
    }

    void scalmul_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = u->val * c;
    }

    void scalmul_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = u->mid * c;
        rad = u->rad * c;
    }

    int scalmul_op::subidentifier(){
        return 7;
    }


    void scalmul_Rop::set_c(double c_in){
        c = c_in;
        cij = {c};
    }

    void scalmul_Rop::zero_order_evaluation(){
        ElemOp *w = precs[0];
        val = c * w->val;
    }

    void scalmul_Rop::first_order_evaluation(){
        ElemOp *w = precs[0];
        mid = c * w->mid;
        rad = c * w->rad;
    }

    int scalmul_Rop::subidentifier(){
        return 8;
    }


    void div_op::zero_order_evaluation(){
        ElemOp *u = precs[0], *w = precs[1];
        val = u->val / w->val;
    }

    void div_op::first_order_evaluation(){
        ElemOp *u = precs[0], *w = precs[1];
        double denominator = w->mid * w->mid - w->rad * w->rad;
        mid = (u->mid * w->mid - u->rad * w->rad)/denominator;
        rad = (u->rad * w->mid - u->mid * w->rad)/denominator;
        cij = {w->mid/denominator, -u->mid/denominator}; //cij = {1.0/w->mid, -u->mid/denominator};
    }

    int div_op::subidentifier(){
        return 4;
    }


    void scaldiv_op::set_c(double c_in){
        c_inv = 1.0/c_in;
        cij = {c_inv};
    }

    void scaldiv_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = u->val * c_inv;
    }

    void scaldiv_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = u->mid * c_inv;
        rad = u->rad * c_inv;
    }

    int scaldiv_op::subidentifier(){
        return 9;
    }


    void scaldiv_Rop::set_c(double c_in){
        c = c_in;
    }

    void scaldiv_Rop::zero_order_evaluation(){
        ElemOp *w = precs[0];
        val = c / w->val;
    }

    void scaldiv_Rop::first_order_evaluation(){
        ElemOp *w = precs[0];
        double denominator = w->mid * w->mid - w->rad * w->rad;
        mid = (c * w->mid)/denominator;
        rad = -(c * w->rad)/denominator;
        cij = {-c/denominator};
    }

    int scaldiv_Rop::subidentifier(){
        return 10;
    }


    void sin_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = sin(u->val);
    }

    void sin_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = sin(u->mid) * cos(u->rad);
        rad = cos(u->mid) * sin(u->rad);
        cij = {cos(u->mid) * sinc_pi(u->rad)};
    }

    int sin_op::subidentifier(){
        return 11;
    }


    void cos_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = cos(u->val);
    }

    void cos_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = cos(u->mid) * cos(u->rad);
        rad = -sin(u->mid) * sin(u->rad);
        cij = {-sin(u->mid) * sinc_pi(u->rad)};
    }

    int cos_op::subidentifier(){
        return 12;
    }


    void exp_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = exp(u->val);
    }

    void exp_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        mid = exp(u->mid) * cosh(u->rad);
        rad = exp(u->mid) * sinh(u->rad);
        cij = {exp(u->mid) * sinhc_pi(u->rad)};
    }

    int exp_op::subidentifier(){
        return 13;
    }


    void log_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = log(u->val);
    }

    void log_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        double fraction = u->rad / u->mid;
        double tmp = atanhc(fraction);

        mid = 0.5*log(u->mid * u->mid - u->rad * u->rad);
        rad = fraction*tmp; // == atanh(fraction);
        cij = {tmp/u->mid}; // == {atanhc(fraction)/u->mid};
    }

    int log_op::subidentifier(){
        return 14;
    }


    void atan_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = atan(u->val);
    }

    void atan_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        double mid_u = u->mid,
                check_u = mid_u - u->rad, hat_u = mid_u + u->rad,
                check_v = atan(check_u), hat_v = atan(hat_u);

        mid = 0.5*(hat_v + check_v);
        rad = 0.5*(hat_v - check_v);
        if(u->rad == 0.0){
            cij = {1.0/(1.0+(mid_u*mid_u))};
        } else {
            cij = {(hat_v - check_v)/(hat_u - check_u)};
        }
    }

    int atan_op::subidentifier(){
        return 15;
    }


    void signSquare_op::zero_order_evaluation(){
        ElemOp *u = precs[0];
        val = abs(u->val) * u->val;
    }

    void signSquare_op::first_order_evaluation(){
        ElemOp *u = precs[0];
        double mid_u = u->mid,
               check_u = mid_u - u->rad, hat_u = mid_u + u->rad,
               check_v = abs(check_u)*check_u, hat_v = abs(hat_u)*hat_u;

        mid = 0.5*(hat_v + check_v);
        rad = 0.5*(hat_v - check_v);
        if(u->rad == 0.0){
            cij = {2.0*abs(mid_u)};
        } else {
            cij = {(hat_v - check_v)/(hat_u - check_u)};
        }
    }

    int signSquare_op::subidentifier(){
        return 16;
    }


    boolOp::boolOp(int in_op_idx, ElemOp *u, ElemOp *w){
        op_idx = in_op_idx;

        precs.push_back(u);
        precs.push_back(w);

        prec_mode = 11;
    }

    boolOp::boolOp(int in_op_idx, ElemOp *u, double w){
        op_idx = in_op_idx;

        precs.push_back(u);
        arg_val_right = w;

        prec_mode = 10;
    }

    boolOp::boolOp(int in_op_idx, double u, ElemOp *w){
        op_idx = in_op_idx;

        arg_val_left = u;
        precs.push_back(w);

        prec_mode = 01;
    }

    boolOp::boolOp(int in_op_idx, boolOp *u, boolOp *w){
        op_idx = in_op_idx;

        bool_precs.push_back(u);
        bool_precs.push_back(w);

        prec_mode = 22;
    }

    boolOp::boolOp(int in_op_idx, boolOp *u, bool w){
        op_idx = in_op_idx;

        bool_precs.push_back(u);
        arg_bool_right = w;

        prec_mode = 20;
    }

    boolOp::boolOp(int in_op_idx, bool u, boolOp *w){
        op_idx = in_op_idx;

        arg_bool_left = u;
        bool_precs.push_back(w);

        prec_mode = 02;
    }

    boolOp::boolOp(bool u){
        val = u;
        mid = u;

        prec_mode = 0;
    }

    int boolOp::get_val(){
        if(val){
            return 1;
        }
        return -1;
    }

    int boolOp::get_mid(){
        if(mid){
            return 1;
        }
        return -1;
    }

    bool boolOp::compare(double left, double right){
        switch(op_idx){
            case 0: {
                if(left == right) return true;
                else return false;
                break;
            }
            case 1: {
                if(left != right) return true;
                else return false;
                break;
            }
            case 2: {
                if(left <= right) return true;
                else return false;
                break;
            }
            case 3: {
                if(left < right) return true;
                else return false;
                break;
            }
            case 4: {
                if(left >= right) return true;
                else return false;
                break;
            }
            case 5: {
                if(left > right) return true;
                else return false;
                break;
            }
        }

        return false; // will never be reached but suppresses warning!
    }

    bool boolOp::compare(bool left, bool right){
        switch(op_idx){
            case 6: {
                if(left && right) return true;
                else return false;
                break;
            }
            case 7: {
                if(left || right) return true;
                else return false;
                break;
            }
        }

        return false; // will never be reached but suppresses warning!
    }

    void boolOp::zero_order_evaluation(){
        for (size_t i = 0; i < bool_precs.size(); i++){
            bool_precs[i]->zero_order_evaluation();
        }

        switch(prec_mode){
            case 11: {
                ElemOp *u = precs[0], *w = precs[1];

                val = compare(u->val, w->val);
                break;
            }
            case 10: {
                ElemOp *u = precs[0];

                val = compare(u->val, arg_val_right);
                break;
            }
            case 01: {
                ElemOp *w = precs[0];

                val = compare(arg_val_left, w->val);
                break;
            }
            case 22: {
                boolOp *u = bool_precs[0], *w = bool_precs[1];

                val = compare(u->val, w->val);
                break;
            }
            case 20: {
                boolOp *u = bool_precs[0];

                val = compare(u->val, arg_bool_right);
                break;
            }
            case 02: {
                boolOp *w = bool_precs[0];

                val = compare(arg_bool_left, w->val);
                break;
            }
            case 0: {
                break;
            }
        }
    }

    void boolOp::first_order_evaluation(){
        for (size_t i = 0; i < bool_precs.size(); i++){
            bool_precs[i]->first_order_evaluation();
        }

        switch(prec_mode){
            case 11: {
                ElemOp *u = precs[0], *w = precs[1];

                mid = compare(u->mid, w->mid);
                break;
            }
            case 10: {
                ElemOp *u = precs[0];

                mid = compare(u->mid, arg_val_right);
                break;
            }
            case 01: {
                ElemOp *w = precs[0];

                mid = compare(arg_val_left, w->mid);
                break;
            }
            case 22: {
                boolOp *u = bool_precs[0], *w = bool_precs[1];

                mid = compare(u->mid, w->mid);
                break;
            }
            case 20: {
                boolOp *u = bool_precs[0];

                mid = compare(u->mid, arg_bool_right);
                break;
            }
            case 02: {
                boolOp *w = bool_precs[0];

                mid = compare(arg_bool_left, w->mid);
                break;
            }
            case 0: {
                break;
            }
        }
    }

    boolOp::~boolOp(){
        for(size_t i = 0; i<bool_precs.size(); i++){
            delete bool_precs[i];
        }
    }



    void CondElemOp::set_condition(boolOp *in_b){
        b = in_b;
    }

    void CondElemOp::zero_order_evaluation(){
        ElemOp *u_then = precs[0], *u_else = precs[1];

        b->zero_order_evaluation();

        if(b->val){
            val = u_then->val;
        } else {
            val = u_else->val;
        }
    }

    void CondElemOp::first_order_evaluation(){
        ElemOp *u_then = precs[0], *u_else = precs[1];

        b->first_order_evaluation();

        if(b->mid){
            mid = u_then->mid;
            rad = u_then->rad;
            cij = {1.0, 0.0};
        } else {
            mid = u_else->mid;
            rad = u_else->rad;
            cij = {0.0, 1.0};
        }
    }

    int CondElemOp::subidentifier(){
        return 5;
    }

    CondElemOp::~CondElemOp(){
        delete b;
    }

};

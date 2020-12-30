/*
 * part of the 1st hearth-piece of cycADa: the header for tape elements
 *
 * __author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
 * __credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
 *                'Oliver Kunst', 'Lutz Lehmann',
 *                'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames
 */


#ifndef elemOp_h
#define elemOp_h elemOp_h

#include <vector>
#include <cmath>
#include <numeric>
#include <algorithm>
// #include <boost/math/special_functions/sinc.hpp>
// #include <boost/math/special_functions/sinhc.hpp>
// #include <boost/math/special_functions/atanh.hpp>
#include <boost/iterator/zip_iterator.hpp>
#include <boost/range.hpp>

// makeshift definition of atanhc
// #include "atanhc.hpp"

#include <iostream>



namespace core{

    using namespace std;



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
    bool absCmp(size_t i, size_t j, const vector<long int> &vec);

    vector<size_t> create_permutation_map(const vector<long int> &vec);

    //template <typename T>
    //void apply_permutation_map(const vector<size_t>& p, vector<T>& vec){
    void apply_permutation_map(const vector<size_t>& p, vector<long int>& vec);



    // ElemOp - Klassen mit großen Buchstaben und CamelCase
    class ElemOp{ // elementary operation

    public:

        // meta informations:
        size_t id;
        vector<ElemOp*> precs, succs; // preceding and succeding operations
        vector<vector<long int>> var_sets; // variables

        // Evaluation:
        double val;

        // AD relevant values:
        double mid; // corresponds to \mathring v_i
        double rad; // corresponds to \delta v_i
        vector<double> cij; //, grad, increments;
        vector<double*> grad_ptr_sets;
        vector<double*> fwd_ptr_sets, bar_ptr_sets;

        // AD flags
        bool is_root = false, is_const = false, is_swVar_node = false, is_abs_node = false, is_dependent = false;

        // class functions:
        virtual void zero_order_evaluation()=0; // evaluates the taped function
        virtual void first_order_evaluation()=0; // evaluates mid, rad and cij
        virtual void sparse_grad(size_t set_idx)=0; // evaluates grad
        virtual void fwd(size_t set_idx)=0; // evaluates forward mode
        virtual void rev(size_t set_idx)=0; // evaluates forward mode

        virtual void set_grad_ptr(size_t set_idx, double *in_grad_ptr)=0;
        virtual void set_fwd_ptr(size_t set_idx, double *in_fwd_ptr)=0;
        virtual void set_bar_ptr(size_t set_idx, double *in_fwd_ptr)=0;

        virtual bool is_active_swVar(size_t set_idx);

        virtual bool is_active(size_t set_idx);

        virtual int identifier()=0;
        virtual int subidentifier()=0;

        virtual ~ElemOp();
    };



    // Operations with constructors
    // ============================

    class UnaryOperation: public ElemOp{ // v = phi(u)

    public:

        UnaryOperation();

        UnaryOperation(ElemOp *u);

        void sparse_grad(size_t set_idx) override;
        void fwd(size_t set_idx) override final;
        void rev(size_t set_idx) override final;

        void set_grad_ptr(size_t set_idx, double *in_grad_ptr) override final;
        void set_fwd_ptr(size_t set_idx, double *in_fwd_ptr) override final;
        void set_bar_ptr(size_t set_idx, double *in_bar_ptr) override final;

        int identifier() override final;
        int subidentifier() override;
    };

    class BinaryOperation: public ElemOp{ // v = phi(u, w)

    public:

        vector<vector<size_t>> map_sets;

        BinaryOperation(ElemOp *u, ElemOp *w);

        void sparse_grad(size_t set_idx) override final;
        void fwd(size_t set_idx) override final;
        void rev(size_t set_idx) override final;

        void set_grad_ptr(size_t set_idx, double *in_grad_ptr) override final;
        void set_fwd_ptr(size_t set_idx, double *in_fwd_ptr) override final;
        void set_bar_ptr(size_t set_idx, double *in_bar_ptr) override final;

        int identifier() override final;
        int subidentifier() override;
    };



    class RootInit: public ElemOp{ // represent variables and parameters (the latter means variables not to differentiate for)

    public:

        vector<bool> is_independent;

        RootInit(size_t num_of_sets);

        void set_var_id(size_t set_idx, long int var_id);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;
        void sparse_grad(size_t set_idx) override final;
        void fwd(size_t set_idx) override final;
        void rev(size_t set_idx) override final;

        void set_grad_ptr(size_t set_idx, double *in_grad_ptr) override final;
        void set_fwd_ptr(size_t set_idx, double *in_fwd_ptr) override final;
        void set_bar_ptr(size_t set_idx, double *in_bar_ptr) override final;

        int identifier() override final;
        int subidentifier() override final;
    };

    class ConstInit: public ElemOp{

    public:

        ConstInit(size_t num_of_sets);

        ConstInit(size_t num_of_sets, double in_c);

        void set_c(double in_c);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;
        void sparse_grad(size_t set_idx) override final;
        void fwd(size_t set_idx) override final;
        void rev(size_t set_idx) override final;

        void set_grad_ptr(size_t set_idx, double *in_grad_ptr) override final;
        void set_fwd_ptr(size_t set_idx, double *in_fwd_ptr) override final;
        void set_bar_ptr(size_t set_idx, double *in_bar_ptr) override final;

        int identifier() override final;
        int subidentifier() override final;
    };



    class abs_op: public ElemOp{

    public:

        abs_op(ElemOp *u, size_t num_of_sets);

        void set_var_id(size_t set_idx, long int var_id);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;
        void sparse_grad(size_t set_idx) override final;
        void fwd(size_t set_idx) override final;
        void rev(size_t set_idx) override final;

        void set_grad_ptr(size_t set_idx, double *in_grad_ptr) override final;
        void set_fwd_ptr(size_t set_idx, double *in_fwd_ptr) override final;
        void set_bar_ptr(size_t set_idx, double *in_bar_ptr) override final;

        int identifier() override final;
        int subidentifier() override final;
    };

    /*
     * recommended for experienced user only
     * recommended for tangent mode or e.g. in spline basis functions |x|*x^(n-1) for n > 1
     */
    class abs2_op: public UnaryOperation{ // non-smoothnes will be ignored in abs2 implementation (e.g. for use in x*|x|)

    public:

        double c;

        using UnaryOperation::UnaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class pos_op: public UnaryOperation{

    public:

        pos_op();

        pos_op(ElemOp *u);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class neg_op: public UnaryOperation{

    public:

        neg_op();

        neg_op(ElemOp *u);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    // Operations without constructor
    // ==============================
    class sum_op: public BinaryOperation{

    public:

        using BinaryOperation::BinaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };

    class incr_op: public UnaryOperation{

    public:

        double c;

        using UnaryOperation::UnaryOperation;

        void set_c(double c_in);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };

    class incr_Rop: public UnaryOperation{

    public:

        double c;

        using UnaryOperation::UnaryOperation;

        void set_c(double c_in);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class sub_op: public BinaryOperation{

    public:

        using BinaryOperation::BinaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };

    class decr_op: public UnaryOperation{

    public:

        double c;

        using UnaryOperation::UnaryOperation;

        void set_c(double c_in);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };

    class decr_Rop: public UnaryOperation{

    public:

        double c;

        using UnaryOperation::UnaryOperation;

        void set_c(double c_in);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class mul_op: public BinaryOperation{

    public:

        using BinaryOperation::BinaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class scalmul_op: public UnaryOperation{

    public:

        double c;

        using UnaryOperation::UnaryOperation;

        void set_c(double c_in);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class scalmul_Rop: public UnaryOperation{

    public:

        double c;

        using UnaryOperation::UnaryOperation;

        void set_c(double c_in);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class div_op: public BinaryOperation{

    public:

        using BinaryOperation::BinaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };

    class scaldiv_op: public UnaryOperation{

    public:

        double c_inv;

        using UnaryOperation::UnaryOperation;

        void set_c(double c_in);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };

    class scaldiv_Rop: public UnaryOperation{

    public:

        double c;

        using UnaryOperation::UnaryOperation;

        void set_c(double c_in);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class sin_op: public UnaryOperation{

    public:

        using UnaryOperation::UnaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };

    class cos_op: public UnaryOperation{

    public:

        using UnaryOperation::UnaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class exp_op: public UnaryOperation{

    public:

        using UnaryOperation::UnaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };

    class log_op: public UnaryOperation{

    public:

        using UnaryOperation::UnaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class atan_op: public UnaryOperation{

    public:

        using UnaryOperation::UnaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    /*
     *  sign square
     *  -----------
     *
     *      sign(x)*(x^2)  ==  abs(x)*x
     *
     *    is an odd version of the even square function.
     *    This is an alternative implementation to avoid clipping and switching variables
     *    if desired.
     */
    class signSquare_op: public UnaryOperation{

    public:

        using UnaryOperation::UnaryOperation;

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;
    };



    class boolOp{

    public:

        boolOp(int in_op_idx, ElemOp *u, ElemOp *w);

        boolOp(int in_op_idx, ElemOp *u, double w);

        boolOp(int in_op_idx, double u, ElemOp *w);

        boolOp(int in_op_idx, boolOp *u, boolOp *w);

        boolOp(int in_op_idx, boolOp *u, bool w);

        boolOp(int in_op_idx, bool u, boolOp *w);

        boolOp(bool u);

        vector<ElemOp*> precs; // preceding and succeding operations
        vector<boolOp*> bool_precs; // preceding and succeding operations

        int op_idx, prec_mode;

        bool val;
        bool mid;

        int get_val();
        int get_mid();

        double arg_val_left, arg_val_right;
        bool arg_bool_left, arg_bool_right;

        bool compare(double left, double right);
        bool compare(bool left, bool right);

        void zero_order_evaluation();
        void first_order_evaluation();

        ~boolOp();
    };

    class CondElemOp: public BinaryOperation{

    public:

        boolOp *b;

        using BinaryOperation::BinaryOperation;

        void set_condition(boolOp *in_b);

        void zero_order_evaluation() override final;
        void first_order_evaluation() override final;

        int subidentifier() override final;

        ~CondElemOp();
    };

};

#endif

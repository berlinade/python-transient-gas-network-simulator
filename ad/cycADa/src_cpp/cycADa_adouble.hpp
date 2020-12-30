/*
 * part of the 1st hearth-piece of cycADa: the header for the encapsulation of elemOp
 *
 * __author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
 * __credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
 *                'Oliver Kunst', 'Lutz Lehmann',
 *                'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames
 */


#ifndef adouble_h
#define adouble_h adouble_h

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

    class Adbool{

    public:

        Adbool();
        Adbool(bool in_b);
        Adbool(boolOp *in_b);

        boolOp *b;
    };



    class Adouble{

    public:

        ElemOp *ptr;
        Tape *t;
        size_t num_of_sets;

        Adouble(); // default constructor
        Adouble(Tape *in_t, vector<bool> is_active_var);
        /*
         * Caution: With the next constructor variables can be initialized with a pre choosen id.
         * But the automatic numbering continues every active variable intialization increases the internal counter by one!
         * Make sure that different variables on the same tape and for the same set_idx don't share the same Id!
         */
        Adouble(Tape *in_t, vector<bool> is_active_var, vector<long int> choosen_IDs);
        Adouble(Tape *in_t, double in_c);
        Adouble(Tape *in_t, ElemOp *op);
        Adouble(Tape *in_t, size_t idx, bool opt);

        size_t get_id();
        vector<ElemOp*> depends_on();
        vector<ElemOp*> dependency_of();

        size_t get_grad_len(size_t set_idx);
        double* get_grad_ptr(size_t set_idx);
        void set_grad_ptr(size_t set_idx, double *in_grad_ptr);

        size_t get_vars_len(size_t set_idx);
        long int* get_vars_ptr(size_t set_idx);

//        void declare_as_dependent();
    //    TODO: implement erase function for elem_OP in general!
    //    BUT: be careful, since different handlings for inputs, sw_vars, outputs and intermediates are necessary!!
        void set_dependent_status(bool state);

    //    bool is_independent(size_t set_idx);

        bool is_root();
        bool is_swVar_node();
        bool is_active_swVar(size_t set_idx);
        bool is_active(size_t set_idx);
        bool is_abs_node();
        bool is_active_abs(size_t set_idx);
        bool is_dependent();
        bool is_const();

        void set_val(double in_val);
        double get_val();

        void set_mid_rad(double in_mid, double in_rad);

        void set_mid(double in_mid);
        double get_mid();

        void set_rad(double in_rad);
        double get_rad();

        int get_identifier();
        int get_subidentifier();

        Adouble operator+();
        Adouble operator+(Adouble w);
        Adouble operator+(double w);

        Adouble operator-();
        Adouble operator-(Adouble w);
        Adouble operator-(double w);

        Adouble operator*(Adouble w);
        Adouble operator*(double w);

        Adouble operator/(Adouble w);
        Adouble operator/(double w);
        Adouble inv();

        Adbool operator==(Adouble w);
        Adbool operator==(double w);

        Adbool operator!=(Adouble w);
        Adbool operator!=(double w);

        Adbool operator<=(Adouble w);
        Adbool operator<=(double w);

        Adbool operator<(Adouble w);
        Adbool operator<(double w);

        Adbool operator>=(Adouble w);
        Adbool operator>=(double w);

        Adbool operator>(Adouble w);
        Adbool operator>(double w);
    };



    Adouble operator+(double u, Adouble w);

    Adouble operator-(double u, Adouble w);

    Adouble operator*(double u, Adouble w);

    Adouble operator/(double u, Adouble w);

    Adbool operator==(double u, Adouble w);

    Adbool operator!=(double u, Adouble w);

    Adbool operator<=(double u, Adouble w);

    Adbool operator<(double u, Adouble w);

    Adbool operator>=(double u, Adouble w);

    Adbool operator>(double u, Adouble w);



    Adbool logical_and(Adbool u, Adbool w);

    Adbool logical_and(Adbool u, bool w);

    Adbool logical_and(bool u, Adbool w);

    bool logical_and(bool u, bool w);

    Adbool logical_or(Adbool u, Adbool w);

    Adbool logical_or(Adbool u, bool w);

    Adbool logical_or(bool u, Adbool w);

    bool logical_or(bool u, bool w);



    Adouble sin(Adouble u);

    Adouble cos(Adouble u);



    Adouble exp(Adouble u);

    Adouble log(Adouble u);



    Adouble atan(Adouble u);



    Adouble signSquare(Adouble u);



    Adouble pow(Adouble u, Adouble w);

    Adouble pow(Adouble u, double w);

    Adouble pow(Adouble u, int w);

    Adouble pow(double u, Adouble w);



    Adouble abs(Adouble w);

    Adouble abs2(Adouble u);



    Adouble cond_assign(Adbool b, Adouble u, Adouble w);

    Adouble cond_assign(Adbool b, Adouble u, double w);

    Adouble cond_assign(Adbool b, double u, Adouble w);

    Adouble cond_assign(bool b, Adouble u, Adouble w);

    Adouble cond_assign(bool b, Adouble u, double w);

    Adouble cond_assign(bool b, double u, Adouble w);

    double cond_assign(bool b, double u, double w);
};

#endif






















































































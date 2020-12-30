/*
 * demo *.cpp file to demonstrate use of cycADa from c++ (requires c++11)
 *
 * __author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
 * __credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
 *                'Oliver Kunst', 'Lutz Lehmann',
 *                'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames
 */


#include "../../src_cpp/cycADa_adouble.hpp"

#include <iostream>

using namespace core;



// The following code is for representation and debugging
// ======================================================

template <typename T>
void _print_vec(const std::vector<T> &vec){
    for(size_t i=0; i<vec.size(); i++){
        cout << vec[i] << "; ";
    }
    cout << endl;
}

double finDiff(double (*func)(double, double), double x, double y, double h, int i){
    if(i == 0){
        return (func(x + h, y) - func(x, y))/h;
    }
    return (func(x, y + h) - func(x, y))/h;
}

template <typename T>
T test_func(T x, T y){
    T v = cond_assign(x < 1.0, x, y);
    return v;
}

int main(){
    cout << "Hello World" << endl;

    // The following is a test- and example-code to check and present certain functionalities of the cycADa_core
    size_t num_of_sets = 1;
    Tape t = Tape(num_of_sets);
    vector<bool> x_is_var = {true}, y_is_var = {true};
    vector<long int> xIDs = {1}, yIDs = {2};

    Adouble xVar = Adouble(&t, x_is_var, xIDs), yVar = Adouble(&t, y_is_var, yIDs), fVar;

    fVar = test_func(xVar, yVar);
    fVar.set_dependent_status(true);

    double xVal = 1.1, yVal = -2.0;
    vector <double> vals = {xVal, yVal};
    cout << "assign : ";
    t.assign_val(vals);
    cout << "check" << "\n" << "zero order eval : ";
    t.zero_order_evaluation();
    cout << "check" << endl;

    cout << fVar.ptr->val << endl;
    cout << test_func(xVal, yVal) << endl;


    xVal = 0.9, yVal = -2.0;
    vals = {xVal, yVal};
    cout << "assign : ";
    t.assign_val(vals);
    cout << "check" << "\n" << "zero order eval : ";
    t.zero_order_evaluation();
    cout << "check" << endl;

    cout << fVar.ptr->val << endl;
    cout << test_func(xVal, yVal) << endl;


    cout << "=======================" << endl;

    double xMid = 1.1, yMid = -2.0;
    vector <double> mids = {xMid, yMid};
    double xRad = 0.0, yRad = 0.0;
    vector <double> rads = {xRad, yRad};
    cout << "mid/rad assign : ";
    t.assign_mid_rad(mids, rads);
    cout << "check" << "\n" << "1st order eval : ";
    t.first_order_evaluation();
    cout << "check" << "\n" << "generating grads : ";

    for(size_t set_idx = 0; set_idx < num_of_sets; set_idx++){
        size_t len = t.get_grad_size_inters(set_idx),
                 s = t.get_grad_size_swVars(set_idx),
                 m = t.get_grad_size_depends(set_idx);
        vector<double> grad_inters(len), grad_swVars(s), grad_depends(m);
        t.set_grad_inters(set_idx, grad_inters.data());
        t.set_grad_swVars(set_idx, grad_swVars.data());
        t.set_grad_depends(set_idx, grad_depends.data());

        cout << "check" << "\n" << "sparse grad : ";
        t.sparse_grad(set_idx);
        cout << "check" << endl;

        cout << "inters  : ";
        _print_vec(grad_inters);
        cout << "swVars  : ";
        _print_vec(grad_swVars);
        cout << "depends : ";
        _print_vec(grad_depends);
    }

    cout << "=======================" << endl;

    xMid = 0.9, yMid = -2.0;
    mids = {xMid, yMid};
    xRad = 0.0, yRad = 0.0;
    rads = {xRad, yRad};
    cout << "mid/rad assign : ";
    t.assign_mid_rad(mids, rads);
    cout << "check" << "\n" << "1st order eval : ";
    t.first_order_evaluation();
    cout << "check" << "\n" << "generating grads : ";

    for(size_t set_idx = 0; set_idx < num_of_sets; set_idx++){
        size_t len = t.get_grad_size_inters(set_idx),
                 s = t.get_grad_size_swVars(set_idx),
                 m = t.get_grad_size_depends(set_idx);
        vector<double> grad_inters(len), grad_swVars(s), grad_depends(m);
        t.set_grad_inters(set_idx, grad_inters.data());
        t.set_grad_swVars(set_idx, grad_swVars.data());
        t.set_grad_depends(set_idx, grad_depends.data());

        cout << "check" << "\n" << "sparse grad : ";
        t.sparse_grad(set_idx);
        cout << "check" << endl;

        cout << "inters  : ";
        _print_vec(grad_inters);
        cout << "swVars  : ";
        _print_vec(grad_swVars);
        cout << "depends : ";
        _print_vec(grad_depends);
    }

    cout << "=======================" << endl;


    cout << "-endOfCode-" << endl;

    return 0;
}























































































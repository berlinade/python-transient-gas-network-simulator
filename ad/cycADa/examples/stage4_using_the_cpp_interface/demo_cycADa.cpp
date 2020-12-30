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

template <typename T>
T test_func(T x, T y){
    T v = 33.0*abs(x + y) * x; // with or without abs!
    return v*v;
}

//template <typename T>
//std::vector<T> test_func_2(std::vector<T> &vec){
//    vector<T> out;
//    size_t x_dim = vec.size();
//
//        out.push_back(sin(vec[0] + 3.0*vec[1]));
//        for(size_t i=1; i<x_dim-1; i++){
//            out.push_back(sin(-3.0*vec[i-1] + vec[i] + 3.0*vec[i+1]));
//        }
//        out.push_back(sin(-3.0*vec[x_dim-2] + vec[x_dim-1]));
//
//    return out;
//}

double finDiff(double (*func)(double, double), double x, double y, double h, int i){
    if(i == 0){
        return (func(x + h, y) - func(x, y))/h;
    }
    return (func(x, y + h) - func(x, y))/h;
}

//void create_some_tape(){
//    size_t num_of_sets = 1;
//    Tape t = Tape(num_of_sets);
//
//    /*
//    vector<bool> x_is_var = {true}, y_is_var = {false};
//    Adouble xVar = Adouble(&t, x_is_var, xIDs), yVar = Adouble(&t, y_is_var, yIDs), fVar;
//    */
//
//    size_t x_dim = 300;
//    vector<Adouble> xVec;
//    vector<vector<bool>> xVec_is_active;
//
//    for(size_t i=0; i<x_dim; i++){
//        xVec_is_active.push_back({true});
//        xVec.push_back(Adouble(&t, xVec_is_active[i]));
//    }
//
//    vector<Adouble> fVec = test_func_2(xVec);
//
//
//    for(size_t i=0; i<x_dim; i++){
//        fVec[i].set_dependent_status(true);
//    }
//
//    // for(size_t i=0; i<t.op_tape.size(); i++){
//    //     delete t.op_tape[i];
//    // }
//
//    cout << "created_some_tape" << endl;
//}

int main(){
    cout << "Hello World" << endl;

    // The following is a test- and example-code to check and present certain functionalities of the cycADa_core
    size_t num_of_sets = 3;
    Tape t = Tape(num_of_sets);
    vector<bool> x_is_var = {true, false, true}, y_is_var = {false, true, true};
    vector<long int> xIDs = {99, 99, -99}, yIDs = {177, 177, 177};

    Adouble xVar = Adouble(&t, x_is_var, xIDs), yVar = Adouble(&t, y_is_var, yIDs), fVar;

    fVar = test_func(xVar, yVar);
    fVar.set_dependent_status(true);

    cout << "fVar indices:" << endl;
    _print_vec(fVar.ptr->var_sets[2]);
    cout << "fVar indices end" << endl;

    for(size_t set_idx = 0; set_idx < 2; set_idx++){
        for(size_t i = 0; i < t.get_n(set_idx); i++){
            cout << t.tape_var_sets[set_idx][i]->id << ", " << endl;
        }
    }

    double xVal = 1.1, yVal = -2.0;
    vector <double> vals = {xVal, yVal};
    cout << "assign : ";
    t.assign_val(vals);
    cout << "check" << "\n" << "zero order eval : ";
    t.zero_order_evaluation();
    cout << "check" << endl;

    for(auto const& v: t.op_tape){
        cout << v->id << " : " << v->val << endl;
    }

    cout << "result          : " << test_func(xVal, yVal) << endl;

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

    // check against finite differences only makes sense when no abs is used in f!
    double h = 0.000001;
    cout << "d approx result : " << finDiff(&test_func, xVal, yVal, h, 0) <<
            ", " << finDiff(&test_func, xVal, yVal, h, 1) << endl;

//    // The following Code verifies that it is not possible to initialize switching vars before user defined vars!
//    size_t num_of_sets = 1;
//    Tape t = Tape(num_of_sets);
//
//    Adouble three = Adouble(&t, -3.0), f;
//    f = abs(three);
//    f.set_dependent_status(true);
//
//    t.zero_order_evaluation();
//    cout << "check" << endl;
//
//    for(auto const& v: t.op_tape){
//        cout << v->id << " : " << v->val << endl;
//    }
//
//    t.first_order_evaluation();
//    _print_vec(f.ptr->var_sets[0]);
//    cout << "bla: " << f.ptr->var_sets[0].size() << endl;

    cout << "new feature: forward mode or fwd:" << endl;

    for(size_t set_idx = 0; set_idx < num_of_sets; set_idx++){
        size_t len_inters_fwd         = t.get_fwd_vec_size_inters(set_idx),
               len_swVars_and_depends = t.get_fwd_vec_size_swVars_and_depends(set_idx);
        vector<double> fwd_vec_inters(len_inters_fwd), fwd_vec_swVars_and_depends(len_swVars_and_depends);
        t.set_fwd_vec_inters(set_idx, fwd_vec_inters.data());
        t.set_fwd_vec_swVars_and_depends(set_idx, fwd_vec_swVars_and_depends.data());

        vector<double> in_incr = {1.0, 0.0};
        t.assign_fwd_incr(set_idx, in_incr);

        cout << "check" << "\n" << "fwd : ";
        t.fwd(set_idx);
        cout << "check" << endl;

        cout << "fwd inters             : ";
        _print_vec(fwd_vec_inters);
        cout << "fwd swVars and depends : ";
        _print_vec(fwd_vec_swVars_and_depends);
    }

    cout << "new feature: identifier of elemOp" << endl;
    //fVar = test_func(xVar, yVar);
    cout << "xVar identifier: " << xVar.get_identifier() << endl;
    cout << "xVar identifier: " << xVar.get_subidentifier() << endl;

    cout << "yVar identifier: " << yVar.get_identifier() << endl;
    cout << "yVar identifier: " << yVar.get_subidentifier() << endl;

    cout << "fVar identifier: " << fVar.get_identifier() << endl;
    cout << "fVar identifier: " << fVar.get_subidentifier() << endl;

    cout << "-endOfCode-" << endl;

    return 0;
}























































































/*
 * part of the 1st hearth-piece of cycADa: the implementation of the encapsulation of elemOp
 *
 * __author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
 * __credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
 *                'Oliver Kunst', 'Lutz Lehmann',
 *                'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames
 */


#include "cycADa_adouble.hpp"

// #include <vector>
// #include <cmath>
// #include <numeric>
// #include <boost/math/special_functions/sinc.hpp>
// #include <boost/math/special_functions/sinhc.hpp>
// #include <boost/math/special_functions/atanh.hpp>

// makeshift definition of atanhc
// #include "atanhc.hpp"



namespace core{

    Adbool::Adbool(){}

    Adbool::Adbool(bool in_b){
        b = new boolOp(in_b);
    }

    Adbool::Adbool(boolOp *in_b){
        b = in_b;
    }



    Adouble::Adouble(){} // default constructor

    Adouble::Adouble(Tape *in_t, vector<bool> is_active_var){ // init new variables
        num_of_sets = in_t->get_num_of_sets();

        RootInit *rootOp = new RootInit(num_of_sets);
        ptr = rootOp;
        t = in_t;
        t->add_op(ptr);
        t->tape_roots.push_back(ptr);

        // set var_id's
        for(size_t set_idx = 0; set_idx < num_of_sets; set_idx++){
            if(is_active_var[set_idx]){
                rootOp->set_var_id(set_idx, t->read_var_id(set_idx));
                t->incr_var_id(set_idx);
                t->tape_var_sets[set_idx].push_back(ptr);
            }
        }
    }

    /*
     * Caution: With this constructor variables can be initialized with a pre choosen id.
     * But the automatic numbering continues every active variable intialization increases the internal counter by one!
     * Make sure that different variables on the same tape and for the same set_idx don't share the same Id!
     */
    Adouble::Adouble(Tape *in_t, vector<bool> is_active_var, vector<long int> choosen_IDs){ // init new variables with index
        num_of_sets = in_t->get_num_of_sets();

        RootInit *rootOp = new RootInit(num_of_sets);
        ptr = rootOp;
        t = in_t;
        t->add_op(ptr);
        t->tape_roots.push_back(ptr);

        // set var_id's
        for(size_t set_idx = 0; set_idx < num_of_sets; set_idx++){
            if(is_active_var[set_idx]){
                rootOp->set_var_id(set_idx, std::abs(choosen_IDs[set_idx]));
                t->incr_var_id(set_idx); // the variable counter will be increased by one!
                t->tape_var_sets[set_idx].push_back(ptr);
            }
        }
    }

    Adouble::Adouble(Tape *in_t, double in_c){ // init constants
        num_of_sets = in_t->get_num_of_sets();
        ptr = new ConstInit(num_of_sets, in_c);
        t = in_t;
        t->add_op(ptr);
    }

    Adouble::Adouble(Tape *in_t, ElemOp *op){ // init new elem. operations
        num_of_sets = in_t->get_num_of_sets();
        ptr = op;
        t = in_t;
        t->add_op(ptr);
    }

    Adouble::Adouble(Tape *in_t, size_t idx, bool opt){ // recreate Adouble from tape_entry
        num_of_sets = in_t->get_num_of_sets();
        t = in_t;
        ptr = t->op_tape[idx];
    }

    size_t Adouble::get_id(){
        return this->ptr->id;
    }

    vector<ElemOp*> Adouble::depends_on(){
        return this->ptr->precs;
    }

    vector<ElemOp*> Adouble::dependency_of(){
        return this->ptr->succs;
    }

    size_t Adouble::get_grad_len(size_t set_idx){
        return get_vars_len(set_idx); //this->ptr->var_sets[set_idx].size();
    }

    double* Adouble::get_grad_ptr(size_t set_idx){
        return this->ptr->grad_ptr_sets[set_idx];
    }

    void Adouble::set_grad_ptr(size_t set_idx, double *in_grad_ptr){
        this->ptr->set_grad_ptr(set_idx, in_grad_ptr);
    }

    size_t Adouble::get_vars_len(size_t set_idx){
        return this->ptr->var_sets[set_idx].size();
    }

    long int* Adouble::get_vars_ptr(size_t set_idx){
        return this->ptr->var_sets[set_idx].data();
    }

//    void Adouble::declare_as_dependent(){
//        if(this->ptr->is_const || this->ptr->is_root || this->ptr->is_swVar_node){
//            Adouble u = +(*this); // draw a new edge, because dependent nodes shall neither be const, root or abs-arg.
//            this->ptr = u.ptr; // steals the pointer
//        }
//
//        if(this->ptr->is_dependent == false){
//            this->ptr->is_dependent = true;
//            this->t->tape_depends.push_back(this->ptr);
//        }
//    }

//    TODO: implement erase function for elem_OP in general!
//    BUT: be careful, since different handlings for inputs, sw_vars, outputs and intermediates are necessary!!
    void Adouble::set_dependent_status(bool state){
        if(state){
            if(this->ptr->is_const || this->ptr->is_root || this->ptr->is_swVar_node || this->ptr->is_abs_node){
                Adouble u = +(*this); // draw a new edge, because dependent nodes shall neither be const, root nor abs
                this->ptr = u.ptr; // steals the pointer
            }

            if(ptr->is_dependent == false){
                ptr->is_dependent = true;
                t->tape_depends.push_back(ptr);
            }
        }else{
            if(ptr->is_dependent == true){
                ptr->is_dependent = false;
                t->tape_depends.erase(find(t->tape_depends.begin(), t->tape_depends.end(), ptr));
            }
        }
    }

    bool Adouble::is_root(){
        return this->ptr->is_root;
    }

    bool Adouble::is_swVar_node(){
        return this->ptr->is_swVar_node;
    }

    bool Adouble::is_active_swVar(size_t set_idx){
        if(this->ptr->is_active_swVar(set_idx)){
            return true;
        }
        return false;
    }

    bool Adouble::is_active(size_t set_idx){
        if(this->ptr->is_active(set_idx)){
            return true;
        }
        return false;
    }

    bool Adouble::is_abs_node(){
        return this->ptr->is_abs_node;
    }

    bool Adouble::is_active_abs(size_t set_idx){
        if( this->ptr->is_abs_node && this->ptr->precs[0]->is_active_swVar(set_idx) ){
            return true;
        }
        return false;
    }

    bool Adouble::is_dependent(){
        return this->ptr->is_dependent;
    }

    bool Adouble::is_const(){
        return this->ptr->is_const;
    }

    void Adouble::set_val(double in_val){
        this->ptr->val = in_val;
    }

    double Adouble::get_val(){
        return this->ptr->val;
    }

    void Adouble::set_mid_rad(double in_mid, double in_rad){
        this->ptr->mid = in_mid;
        this->ptr->rad = in_rad;
    }

    void Adouble::set_mid(double in_mid){
        this->ptr->mid = in_mid;
    }

    double Adouble::get_mid(){
        return this->ptr->mid;
    }

    void Adouble::set_rad(double in_rad){
        this->ptr->rad = in_rad;
    }

    double Adouble::get_rad(){
        return this->ptr->rad;
    }

    int Adouble::get_identifier(){
        return this->ptr->identifier();
    }

    int Adouble::get_subidentifier(){
        return this->ptr->subidentifier();
    }



    Adouble Adouble::operator+(){ // +this (unary plus)
        pos_op *pos = new pos_op(this->ptr);
        Adouble v = Adouble(this->t, pos);
        return v;
    }

    Adouble Adouble::operator+(Adouble w){ // v = this + w
        sum_op *sum = new sum_op(this->ptr, w.ptr);
        Adouble v = Adouble(this->t, sum);
        return v;
    }

    Adouble Adouble::operator+(double w){ // v = this + w
        incr_op *incr = new incr_op(this->ptr);
        incr->set_c(w);
        Adouble v = Adouble(this->t, incr);
        return v;
    }

    Adouble operator+(double u, Adouble w){ // v = u + this
        incr_Rop *incr = new incr_Rop(w.ptr);
        incr->set_c(u);
        Adouble v = Adouble(w.t, incr);
        return v;
    }


    Adouble Adouble::operator-(){ // -this (unary minus)
        neg_op *neg = new neg_op(this->ptr);
        Adouble v = Adouble(this->t, neg);
        return v;
    }

    Adouble Adouble::operator-(Adouble w){ // v = this + w
        sub_op *sub = new sub_op(this->ptr, w.ptr);
        Adouble v = Adouble(this->t, sub);
        return v;
    }

    Adouble Adouble::operator-(double w){ // v = this + w
        decr_op *decr = new decr_op(this->ptr);
        decr->set_c(w);
        Adouble v = Adouble(this->t, decr);
        return v;
    }

    Adouble operator-(double u, Adouble w){ // v = u + this
        decr_Rop *decr = new decr_Rop(w.ptr);
        decr->set_c(u);
        Adouble v = Adouble(w.t, decr);
        return v;
    }



    Adouble Adouble::operator*(Adouble w){ // v = this * w
        mul_op *mul = new mul_op(this->ptr, w.ptr);
        Adouble v = Adouble(this->t, mul);
        return v;
    }

    Adouble Adouble::operator*(double w){ // v = this * w
        scalmul_op *scalmul = new scalmul_op(this->ptr);
        scalmul->set_c(w);
        Adouble v = Adouble(this->t, scalmul);
        return v;
    }

    Adouble operator*(double u, Adouble w){ // v = u * this
        scalmul_Rop *scalmul = new scalmul_Rop(w.ptr);
        scalmul->set_c(u);
        Adouble v = Adouble(w.t, scalmul);
        return v;
    }



    Adouble Adouble::operator/(Adouble w){ // v = this * w
        div_op *div = new div_op(this->ptr, w.ptr);
        Adouble v = Adouble(this->t, div);
        return v;
    }

    Adouble Adouble::operator/(double w){ // v = this * w
        scaldiv_op *scaldiv = new scaldiv_op(this->ptr);
        scaldiv->set_c(w);
        Adouble v = Adouble(this->t, scaldiv);
        return v;
    }

    Adouble operator/(double u, Adouble w){ // v = u * this
        scaldiv_Rop *scaldiv = new scaldiv_Rop(w.ptr);
        scaldiv->set_c(u);
        Adouble v = Adouble(w.t, scaldiv);
        return v;
    }

    Adouble Adouble::inv(){ // v = u * this
        scaldiv_Rop *scaldiv = new scaldiv_Rop(this->ptr);
        scaldiv->set_c(1.0);
        Adouble v = Adouble(this->t, scaldiv);
        return v;
    }



    Adbool Adouble::operator==(Adouble w){ // b = (this == w)
        boolOp *eq = new boolOp(0, this->ptr, w.ptr);
        Adbool b = Adbool(eq);
        return b;
    }

    Adbool Adouble::operator==(double w){ // b = (this == w)
        boolOp *eq = new boolOp(0, this->ptr, w);
        Adbool b = Adbool(eq);
        return b;
    }

    Adbool operator==(double u, Adouble w){ // b = (u == this)
        boolOp *eq = new boolOp(0, u, w.ptr);
        Adbool b = Adbool(eq);
        return b;
    }



    Adbool Adouble::operator!=(Adouble w){ // b = (this != w)
        boolOp *ne = new boolOp(1, this->ptr, w.ptr);
        Adbool b = Adbool(ne);
        return b;
    }

    Adbool Adouble::operator!=(double w){ // b = (this != w)
        boolOp *ne = new boolOp(1, this->ptr, w);
        Adbool b = Adbool(ne);
        return b;
    }

    Adbool operator!=(double u, Adouble w){ // b = (u != this)
        boolOp *ne = new boolOp(1, u, w.ptr);
        Adbool b = Adbool(ne);
        return b;
    }



    Adbool Adouble::operator<=(Adouble w){ // b = (this <= w)
        boolOp *le = new boolOp(2, this->ptr, w.ptr);
        Adbool b = Adbool(le);
        return b;
    }

    Adbool Adouble::operator<=(double w){ // b = (this <= w)
        boolOp *le = new boolOp(2, this->ptr, w);
        Adbool b = Adbool(le);
        return b;
    }

    Adbool operator<=(double u, Adouble w){ // b = (u <= this)
        boolOp *le = new boolOp(2, u, w.ptr);
        Adbool b = Adbool(le);
        return b;
    }



    Adbool Adouble::operator<(Adouble w){ // b = (this < w)
        boolOp *lt = new boolOp(3, this->ptr, w.ptr);
        Adbool b = Adbool(lt);
        return b;
    }

    Adbool Adouble::operator<(double w){ // b = (this < w)
        boolOp *lt = new boolOp(3, this->ptr, w);
        Adbool b = Adbool(lt);
        return b;
    }

    Adbool operator<(double u, Adouble w){ // b = (u < this)
        boolOp *lt = new boolOp(3, u, w.ptr);
        Adbool b = Adbool(lt);
        return b;
    }



    Adbool Adouble::operator>=(Adouble w){ // b = (this >= w)
        boolOp *ge = new boolOp(4, this->ptr, w.ptr);
        Adbool b = Adbool(ge);
        return b;
    }

    Adbool Adouble::operator>=(double w){ // b = (this >= w)
        boolOp *ge = new boolOp(4, this->ptr, w);
        Adbool b = Adbool(ge);
        return b;
    }

    Adbool operator>=(double u, Adouble w){ // b = (u >= this)
        boolOp *ge = new boolOp(4, u, w.ptr);
        Adbool b = Adbool(ge);
        return b;
    }



    Adbool Adouble::operator>(Adouble w){ // b = (this > w)
        boolOp *gt = new boolOp(5, this->ptr, w.ptr);
        Adbool b = Adbool(gt);
        return b;
    }

    Adbool Adouble::operator>(double w){ // b = (this > w)
        boolOp *gt = new boolOp(5, this->ptr, w);
        Adbool b = Adbool(gt);
        return b;
    }

    Adbool operator>(double u, Adouble w){ // b = (u > this)
        boolOp *gt = new boolOp(5, u, w.ptr);
        Adbool b = Adbool(gt);
        return b;
    }



    Adbool logical_and(Adbool u, Adbool w){
        boolOp *Land = new boolOp(6, u.b, w.b);
        Adbool b = Adbool(Land);
        return b;
    }

    Adbool logical_and(Adbool u, bool w){
        boolOp *Land = new boolOp(6, u.b, w);
        Adbool b = Adbool(Land);
        return b;
    }

    Adbool logical_and(bool u, Adbool w){
        boolOp *Land = new boolOp(6, u, w.b);
        Adbool b = Adbool(Land);
        return b;
    }

    bool logical_and(bool u, bool w){
        return (u and w);
    }



    Adbool logical_or(Adbool u, Adbool w){
        boolOp *Lor = new boolOp(7, u.b, w.b);
        Adbool b = Adbool(Lor);
        return b;
    }

    Adbool logical_or(Adbool u, bool w){
        boolOp *Lor = new boolOp(7, u.b, w);
        Adbool b = Adbool(Lor);
        return b;
    }

    Adbool logical_or(bool u, Adbool w){
        boolOp *Lor = new boolOp(7, u, w.b);
        Adbool b = Adbool(Lor);
        return b;
    }

    bool logical_or(bool u, bool w){
        return (u or w);
    }



    Adouble sin(Adouble u){
        sin_op *sine = new sin_op(u.ptr);
        Adouble v = Adouble(u.t, sine);
        return v;
    }

    Adouble cos(Adouble u){
        cos_op *cosine = new cos_op(u.ptr);
        Adouble v = Adouble(u.t, cosine);
        return v;
    }



    Adouble exp(Adouble u){
        exp_op *expo = new exp_op(u.ptr);
        Adouble v = Adouble(u.t, expo);
        return v;
    }

    Adouble log(Adouble u){
        log_op *loga = new log_op(u.ptr);
        Adouble v = Adouble(u.t, loga);
        return v;
    }



    Adouble atan(Adouble u){
        atan_op *arctan = new atan_op(u.ptr);
        Adouble v = Adouble(u.t, arctan);
        return v;
    }



    Adouble signSquare(Adouble u){
        signSquare_op *signSquare = new signSquare_op(u.ptr);
        Adouble v = Adouble(u.t, signSquare);
        return v;
    }



    Adouble pow(Adouble u, Adouble w){
        return exp(w*log(u));
    }

    Adouble pow(Adouble u, double w){
        return exp(w*log(u));
    }

    Adouble pow(Adouble u, int w){
        int sign_w = w < 0 ? -1 : 1;
        w *= sign_w;

        if(w == 0){
            return 0.0 * u + 1.0; // TODO: huebsch machen
        }

        Adouble v = +u;

        for(int i=1; i < w; i++){
            v = v*u;
        }

        if(sign_w < 0){
            return 1.0/v;
        }

        return v;
    }

    Adouble pow(double u, Adouble w){
        return exp(w*std::log(u));
    }



    Adouble abs(Adouble w){
        Adouble u = +w; // draw a new edge, because if w is dependent it should not be a switching variable.
        Tape *t = u.t;

//        // alternativetweak to reduce number of copies!
//        Adouble u;
//
//        if(w.is_root() || w.is_swVar_node() || w.is_const() || w.is_dependent() || w.is_abs_node){
//            u = +w;
//        }else{
//            u = w;
//        }

        abs_op *absolute = new abs_op(u.ptr, t->get_num_of_sets()); // , u.t->get_var_id());

        // set var_id's
        for(size_t set_idx = 0; set_idx < t->get_num_of_sets(); set_idx++){
            if(u.is_active_swVar(set_idx)){
                absolute->set_var_id(set_idx, t->read_var_id(set_idx));
                t->incr_var_id(set_idx);
                t->tape_swVar_sets[set_idx].push_back(u.ptr);
                t->tape_abs_sets[set_idx].push_back(absolute);
            }
        }

    //    t->abs_ops.push_back(absolute); // when uncommenting this -> it may be need to instantiated

        Adouble v = Adouble(t, absolute);

        return v;
    }

    Adouble abs2(Adouble u){
        abs2_op *abs2 = new abs2_op(u.ptr);
        Adouble v = Adouble(u.t, abs2);
        return v;
    }



    Adouble cond_assign(Adbool b, Adouble u, Adouble w){
        CondElemOp *cond = new CondElemOp(u.ptr, w.ptr);
        cond->set_condition(b.b);

        Adouble v = Adouble(u.t, cond);
        return v;
    }

    Adouble cond_assign(Adbool b, Adouble u, double w){
        ConstInit *wOp = new ConstInit(u.t->get_num_of_sets(), w);
        u.t->add_op(wOp);

        CondElemOp *cond = new CondElemOp(u.ptr, wOp);
        cond->set_condition(b.b);

        Adouble v = Adouble(u.t, cond);
        return v;
    }

    Adouble cond_assign(Adbool b, double u, Adouble w){
        ConstInit *uOp = new ConstInit(w.t->get_num_of_sets(), u);
        w.t->add_op(uOp);

        CondElemOp *cond = new CondElemOp(uOp, w.ptr);
        cond->set_condition(b.b);

        Adouble v = Adouble(w.t, cond);
        return v;
    }

    Adouble cond_assign(bool b, Adouble u, Adouble w){
        boolOp *bb = new boolOp(b);

        CondElemOp *cond = new CondElemOp(u.ptr, w.ptr);
        cond->set_condition(bb);

        Adouble v = Adouble(u.t, cond);
        return v;
    }

    Adouble cond_assign(bool b, Adouble u, double w){
        boolOp *bb = new boolOp(b);

        ConstInit *wOp = new ConstInit(u.t->get_num_of_sets(), w);
        u.t->add_op(wOp);

        CondElemOp *cond = new CondElemOp(u.ptr, wOp);
        cond->set_condition(bb);

        Adouble v = Adouble(u.t, cond);
        return v;
    }

    Adouble cond_assign(bool b, double u, Adouble w){
        boolOp *bb = new boolOp(b);

        ConstInit *uOp = new ConstInit(w.t->get_num_of_sets(), u);
        w.t->add_op(uOp);

        CondElemOp *cond = new CondElemOp(uOp, w.ptr);
        cond->set_condition(bb);

        Adouble v = Adouble(w.t, cond);
        return v;
    }

    double cond_assign(bool b, double u, double w){
        if(b){
            return u;
        } else {
            return w;
        }
    }



//    Adouble::Adouble(Tape *in_t, double in_c){ // init constants
//        num_of_sets = in_t->get_num_of_sets();
//        ptr = new ConstInit(num_of_sets, in_c);
//        t = in_t;
//        t->add_op(ptr);
//    }
};

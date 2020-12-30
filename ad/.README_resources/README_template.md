# cycADa - _cython based algorthmic differentiation_

## Table Of Contents

1. [About cycADa](#about)
2. [On the Math](#maths)
3. [On the Installation](#install)
4. [Just After the Installation](#post_install)
5. [(some) Troubleshooting](#trouble)
6. [(some related) References](#refs)

## <a name="about">About cycADa</a>

__cycADa__ (or _cython based algorthmic differentiation_) 
is a tool for _algorithmic (smooth and piecewise)
differentiation_ (sometimes also refered to as 
_automatic (smooth and piecewise) differentiation_) by 
operator overloading in __c++__ for the use in __python__ 
(i.e. __cycADa__ can be used in either language, but it was primarily developed 
and tuned for the use in __python__).

__cycADa__ offers _1st order_ _sparse_ _forward mode_ for the computation of 
 * secant __CSR__-matrices
 * Jacobian __CSR__-matrices (__note__: special case of secant mode)
 * _secant_ piecewise linear operators in block __CSR__-matrix form
   referred to as _Abs-Linear Form_ or ALF
   (__note__: for piecewise differentiable functions)
 * _tangent_ piecewise linear operators in block __CSR__-matrix form 
   referred to as _Abs-Linear Form_ or ALF
   (__note__: for piecewise differentiable functions and special case
   of secant mode)

By __CSR__ we refer to sparse matrices in the so called and well known 
_compressed sparse row_ format. 

Additionally and as more recent feature __cycADa__ also offers 
 * _secant forward_ smooth directional differentiation
 * _tangent forward_ smooth directional differentiation 
   (__note__: special case of secant mode)
 * _secant forward_ piecewise smooth directional differentiation
   (__note__: for piecewise differentiable functions)
 * _tangent forward_ piecewise smooth directional differentiation
   (__note__: for piecewise differentiable functions and special case
   of secant mode)
 * _secant reverse_ smooth directional differentiation 
   (__note__: _reverse_ mode does not exist in the piecewise smooth setting)
 * _tangent reverse_ smooth directional differentiation 
   (__note__: _reverse_ mode does not exist in the piecewise smooth setting
   and special case of secant mode)

Examples on the use of __cycADa__ from __python__ can be found 
within the /ad/cycADa/examples folder.

At its core __cycADa__ is a __c++__ program with a __cython__ shell around
to make it callable/executable/importable from __python__.
Thus the __c++__ parts need to be compiled prior first use!
As of yet there is no install option to install/configure __cycADa__ globally 
(consider it a feature). 

## <a name="maths">BRIEF Mathematical Excerpt on the Algorithmic Piecewise Differentiation of cycADa</a>

> As a general __note__: if you look for a comprehensive introduction on (smooth) 
> _algorithmic_ or _automatic differentiation_ see e.g. [Grie2008](#Grie2008). It 
> serves as theoretical foundation for the algorithmic piecewise linearization 
> as scratched or hinted herein.

With __cycADa__ you can differentiate functions <!--$ f:\, \mathcal D \subseteq \R^n \to \R^k $--> 
that are chains of so-called elementary operations
 * differentiable, unary <!--$ \varphi:\, \mathcal D_i \subseteq \R \to \R $--> functions 
   with Lipschitz continuous first order derivative, 
   i.e. <!--$ \varphi \in \mathcal C^{1, 1}(\mathcal D_i \subseteq \R, \R) $-->
 * absolute value function
 * a binary addition <!--$ +:\, \R\times\R \to \R $--> 
   (__note__: binary here refers to the fact that the addition takes 
   exactly two summands)
 * as well as actually 3 more binary operations that are implemented and handled 
   by __cycADa__ directly:
      - the binary subtraction <!--$ -:\, \R\times\R \to \R $--> 
      - the binary multiplication <!--$ \cdot:\, \R\times\R \to \R $--> 
      - the binary division <!--$ \div:\, \R\times\R_{\neq 0} \to \R $--> 
    
   but which for the remainder of this excerpt should be understood in 
   terms of the other elementary operations:
      - _subtraction_ (via _addition_): <!--$ x - y = x + (-y) $-->
      - _multiplication_ (via _babylonian identity_): <!--$ x\cdot y = ((x + y)^2 - (x - y)^2)/4 $--> 
        (__note__: __cycADa__ execute and differentiate multiplications 
        directly and does not use this identity! This identity is used here for 
        explanatory purpose, only.)
      - _division_ (via _multiplication_): <!--$ x\div y\ (= x/y)\ = x \cdot y^{-1} $-->
        (__note__: __cycADa__ execute and differentiate divisions directly. 
        See __note__ on _multiplication_)

Thus in theory you may interpret the evaluation of such a vector-valued 
function <!--$ f:\, \mathcal D\subseteq \R^n \to \R^k $--> as a partially ordered 
vector of intermediate functions (each of them advancing by a 
single elementary operation)

<!--[LATEX]
   v_i(x) = \begin{cases}
      \varphi_i(v_j(x)) & j \prec i \text{ if this operation is smooth and unary} \\
      v_j(x) + v_k(x) & j, k \prec i \text{ if this operation is a sum} \\
      |v_j(x)| & j \prec i \text{ if this operation is abs}
   \end{cases}
[LATEX END]-->

Here the <!--$ \prec $--> is the so called _data dependence relation_, 
i.e. <!--$ i \prec j $--> means that the computation of <!--$ v_i(x) $--> requires 
the value of <!--$ v_j(x) $--> beforehand. 
Some <!--$ v_j(x) $--> have no dependencies in which case they are the independent 
inputs <!--$ x = (v_j(x))_{j \in \mathcal J} $--> of the function whereas 
some <!--$ v_i(x) $--> have no successors in which case they are the 
final dependants <!--$ f(x) = (v_i(x))_{i \in \mathcal I} $-->. 
In [Grie2013](#Grie2013) rules for piecewise linearization have been proposed

<!--[LATEX]
   \Delta v_i &= c_{i, j}\cdot \Delta v_j &\text{ if } v_i(x) &= \varphi(v_j(x)) \\
   \Delta v_i &= \Delta v_j + \Delta v_k &\text{ if } v_i(x) &= v_j(x) + v_k(x) \\
   \Delta v_i &= |\mathring v_j + \Delta v_j| - \mathring v_i &\text{ if } v_i(x) &= |v_j(x)|
[LATEX END]-->

where <!--$ \mathring v = (v(\check x) + v(\hat x))/2 $--> for two 
reference points <!--$ \check x, \hat x \in \mathcal D\subseteq \R^n $--> and 

<!--[LATEX]
   c_{i, j} \equiv \begin{cases}
      \frac{\hat v_i - \check v_i}{\hat v_j - \check v_j} &\text{if } \hat v_j \neq \check v_j \\
      \frac{\mathrm d}{\mathrm dv_j} \varphi(\mathring v_j) &\text{if } \hat v_j = \check v_j = \mathring v_j
   \end{cases}
[LATEX END]-->

the secant-tangent slope of the elementary function <!--$ \varphi_i $-->. 

__note__: __cycADa__ rarely uses the secant-tangent slope formula directly but other 
optimized and so called 'singularity-free' formulas (see [Grie2018](#Grie2018) 
for more details).

Also in [Grie2013](#Grie2013) it has been proven for this set of 
rules for piecewise linearization that

<!--[LATEX]
   f(\mathring x + \Delta x) = \mathring f + \Delta f + \mathcal O(\lVert x - \hat x\rVert \lVert x - \check x\rVert)
[LATEX END]-->

where <!--$ \mathring f = (\mathring v_i)_{i \in \mathcal I} $--> is a function evaluation
and <!--$ \Delta f = (\Delta v_i)_{i \in \mathcal I} $--> is
the so called _increment_. This statement simplifies further into the well known 
_Theorem of Taylor for first order expansions_ namely

<!--[LATEX]
   f(\mathring x + \Delta x) = \mathring f + \Delta f + \mathcal O(\lVert x - \mathring x\rVert^2)
[LATEX END]-->

whenever <!--$ \hat x = \check x $--> coalesce.

__note__: If the function <!--$ f:\, \mathcal D\subseteq \R^n\to\R^k$--> does not 
involve any absolute value operation then it already is differentiable in the classical 
meaning of _Fréchet Differentiability_, i.e. <!--$ f \in \mathcal C^{1, 1}(\R^n, \R^k) $-->.
In that case we already find the increment

<!--[LATEX]
   \Delta f = J_f[\mathring x]\cdot \Delta x \qquad = \quad \lim_{h\searrow 0} \frac{f(\mathring x + h\Delta x) - f(\mathring x)}h
[LATEX END]-->

actually to be a secant or tangent directional derivative, 
where <!--$ J_f[\mathring x] $--> either 
is a secant matrix (if <!--$ \hat x \neq \check x $-->) or the 
Jacobian (if <!--$ \hat x = \check x = \mathring x $-->) of <!--$ f $-->.

Because it is often necessary to compute many increments <!--$ \Delta f $--> in
various directions <!--$ \Delta x $--> for a fixed choice the reference 
points <!--$ \hat x, \check x $--> (e.g. for a generalized or piecewise differentiable
Newton method, see [Grie2018](#Grie2018)), 
__cycADa__ can compute secant or tangent piecewise linear operators

<!--[LATEX]
   \begin{bmatrix}
      z(x) \\
      \mathring f + \Delta f
   \end{bmatrix} = 
   \begin{bmatrix}
      c \\
      b
   \end{bmatrix} + 
   \begin{bmatrix}
      Z & L \\
      J & Y
   \end{bmatrix}\cdot
   \begin{bmatrix}
      \mathring x + \Delta x \\
      |z(x)| - |\mathring z|
   \end{bmatrix} 
[LATEX END]-->

referred to as _Abs-Linear Form_ or _ALF_ (in older literature still _Abs-Normal Form_ or _ANF_)
that generalize the idea of secant or Jacobian matrices of a function. For more discussions
regarding the concept of _ALF_ see [Grie2015](#Grie2015) or [Streub2014](#Streub2014).
For another example on how to use piecewise linearization to integrate a system of 
ordinary differential equations with picewise differentiable 
right-hand-side system function (ODE) see [GrHa2018](#GrHa2018).

## <a name="install">On the Installation</a>

__note:__ This installation process was successful many times on __Ubuntu__. 
Someone gave positive feedback for installing on __MacOs__. 
There is no experience for __Windows__ so far!

Make sure to have the following dependencies installed:
 * __cython__
 * __g++__ 
 * __boost__ (c++ libraries)
 * __numpy__
 * __scipy__
 * __pyyaml__

There is a __Makefile__ organizing the installation process:
 1. open __bash__ (or any other shell)
 2. _cd_ your way to .../ad/cycADa/
 3. _execute_ or _call_
    
        make
    
    and follow the instructions

Alternatively (and since there is a setup.py) you can install __cycADa__ e.g.
as you wish and need.

## <a name="post_install">Just after the Installation</a>

Once the __Makefile__ completed its task __cycADa__ is ready to 
use already (-> check .../ad/cycADa/examples).
if you want to use __cycADa__ within your project you will need to 
add __cycADa__ (or more specifically the parent folder of 'ad/') to the __PYTHONPATH__ 
in some way or another. In case you want to extend the __PYTHONPATH__ variable
manually you can e.g. follow:
  
 4. open __bash__
 5. _execute_:
     
        export PYTHONPATH="${PYTHONPATH}:/<path parent folder of 'ad/'>/"
   
## <a name="refs">(some related) References</a>
 * <a name="Grie2008">[Grie2008]</a> Andreas Griewank & Andrea Walther (2008) Evaluating Derivatives: 
   Principles and Techniques of Algorithmic Differentiation - Second Edition,
   Society for Industrial and Applied Mathematics, DOI: 10.1137/1.9780898717761
 * <a name="Grie2013">[Grie2013]</a> Andreas Griewank (2013) On stable piecewise linearization and 
   generalized algorithmic differentiation, Optimization Methods and Software, 
   28:6, 1139-1178, DOI: 10.1080/10556788.2013.796683
 * <a name="Grie2018">[Grie2018]</a> Andreas Griewank, Tom Streubel, Lutz Lehmann, 
   Manuel Radons & Richard Hasenfelder (2018) Piecewise linear secant approximation 
   via algorithmic piecewise differentiation, Optimization Methods and Software, 
   33:4-6, 1108-1126, DOI: 10.1080/10556788.2017.1387256
 * <a name="Grie2015">[Grie2015]</a> Andreas Griewank, Jens-Uwe Bernt, Manuel Radons & Tom 
   Streubel (2015) Solving piecewise linear systems in abs-normal form, Linear 
   Algebra and its Applications, Volume 471, Pages 500-530, ISSN 0024-3795,
   DOI: 10.1016/j.laa.2014.12.017
 * <a name="Streub2014">[Streub2014]</a> Tom Streubel, Andreas Griewank, Manuel Radons & Jens-Uwe 
   Bernt (2014) Representation and Analysis of Piecewise Linear Functions 
   in Abs-Normal Form, In: Pötzsche C., Heuberger C., Kaltenbacher B., 
   Rendl F. (eds) System Modeling and Optimization, CSMO 2013, IFIP Advances in 
   Information and Communication Technology, vol 443. Springer, 
   Berlin, Heidelberg, DOI: 10.1007/978-3-662-45504-3_32
 * <a name="GrHa2018">[GrHa2018]</a> Andreas Griewank, Richard Hasenfelder, Manuel Radons, 
   Lutz Lehmann & Tom Streubel (2018) Integrating Lipschitzian dynamical 
   systems using piecewise algorithmic differentiation, Optimization Methods 
   and Software, 33:4-6, 1089-1107, DOI: 10.1080/10556788.2017.1378653
   
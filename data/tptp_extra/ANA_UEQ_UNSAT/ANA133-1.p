%------------------------------------------------------------------------------
% File     : ANA133-1 : TPTP v9.2.1. Released v8.1.0.
% Domain   : Analysis
% Problem  : Find the integral of x cos x.
% Version  : Especial
% English  : 

% Refs     : [Sma21] Smallbone (2021), Email to Geoff Sutcliffe
% Source   : [Sma21]
% Names    : deriv.p [Sma21]

% Status   : Unsatisfiable
% Rating   : 0.39 v9.1.0, 0.50 v8.2.0, 0.54 v8.1.0
% Syntax   : Number of clauses     :   17 (  17 unt;   0 nHn;   4 RR)
%            Number of literals    :   17 (  17 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    9 (   9 usr;   3 con; 0-2 aty)
%            Number of variables   :   24 (   2 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : 
%------------------------------------------------------------------------------
cnf(commutativity_of_plus,axiom,
    '+'(X,Y) = '+'(Y,X) ).

cnf(associtivity_of_plus,axiom,
    '+'(X,'+'(Y,Z)) = '+'('+'(X,Y),Z) ).

cnf(commutativity_of_times,axiom,
    times(X,Y) = times(Y,X) ).

cnf(associativity_of_times,axiom,
    times(X,times(Y,Z)) = times(times(X,Y),Z) ).

cnf(plus_zero,axiom,
    '+'(zero,X) = X ).

cnf(times_zero,axiom,
    times(zero,X) = zero ).

cnf(times_one,axiom,
    times(one,X) = X ).

cnf(distributivity,axiom,
    times(X,'+'(Y,Z)) = '+'(times(X,Y),times(X,Z)) ).

cnf(minus,axiom,
    '+'(X,minus(X)) = zero ).

cnf(derivative_of_zero,axiom,
    d(zero) = zero ).

cnf(derivative_of_one,axiom,
    d(one) = zero ).

cnf(derivative_of_x,axiom,
    d(x) = one ).

cnf(derivative_of_plus,axiom,
    d('+'(T,U)) = '+'(d(T),d(U)) ).

cnf(derivative_of_times,axiom,
    d(times(T,U)) = '+'(times(T,d(U)),times(U,d(T))) ).

cnf(derivative_of_sin,axiom,
    d(sin(T)) = times(cos(T),d(T)) ).

cnf(derivative_of_cos,axiom,
    d(cos(T)) = minus(times(sin(T),d(T))) ).

cnf(goal,negated_conjecture,
    d(T) != times(x,cos(x)) ).

%------------------------------------------------------------------------------

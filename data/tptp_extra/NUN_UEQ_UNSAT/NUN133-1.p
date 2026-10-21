%------------------------------------------------------------------------------
% File     : NUN133-1 : TPTP v9.2.1. Released v8.1.0.
% Domain   : Number Theory
% Problem  : Nicomachus' theorem - proof by induction, step case
% Version  : Especial.
% English  :

% Refs     : [Sma21] Smallbone (2021), Email to Geoff Sutcliffe
% Source   : [Sma21]
% Names    : nicomachus.p [Sma21]

% Status   : Unsatisfiable
% Rating   : 0.74 v9.1.0, 0.68 v8.2.0, 0.75 v8.1.0
% Syntax   : Number of clauses     :   18 (  18 unt;   0 nHn;   4 RR)
%            Number of literals    :   18 (  18 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    8 (   8 usr;   3 con; 0-2 aty)
%            Number of variables   :   26 (   1 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : 
%------------------------------------------------------------------------------
cnf(plus_comm,axiom,
    '+'(X,Y) = '+'(Y,X) ).

cnf(plus_assoc,axiom,
    '+'(X,'+'(Y,Z)) = '+'('+'(X,Y),Z) ).

cnf(times_comm,axiom,
    times(X,Y) = times(Y,X) ).

cnf(times_assoc,axiom,
    times(X,times(Y,Z)) = times(times(X,Y),Z) ).

cnf(plus_zero,axiom,
    '+'(X,zero) = X ).

cnf(times_zero,axiom,
    times(X,zero) = zero ).

cnf(times_one,axiom,
    times(X,one) = X ).

cnf(distr,axiom,
    times(X,'+'(Y,Z)) = '+'(times(X,Y),times(X,Z)) ).

cnf(distr_001,axiom,
    times('+'(X,Y),Z) = '+'(times(X,Z),times(Y,Z)) ).

cnf(plus_s,axiom,
    '+'(s(X),Y) = s('+'(X,Y)) ).

cnf(times_s,axiom,
    times(s(X),Y) = '+'(Y,times(X,Y)) ).

cnf(sum_zero,axiom,
    sum(zero) = zero ).

cnf(sum_s,axiom,
    sum(s(N)) = '+'(s(N),sum(N)) ).

cnf(cubes_zero,axiom,
    cubes(zero) = zero ).

cnf(cubes_s,axiom,
    cubes(s(N)) = '+'(times(s(N),times(s(N),s(N))),cubes(N)) ).

cnf(plus_sum,axiom,
    '+'(sum(N),sum(N)) = times(N,s(N)) ).

cnf(induction_hypothesis,axiom,
    times(sum(a),sum(a)) = cubes(a) ).

cnf(goal,negated_conjecture,
    times(sum(s(a)),sum(s(a))) != cubes(s(a)) ).

%------------------------------------------------------------------------------

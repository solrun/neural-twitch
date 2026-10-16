%------------------------------------------------------------------------------
% File     : NUM284-10.014 : TPTP v9.2.1. Released v7.3.0.
% Domain   : Puzzles
% Problem  : Calculation of fibonacci numbers
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.96 v9.1.0, 0.95 v9.0.0, 1.00 v7.3.0
% Syntax   : Number of clauses     :    7 (   7 unt;   0 nHn;   3 RR)
%            Number of literals    :    7 (   7 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :   16 (   3 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    6 (   6 usr;   2 con; 0-4 aty)
%            Number of variables   :   14 (   2 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from NUM284-1.014 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq(A,A,B,C) = B ).

cnf(fibonacci_0,axiom,
    fibonacci(n0,s(n0)) = true ).

cnf(fibonacci_1,axiom,
    fibonacci(s(n0),s(n0)) = true ).

cnf(fibonacci_N,axiom,
    ifeq(sum(F1,F2,FN),true,ifeq(sum(N2,s(s(n0)),N),true,ifeq(sum(N1,s(n0),N),true,ifeq(fibonacci(N2,F2),true,ifeq(fibonacci(N1,F1),true,fibonacci(N,FN),true),true),true),true),true) = true ).

cnf(add_0,axiom,
    sum(X,n0,X) = true ).

cnf(add,axiom,
    ifeq(sum(X,Y,Z),true,sum(X,s(Y),s(Z)),true) = true ).

cnf(prove_fibonacci,negated_conjecture,
    fibonacci(s(s(s(s(s(s(s(s(s(s(s(s(s(s(n0)))))))))))))),Result) != true ).

%------------------------------------------------------------------------------

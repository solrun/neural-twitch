%------------------------------------------------------------------------------
% File     : KLE169-10 : TPTP v9.2.1. Released v7.5.0.
% Domain   : Puzzles
% Problem  : Exponential automata
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.65 v9.1.0, 0.73 v9.0.0, 0.64 v8.2.0, 0.67 v8.1.0, 0.75 v7.5.0
% Syntax   : Number of clauses     :   22 (  22 unt;   0 nHn;   2 RR)
%            Number of literals    :   22 (  22 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   13 (  13 usr;   6 con; 0-4 aty)
%            Number of variables   :   41 (   5 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from KLE169+1 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq3(A,A,B,C) = B ).

cnf(ifeq_axiom_001,axiom,
    ifeq2(A,A,B,C) = B ).

cnf(ifeq_axiom_002,axiom,
    ifeq(A,A,B,C) = B ).

cnf(additive_commutativity,axiom,
    addition(A,B) = addition(B,A) ).

cnf(additive_associativity,axiom,
    addition(A,addition(B,C)) = addition(addition(A,B),C) ).

cnf(additive_identity,axiom,
    addition(A,zero) = A ).

cnf(additive_idempotence,axiom,
    addition(A,A) = A ).

cnf(multiplicative_associativity,axiom,
    multiplication(A,multiplication(B,C)) = multiplication(multiplication(A,B),C) ).

cnf(multiplicative_right_identity,axiom,
    multiplication(A,one) = A ).

cnf(multiplicative_left_identity,axiom,
    multiplication(one,A) = A ).

cnf(right_distributivity,axiom,
    multiplication(A,addition(B,C)) = addition(multiplication(A,B),multiplication(A,C)) ).

cnf(left_distributivity,axiom,
    multiplication(addition(A,B),C) = addition(multiplication(A,C),multiplication(B,C)) ).

cnf(right_annihilation,axiom,
    multiplication(A,zero) = zero ).

cnf(left_annihilation,axiom,
    multiplication(zero,A) = zero ).

cnf(order_1,axiom,
    ifeq2(leq(A,B),true,addition(A,B),B) = B ).

cnf(order,axiom,
    ifeq3(addition(A,B),B,leq(A,B),true) = true ).

cnf(star_unfold_right,axiom,
    leq(addition(one,multiplication(A,star(A))),star(A)) = true ).

cnf(star_unfold_left,axiom,
    leq(addition(one,multiplication(star(A),A)),star(A)) = true ).

cnf(star_induction_left,axiom,
    ifeq(leq(addition(multiplication(A,B),C),B),true,leq(multiplication(star(A),C),B),true) = true ).

cnf(star_induction_right,axiom,
    ifeq(leq(addition(multiplication(A,B),C),A),true,leq(multiplication(C,star(B)),A),true) = true ).

cnf(an,axiom,
    sigma = addition(a,b) ).

cnf(a,negated_conjecture,
    leq(multiplication(a,multiplication(b,a)),multiplication(star(sigma),multiplication(a,multiplication(sigma,a)))) != true ).

%------------------------------------------------------------------------------

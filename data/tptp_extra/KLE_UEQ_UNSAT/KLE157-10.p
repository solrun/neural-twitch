%------------------------------------------------------------------------------
% File     : KLE157-10 : TPTP v9.2.1. Released v7.3.0.
% Domain   : Puzzles
% Problem  : Semicommuation law of finite iteration
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 1.00 v7.3.0
% Syntax   : Number of clauses     :   24 (  24 unt;   0 nHn;   2 RR)
%            Number of literals    :   24 (  24 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   13 (  13 usr;   5 con; 0-4 aty)
%            Number of variables   :   45 (   4 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from KLE157+1 to UEQ using [CS18].
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

cnf(idempotence,axiom,
    addition(A,A) = A ).

cnf(multiplicative_associativity,axiom,
    multiplication(A,multiplication(B,C)) = multiplication(multiplication(A,B),C) ).

cnf(multiplicative_right_identity,axiom,
    multiplication(A,one) = A ).

cnf(multiplicative_left_identity,axiom,
    multiplication(one,A) = A ).

cnf(distributivity1,axiom,
    multiplication(A,addition(B,C)) = addition(multiplication(A,B),multiplication(A,C)) ).

cnf(distributivity2,axiom,
    multiplication(addition(A,B),C) = addition(multiplication(A,C),multiplication(B,C)) ).

cnf(left_annihilation,axiom,
    multiplication(zero,A) = zero ).

cnf(star_unfold1,axiom,
    addition(one,multiplication(A,star(A))) = star(A) ).

cnf(star_unfold2,axiom,
    addition(one,multiplication(star(A),A)) = star(A) ).

cnf(star_induction1,axiom,
    ifeq(leq(addition(multiplication(A,C),B),C),true,leq(multiplication(star(A),B),C),true) = true ).

cnf(star_induction2,axiom,
    ifeq(leq(addition(multiplication(C,A),B),C),true,leq(multiplication(B,star(A)),C),true) = true ).

cnf(infty_unfold1,axiom,
    strong_iteration(A) = addition(multiplication(A,strong_iteration(A)),one) ).

cnf(infty_coinduction,axiom,
    ifeq(leq(C,addition(multiplication(A,C),B)),true,leq(C,multiplication(strong_iteration(A),B)),true) = true ).

cnf(isolation,axiom,
    strong_iteration(A) = addition(star(A),multiplication(strong_iteration(A),zero)) ).

cnf(order_1,axiom,
    ifeq2(leq(A,B),true,addition(A,B),B) = B ).

cnf(order,axiom,
    ifeq3(addition(A,B),B,leq(A,B),true) = true ).

cnf(goals,negated_conjecture,
    leq(multiplication(sK2_goals_X0,sK1_goals_X1),multiplication(sK1_goals_X1,sK2_goals_X0)) = true ).

cnf(goals_1,negated_conjecture,
    strong_iteration(addition(sK1_goals_X1,sK2_goals_X0)) != multiplication(strong_iteration(sK1_goals_X1),strong_iteration(sK2_goals_X0)) ).

%------------------------------------------------------------------------------

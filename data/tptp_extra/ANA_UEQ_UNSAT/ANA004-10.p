%------------------------------------------------------------------------------
% File     : ANA004-10 : TPTP v9.2.1. Released v7.5.0.
% Domain   : Puzzles
% Problem  : Lemma 2 for the sum of two continuous functions is continuous
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 1.00 v7.5.0
% Syntax   : Number of clauses     :   25 (  25 unt;   0 nHn;   2 RR)
%            Number of literals    :   25 (  25 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    9 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   23 (  23 usr;   8 con; 0-4 aty)
%            Number of variables   :   44 (   3 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from ANA004-1 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq3(A,A,B,C) = B ).

cnf(ifeq_axiom_001,axiom,
    ifeq2(A,A,B,C) = B ).

cnf(ifeq_axiom_002,axiom,
    ifeq(A,A,B,C) = B ).

cnf(right_identity,axiom,
    add(X,n0) = X ).

cnf(left_identity,axiom,
    add(n0,X) = X ).

cnf(transitivity_of_less_than,axiom,
    ifeq3(less_than(Y,Z),true,ifeq3(less_than(X,Y),true,less_than(X,Z),true),true) = true ).

cnf(axiom_2_1,axiom,
    ifeq3(less_than(n0,Y),true,ifeq3(less_than(n0,X),true,less_than(n0,minimum(X,Y)),true),true) = true ).

cnf(axiom_2_2,axiom,
    ifeq3(less_than(n0,Y),true,ifeq3(less_than(n0,X),true,less_than(minimum(X,Y),X),true),true) = true ).

cnf(axiom_2_3,axiom,
    ifeq3(less_than(n0,Y),true,ifeq3(less_than(n0,X),true,less_than(minimum(X,Y),Y),true),true) = true ).

cnf(axiom_3,axiom,
    ifeq3(less_than(Y,half(Xa)),true,ifeq3(less_than(X,half(Xa)),true,less_than(add(X,Y),Xa),true),true) = true ).

cnf(c_17,axiom,
    ifeq3(less_than(add(absolute(X),absolute(Y)),Xa),true,less_than(absolute(add(X,Y)),Xa),true) = true ).

cnf(axiom_5,axiom,
    add(add(X,Y),Z) = add(X,add(Y,Z)) ).

cnf(axiom_6_1,axiom,
    add(X,Y) = add(Y,X) ).

cnf(axiom_6_2,axiom,
    ifeq3(less_than(n0,Xa),true,less_than(n0,half(Xa)),true) = true ).

cnf(axiom_7,axiom,
    ifeq3(less_than(n0,Xa),true,less_than(n0,half(Xa)),true) = true ).

cnf(axiom_8,axiom,
    minus(add(X,Y)) = add(minus(X),minus(Y)) ).

cnf(c_10,negated_conjecture,
    ifeq3(less_than(n0,X),true,less_than(n0,fp31(X)),true) = true ).

cnf(c_11,negated_conjecture,
    ifeq3(less_than(absolute(add(Y,minus(a))),fp31(X)),true,ifeq3(less_than(n0,X),true,less_than(absolute(add(f(Y),minus(l1))),X),true),true) = true ).

cnf(c_12,negated_conjecture,
    ifeq3(less_than(n0,X),true,less_than(n0,fp32(X)),true) = true ).

cnf(c_13,negated_conjecture,
    ifeq3(less_than(absolute(add(Y,minus(a))),fp32(X)),true,ifeq3(less_than(n0,X),true,less_than(absolute(add(g(Y),minus(l2))),X),true),true) = true ).

cnf(c_14,negated_conjecture,
    less_than(n0,b) = true ).

cnf(c_15,negated_conjecture,
    ifeq3(less_than(n0,X),true,less_than(absolute(add(fp33(X),minus(a))),X),true) = true ).

cnf(reflexivity_of_less_than,axiom,
    ifeq2(less_than(X,X),true,a2,b2) = b2 ).

cnf(c_16,negated_conjecture,
    ifeq(tuple(less_than(n0,X),less_than(absolute(add(add(f(fp33(X)),minus(l1)),add(g(fp33(X)),minus(l2)))),b)),tuple(true,true),a2,b2) = b2 ).

cnf(goal,negated_conjecture,
    a2 != b2 ).

%------------------------------------------------------------------------------

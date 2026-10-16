%------------------------------------------------------------------------------
% File     : MSC015-10.027 : TPTP v9.2.1. Released v7.3.0.
% Domain   : Puzzles
% Problem  : Binary counter k=27
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 1.00 v7.3.0
% Syntax   : Number of clauses     :   30 (  30 unt;   0 nHn;   3 RR)
%            Number of literals    :   30 (  30 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    5 (   5 usr;   3 con; 0-27 aty)
%            Number of variables   :  354 (   1 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from MSC015-1.027 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq(A,A,B,C) = B ).

cnf(init,axiom,
    p(s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0) = true ).

cnf(rule1,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,X22,X23,X24,X25,s0),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,X22,X23,X24,X25,s1),true) = true ).

cnf(rule2,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,X22,X23,X24,s0,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,X22,X23,X24,s1,s0),true) = true ).

cnf(rule3,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,X22,X23,s0,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,X22,X23,s1,s0,s0),true) = true ).

cnf(rule4,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,X22,s0,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,X22,s1,s0,s0,s0),true) = true ).

cnf(rule5,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,s0,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,X21,s1,s0,s0,s0,s0),true) = true ).

cnf(rule6,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,s0,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,X20,s1,s0,s0,s0,s0,s0),true) = true ).

cnf(rule7,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,s0,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,X19,s1,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule8,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,s0,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,X18,s1,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule9,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,s0,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,X17,s1,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule10,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,X16,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule11,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,X15,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule12,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,X14,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule13,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,X13,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule14,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,X12,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule15,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,X11,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule16,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,X10,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule17,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,X9,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule18,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,X8,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,X8,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule19,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,X7,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,X7,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule20,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,X6,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,X6,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule21,axiom,
    ifeq(p(X0,X1,X2,X3,X4,X5,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,X5,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule22,axiom,
    ifeq(p(X0,X1,X2,X3,X4,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,X4,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule23,axiom,
    ifeq(p(X0,X1,X2,X3,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,X3,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule24,axiom,
    ifeq(p(X0,X1,X2,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,X2,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule25,axiom,
    ifeq(p(X0,X1,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,X1,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule26,axiom,
    ifeq(p(X0,s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(X0,s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(rule27,axiom,
    ifeq(p(s0,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1),true,p(s1,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0),true) = true ).

cnf(goal,negated_conjecture,
    p(s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1,s1) != true ).

%------------------------------------------------------------------------------

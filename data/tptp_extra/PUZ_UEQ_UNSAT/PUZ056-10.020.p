%------------------------------------------------------------------------------
% File     : PUZ056-10.020 : TPTP v9.2.1. Released v7.3.0.
% Domain   : Puzzles
% Problem  : Towers of Hanoi k=20
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 1.00 v7.3.0
% Syntax   : Number of clauses     :   34 (  34 unt;   0 nHn;  12 RR)
%            Number of literals    :   34 (  34 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :   41 (   3 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   10 (  10 usr;   6 con; 0-20 aty)
%            Number of variables   :  426 (   4 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from PUZ056-2.020 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq2(A,A,B,C) = B ).

cnf(ifeq_axiom_001,axiom,
    ifeq(A,A,B,C) = B ).

cnf(rule1,axiom,
    ifeq2(p(I,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(J,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true) = true ).

cnf(rule2,axiom,
    ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,I,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,J,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true) = true ).

cnf(rule3,axiom,
    ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,I,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,J,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true) = true ).

cnf(rule4,axiom,
    ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,I,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,J,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true) = true ).

cnf(rule5,axiom,
    ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,I,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,J,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule6,axiom,
    ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,I,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,J,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule7,axiom,
    ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,I,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,J,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule8,axiom,
    ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,I,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,J,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule9,axiom,
    ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,I,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,J,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule10,axiom,
    ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,I,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,J,T10,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule11,axiom,
    ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,I,T11,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,J,T11,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule12,axiom,
    ifeq2(neq(T10,J),true,ifeq2(neq(T10,I),true,ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,I,T12,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,J,T12,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule13,axiom,
    ifeq2(neq(T11,J),true,ifeq2(neq(T11,I),true,ifeq2(neq(T10,J),true,ifeq2(neq(T10,I),true,ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,I,T13,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,J,T13,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule14,axiom,
    ifeq2(neq(T12,J),true,ifeq2(neq(T12,I),true,ifeq2(neq(T11,J),true,ifeq2(neq(T11,I),true,ifeq2(neq(T10,J),true,ifeq2(neq(T10,I),true,ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,I,T14,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,J,T14,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule15,axiom,
    ifeq2(neq(T13,J),true,ifeq2(neq(T13,I),true,ifeq2(neq(T12,J),true,ifeq2(neq(T12,I),true,ifeq2(neq(T11,J),true,ifeq2(neq(T11,I),true,ifeq2(neq(T10,J),true,ifeq2(neq(T10,I),true,ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,I,T15,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,J,T15,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule16,axiom,
    ifeq2(neq(T14,J),true,ifeq2(neq(T14,I),true,ifeq2(neq(T13,J),true,ifeq2(neq(T13,I),true,ifeq2(neq(T12,J),true,ifeq2(neq(T12,I),true,ifeq2(neq(T11,J),true,ifeq2(neq(T11,I),true,ifeq2(neq(T10,J),true,ifeq2(neq(T10,I),true,ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,I,T16,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,J,T16,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule17,axiom,
    ifeq2(neq(T15,J),true,ifeq2(neq(T15,I),true,ifeq2(neq(T14,J),true,ifeq2(neq(T14,I),true,ifeq2(neq(T13,J),true,ifeq2(neq(T13,I),true,ifeq2(neq(T12,J),true,ifeq2(neq(T12,I),true,ifeq2(neq(T11,J),true,ifeq2(neq(T11,I),true,ifeq2(neq(T10,J),true,ifeq2(neq(T10,I),true,ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,I,T17,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,J,T17,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule18,axiom,
    ifeq2(neq(T16,J),true,ifeq2(neq(T16,I),true,ifeq2(neq(T15,J),true,ifeq2(neq(T15,I),true,ifeq2(neq(T14,J),true,ifeq2(neq(T14,I),true,ifeq2(neq(T13,J),true,ifeq2(neq(T13,I),true,ifeq2(neq(T12,J),true,ifeq2(neq(T12,I),true,ifeq2(neq(T11,J),true,ifeq2(neq(T11,I),true,ifeq2(neq(T10,J),true,ifeq2(neq(T10,I),true,ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,I,T18,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,J,T18,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule19,axiom,
    ifeq2(neq(T17,J),true,ifeq2(neq(T17,I),true,ifeq2(neq(T16,J),true,ifeq2(neq(T16,I),true,ifeq2(neq(T15,J),true,ifeq2(neq(T15,I),true,ifeq2(neq(T14,J),true,ifeq2(neq(T14,I),true,ifeq2(neq(T13,J),true,ifeq2(neq(T13,I),true,ifeq2(neq(T12,J),true,ifeq2(neq(T12,I),true,ifeq2(neq(T11,J),true,ifeq2(neq(T11,I),true,ifeq2(neq(T10,J),true,ifeq2(neq(T10,I),true,ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,I,T19),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,J,T19),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(rule20,axiom,
    ifeq2(neq(T18,J),true,ifeq2(neq(T18,I),true,ifeq2(neq(T17,J),true,ifeq2(neq(T17,I),true,ifeq2(neq(T16,J),true,ifeq2(neq(T16,I),true,ifeq2(neq(T15,J),true,ifeq2(neq(T15,I),true,ifeq2(neq(T14,J),true,ifeq2(neq(T14,I),true,ifeq2(neq(T13,J),true,ifeq2(neq(T13,I),true,ifeq2(neq(T12,J),true,ifeq2(neq(T12,I),true,ifeq2(neq(T11,J),true,ifeq2(neq(T11,I),true,ifeq2(neq(T10,J),true,ifeq2(neq(T10,I),true,ifeq2(neq(T9,J),true,ifeq2(neq(T9,I),true,ifeq2(neq(T8,J),true,ifeq2(neq(T8,I),true,ifeq2(neq(T7,J),true,ifeq2(neq(T7,I),true,ifeq2(neq(T6,J),true,ifeq2(neq(T6,I),true,ifeq2(neq(T5,J),true,ifeq2(neq(T5,I),true,ifeq2(neq(T4,J),true,ifeq2(neq(T4,I),true,ifeq2(neq(T3,J),true,ifeq2(neq(T3,I),true,ifeq2(neq(T2,J),true,ifeq2(neq(T2,I),true,ifeq2(neq(T1,J),true,ifeq2(neq(T1,I),true,ifeq2(neq(T0,J),true,ifeq2(neq(T0,I),true,ifeq2(p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,I),true,p(T0,T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,T13,T14,T15,T16,T17,T18,J),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true),true) = true ).

cnf(neq2,axiom,
    neq(s0,s1) = true ).

cnf(neq3,axiom,
    neq(s0,s2) = true ).

cnf(neq4,axiom,
    neq(s1,s0) = true ).

cnf(neq6,axiom,
    neq(s1,s2) = true ).

cnf(neq7,axiom,
    neq(s2,s0) = true ).

cnf(neq8,axiom,
    neq(s2,s1) = true ).

cnf(init,axiom,
    p(s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0,s0) = true ).

cnf(neq1,axiom,
    ifeq(neq(s0,s0),true,a,b) = b ).

cnf(neq5,axiom,
    ifeq(neq(s1,s1),true,a,b) = b ).

cnf(neq9,axiom,
    ifeq(neq(s2,s2),true,a,b) = b ).

cnf(goal,negated_conjecture,
    ifeq(p(s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2,s2),true,a,b) = b ).

cnf(goal_002,negated_conjecture,
    a != b ).

%------------------------------------------------------------------------------

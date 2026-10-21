%------------------------------------------------------------------------------
% File     : TOP050-1 : TPTP v9.2.1. Released v8.1.0.
% Domain   : Topology (Knot theory)
% Problem  : Freedman unknot
% Version  : [FL14] axioms.
% English  :

% Refs     : [FL14]  Fish & Lisitsa (2014), Detecting Unknots via Equationa
%          : [Sma21] Smallbone (2021), Email to Geoff Sutcliffe
% Source   : [Sma21]
% Names    : freedman.p [WM89]

% Status   : Unsatisfiable
% Rating   : 0.17 v9.1.0, 0.27 v9.0.0, 0.18 v8.2.0, 0.25 v8.1.0
% Syntax   : Number of clauses     :   35 (  35 unt;   0 nHn;  32 RR)
%            Number of literals    :   35 (  35 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   34 (  34 usr;  32 con; 0-31 aty)
%            Number of variables   :    6 (   0 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : See https://cgi.csc.liv.ac.uk/~alexei/Unknot/
%------------------------------------------------------------------------------
cnf(involutory_quandle,axiom,
    product(X,X) = X ).

cnf(involutory_quandle_01,axiom,
    product(product(X,Y),Y) = X ).

cnf(involutory_quandle_02,axiom,
    product(product(X,Y),Z) = product(product(X,Z),product(Y,Z)) ).

cnf(knot,axiom,
    product(a1,a31) = a2 ).

cnf(knot_03,axiom,
    product(a2,a25) = a3 ).

cnf(knot_04,axiom,
    product(a3,a29) = a4 ).

cnf(knot_05,axiom,
    product(a4,a11) = a5 ).

cnf(knot_06,axiom,
    product(a5,a15) = a6 ).

cnf(knot_07,axiom,
    product(a7,a19) = a8 ).

cnf(knot_08,axiom,
    product(a8,a5) = a9 ).

cnf(knot_09,axiom,
    product(a9,a17) = a10 ).

cnf(knot_10,axiom,
    product(a10,a7) = a11 ).

cnf(knot_11,axiom,
    product(a11,a5) = a12 ).

cnf(knot_12,axiom,
    product(a12,a19) = a13 ).

cnf(knot_13,axiom,
    product(a13,a7) = a14 ).

cnf(knot_14,axiom,
    product(a14,a17) = a15 ).

cnf(knot_15,axiom,
    product(a15,a5) = a16 ).

cnf(knot_16,axiom,
    product(a16,a19) = a17 ).

cnf(knot_17,axiom,
    product(a17,a9) = a18 ).

cnf(knot_18,axiom,
    product(a18,a15) = a19 ).

cnf(knot_19,axiom,
    product(a19,a11) = a20 ).

cnf(knot_20,axiom,
    product(a20,a29) = a21 ).

cnf(knot_21,axiom,
    product(a21,a25) = a22 ).

cnf(knot_22,axiom,
    product(a22,a31) = a23 ).

cnf(knot_23,axiom,
    product(a23,a21) = a24 ).

cnf(knot_24,axiom,
    product(a24,a3) = a25 ).

cnf(knot_25,axiom,
    product(a25,a23) = a26 ).

cnf(knot_26,axiom,
    product(a26,a1) = a27 ).

cnf(knot_27,axiom,
    product(a27,a21) = a28 ).

cnf(knot_28,axiom,
    product(a28,a3) = a29 ).

cnf(knot_29,axiom,
    product(a29,a1) = a30 ).

cnf(knot_30,axiom,
    product(a30,a23) = a31 ).

cnf(knot_31,axiom,
    product(a31,a3) = a32 ).

cnf(knot_32,axiom,
    product(a32,a21) = a1 ).

cnf(goal,negated_conjecture,
    tuple(a1,a30,a31,a2,a24,a25,a3,a28,a29,a4,a10,a11,a5,a14,a15,a6,a7,a18,a19,a8,a9,a16,a17,a12,a13,a20,a21,a22,a23,a26,a27) != tuple(a2,a31,a32,a3,a25,a26,a4,a29,a30,a5,a11,a12,a6,a15,a16,a7,a8,a19,a20,a9,a10,a17,a18,a13,a14,a21,a22,a23,a24,a27,a28) ).

%------------------------------------------------------------------------------

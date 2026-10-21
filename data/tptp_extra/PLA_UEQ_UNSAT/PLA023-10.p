%------------------------------------------------------------------------------
% File     : PLA023-10 : TPTP v9.2.1. Released v7.3.0.
% Domain   : Puzzles
% Problem  : Block D on A on C
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 1.00 v7.3.0
% Syntax   : Number of clauses     :   32 (  32 unt;   0 nHn;  19 RR)
%            Number of literals    :   32 (  32 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    7 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   18 (  18 usr;   8 con; 0-4 aty)
%            Number of variables   :   40 (   6 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from PLA023-1 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq(A,A,B,C) = B ).

cnf(and_definition,axiom,
    ifeq(holds(Y,State),true,ifeq(holds(X,State),true,holds(and(X,Y),State),true),true) = true ).

cnf(pickup_1,axiom,
    ifeq(differ(X,table),true,ifeq(holds(empty,State),true,ifeq(holds(clear(X),State),true,holds(holding(X),do(pickup(X),State)),true),true),true) = true ).

cnf(pickup_2,axiom,
    ifeq(holds(on(X,Y),State),true,ifeq(holds(empty,State),true,ifeq(holds(clear(X),State),true,holds(clear(Y),do(pickup(X),State)),true),true),true) = true ).

cnf(pickup_3,axiom,
    ifeq(differ(X,Z),true,ifeq(holds(on(X,Y),State),true,holds(on(X,Y),do(pickup(Z),State)),true),true) = true ).

cnf(pickup_4,axiom,
    ifeq(differ(X,Z),true,ifeq(holds(clear(X),State),true,holds(clear(X),do(pickup(Z),State)),true),true) = true ).

cnf(putdown_1,axiom,
    ifeq(holds(holding(X),State),true,ifeq(holds(clear(Y),State),true,holds(empty,do(putdown(X,Y),State)),true),true) = true ).

cnf(putdown_2,axiom,
    ifeq(holds(holding(X),State),true,ifeq(holds(clear(Y),State),true,holds(on(X,Y),do(putdown(X,Y),State)),true),true) = true ).

cnf(putdown_3,axiom,
    ifeq(holds(holding(X),State),true,ifeq(holds(clear(Y),State),true,holds(clear(X),do(putdown(X,Y),State)),true),true) = true ).

cnf(putdown_4,axiom,
    ifeq(holds(on(X,Y),State),true,holds(on(X,Y),do(putdown(Z,W),State)),true) = true ).

cnf(putdown_5,axiom,
    ifeq(differ(Z,Y),true,ifeq(holds(clear(Z),State),true,holds(clear(Z),do(putdown(X,Y),State)),true),true) = true ).

cnf(symmetry_of_differ,axiom,
    ifeq(differ(Y,X),true,differ(X,Y),true) = true ).

cnf(differ_a_b,axiom,
    differ(a,b) = true ).

cnf(differ_a_c,axiom,
    differ(a,c) = true ).

cnf(differ_a_d,axiom,
    differ(a,d) = true ).

cnf(differ_a_table,axiom,
    differ(a,table) = true ).

cnf(differ_b_c,axiom,
    differ(b,c) = true ).

cnf(differ_b_d,axiom,
    differ(b,d) = true ).

cnf(differ_b_table,axiom,
    differ(b,table) = true ).

cnf(differ_c_d,axiom,
    differ(c,d) = true ).

cnf(differ_c_table,axiom,
    differ(c,table) = true ).

cnf(differ_d_table,axiom,
    differ(d,table) = true ).

cnf(initial_state1,axiom,
    holds(on(a,table),s0) = true ).

cnf(initial_state2,axiom,
    holds(on(b,table),s0) = true ).

cnf(initial_state3,axiom,
    holds(on(c,d),s0) = true ).

cnf(initial_state4,axiom,
    holds(on(d,table),s0) = true ).

cnf(initial_state5,axiom,
    holds(clear(a),s0) = true ).

cnf(initial_state6,axiom,
    holds(clear(b),s0) = true ).

cnf(initial_state7,axiom,
    holds(clear(c),s0) = true ).

cnf(initial_state8,axiom,
    holds(empty,s0) = true ).

cnf(clear_table,axiom,
    holds(clear(table),State) = true ).

cnf(prove_DAC,negated_conjecture,
    holds(and(on(d,a),on(a,c)),State) != true ).

%------------------------------------------------------------------------------

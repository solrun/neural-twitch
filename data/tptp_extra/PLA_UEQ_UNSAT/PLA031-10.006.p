%------------------------------------------------------------------------------
% File     : PLA031-10.006 : TPTP v9.2.1. Released v7.3.0.
% Domain   : Puzzles
% Problem  : Driver's log k=06
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 1.00 v7.3.0
% Syntax   : Number of clauses     :  160 ( 160 unt;   0 nHn;  97 RR)
%            Number of literals    :  160 ( 160 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    5 (   1 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   18 (  18 usr;  12 con; 0-11 aty)
%            Number of variables   :  622 (   3 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from PLA031-1.006 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq2(A,A,B,C) = B ).

cnf(ifeq_axiom_001,axiom,
    ifeq(A,A,B,C) = B ).

cnf(load1,axiom,
    ifeq2(s(L,O2,O3,O4,O5,D1,D2,D3,L,T2,T3),true,s(truck1,O2,O3,O4,O5,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load2,axiom,
    ifeq2(s(truck1,O2,O3,O4,O5,D1,D2,D3,L,T2,T3),true,s(L,O2,O3,O4,O5,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load3,axiom,
    ifeq2(s(L,O2,O3,O4,O5,D1,D2,D3,T1,L,T3),true,s(truck2,O2,O3,O4,O5,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load4,axiom,
    ifeq2(s(truck2,O2,O3,O4,O5,D1,D2,D3,T1,L,T3),true,s(L,O2,O3,O4,O5,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load5,axiom,
    ifeq2(s(L,O2,O3,O4,O5,D1,D2,D3,T1,T2,L),true,s(truck3,O2,O3,O4,O5,D1,D2,D3,T1,T2,L),true) = true ).

cnf(load6,axiom,
    ifeq2(s(truck3,O2,O3,O4,O5,D1,D2,D3,T1,T2,L),true,s(L,O2,O3,O4,O5,D1,D2,D3,T1,T2,L),true) = true ).

cnf(load7,axiom,
    ifeq2(s(O1,L,O3,O4,O5,D1,D2,D3,L,T2,T3),true,s(O1,truck1,O3,O4,O5,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load8,axiom,
    ifeq2(s(O1,truck1,O3,O4,O5,D1,D2,D3,L,T2,T3),true,s(O1,L,O3,O4,O5,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load9,axiom,
    ifeq2(s(O1,L,O3,O4,O5,D1,D2,D3,T1,L,T3),true,s(O1,truck2,O3,O4,O5,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load10,axiom,
    ifeq2(s(O1,truck2,O3,O4,O5,D1,D2,D3,T1,L,T3),true,s(O1,L,O3,O4,O5,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load11,axiom,
    ifeq2(s(O1,L,O3,O4,O5,D1,D2,D3,T1,T2,L),true,s(O1,truck3,O3,O4,O5,D1,D2,D3,T1,T2,L),true) = true ).

cnf(load12,axiom,
    ifeq2(s(O1,truck3,O3,O4,O5,D1,D2,D3,T1,T2,L),true,s(O1,L,O3,O4,O5,D1,D2,D3,T1,T2,L),true) = true ).

cnf(load13,axiom,
    ifeq2(s(O1,O2,L,O4,O5,D1,D2,D3,L,T2,T3),true,s(O1,O2,truck1,O4,O5,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load14,axiom,
    ifeq2(s(O1,O2,truck1,O4,O5,D1,D2,D3,L,T2,T3),true,s(O1,O2,L,O4,O5,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load15,axiom,
    ifeq2(s(O1,O2,L,O4,O5,D1,D2,D3,T1,L,T3),true,s(O1,O2,truck2,O4,O5,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load16,axiom,
    ifeq2(s(O1,O2,truck2,O4,O5,D1,D2,D3,T1,L,T3),true,s(O1,O2,L,O4,O5,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load17,axiom,
    ifeq2(s(O1,O2,L,O4,O5,D1,D2,D3,T1,T2,L),true,s(O1,O2,truck3,O4,O5,D1,D2,D3,T1,T2,L),true) = true ).

cnf(load18,axiom,
    ifeq2(s(O1,O2,truck3,O4,O5,D1,D2,D3,T1,T2,L),true,s(O1,O2,L,O4,O5,D1,D2,D3,T1,T2,L),true) = true ).

cnf(load19,axiom,
    ifeq2(s(O1,O2,O3,L,O5,D1,D2,D3,L,T2,T3),true,s(O1,O2,O3,truck1,O5,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load20,axiom,
    ifeq2(s(O1,O2,O3,truck1,O5,D1,D2,D3,L,T2,T3),true,s(O1,O2,O3,L,O5,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load21,axiom,
    ifeq2(s(O1,O2,O3,L,O5,D1,D2,D3,T1,L,T3),true,s(O1,O2,O3,truck2,O5,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load22,axiom,
    ifeq2(s(O1,O2,O3,truck2,O5,D1,D2,D3,T1,L,T3),true,s(O1,O2,O3,L,O5,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load23,axiom,
    ifeq2(s(O1,O2,O3,L,O5,D1,D2,D3,T1,T2,L),true,s(O1,O2,O3,truck3,O5,D1,D2,D3,T1,T2,L),true) = true ).

cnf(load24,axiom,
    ifeq2(s(O1,O2,O3,truck3,O5,D1,D2,D3,T1,T2,L),true,s(O1,O2,O3,L,O5,D1,D2,D3,T1,T2,L),true) = true ).

cnf(load25,axiom,
    ifeq2(s(O1,O2,O3,O4,L,D1,D2,D3,L,T2,T3),true,s(O1,O2,O3,O4,truck1,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load26,axiom,
    ifeq2(s(O1,O2,O3,O4,truck1,D1,D2,D3,L,T2,T3),true,s(O1,O2,O3,O4,L,D1,D2,D3,L,T2,T3),true) = true ).

cnf(load27,axiom,
    ifeq2(s(O1,O2,O3,O4,L,D1,D2,D3,T1,L,T3),true,s(O1,O2,O3,O4,truck2,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load28,axiom,
    ifeq2(s(O1,O2,O3,O4,truck2,D1,D2,D3,T1,L,T3),true,s(O1,O2,O3,O4,L,D1,D2,D3,T1,L,T3),true) = true ).

cnf(load29,axiom,
    ifeq2(s(O1,O2,O3,O4,L,D1,D2,D3,T1,T2,L),true,s(O1,O2,O3,O4,truck3,D1,D2,D3,T1,T2,L),true) = true ).

cnf(load30,axiom,
    ifeq2(s(O1,O2,O3,O4,truck3,D1,D2,D3,T1,T2,L),true,s(O1,O2,O3,O4,L,D1,D2,D3,T1,T2,L),true) = true ).

cnf(board1,axiom,
    ifeq2(neq(D3,truck1),true,ifeq2(neq(D2,truck1),true,ifeq2(s(O1,O2,O3,O4,O5,L,D2,D3,L,T2,T3),true,s(O1,O2,O3,O4,O5,truck1,D2,D3,L,T2,T3),true),true),true) = true ).

cnf(board2,axiom,
    ifeq2(s(O1,O2,O3,O4,O5,truck1,D2,D3,L,T2,T3),true,s(O1,O2,O3,O4,O5,L,D2,D3,L,T2,T3),true) = true ).

cnf(board3,axiom,
    ifeq2(neq(D3,truck2),true,ifeq2(neq(D2,truck2),true,ifeq2(s(O1,O2,O3,O4,O5,L,D2,D3,T1,L,T3),true,s(O1,O2,O3,O4,O5,truck2,D2,D3,T1,L,T3),true),true),true) = true ).

cnf(board4,axiom,
    ifeq2(s(O1,O2,O3,O4,O5,truck2,D2,D3,T1,L,T3),true,s(O1,O2,O3,O4,O5,L,D2,D3,T1,L,T3),true) = true ).

cnf(board5,axiom,
    ifeq2(neq(D3,truck3),true,ifeq2(neq(D2,truck3),true,ifeq2(s(O1,O2,O3,O4,O5,L,D2,D3,T1,T2,L),true,s(O1,O2,O3,O4,O5,truck3,D2,D3,T1,T2,L),true),true),true) = true ).

cnf(board6,axiom,
    ifeq2(s(O1,O2,O3,O4,O5,truck3,D2,D3,T1,T2,L),true,s(O1,O2,O3,O4,O5,L,D2,D3,T1,T2,L),true) = true ).

cnf(board7,axiom,
    ifeq2(neq(D3,truck1),true,ifeq2(neq(D1,truck1),true,ifeq2(s(O1,O2,O3,O4,O5,D1,L,D3,L,T2,T3),true,s(O1,O2,O3,O4,O5,D1,truck1,D3,L,T2,T3),true),true),true) = true ).

cnf(board8,axiom,
    ifeq2(s(O1,O2,O3,O4,O5,D1,truck1,D3,L,T2,T3),true,s(O1,O2,O3,O4,O5,D1,L,D3,L,T2,T3),true) = true ).

cnf(board9,axiom,
    ifeq2(neq(D3,truck2),true,ifeq2(neq(D1,truck2),true,ifeq2(s(O1,O2,O3,O4,O5,D1,L,D3,T1,L,T3),true,s(O1,O2,O3,O4,O5,D1,truck2,D3,T1,L,T3),true),true),true) = true ).

cnf(board10,axiom,
    ifeq2(s(O1,O2,O3,O4,O5,D1,truck2,D3,T1,L,T3),true,s(O1,O2,O3,O4,O5,D1,L,D3,T1,L,T3),true) = true ).

cnf(board11,axiom,
    ifeq2(neq(D3,truck3),true,ifeq2(neq(D1,truck3),true,ifeq2(s(O1,O2,O3,O4,O5,D1,L,D3,T1,T2,L),true,s(O1,O2,O3,O4,O5,D1,truck3,D3,T1,T2,L),true),true),true) = true ).

cnf(board12,axiom,
    ifeq2(s(O1,O2,O3,O4,O5,D1,truck3,D3,T1,T2,L),true,s(O1,O2,O3,O4,O5,D1,L,D3,T1,T2,L),true) = true ).

cnf(board13,axiom,
    ifeq2(neq(D2,truck1),true,ifeq2(neq(D1,truck1),true,ifeq2(s(O1,O2,O3,O4,O5,D1,D2,L,L,T2,T3),true,s(O1,O2,O3,O4,O5,D1,D2,truck1,L,T2,T3),true),true),true) = true ).

cnf(board14,axiom,
    ifeq2(s(O1,O2,O3,O4,O5,D1,D2,truck1,L,T2,T3),true,s(O1,O2,O3,O4,O5,D1,D2,L,L,T2,T3),true) = true ).

cnf(board15,axiom,
    ifeq2(neq(D2,truck2),true,ifeq2(neq(D1,truck2),true,ifeq2(s(O1,O2,O3,O4,O5,D1,D2,L,T1,L,T3),true,s(O1,O2,O3,O4,O5,D1,D2,truck2,T1,L,T3),true),true),true) = true ).

cnf(board16,axiom,
    ifeq2(s(O1,O2,O3,O4,O5,D1,D2,truck2,T1,L,T3),true,s(O1,O2,O3,O4,O5,D1,D2,L,T1,L,T3),true) = true ).

cnf(board17,axiom,
    ifeq2(neq(D2,truck3),true,ifeq2(neq(D1,truck3),true,ifeq2(s(O1,O2,O3,O4,O5,D1,D2,L,T1,T2,L),true,s(O1,O2,O3,O4,O5,D1,D2,truck3,T1,T2,L),true),true),true) = true ).

cnf(board18,axiom,
    ifeq2(s(O1,O2,O3,O4,O5,D1,D2,truck3,T1,T2,L),true,s(O1,O2,O3,O4,O5,D1,D2,L,T1,T2,L),true) = true ).

cnf(drive1,axiom,
    ifeq2(link(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,truck1,D2,D3,S,T2,T3),true,s(O1,O2,O3,O4,O5,truck1,D2,D3,D,T2,T3),true),true) = true ).

cnf(drive2,axiom,
    ifeq2(link(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,truck2,D2,D3,T1,S,T3),true,s(O1,O2,O3,O4,O5,truck2,D2,D3,T1,D,T3),true),true) = true ).

cnf(drive3,axiom,
    ifeq2(link(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,truck3,D2,D3,T1,T2,S),true,s(O1,O2,O3,O4,O5,truck3,D2,D3,T1,T2,D),true),true) = true ).

cnf(drive4,axiom,
    ifeq2(link(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,D1,truck1,D3,S,T2,T3),true,s(O1,O2,O3,O4,O5,D1,truck1,D3,D,T2,T3),true),true) = true ).

cnf(drive5,axiom,
    ifeq2(link(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,D1,truck2,D3,T1,S,T3),true,s(O1,O2,O3,O4,O5,D1,truck2,D3,T1,D,T3),true),true) = true ).

cnf(drive6,axiom,
    ifeq2(link(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,D1,truck3,D3,T1,T2,S),true,s(O1,O2,O3,O4,O5,D1,truck3,D3,T1,T2,D),true),true) = true ).

cnf(drive7,axiom,
    ifeq2(link(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,D1,D2,truck1,S,T2,T3),true,s(O1,O2,O3,O4,O5,D1,D2,truck1,D,T2,T3),true),true) = true ).

cnf(drive8,axiom,
    ifeq2(link(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,D1,D2,truck2,T1,S,T3),true,s(O1,O2,O3,O4,O5,D1,D2,truck2,T1,D,T3),true),true) = true ).

cnf(drive9,axiom,
    ifeq2(link(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,D1,D2,truck3,T1,T2,S),true,s(O1,O2,O3,O4,O5,D1,D2,truck3,T1,T2,D),true),true) = true ).

cnf(walk1,axiom,
    ifeq2(path(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,S,D2,D3,T1,T2,T3),true,s(O1,O2,O3,O4,O5,D,D2,D3,T1,T2,T3),true),true) = true ).

cnf(walk2,axiom,
    ifeq2(path(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,D1,S,D3,T1,T2,T3),true,s(O1,O2,O3,O4,O5,D1,D,D3,T1,T2,T3),true),true) = true ).

cnf(walk3,axiom,
    ifeq2(path(S,D),true,ifeq2(s(O1,O2,O3,O4,O5,D1,D2,S,T1,T2,T3),true,s(O1,O2,O3,O4,O5,D1,D2,D,T1,T2,T3),true),true) = true ).

cnf(neq2,axiom,
    neq(truck1,truck2) = true ).

cnf(neq3,axiom,
    neq(truck1,truck3) = true ).

cnf(neq4,axiom,
    neq(truck1,s0) = true ).

cnf(neq5,axiom,
    neq(truck1,s1) = true ).

cnf(neq6,axiom,
    neq(truck1,s2) = true ).

cnf(neq7,axiom,
    neq(truck1,p0_1) = true ).

cnf(neq8,axiom,
    neq(truck1,p0_2) = true ).

cnf(neq9,axiom,
    neq(truck1,p1_0) = true ).

cnf(neq10,axiom,
    neq(truck2,truck1) = true ).

cnf(neq12,axiom,
    neq(truck2,truck3) = true ).

cnf(neq13,axiom,
    neq(truck2,s0) = true ).

cnf(neq14,axiom,
    neq(truck2,s1) = true ).

cnf(neq15,axiom,
    neq(truck2,s2) = true ).

cnf(neq16,axiom,
    neq(truck2,p0_1) = true ).

cnf(neq17,axiom,
    neq(truck2,p0_2) = true ).

cnf(neq18,axiom,
    neq(truck2,p1_0) = true ).

cnf(neq19,axiom,
    neq(truck3,truck1) = true ).

cnf(neq20,axiom,
    neq(truck3,truck2) = true ).

cnf(neq22,axiom,
    neq(truck3,s0) = true ).

cnf(neq23,axiom,
    neq(truck3,s1) = true ).

cnf(neq24,axiom,
    neq(truck3,s2) = true ).

cnf(neq25,axiom,
    neq(truck3,p0_1) = true ).

cnf(neq26,axiom,
    neq(truck3,p0_2) = true ).

cnf(neq27,axiom,
    neq(truck3,p1_0) = true ).

cnf(neq28,axiom,
    neq(s0,truck1) = true ).

cnf(neq29,axiom,
    neq(s0,truck2) = true ).

cnf(neq30,axiom,
    neq(s0,truck3) = true ).

cnf(neq32,axiom,
    neq(s0,s1) = true ).

cnf(neq33,axiom,
    neq(s0,s2) = true ).

cnf(neq34,axiom,
    neq(s0,p0_1) = true ).

cnf(neq35,axiom,
    neq(s0,p0_2) = true ).

cnf(neq36,axiom,
    neq(s0,p1_0) = true ).

cnf(neq37,axiom,
    neq(s1,truck1) = true ).

cnf(neq38,axiom,
    neq(s1,truck2) = true ).

cnf(neq39,axiom,
    neq(s1,truck3) = true ).

cnf(neq40,axiom,
    neq(s1,s0) = true ).

cnf(neq42,axiom,
    neq(s1,s2) = true ).

cnf(neq43,axiom,
    neq(s1,p0_1) = true ).

cnf(neq44,axiom,
    neq(s1,p0_2) = true ).

cnf(neq45,axiom,
    neq(s1,p1_0) = true ).

cnf(neq46,axiom,
    neq(s2,truck1) = true ).

cnf(neq47,axiom,
    neq(s2,truck2) = true ).

cnf(neq48,axiom,
    neq(s2,truck3) = true ).

cnf(neq49,axiom,
    neq(s2,s0) = true ).

cnf(neq50,axiom,
    neq(s2,s1) = true ).

cnf(neq52,axiom,
    neq(s2,p0_1) = true ).

cnf(neq53,axiom,
    neq(s2,p0_2) = true ).

cnf(neq54,axiom,
    neq(s2,p1_0) = true ).

cnf(neq55,axiom,
    neq(p0_1,truck1) = true ).

cnf(neq56,axiom,
    neq(p0_1,truck2) = true ).

cnf(neq57,axiom,
    neq(p0_1,truck3) = true ).

cnf(neq58,axiom,
    neq(p0_1,s0) = true ).

cnf(neq59,axiom,
    neq(p0_1,s1) = true ).

cnf(neq60,axiom,
    neq(p0_1,s2) = true ).

cnf(neq62,axiom,
    neq(p0_1,p0_2) = true ).

cnf(neq63,axiom,
    neq(p0_1,p1_0) = true ).

cnf(neq64,axiom,
    neq(p0_2,truck1) = true ).

cnf(neq65,axiom,
    neq(p0_2,truck2) = true ).

cnf(neq66,axiom,
    neq(p0_2,truck3) = true ).

cnf(neq67,axiom,
    neq(p0_2,s0) = true ).

cnf(neq68,axiom,
    neq(p0_2,s1) = true ).

cnf(neq69,axiom,
    neq(p0_2,s2) = true ).

cnf(neq70,axiom,
    neq(p0_2,p0_1) = true ).

cnf(neq72,axiom,
    neq(p0_2,p1_0) = true ).

cnf(neq73,axiom,
    neq(p1_0,truck1) = true ).

cnf(neq74,axiom,
    neq(p1_0,truck2) = true ).

cnf(neq75,axiom,
    neq(p1_0,truck3) = true ).

cnf(neq76,axiom,
    neq(p1_0,s0) = true ).

cnf(neq77,axiom,
    neq(p1_0,s1) = true ).

cnf(neq78,axiom,
    neq(p1_0,s2) = true ).

cnf(neq79,axiom,
    neq(p1_0,p0_1) = true ).

cnf(neq80,axiom,
    neq(p1_0,p0_2) = true ).

cnf(map1,axiom,
    path(s0,p0_1) = true ).

cnf(map2,axiom,
    path(p0_1,s0) = true ).

cnf(map3,axiom,
    path(s1,p0_1) = true ).

cnf(map4,axiom,
    path(p0_1,s1) = true ).

cnf(map5,axiom,
    path(s0,p0_2) = true ).

cnf(map6,axiom,
    path(p0_2,s0) = true ).

cnf(map7,axiom,
    path(s2,p0_2) = true ).

cnf(map8,axiom,
    path(p0_2,s2) = true ).

cnf(map9,axiom,
    link(s0,s1) = true ).

cnf(map10,axiom,
    link(s1,s0) = true ).

cnf(map11,axiom,
    link(s1,s2) = true ).

cnf(map12,axiom,
    link(s2,s1) = true ).

cnf(map13,axiom,
    link(s2,s0) = true ).

cnf(map14,axiom,
    link(s0,s2) = true ).

cnf(init,axiom,
    s(s2,s1,s0,s1,s2,s1,s2,s2,s2,s1,s0) = true ).

cnf(neq1,axiom,
    ifeq(neq(truck1,truck1),true,a,b) = b ).

cnf(neq11,axiom,
    ifeq(neq(truck2,truck2),true,a,b) = b ).

cnf(neq21,axiom,
    ifeq(neq(truck3,truck3),true,a,b) = b ).

cnf(neq31,axiom,
    ifeq(neq(s0,s0),true,a,b) = b ).

cnf(neq41,axiom,
    ifeq(neq(s1,s1),true,a,b) = b ).

cnf(neq51,axiom,
    ifeq(neq(s2,s2),true,a,b) = b ).

cnf(neq61,axiom,
    ifeq(neq(p0_1,p0_1),true,a,b) = b ).

cnf(neq71,axiom,
    ifeq(neq(p0_2,p0_2),true,a,b) = b ).

cnf(neq81,axiom,
    ifeq(neq(p1_0,p1_0),true,a,b) = b ).

cnf(goal,negated_conjecture,
    ifeq(s(s1,s0,s2,s2,s1,X6,s1,s2,s1,s2,s0),true,a,b) = b ).

cnf(goal_002,negated_conjecture,
    a != b ).

%------------------------------------------------------------------------------

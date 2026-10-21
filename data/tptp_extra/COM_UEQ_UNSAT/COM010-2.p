%------------------------------------------------------------------------------
% File     : COM010-2 : TPTP v9.2.1. Released v3.2.0.
% Domain   : Computing Theory
% Problem  : Problem about UNITY theory
% Version  : [Pau06] axioms : Reduced > Especial.
% English  :

% Refs     : [Pau06] Paulson (2006), Email to G. Sutcliffe
% Source   : [Pau06]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.00 v8.1.0, 0.05 v7.5.0, 0.04 v7.4.0, 0.09 v7.3.0, 0.05 v7.1.0, 0.00 v7.0.0, 0.05 v6.3.0, 0.06 v6.2.0, 0.07 v6.1.0, 0.06 v6.0.0, 0.14 v5.5.0, 0.11 v5.4.0, 0.00 v5.1.0, 0.07 v5.0.0, 0.00 v4.0.1, 0.07 v4.0.0, 0.08 v3.7.0, 0.11 v3.4.0, 0.12 v3.3.0, 0.07 v3.2.0
% Syntax   : Number of clauses     :    5 (   5 unt;   0 nHn;   4 RR)
%            Number of literals    :    5 (   5 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    7 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   10 (  10 usr;   3 con; 0-4 aty)
%            Number of variables   :    2 (   0 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : The problems in the [Pau06] collection each have very many axioms,
%            of which only a small selection are required for the refutation.
%            The mission is to find those few axioms, after which a refutation
%            can be quite easily found. This version has only the necessary
%            axioms.
%------------------------------------------------------------------------------
cnf(cls_conjecture_0,negated_conjecture,
    c_UNITY_OInit(v_F,t_a) = c_UNITY_OInit(v_G,t_a) ).

cnf(cls_conjecture_1,negated_conjecture,
    c_UNITY_OActs(v_F,t_a) = c_UNITY_OActs(v_G,t_a) ).

cnf(cls_conjecture_2,negated_conjecture,
    c_UNITY_OAllowedActs(v_F,t_a) = c_UNITY_OAllowedActs(v_G,t_a) ).

cnf(cls_conjecture_3,negated_conjecture,
    v_F != v_G ).

cnf(cls_UNITY_Osurjective__mk__program_0,axiom,
    c_UNITY_Omk__program(c_Pair(c_UNITY_OInit(V_y,T_a),c_Pair(c_UNITY_OActs(V_y,T_a),c_UNITY_OAllowedActs(V_y,T_a),tc_set(tc_set(tc_prod(T_a,T_a))),tc_set(tc_set(tc_prod(T_a,T_a)))),tc_set(T_a),tc_prod(tc_set(tc_set(tc_prod(T_a,T_a))),tc_set(tc_set(tc_prod(T_a,T_a))))),T_a) = V_y ).

%------------------------------------------------------------------------------

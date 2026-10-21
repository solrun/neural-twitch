%------------------------------------------------------------------------------
% File     : SWV262-2 : TPTP v9.2.1. Released v3.2.0.
% Domain   : Software Verification (Security)
% Problem  : Cryptographic protocol problem for messages
% Version  : [Pau06] axioms : Reduced > Especial.
% English  :

% Refs     : [Pau06] Paulson (2006), Email to G. Sutcliffe
% Source   : [Pau06]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.00 v9.1.0, 0.09 v9.0.0, 0.05 v8.2.0, 0.08 v8.1.0, 0.10 v7.5.0, 0.08 v7.4.0, 0.13 v7.3.0, 0.05 v7.1.0, 0.00 v7.0.0, 0.11 v6.4.0, 0.16 v6.3.0, 0.12 v6.2.0, 0.14 v6.1.0, 0.12 v6.0.0, 0.24 v5.5.0, 0.21 v5.4.0, 0.07 v5.3.0, 0.08 v5.2.0, 0.14 v5.1.0, 0.07 v5.0.0, 0.00 v4.0.1, 0.07 v4.0.0, 0.08 v3.7.0, 0.11 v3.4.0, 0.12 v3.3.0, 0.14 v3.2.0
% Syntax   : Number of clauses     :    4 (   4 unt;   0 nHn;   1 RR)
%            Number of literals    :    4 (   4 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    8 (   8 usr;   5 con; 0-3 aty)
%            Number of variables   :    8 (   1 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : The problems in the [Pau06] collection each have very many axioms,
%            of which only a small selection are required for the refutation.
%            The mission is to find those few axioms, after which a refutation
%            can be quite easily found. This version has only the necessary
%            axioms.
%------------------------------------------------------------------------------
cnf(cls_conjecture_0,negated_conjecture,
    c_Message_Oparts(c_insert(v_X,c_insert(v_Y,v_H,tc_Message_Omsg),tc_Message_Omsg)) != c_union(c_union(c_Message_Oparts(c_insert(v_X,c_emptyset,tc_Message_Omsg)),c_Message_Oparts(c_insert(v_Y,c_emptyset,tc_Message_Omsg)),tc_Message_Omsg),c_Message_Oparts(v_H),tc_Message_Omsg) ).

cnf(cls_Message_Oparts__Un_0,axiom,
    c_Message_Oparts(c_union(V_G,V_H,tc_Message_Omsg)) = c_union(c_Message_Oparts(V_G),c_Message_Oparts(V_H),tc_Message_Omsg) ).

cnf(cls_Set_OUn__empty__left_0,axiom,
    c_union(c_emptyset,V_y,T_a) = V_y ).

cnf(cls_Set_OUn__insert__left_0,axiom,
    c_union(c_insert(V_a,V_B,T_a),V_C,T_a) = c_insert(V_a,c_union(V_B,V_C,T_a),T_a) ).

%------------------------------------------------------------------------------

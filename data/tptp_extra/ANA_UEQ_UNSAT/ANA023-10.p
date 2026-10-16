%------------------------------------------------------------------------------
% File     : ANA023-10 : TPTP v9.2.1. Released v7.5.0.
% Domain   : Puzzles
% Problem  : Problem about Big-O notation
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.09 v9.1.0, 0.14 v8.2.0, 0.12 v8.1.0, 0.10 v7.5.0
% Syntax   : Number of clauses     :   14 (  14 unt;   0 nHn;   4 RR)
%            Number of literals    :   14 (  14 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   17 (  17 usr;   4 con; 0-4 aty)
%            Number of variables   :   24 (   2 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from ANA023-2 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq2(A,A,B,C) = B ).

cnf(ifeq_axiom_001,axiom,
    ifeq(A,A,B,C) = B ).

cnf(cls_OrderedGroup_Ocomm__monoid__add__class_Oaxioms_0,axiom,
    ifeq2(class_OrderedGroup_Ocomm__monoid__add(T_a),true,c_plus(c_0,V_y,T_a),V_y) = V_y ).

cnf(cls_OrderedGroup_Ocompare__rls__9_0,axiom,
    ifeq(class_OrderedGroup_Opordered__ab__group__add(T_a),true,ifeq(c_lessequals(V_a,c_minus(V_c,V_b,T_a),T_a),true,c_lessequals(c_plus(V_a,V_b,T_a),V_c,T_a),true),true) = true ).

cnf(cls_OrderedGroup_Ocompare__rls__9_1,axiom,
    ifeq(class_OrderedGroup_Opordered__ab__group__add(T_a),true,ifeq(c_lessequals(c_plus(V_a,V_b,T_a),V_c,T_a),true,c_lessequals(V_a,c_minus(V_c,V_b,T_a),T_a),true),true) = true ).

cnf(cls_Orderings_Oorder__class_Oorder__trans_0,axiom,
    ifeq(class_Orderings_Oorder(T_a),true,ifeq(c_lessequals(V_x,V_y,T_a),true,ifeq(c_lessequals(V_y,V_z,T_a),true,c_lessequals(V_x,V_z,T_a),true),true),true) = true ).

cnf(cls_conjecture_1,negated_conjecture,
    c_lessequals(c_0,c_minus(v_k(v_x),v_g(v_x),t_b),t_b) = true ).

cnf(cls_conjecture_2,negated_conjecture,
    c_lessequals(v_k(v_x),v_f(v_x),t_b) = true ).

cnf(cls_conjecture_3,negated_conjecture,
    c_lessequals(c_0,c_minus(v_f(v_x),v_g(v_x),t_b),t_b) != true ).

cnf(clsrel_Orderings_Olinorder_4,axiom,
    ifeq(class_Orderings_Olinorder(T),true,class_Orderings_Oorder(T),true) = true ).

cnf(clsrel_Ring__and__Field_Oordered__idom_23,axiom,
    ifeq(class_Ring__and__Field_Oordered__idom(T),true,class_OrderedGroup_Ocomm__monoid__add(T),true) = true ).

cnf(clsrel_Ring__and__Field_Oordered__idom_33,axiom,
    ifeq(class_Ring__and__Field_Oordered__idom(T),true,class_Orderings_Olinorder(T),true) = true ).

cnf(clsrel_Ring__and__Field_Oordered__idom_54,axiom,
    ifeq(class_Ring__and__Field_Oordered__idom(T),true,class_OrderedGroup_Opordered__ab__group__add(T),true) = true ).

cnf(tfree_tcs,negated_conjecture,
    class_Ring__and__Field_Oordered__idom(t_b) = true ).

%------------------------------------------------------------------------------

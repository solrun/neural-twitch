%------------------------------------------------------------------------------
% File     : ANA034-10 : TPTP v9.2.1. Released v7.3.0.
% Domain   : Puzzles
% Problem  : Problem about Big-O notation
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.26 v9.1.0, 0.32 v8.2.0, 0.33 v8.1.0, 0.25 v7.5.0, 0.42 v7.4.0, 0.43 v7.3.0
% Syntax   : Number of clauses     :   17 (  17 unt;   0 nHn;   6 RR)
%            Number of literals    :   17 (  17 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    8 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   21 (  21 usr;   6 con; 0-4 aty)
%            Number of variables   :   26 (   3 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from ANA034-2 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq2(A,A,B,C) = B ).

cnf(ifeq_axiom_001,axiom,
    ifeq(A,A,B,C) = B ).

cnf(cls_Ring__and__Field_Oabs__mult_0,axiom,
    ifeq2(class_Ring__and__Field_Oordered__idom(T_a),true,c_times(c_HOL_Oabs(V_a,T_a),c_HOL_Oabs(V_b,T_a),T_a),c_HOL_Oabs(c_times(V_a,V_b,T_a),T_a)) = c_HOL_Oabs(c_times(V_a,V_b,T_a),T_a) ).

cnf(cls_Ring__and__Field_Omult__mono_0,axiom,
    ifeq(c_lessequals(c_0,V_b,T_a),true,ifeq(c_lessequals(c_0,V_c,T_a),true,ifeq(c_lessequals(V_a,V_b,T_a),true,ifeq(c_lessequals(V_c,V_d,T_a),true,ifeq(class_Ring__and__Field_Opordered__semiring(T_a),true,c_lessequals(c_times(V_a,V_c,T_a),c_times(V_b,V_d,T_a),T_a),true),true),true),true),true) = true ).

cnf(cls_Ring__and__Field_Omult__nonneg__nonneg_0,axiom,
    ifeq(class_Ring__and__Field_Opordered__cancel__semiring(T_a),true,ifeq(c_lessequals(c_0,V_a,T_a),true,ifeq(c_lessequals(c_0,V_b,T_a),true,c_lessequals(c_0,c_times(V_a,V_b,T_a),T_a),true),true),true) = true ).

cnf(cls_Orderings_Oorder__less__imp__le_0,axiom,
    ifeq(c_less(V_x,V_y,T_a),true,ifeq(class_Orderings_Oorder(T_a),true,c_lessequals(V_x,V_y,T_a),true),true) = true ).

cnf(cls_OrderedGroup_Oabs__ge__zero_0,axiom,
    ifeq(class_OrderedGroup_Olordered__ab__group__abs(T_a),true,c_lessequals(c_0,c_HOL_Oabs(V_a,T_a),T_a),true) = true ).

cnf(cls_conjecture_0,negated_conjecture,
    c_less(c_0,v_c,t_b) = true ).

cnf(cls_conjecture_2,negated_conjecture,
    c_lessequals(c_HOL_Oabs(v_a(v_x),t_b),c_times(v_c,c_HOL_Oabs(v_f(v_x),t_b),t_b),t_b) = true ).

cnf(cls_conjecture_3,negated_conjecture,
    c_lessequals(c_HOL_Oabs(v_b(v_x),t_b),c_times(v_ca,c_HOL_Oabs(v_g(v_x),t_b),t_b),t_b) = true ).

cnf(cls_conjecture_4,negated_conjecture,
    c_times(c_times(v_c,v_ca,t_b),c_HOL_Oabs(c_times(v_f(v_x),v_g(v_x),t_b),t_b),t_b) = c_times(c_times(v_c,c_HOL_Oabs(v_f(v_x),t_b),t_b),c_times(v_ca,c_HOL_Oabs(v_g(v_x),t_b),t_b),t_b) ).

cnf(cls_conjecture_5,negated_conjecture,
    c_lessequals(c_HOL_Oabs(c_times(v_a(v_x),v_b(v_x),t_b),t_b),c_times(c_times(v_c,v_ca,t_b),c_HOL_Oabs(c_times(v_f(v_x),v_g(v_x),t_b),t_b),t_b),t_b) != true ).

cnf(tfree_tcs,negated_conjecture,
    class_Ring__and__Field_Oordered__idom(t_b) = true ).

cnf(clsrel_OrderedGroup_Olordered__ab__group__abs_17,axiom,
    ifeq(class_OrderedGroup_Olordered__ab__group__abs(T),true,class_Orderings_Oorder(T),true) = true ).

cnf(clsrel_Ring__and__Field_Oordered__idom_40,axiom,
    ifeq(class_Ring__and__Field_Oordered__idom(T),true,class_Ring__and__Field_Opordered__cancel__semiring(T),true) = true ).

cnf(clsrel_Ring__and__Field_Oordered__idom_42,axiom,
    ifeq(class_Ring__and__Field_Oordered__idom(T),true,class_Ring__and__Field_Opordered__semiring(T),true) = true ).

cnf(clsrel_Ring__and__Field_Oordered__idom_50,axiom,
    ifeq(class_Ring__and__Field_Oordered__idom(T),true,class_OrderedGroup_Olordered__ab__group__abs(T),true) = true ).

%------------------------------------------------------------------------------

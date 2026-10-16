%------------------------------------------------------------------------------
% File     : SEU323-10 : TPTP v9.2.1. Released v7.3.0.
% Domain   : Puzzles
% Problem  : MPTP bushy problem t51_tops_1
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.04 v9.1.0, 0.09 v8.2.0, 0.08 v8.1.0, 0.05 v7.5.0, 0.08 v7.4.0, 0.09 v7.3.0
% Syntax   : Number of clauses     :   25 (  25 unt;   0 nHn;   6 RR)
%            Number of literals    :   25 (  25 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    8 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   22 (  22 usr;   5 con; 0-4 aty)
%            Number of variables   :   33 (   2 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from SEU323+1 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq2(A,A,B,C) = B ).

cnf(ifeq_axiom_001,axiom,
    ifeq(A,A,B,C) = B ).

cnf(fc3_tops_1,axiom,
    ifeq(element(B,powerset(the_carrier(A))),true,ifeq(closed_subset(B,A),true,ifeq(topological_space(A),true,ifeq(top_str(A),true,open_subset(subset_complement(the_carrier(A),B),A),true),true),true),true) = true ).

cnf(rc6_pre_topc_1,axiom,
    ifeq(topological_space(A),true,ifeq(top_str(A),true,element(sK7_rc6_pre_topc_B(A),powerset(the_carrier(A))),true),true) = true ).

cnf(rc6_pre_topc,axiom,
    ifeq(topological_space(A),true,ifeq(top_str(A),true,closed_subset(sK7_rc6_pre_topc_B(A),A),true),true) = true ).

cnf(involutiveness_k3_subset_1,axiom,
    ifeq2(element(B,powerset(A)),true,subset_complement(A,subset_complement(A,B)),B) = B ).

cnf(reflexivity_r1_tarski,axiom,
    subset(A,A) = true ).

cnf(existence_l1_struct_0,axiom,
    one_sorted_str(sK6_existence_l1_struct_0_A) = true ).

cnf(dt_k3_subset_1,axiom,
    ifeq(element(B,powerset(A)),true,element(subset_complement(A,B),powerset(A)),true) = true ).

cnf(dt_k6_pre_topc,axiom,
    ifeq(element(B,powerset(the_carrier(A))),true,ifeq(top_str(A),true,element(topstr_closure(A,B),powerset(the_carrier(A))),true),true) = true ).

cnf(fc2_tops_1,axiom,
    ifeq(element(B,powerset(the_carrier(A))),true,ifeq(topological_space(A),true,ifeq(top_str(A),true,closed_subset(topstr_closure(A,B),A),true),true),true) = true ).

cnf(fc4_tops_1,axiom,
    ifeq(open_subset(B,A),true,ifeq(element(B,powerset(the_carrier(A))),true,ifeq(topological_space(A),true,ifeq(top_str(A),true,closed_subset(subset_complement(the_carrier(A),B),A),true),true),true),true) = true ).

cnf(existence_l1_pre_topc,axiom,
    top_str(sK5_existence_l1_pre_topc_A) = true ).

cnf(existence_m1_subset_1,axiom,
    element(sK4_existence_m1_subset_1_B(A),A) = true ).

cnf(dt_k1_tops_1,axiom,
    ifeq(element(B,powerset(the_carrier(A))),true,ifeq(top_str(A),true,element(interior(A,B),powerset(the_carrier(A))),true),true) = true ).

cnf(dt_l1_pre_topc,axiom,
    ifeq(top_str(A),true,one_sorted_str(A),true) = true ).

cnf(rc1_tops_1_1,axiom,
    ifeq(topological_space(A),true,ifeq(top_str(A),true,open_subset(sK3_rc1_tops_1_B(A),A),true),true) = true ).

cnf(rc1_tops_1,axiom,
    ifeq(topological_space(A),true,ifeq(top_str(A),true,element(sK3_rc1_tops_1_B(A),powerset(the_carrier(A))),true),true) = true ).

cnf(t3_subset_1,axiom,
    ifeq(subset(A,B),true,element(A,powerset(B)),true) = true ).

cnf(t3_subset,axiom,
    ifeq(element(A,powerset(B)),true,subset(A,B),true) = true ).

cnf(d1_tops_1,axiom,
    ifeq2(element(B,powerset(the_carrier(A))),true,ifeq2(top_str(A),true,subset_complement(the_carrier(A),topstr_closure(A,subset_complement(the_carrier(A),B))),interior(A,B)),interior(A,B)) = interior(A,B) ).

cnf(t51_tops_1,negated_conjecture,
    top_str(sK2_t51_tops_1_A) = true ).

cnf(t51_tops_1_1,negated_conjecture,
    topological_space(sK2_t51_tops_1_A) = true ).

cnf(t51_tops_1_2,negated_conjecture,
    element(sK1_t51_tops_1_B,powerset(the_carrier(sK2_t51_tops_1_A))) = true ).

cnf(t51_tops_1_3,negated_conjecture,
    open_subset(interior(sK2_t51_tops_1_A,sK1_t51_tops_1_B),sK2_t51_tops_1_A) != true ).

%------------------------------------------------------------------------------

%------------------------------------------------------------------------------
% File     : SWV819-1 : TPTP v9.2.1. Released v4.1.0.
% Domain   : Software Verification
% Problem  : Hoare logic with procedures 116_1
% Version  : Especial.
% English  : Completeness is taken relative to completeness of the underlying
%            logic. Two versions of completeness proof: nested single recursion
%            and simultaneous recursion in call rule.

% Refs     : [Nip10] Nipkow (2010), Email to Geoff Sutcliffe
%          : [BN10]  Boehme & Nipkow (2010), Sledgehammer: Judgement Day
% Source   : [Nip10]
% Names    : Hoare-116_1 [Nip10]

% Status   : Unsatisfiable
% Rating   : 0.09 v8.2.0, 0.04 v8.1.0, 0.00 v7.5.0, 0.04 v7.4.0, 0.13 v7.3.0, 0.05 v7.1.0, 0.11 v6.4.0, 0.05 v6.3.0, 0.06 v6.2.0, 0.07 v6.1.0, 0.06 v6.0.0, 0.10 v5.5.0, 0.05 v5.4.0, 0.07 v5.3.0, 0.08 v5.2.0, 0.07 v4.1.0
% Syntax   : Number of clauses     :    5 (   5 unt;   0 nHn;   3 RR)
%            Number of literals    :    5 (   5 equ;   2 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    2 (   1 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    6 (   6 usr;   5 con; 0-3 aty)
%            Number of variables   :    4 (   3 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments :
%------------------------------------------------------------------------------
cnf(cls_tracing__def_0,axiom,
    c_Code__Evaluation_Otracing(V_s,V_x,T_a) = V_x ).

cnf(cls_tracing__def__raw_0,axiom,
    c_Code__Evaluation_Otracing(v_s,v_x,t_a) = v_x ).

cnf(cls_conjecture_0,negated_conjecture,
    v_s != v_t ).

cnf(cls_conjecture_1,negated_conjecture,
    V_s = v_ta ).

cnf(cls_conjecture_2,negated_conjecture,
    v_ta != v_t ).

%------------------------------------------------------------------------------

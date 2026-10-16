%------------------------------------------------------------------------------
% File     : PUZ039-10 : TPTP v9.2.1. Released v7.5.0.
% Domain   : Puzzles
% Problem  : Quo vadis 2
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.22 v9.1.0, 0.32 v9.0.0, 0.27 v8.2.0, 0.25 v8.1.0, 0.35 v7.5.0
% Syntax   : Number of clauses     :   44 (  44 unt;   0 nHn;   2 RR)
%            Number of literals    :   44 (  44 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    7 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   17 (  17 usr;   2 con; 0-12 aty)
%            Number of variables   :  494 (  12 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from PUZ039-1 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq(A,A,B,C) = B ).

cnf(s1_right,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,s1(X,Y),S2,S3,S4,e1(X,s(Y)),E2),true,state(B,V1,V2,V3,V4,H,s1(X,s(Y)),S2,S3,S4,e1(X,Y),E2),true) = true ).

cnf(s1_left,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,s1(X,s(Y)),S2,S3,S4,e1(X,Y),E2),true,state(B,V1,V2,V3,V4,H,s1(X,Y),S2,S3,S4,e1(X,s(Y)),E2),true) = true ).

cnf(s1_down,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,s1(X,Y),S2,S3,S4,e1(s(X),Y),E2),true,state(B,V1,V2,V3,V4,H,s1(s(X),Y),S2,S3,S4,e1(X,Y),E2),true) = true ).

cnf(s1_up,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,s1(s(X),Y),S2,S3,S4,e1(X,Y),E2),true,state(B,V1,V2,V3,V4,H,s1(X,Y),S2,S3,S4,e1(s(X),Y),E2),true) = true ).

cnf(s2_right,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,s2(X,Y),S3,S4,e1(X,s(Y)),E2),true,state(B,V1,V2,V3,V4,H,S1,s2(X,s(Y)),S3,S4,e1(X,Y),E2),true) = true ).

cnf(s2_left,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,s2(X,s(Y)),S3,S4,e1(X,Y),E2),true,state(B,V1,V2,V3,V4,H,S1,s2(X,Y),S3,S4,e1(X,s(Y)),E2),true) = true ).

cnf(s2_down,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,s2(X,Y),S3,S4,e1(s(X),Y),E2),true,state(B,V1,V2,V3,V4,H,S1,s2(s(X),Y),S3,S4,e1(X,Y),E2),true) = true ).

cnf(s2_up,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,s2(s(X),Y),S3,S4,e1(X,Y),E2),true,state(B,V1,V2,V3,V4,H,S1,s2(X,Y),S3,S4,e1(s(X),Y),E2),true) = true ).

cnf(s3_right,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,S2,s3(X,Y),S4,e1(X,s(Y)),E2),true,state(B,V1,V2,V3,V4,H,S1,S2,s3(X,s(Y)),S4,e1(X,Y),E2),true) = true ).

cnf(s3_left,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,S2,s3(X,s(Y)),S4,e1(X,Y),E2),true,state(B,V1,V2,V3,V4,H,S1,S2,s3(X,Y),S4,e1(X,s(Y)),E2),true) = true ).

cnf(s3_down,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,S2,s3(X,Y),S4,e1(s(X),Y),E2),true,state(B,V1,V2,V3,V4,H,S1,S2,s3(s(X),Y),S4,e1(X,Y),E2),true) = true ).

cnf(s3_up,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,S2,s3(s(X),Y),S4,e1(X,Y),E2),true,state(B,V1,V2,V3,V4,H,S1,S2,s3(X,Y),S4,e1(s(X),Y),E2),true) = true ).

cnf(s4_right,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,S2,S3,s4(X,Y),e1(X,s(Y)),E2),true,state(B,V1,V2,V3,V4,H,S1,S2,S3,s4(X,s(Y)),e1(X,Y),E2),true) = true ).

cnf(s4_left,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,S2,S3,s4(X,s(Y)),e1(X,Y),E2),true,state(B,V1,V2,V3,V4,H,S1,S2,S3,s4(X,Y),e1(X,s(Y)),E2),true) = true ).

cnf(s4_down,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,S2,S3,s4(X,Y),e1(s(X),Y),E2),true,state(B,V1,V2,V3,V4,H,S1,S2,S3,s4(s(X),Y),e1(X,Y),E2),true) = true ).

cnf(s4_up,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,S2,S3,s4(s(X),Y),e1(X,Y),E2),true,state(B,V1,V2,V3,V4,H,S1,S2,S3,s4(X,Y),e1(s(X),Y),E2),true) = true ).

cnf(v1_right,axiom,
    ifeq(state(B,v1(X,Y),V2,V3,V4,H,S1,S2,S3,S4,e1(X,s(Y)),e2(s(X),s(Y))),true,state(B,v1(X,s(Y)),V2,V3,V4,H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true) = true ).

cnf(v1_left,axiom,
    ifeq(state(B,v1(X,s(Y)),V2,V3,V4,H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true,state(B,v1(X,Y),V2,V3,V4,H,S1,S2,S3,S4,e1(X,s(Y)),e2(s(X),s(Y))),true) = true ).

cnf(v1_down,axiom,
    ifeq(state(B,v1(X,Y),V2,V3,V4,H,S1,S2,S3,S4,e1(s(s(X)),Y),E2),true,state(B,v1(s(X),Y),V2,V3,V4,H,S1,S2,S3,S4,e1(X,Y),E2),true) = true ).

cnf(v1_up,axiom,
    ifeq(state(B,v1(s(X),Y),V2,V3,V4,H,S1,S2,S3,S4,e1(X,Y),E2),true,state(B,v1(X,Y),V2,V3,V4,H,S1,S2,S3,S4,e1(s(s(X)),Y),E2),true) = true ).

cnf(v2_right,axiom,
    ifeq(state(B,V1,v2(X,Y),V3,V4,H,S1,S2,S3,S4,e1(X,s(Y)),e2(s(X),s(Y))),true,state(B,V1,v2(X,s(Y)),V3,V4,H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true) = true ).

cnf(v2_left,axiom,
    ifeq(state(B,V1,v2(X,s(Y)),V3,V4,H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true,state(B,V1,v2(X,Y),V3,V4,H,S1,S2,S3,S4,e1(X,s(Y)),e2(s(X),s(Y))),true) = true ).

cnf(v2_down,axiom,
    ifeq(state(B,V1,v2(X,Y),V3,V4,H,S1,S2,S3,S4,e1(s(s(X)),Y),E2),true,state(B,V1,v2(s(X),Y),V3,V4,H,S1,S2,S3,S4,e1(X,Y),E2),true) = true ).

cnf(v2_up,axiom,
    ifeq(state(B,V1,v2(s(X),Y),V3,V4,H,S1,S2,S3,S4,e1(X,Y),E2),true,state(B,V1,v2(X,Y),V3,V4,H,S1,S2,S3,S4,e1(s(s(X)),Y),E2),true) = true ).

cnf(v3_right,axiom,
    ifeq(state(B,V1,V2,v3(X,Y),V4,H,S1,S2,S3,S4,e1(X,s(Y)),e2(s(X),s(Y))),true,state(B,V1,V2,v3(X,s(Y)),V4,H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true) = true ).

cnf(v3_left,axiom,
    ifeq(state(B,V1,V2,v3(X,s(Y)),V4,H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true,state(B,V1,V2,v3(X,Y),V4,H,S1,S2,S3,S4,e1(X,s(Y)),e2(s(X),s(Y))),true) = true ).

cnf(v3_down,axiom,
    ifeq(state(B,V1,V2,v3(X,Y),V4,H,S1,S2,S3,S4,e1(s(s(X)),Y),E2),true,state(B,V1,V2,v3(s(X),Y),V4,H,S1,S2,S3,S4,e1(X,Y),E2),true) = true ).

cnf(v3_up,axiom,
    ifeq(state(B,V1,V2,v3(s(X),Y),V4,H,S1,S2,S3,S4,e1(X,Y),E2),true,state(B,V1,V2,v3(X,Y),V4,H,S1,S2,S3,S4,e1(s(s(X)),Y),E2),true) = true ).

cnf(v4_right,axiom,
    ifeq(state(B,V1,V2,V3,v4(X,Y),H,S1,S2,S3,S4,e1(X,s(Y)),e2(s(X),s(Y))),true,state(B,V1,V2,V3,v4(X,s(Y)),H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true) = true ).

cnf(v4_left,axiom,
    ifeq(state(B,V1,V2,V3,v4(X,s(Y)),H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true,state(B,V1,V2,V3,v4(X,Y),H,S1,S2,S3,S4,e1(X,s(Y)),e2(s(X),s(Y))),true) = true ).

cnf(v4_down,axiom,
    ifeq(state(B,V1,V2,V3,v4(X,Y),H,S1,S2,S3,S4,e1(s(s(X)),Y),E2),true,state(B,V1,V2,V3,v4(s(X),Y),H,S1,S2,S3,S4,e1(X,Y),E2),true) = true ).

cnf(v4_up,axiom,
    ifeq(state(B,V1,V2,V3,v4(s(X),Y),H,S1,S2,S3,S4,e1(X,Y),E2),true,state(B,V1,V2,V3,v4(X,Y),H,S1,S2,S3,S4,e1(s(s(X)),Y),E2),true) = true ).

cnf(h_right,axiom,
    ifeq(state(B,V1,V2,V3,V4,h(X,Y),S1,S2,S3,S4,e1(X,s(s(Y))),E2),true,state(B,V1,V2,V3,V4,h(X,s(Y)),S1,S2,S3,S4,e1(X,Y),E2),true) = true ).

cnf(h_left,axiom,
    ifeq(state(B,V1,V2,V3,V4,h(X,s(Y)),S1,S2,S3,S4,e1(X,Y),E2),true,state(B,V1,V2,V3,V4,h(X,Y),S1,S2,S3,S4,e1(X,s(s(Y))),E2),true) = true ).

cnf(h_down,axiom,
    ifeq(state(B,V1,V2,V3,V4,h(X,Y),S1,S2,S3,S4,e1(s(X),Y),e2(s(X),s(Y))),true,state(B,V1,V2,V3,V4,h(s(X),Y),S1,S2,S3,S4,e1(X,Y),e2(X,s(Y))),true) = true ).

cnf(h_up,axiom,
    ifeq(state(B,V1,V2,V3,V4,h(s(X),Y),S1,S2,S3,S4,e1(X,Y),e2(X,s(Y))),true,state(B,V1,V2,V3,V4,h(X,Y),S1,S2,S3,S4,e1(s(X),Y),e2(s(X),s(Y))),true) = true ).

cnf(b_right,axiom,
    ifeq(state(bb(X,Y),V1,V2,V3,V4,H,S1,S2,S3,S4,e1(X,s(s(Y))),e2(s(X),s(s(Y)))),true,state(bb(X,s(Y)),V1,V2,V3,V4,H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true) = true ).

cnf(b_left,axiom,
    ifeq(state(bb(X,s(Y)),V1,V2,V3,V4,H,S1,S2,S3,S4,e1(X,Y),e2(s(X),Y)),true,state(bb(X,Y),V1,V2,V3,V4,H,S1,S2,S3,S4,e1(X,s(s(Y))),e2(s(X),s(s(Y)))),true) = true ).

cnf(b_down,axiom,
    ifeq(state(bb(X,Y),V1,V2,V3,V4,H,S1,S2,S3,S4,e1(s(s(X)),Y),e2(s(s(X)),s(Y))),true,state(bb(s(X),Y),V1,V2,V3,V4,H,S1,S2,S3,S4,e1(X,Y),e2(X,s(Y))),true) = true ).

cnf(b_up,axiom,
    ifeq(state(bb(s(X),Y),V1,V2,V3,V4,H,S1,S2,S3,S4,e1(X,Y),e2(X,s(Y))),true,state(bb(X,Y),V1,V2,V3,V4,H,S1,S2,S3,S4,e1(s(s(X)),Y),e2(s(s(X)),s(Y))),true) = true ).

cnf(swap_blanks,axiom,
    ifeq(state(B,V1,V2,V3,V4,H,S1,S2,S3,S4,e1(X,Y),e2(Q,W)),true,state(B,V1,V2,V3,V4,H,S1,S2,S3,S4,e1(Q,W),e2(X,Y)),true) = true ).

cnf(initial_state,hypothesis,
    state(bb(o,s(o)),v1(o,o),v2(o,s(s(s(o)))),v3(s(s(o)),o),v4(s(s(o)),s(s(s(o)))),h(s(s(o)),s(o)),s1(s(s(s(o))),s(o)),s2(s(s(s(o))),s(s(o))),s3(s(s(s(s(o)))),s(o)),s4(s(s(s(s(o)))),s(s(o))),e1(s(s(s(s(o)))),o),e2(s(s(s(s(o)))),s(s(s(o))))) = true ).

cnf(goal_state,negated_conjecture,
    state(B,V1,V2,V3,v4(s(s(o)),s(s(o))),H,S1,S2,S3,S4,E1,E2) != true ).

%------------------------------------------------------------------------------

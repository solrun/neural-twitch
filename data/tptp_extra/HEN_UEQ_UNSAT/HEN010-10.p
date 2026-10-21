%------------------------------------------------------------------------------
% File     : HEN010-10 : TPTP v9.2.1. Released v7.3.0.
% Domain   : Puzzles
% Problem  : Define X' as identity/X. Then X' = X'/(identity/X')
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.70 v9.1.0, 0.68 v9.0.0, 0.64 v8.2.0, 0.50 v8.1.0, 0.55 v7.5.0, 0.75 v7.4.0, 0.70 v7.3.0
% Syntax   : Number of clauses     :   23 (  23 unt;   0 nHn;   4 RR)
%            Number of literals    :   23 (  23 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    7 (   1 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   12 (  12 usr;   7 con; 0-4 aty)
%            Number of variables   :   53 (   7 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from HEN010-7 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq2(A,A,B,C) = B ).

cnf(ifeq_axiom_001,axiom,
    ifeq(A,A,B,C) = B ).

cnf(quotient_less_equal,axiom,
    ifeq(less_equal(X,Y),true,quotient(X,Y,zero),true) = true ).

cnf(less_equal_quotient,axiom,
    ifeq(quotient(X,Y,zero),true,less_equal(X,Y),true) = true ).

cnf(divisor_existence,axiom,
    ifeq(quotient(X,Y,Z),true,less_equal(Z,X),true) = true ).

cnf(quotient_property,axiom,
    ifeq(quotient(V3,V2,V4),true,ifeq(quotient(V1,Z,V5),true,ifeq(quotient(Y,Z,V2),true,ifeq(quotient(X,Z,V3),true,ifeq(quotient(X,Y,V1),true,less_equal(V4,V5),true),true),true),true),true) = true ).

cnf(zero_is_smallest,axiom,
    less_equal(zero,X) = true ).

cnf(less_equal_and_equal,axiom,
    ifeq2(less_equal(Y,X),true,ifeq2(less_equal(X,Y),true,X,Y),Y) = Y ).

cnf(identity_is_largest,axiom,
    less_equal(X,identity) = true ).

cnf(closure,axiom,
    quotient(X,Y,divide(X,Y)) = true ).

cnf(well_defined,axiom,
    ifeq2(quotient(X,Y,W),true,ifeq2(quotient(X,Y,Z),true,Z,W),W) = W ).

cnf(everything_divide_identity_is_zero,axiom,
    quotient(X,identity,zero) = true ).

cnf(zero_divide_anything_is_zero,axiom,
    quotient(zero,X,zero) = true ).

cnf(x_divide_x_is_zero,axiom,
    quotient(X,X,zero) = true ).

cnf(x_divde_zero_is_x,axiom,
    quotient(X,zero,X) = true ).

cnf(transitivity_of_less_equal,axiom,
    ifeq(less_equal(Y,Z),true,ifeq(less_equal(X,Y),true,less_equal(X,Z),true),true) = true ).

cnf(xQyLEz_implies_xQzLEy,axiom,
    ifeq(quotient(X,Z,W2),true,ifeq(quotient(X,Y,W1),true,ifeq(less_equal(W1,Z),true,less_equal(W2,Y),true),true),true) = true ).

cnf(xLEy_implies_zQyLEzQx,axiom,
    ifeq(quotient(Z,Y,W1),true,ifeq(quotient(Z,X,W2),true,ifeq(less_equal(X,Y),true,less_equal(W1,W2),true),true),true) = true ).

cnf(xLEy_implies_xQzLEyQz,axiom,
    ifeq(quotient(Y,Z,W2),true,ifeq(quotient(X,Z,W1),true,ifeq(less_equal(X,Y),true,less_equal(W1,W2),true),true),true) = true ).

cnf(identity_divide_a,hypothesis,
    quotient(identity,a,idQa) = true ).

cnf(identity_divide_idQa,hypothesis,
    quotient(identity,idQa,idQ_idQa) = true ).

cnf(identity_divide_idQ_idQa,hypothesis,
    quotient(idQa,idQ_idQa,idQa_Q__idQ_idQa) = true ).

cnf(prove_idQa_equals_idQa_Q__idQ_idQa,negated_conjecture,
    idQa != idQa_Q__idQ_idQa ).

%------------------------------------------------------------------------------

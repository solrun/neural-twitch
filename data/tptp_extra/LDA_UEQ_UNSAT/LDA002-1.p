%--------------------------------------------------------------------------
% File     : LDA002-1 : TPTP v9.2.1. Released v1.0.0.
% Domain   : LD-Algebras
% Problem  : Verify 3*2(U2)(UU(UU)) = U1(U3)(UU(UU))
% Version  : [Jec93] (equality) axioms.
% English  :

% Refs     : [Jec93] Jech (1993), LD-Algebras
% Source   : [Jec93]
% Names    : Problem 2 [Jec93]

% Status   : Unsatisfiable
% Rating   : 0.00 v9.1.0, 0.05 v8.2.0, 0.08 v8.1.0, 0.10 v7.5.0, 0.08 v7.4.0, 0.22 v7.3.0, 0.11 v7.1.0, 0.06 v7.0.0, 0.11 v6.4.0, 0.21 v6.3.0, 0.18 v6.2.0, 0.21 v6.1.0, 0.06 v6.0.0, 0.24 v5.5.0, 0.21 v5.4.0, 0.00 v5.2.0, 0.07 v4.1.0, 0.09 v4.0.1, 0.07 v4.0.0, 0.08 v3.7.0, 0.11 v3.4.0, 0.12 v3.3.0, 0.00 v2.2.1, 0.22 v2.2.0, 0.29 v2.1.0, 0.38 v2.0.0
% Syntax   : Number of clauses     :   12 (  12 unt;   0 nHn;  11 RR)
%            Number of literals    :   12 (  12 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   12 (  12 usr;  11 con; 0-2 aty)
%            Number of variables   :    3 (   0 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments :
%--------------------------------------------------------------------------
%----A1: x(yz)=xy(xz)
cnf(a1,axiom,
    f(X,f(Y,Z)) = f(f(X,Y),f(X,Z)) ).

cnf(clause_2,axiom,
    n2 = f(n1,n1) ).

cnf(clause_3,axiom,
    n3 = f(n2,n1) ).

cnf(clause_4,axiom,
    u = f(n2,n2) ).

cnf(clause_5,axiom,
    u1 = f(u,n1) ).

cnf(clause_6,axiom,
    u2 = f(u,n2) ).

cnf(clause_7,axiom,
    u3 = f(u,n3) ).

cnf(clause_8,axiom,
    uu = f(u,u) ).

cnf(clause_9,axiom,
    a = f(f(n3,n2),u2) ).

cnf(clause_10,axiom,
    b = f(u1,u3) ).

cnf(clause_11,axiom,
    v = f(uu,uu) ).

%----3*2*U2*(UU*UU) = U1*U3*(uU*UU)
cnf(prove_equation,negated_conjecture,
    f(a,v) != f(b,v) ).

%--------------------------------------------------------------------------

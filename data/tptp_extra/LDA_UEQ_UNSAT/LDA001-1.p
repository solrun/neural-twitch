%--------------------------------------------------------------------------
% File     : LDA001-1 : TPTP v9.2.1. Released v1.0.0.
% Domain   : LD-Algebras
% Problem  : Verify 3*2*U = UUU, where U = 2*2
% Version  : [Jec93] (equality) axioms.
% English  :

% Refs     : [Jec93] Jech (1993), LD-Algebras
% Source   : [Jec93]
% Names    : Problem 1 [Jec93]

% Status   : Unsatisfiable
% Rating   : 0.00 v7.4.0, 0.04 v7.3.0, 0.00 v7.0.0, 0.05 v6.3.0, 0.06 v6.2.0, 0.07 v6.1.0, 0.06 v6.0.0, 0.10 v5.5.0, 0.11 v5.4.0, 0.00 v2.2.1, 0.22 v2.2.0, 0.29 v2.1.0, 0.25 v2.0.0
% Syntax   : Number of clauses     :    5 (   5 unt;   0 nHn;   4 RR)
%            Number of literals    :    5 (   5 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    5 (   5 usr;   4 con; 0-2 aty)
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

%----3*2*U = U*U*U
cnf(prove_equation,negated_conjecture,
    f(f(n3,n2),u) != f(f(u,u),u) ).

%--------------------------------------------------------------------------

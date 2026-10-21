%--------------------------------------------------------------------------
% File     : LDA007-3 : TPTP v9.2.1. Released v1.0.0.
% Domain   : LD-Algebras (Embedding algebras)
% Problem  : Let g = cr(t). Show that t(tsg) = tt(ts)(tg)
% Version  : [Jec93] axioms : Incomplete > Reduced & Augmented > Incomplete.
% English  :

% Refs     : [Jec93] Jech (1993), LD-Algebras
% Source   : [Jec93]
% Names    : Problem 8 [Jec93]

% Status   : Unsatisfiable
% Rating   : 0.00 v7.4.0, 0.09 v7.3.0, 0.05 v7.1.0, 0.00 v7.0.0, 0.05 v6.3.0, 0.06 v6.2.0, 0.07 v6.1.0, 0.06 v6.0.0, 0.05 v5.4.0, 0.00 v2.2.1, 0.11 v2.2.0, 0.14 v2.1.0, 0.13 v2.0.0
% Syntax   : Number of clauses     :    7 (   7 unt;   0 nHn;   6 RR)
%            Number of literals    :    7 (   7 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    3 (   1 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    9 (   9 usr;   8 con; 0-2 aty)
%            Number of variables   :    3 (   0 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments :
%--------------------------------------------------------------------------
%----Include Embedding algebra axioms
% include('Axioms/LDA001-0.ax').
%--------------------------------------------------------------------------
cnf(a1,axiom,
    f(X,f(Y,Z)) = f(f(X,Y),f(X,Z)) ).

cnf(clause_1,axiom,
    tt = f(t,t) ).

cnf(clause_2,axiom,
    ts = f(t,s) ).

cnf(clause_3,axiom,
    tt_ts = f(tt,ts) ).

cnf(clause_4,axiom,
    tk = f(t,k) ).

cnf(clause_5,axiom,
    tsk = f(ts,k) ).

%----t(tsk) = tt(ts)(tk), where k=crit(t)
cnf(prove_equation,negated_conjecture,
    f(t,tsk) != f(tt_ts,tk) ).

%--------------------------------------------------------------------------

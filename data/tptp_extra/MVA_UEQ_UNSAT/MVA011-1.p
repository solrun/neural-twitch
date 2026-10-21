%------------------------------------------------------------------------------
% File     : MVA011-1 : TPTP v9.2.1. Released v8.1.0.
% Domain   : MV-algebras
% Problem  : 1 @ (x \ 1) = x \ 1
% Version  : [Ver10] (equality) axioms.
% English  :

% Refs     : [GT05]  Galatos & Tsinakis (2005), Generalized MV-algebras
%          : [GJ+07] Galatos et al. (2007), Residuated Lattices: An Algebra
%          : [Ver10] Veroff (2010), Email to Geoff Sutcliffe
%          : [Sma21] Smallbone (2021), Email to Geoff Sutcliffe
% Source   : [Ver10]
% Names    : gmv11.p [Sma21]

% Status   : Unsatisfiable
% Rating   : 0.74 v9.1.0, 0.73 v8.2.0, 0.71 v8.1.0
% Syntax   : Number of clauses     :   19 (  19 unt;   0 nHn;   1 RR)
%            Number of literals    :   19 (  19 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    5 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    8 (   8 usr;   2 con; 0-2 aty)
%            Number of variables   :   39 (   6 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : See https://www.cs.unm.edu/~veroff/GMV/
%------------------------------------------------------------------------------
include('Axioms/MVA001-0.ax').
%------------------------------------------------------------------------------
cnf(goal,negated_conjecture,
    at(unit,ld(x,unit)) != ld(x,unit) ).

%------------------------------------------------------------------------------

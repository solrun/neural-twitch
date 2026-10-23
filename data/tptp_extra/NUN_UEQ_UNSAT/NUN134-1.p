%------------------------------------------------------------------------------
% File     : NUN134-1 : TPTP v9.2.1. Released v8.1.0.
% Note     : Modified for neural-twitch: the quoted symbol '+' is renamed plus,
%            because Twee prints '+' infix and Twitch's term parser
%            only reads prefix terms.
% Domain   : Number Theory
% Problem  : Sum of first n natural numbers is n(n+1)/2 - step case
% Version  : Especial.
% English  :

% Refs     : [Sma21] Smallbone (2021), Email to Geoff Sutcliffe
% Source   : [Sma21]
% Names    : squares.p [Sma21]

% Status   : Unsatisfiable
% Rating   : 0.22 v9.1.0, 0.32 v9.0.0, 0.27 v8.2.0, 0.29 v8.1.0
% Syntax   : Number of clauses     :   15 (  15 unt;   0 nHn;   3 RR)
%            Number of literals    :   15 (  15 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    4 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    7 (   7 usr;   3 con; 0-2 aty)
%            Number of variables   :   24 (   1 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments :
%------------------------------------------------------------------------------
cnf(plus_comm,axiom,
    plus(X,Y) = plus(Y,X) ).

cnf(plus_assoc,axiom,
    plus(X,plus(Y,Z)) = plus(plus(X,Y),Z) ).

cnf(times_comm,axiom,
    times(X,Y) = times(Y,X) ).

cnf(times_assoc,axiom,
    times(X,times(Y,Z)) = times(times(X,Y),Z) ).

cnf(plus_zero,axiom,
    plus(X,zero) = X ).

cnf(times_zero,axiom,
    times(X,zero) = zero ).

cnf(times_one,axiom,
    times(X,one) = X ).

cnf(distr,axiom,
    times(X,plus(Y,Z)) = plus(times(X,Y),times(X,Z)) ).

cnf(distr_001,axiom,
    times(plus(X,Y),Z) = plus(times(X,Z),times(Y,Z)) ).

cnf(plus_s,axiom,
    plus(s(X),Y) = s(plus(X,Y)) ).

cnf(times_s,axiom,
    times(s(X),Y) = plus(Y,times(X,Y)) ).

cnf(sum_zero,axiom,
    sum(zero) = zero ).

cnf(sum_s,axiom,
    sum(s(N)) = plus(s(N),sum(N)) ).

cnf(induction_hypothesis,axiom,
    plus(sum(a),sum(a)) = times(a,s(a)) ).

cnf(goal,negated_conjecture,
    plus(sum(s(a)),sum(s(a))) != times(s(a),s(s(a))) ).

%------------------------------------------------------------------------------

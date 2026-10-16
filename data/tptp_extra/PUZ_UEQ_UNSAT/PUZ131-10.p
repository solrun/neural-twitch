%------------------------------------------------------------------------------
% File     : PUZ131-10 : TPTP v9.2.1. Released v7.5.0.
% Domain   : Puzzles
% Problem  : Victor teaches Michael
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 0.22 v9.1.0, 0.18 v8.2.0, 0.17 v8.1.0, 0.05 v7.5.0
% Syntax   : Number of clauses     :   21 (  21 unt;   0 nHn;   9 RR)
%            Number of literals    :   21 (  21 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    7 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   19 (  19 usr;   7 con; 0-4 aty)
%            Number of variables   :   16 (   1 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from PUZ131+1 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq(A,A,B,C) = B ).

cnf(student_type,axiom,
    student(sK7_student_type_A) = true ).

cnf(professor_type,axiom,
    professor(sK6_professor_type_A) = true ).

cnf(course_type,axiom,
    course(sK5_course_type_A) = true ).

cnf(michael_type,axiom,
    student(michael) = true ).

cnf(victor_type,axiom,
    professor(victor) = true ).

cnf(csc410_type,axiom,
    course(csc410) = true ).

cnf(coordinator_of_type,axiom,
    ifeq(course(A),true,professor(coordinatorof(A)),true) = true ).

cnf(student_enrolled_axiom_1,axiom,
    ifeq(student(X),true,enrolled(X,sK4_student_enrolled_axiom_Y(X)),true) = true ).

cnf(student_enrolled_axiom,axiom,
    ifeq(student(X),true,course(sK4_student_enrolled_axiom_Y(X)),true) = true ).

cnf(professor_teaches_1,axiom,
    ifeq(professor(X),true,teaches(X,sK3_professor_teaches_Y(X)),true) = true ).

cnf(professor_teaches,axiom,
    ifeq(professor(X),true,course(sK3_professor_teaches_Y(X)),true) = true ).

cnf(course_enrolled_1,axiom,
    ifeq(course(X),true,enrolled(sK2_course_enrolled_Y(X),X),true) = true ).

cnf(course_enrolled,axiom,
    ifeq(course(X),true,student(sK2_course_enrolled_Y(X)),true) = true ).

cnf(course_teaches_1,axiom,
    ifeq(course(X),true,teaches(sK1_course_teaches_Y(X),X),true) = true ).

cnf(course_teaches,axiom,
    ifeq(course(X),true,professor(sK1_course_teaches_Y(X)),true) = true ).

cnf(coordinator_teaches,axiom,
    ifeq(course(X),true,teaches(coordinatorof(X),X),true) = true ).

cnf(student_enrolled_taught,axiom,
    ifeq(teaches(Z,Y),true,ifeq(enrolled(X,Y),true,ifeq(course(Y),true,ifeq(professor(Z),true,ifeq(student(X),true,taughtby(X,Z),true),true),true),true),true) = true ).

cnf(michael_enrolled_csc410_axiom,axiom,
    enrolled(michael,csc410) = true ).

cnf(victor_coordinator_csc410_axiom,axiom,
    coordinatorof(csc410) = victor ).

cnf(teaching_conjecture,negated_conjecture,
    taughtby(michael,victor) != true ).

%------------------------------------------------------------------------------

%------------------------------------------------------------------------------
% File     : SWV234-10 : TPTP v9.2.1. Released v7.5.0.
% Domain   : Puzzles
% Problem  : XOR typecast attack on the 4758 CCA API
% Version  : Especial.
% English  :

% Refs     : [CS18]  Claessen & Smallbone (2018), Efficient Encodings of Fi
%          : [Sma18] Smallbone (2018), Email to Geoff Sutcliffe
% Source   : [Sma18]
% Names    :

% Status   : Unsatisfiable
% Rating   : 1.00 v7.5.0
% Syntax   : Number of clauses     :   27 (  27 unt;   0 nHn;  10 RR)
%            Number of literals    :   27 (  27 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    9 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :   17 (  17 usr;  12 con; 0-4 aty)
%            Number of variables   :   44 (   2 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Converted from SWV234+1 to UEQ using [CS18].
%------------------------------------------------------------------------------
cnf(ifeq_axiom,axiom,
    ifeq(A,A,B,C) = B ).

cnf(xor_commutative,axiom,
    xor(X1,X2) = xor(X2,X1) ).

cnf(xor_associative,axiom,
    xor(X1,xor(X2,X3)) = xor(xor(X1,X2),X3) ).

cnf(encryption_decryption_cancellation,axiom,
    decrypt(X1,crypt(X1,X2)) = X2 ).

cnf(xor_rules_1,axiom,
    xor(X1,id) = X1 ).

cnf(xor_rules_2,axiom,
    xor(X1,X1) = id ).

cnf(key_import,axiom,
    ifeq(p(crypt(xor(km,imp),Xkek2)),true,ifeq(p(crypt(xor(Xkek1,Xtype1),Xk1)),true,ifeq(p(Xtype2),true,p(crypt(xor(km,Xtype2),decrypt(xor(Xkek2,Xtype2),crypt(xor(Xkek1,Xtype1),Xk1)))),true),true),true) = true ).

cnf(key_export,axiom,
    ifeq(p(crypt(xor(km,exp),Xkek1)),true,ifeq(p(crypt(xor(km,Xtype),Xk1)),true,ifeq(p(Xtype),true,p(crypt(xor(Xkek1,Xtype),Xk1)),true),true),true) = true ).

cnf(key_part_import___part_1,axiom,
    ifeq(p(Xtype),true,ifeq(p(Xk),true,p(crypt(xor(km,xor(kp,Xtype)),Xk)),true),true) = true ).

cnf(key_part_import___part_2,axiom,
    ifeq(p(crypt(xor(km,xor(kp,Xtype)),Xk2)),true,ifeq(p(Xtype),true,ifeq(p(Xk1),true,p(crypt(xor(km,xor(Xtype,kp)),xor(Xk1,Xk2))),true),true),true) = true ).

cnf(key_part_import___part_3,axiom,
    ifeq(p(crypt(xor(km,xor(Xtype,kp)),Xk2)),true,ifeq(p(Xtype),true,ifeq(p(Xk1),true,p(crypt(xor(km,Xtype),xor(Xk2,Xk1))),true),true),true) = true ).

cnf(encrypt_data,axiom,
    ifeq(p(crypt(xor(km,data),Xk1)),true,ifeq(p(X1),true,p(crypt(Xk1,X1)),true),true) = true ).

cnf(decrypt_data,axiom,
    ifeq(p(crypt(xor(km,data),Xk1)),true,ifeq(p(X1),true,p(decrypt(Xk1,X1)),true),true) = true ).

cnf(key_translate,axiom,
    ifeq(p(crypt(xor(km,exp),Xkek2)),true,ifeq(p(crypt(xor(km,imp),Xkek1)),true,ifeq(p(crypt(Xk,Xk1)),true,ifeq(p(Xtype2),true,p(crypt(xor(Xkek2,Xtype),decrypt(xor(Xtype2,Xkek1),crypt(Xk,Xk1)))),true),true),true),true) = true ).

cnf(combine_with_XOR,axiom,
    ifeq(p(X2),true,ifeq(p(X1),true,p(xor(X1,X2)),true),true) = true ).

cnf(decrypt_knowledge,axiom,
    ifeq(p(crypt(X1,X2)),true,ifeq(p(X1),true,p(X2),true),true) = true ).

cnf(encrypt_knowledge,axiom,
    ifeq(p(X2),true,ifeq(p(X1),true,p(crypt(X1,X2)),true),true) = true ).

cnf(inital_knowledge_of_intruder_1,axiom,
    p(kp) = true ).

cnf(inital_knowledge_of_intruder_2,axiom,
    p(imp) = true ).

cnf(inital_knowledge_of_intruder_3,axiom,
    p(data) = true ).

cnf(inital_knowledge_of_intruder_4,axiom,
    p(id) = true ).

cnf(inital_knowledge_of_intruder_5,axiom,
    p(pin) = true ).

cnf(pin_key_encrypted_for_transfer,axiom,
    p(crypt(xor(kek,pin),pp)) = true ).

cnf(an_account_number,axiom,
    p(a) = true ).

cnf(key_part,axiom,
    p(k3) = true ).

cnf(partially_completed_key,axiom,
    p(crypt(xor(km,xor(kp,imp)),xor(kek,k3))) = true ).

cnf(find_pin,negated_conjecture,
    p(crypt(pp,a)) != true ).

%------------------------------------------------------------------------------

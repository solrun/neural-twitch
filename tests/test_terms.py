from nt.terms import (App, Var, ParseError, canonical, is_linear, normalize,
                      parse, parse_definition, size, skeleton_weight)
import pytest


def test_parse_and_print_roundtrip():
    s = "f(f(A, B), f(A, c))"
    assert str(parse(s)) == s


def test_alpha_normalization_identifies_renamings():
    assert canonical("f(A, A)") == canonical("f(Y, Y)") == "f(X0, X0)"
    assert canonical("f(A, B)") != canonical("f(A, A)")


def test_first_occurrence_order():
    assert str(normalize(parse("f(B, g(A, B))"))) == "f(X0, g(X1, X0))"


def test_definition_line():
    name, body = parse_definition("fn_2(A) = f(A, A)")
    assert name == "fn_2" and body == App("f", (Var("A"), Var("A")))


def test_higher_order_rejected():
    with pytest.raises(ParseError):
        parse("B(B(A))")
    assert canonical("fn_4(A, B) = B(B(A))") is None


def test_bare_variable_rejected():
    assert canonical("X") is None


def test_weights_match_twitch_example():
    # plus(times(x,y),times(x,z)): skeleton weight 3 (Twitch Sect. 4.1)
    t = parse("plus(times(X, Y), times(X, Z))")
    assert skeleton_weight(t) == 3
    assert size(t) == 7
    assert not is_linear(t)


def test_constants():
    assert canonical("fn_5 = multiply(b, a)") == "multiply(b, a)"

#!/usr/bin/env python3
"""
divisibility.py -- the single divisibility predicate used by the OFFLINE gate components
(verify_notebook_I.py, freeze_check.py, test_freeze_gate_mutations.py).

Contract
--------
polynomially_divisible(poly, factor) is True iff poly/factor, after cancellation, is a
polynomial in its free symbols. A nonzero *rational constant* quotient counts as polynomial
(1/2 is a polynomial of degree 0 over QQ); a transcendental quotient such as sin(x) does not.
factor must be nonzero; a zero factor raises ValueError.

Why this file exists
--------------------
Two revisions shipped a "test" of the form  q = cancel(R/F); assert R - F*q == 0, which is a
TAUTOLOGY. A later revision guarded against that by string matching, which an adversarial
mutation defeated. The gate therefore tests BEHAVIOUR: one predicate, positive and negative
controls, and END-TO-END package mutations (test_freeze_gate_mutations.py) that bypass the
predicate at its call sites and require the whole gate to go red.
"""
import sympy as sp

__all__ = ["polynomially_divisible", "self_test"]


def polynomially_divisible(poly, factor):
    factor = sp.sympify(factor)
    if sp.simplify(factor) == 0:
        raise ValueError("factor must be nonzero")
    poly = sp.expand(sp.sympify(poly))
    q = sp.cancel(sp.together(poly / factor))
    gens = sorted(q.free_symbols, key=sp.default_sort_key)
    if gens and not q.is_polynomial(*gens):
        return False                      # e.g. sin(x): quotient is not polynomial
    return sp.simplify(sp.expand(poly - sp.expand(factor * q))) == 0


def self_test(verbose=False):
    """Positive AND negative controls, including the contract cases."""
    a, m, J1, J2, x = sp.symbols("alpha mu J1 J2 x")
    F = m**2 + a*m - 1
    G = x + 1
    cases = [
        ("positive: F*(J1-J2) / F",                       F*(J1 - J2),          F, True),
        ("positive: mu*(J1-J2)*(J1+J2)*F / F",            m*(J1-J2)*(J1+J2)*F,  F, True),
        ("positive: 0 / F",                               sp.S(0),              F, True),
        ("positive: rational-constant quotient (G/2)/G",  G/2,                  G, True),
        ("NEGATIVE: (F + 1) / F",                         F + 1,                F, False),
        ("NEGATIVE: mu / F",                              m,                    F, False),
        ("NEGATIVE: (F*(J1-J2) + mu) / F",                F*(J1-J2) + m,        F, False),
        ("NEGATIVE: (mu^2 + a*mu) / F",                   m**2 + a*m,           F, False),
        ("NEGATIVE: transcendental quotient G*sin(x)/G",  G*sp.sin(x),          G, False),
    ]
    fails = []
    for desc, expr, fac, want in cases:
        got = polynomially_divisible(expr, fac)
        if got != want:
            fails.append("%s  (expected %s, got %s)" % (desc, want, got))
        elif verbose:
            print("    [ok] %s" % desc)
    # zero-factor control
    try:
        polynomially_divisible(sp.Symbol("x"), sp.S(0))
        fails.append("zero factor did not raise ValueError")
    except ValueError:
        if verbose:
            print("    [ok] zero factor raises ValueError")
    except Exception as exc:
        fails.append("zero factor raised %r, expected ValueError" % exc)
    return (not fails), fails


if __name__ == "__main__":
    import sys
    ok, fails = self_test(verbose=True)
    if not ok:
        for f in fails:
            print("  FAIL:", f)
        sys.exit(1)
    print("divisibility.py: positive, negative and contract controls pass")

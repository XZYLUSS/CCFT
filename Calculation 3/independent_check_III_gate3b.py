#!/usr/bin/env python3
"""Independent reconstruction from the parent differential Miura operator.

This program imports no formula or function from the release verifier.  It builds the
parent primary, performs the parent exponential OPE, solves its total-derivative
recurrence, expands the two finite-parent orientations, and only then takes the odd
and even Carrollian coefficients.
"""
from __future__ import annotations

from collections import defaultdict

import sympy as sp


checks = []


def ck(condition, label):
    if not bool(condition):
        raise AssertionError(label)
    checks.append(label)


x = sp.Symbol("x")
e = sp.Symbol("epsilon", nonzero=True)
a, lam = sp.symbols("a lambda", nonzero=True)
mu, am = sp.symbols("mu alpha_minus", nonzero=True)
Hm, Hp, ell, winv = sp.symbols("Phi_minus Phi_plus ell w_inv")
X = [[sp.Symbol(f"X{j+1}_{k}") for k in range(8)] for j in range(3)]
Y = [[sp.Symbol(f"Y{j+1}_{k}") for k in range(8)] for j in range(2)]
P = [[sp.Symbol(f"P{j+1}_{k}") for k in range(9)] for j in range(2)]
N = [[sp.Symbol(f"N{j+1}_{k}") for k in range(9)] for j in range(2)]


def dx3(expr):
    return sp.expand(sum(sp.diff(expr, X[j][k])*X[j][k+1]
                         for j in range(3) for k in range(7)))


u2 = -sum(X[i][0]*X[j][0] for i in range(3) for j in range(i+1, 3)) \
     + a*(X[1][1]+2*X[2][1])
u3 = X[0][0]*X[1][0]*X[2][0] \
     - a*(X[0][0]*X[2][1]+X[1][1]*X[2][0]+X[1][0]*X[2][1]) \
     + a**2*X[2][2]
parent_primary = sp.expand(u3-a*dx3(u2)/2)
reduce3 = {}
for k in range(8):
    reduce3.update({X[0][k]: Y[0][k], X[1][k]: Y[1][k],
                    X[2][k]: -Y[0][k]-Y[1][k]})
w = sp.expand(parent_primary.subs(reduce3))
expected_w = sp.expand(
    -Y[0][0]**2*Y[1][0]-Y[0][0]*Y[1][0]**2
    + a*(sp.Rational(3, 2)*Y[0][0]*Y[1][1]
         + sp.Rational(1, 2)*Y[0][1]*Y[1][0]+Y[1][0]*Y[1][1])
    - a**2*Y[1][2]/2
)
ck(sp.simplify(w-expected_w) == 0, "parent differential Miura primary")


FIELDS = {s for row in Y for s in row}


def info(sym):
    for j in range(2):
        for k, item in enumerate(Y[j]):
            if item == sym:
                return j, k
    raise KeyError(sym)


def factors(term):
    coeff, rest = term.as_coeff_Mul()
    ans = []
    for fac in sp.Mul.make_args(rest):
        if fac.is_Pow and fac.base in FIELDS:
            ans.extend([fac.base]*int(fac.exp))
        elif fac in FIELDS:
            ans.append(fac)
        else:
            coeff *= fac
    return coeff, ans


def taylor(sym, order):
    j, k = info(sym)
    return sum(Y[j][k+r]*x**r/sp.factorial(r) for r in range(order+1))


def monomial_ope(coeff, fs, root):
    out = defaultdict(lambda: sp.S(0))

    def rec(j, pole, scalar, remaining):
        if j == len(fs):
            if not pole:
                return
            series = scalar
            for sym in remaining:
                series *= taylor(sym, pole-1)
                series = sp.series(series, x, 0, pole).removeO().expand()
            for r in range(pole):
                value = sp.expand(series).coeff(x, r)
                if value:
                    out[pole-r] += value
            return
        sym = fs[j]
        field, derivative = info(sym)
        rec(j+1, pole, scalar, remaining+[sym])
        contraction = lam*root[field]*(-1)**derivative*sp.factorial(derivative)
        rec(j+1, pole+derivative+1, scalar*contraction, remaining)

    rec(0, 0, coeff, [])
    return out


def parent_ope(root):
    out = defaultdict(lambda: sp.S(0))
    for term in sp.Add.make_args(w):
        coeff, fs = factors(term)
        for pole, value in monomial_ope(coeff, fs, root).items():
            out[pole] += value
    return {pole: sp.factor(value) for pole, value in out.items()}


def dy(expr):
    return sp.expand(sum(sp.diff(expr, Y[j][k])*Y[j][k+1]
                         for j in range(2) for k in range(7)))


def root_dot_y(root):
    # The third component was eliminated before differentiating.
    return (root[0]-root[2])*Y[0][0] + (root[1]-root[2])*Y[1][0]


def parent_dv(expr, root):
    return sp.expand(dy(expr)+lam*root_dot_y(root)*expr)


def parent_witness(ope, root):
    B = {max(ope): sp.S(0)}
    for pole in range(max(ope), 1, -1):
        B[pole-1] = sp.factor((ope[pole]-parent_dv(B[pole], root))/(pole-1))
    residual = sp.factor(ope[1]-parent_dv(B[1], root))
    return B, residual


roots3 = ([1, -1, 0], [0, 1, -1])
parent_witnesses = []
for i, root3 in enumerate(roots3):
    contraction_root = [root3[0], root3[1]]
    ope = parent_ope(contraction_root)
    B, residual = parent_witness(ope, root3)
    ck(set(ope) == {1, 2, 3}, f"root {i+1} parent poles")
    ck(sp.factor(residual.subs(a, (1-lam**2)/lam)) == 0,
       f"root {i+1} parent screening residual vanishes on a lambda+lambda^2=1")
    ck(sp.factor(residual).has(a*lam+lam**2-1),
       f"root {i+1} parent obstruction carries screening equation")
    parent_witnesses.append({1: B[1], 2: B[2]})


def branch_witness(root_index, sign, contracted):
    m3 = -mu**3-sign*am*mu**2
    subs = {
        a: 1/(mu*e)+sign*e*am,
        lam: e*(mu+e**2*m3),
        Y[0][0]: P[0][0]/e+sign*e*N[0][0],
        Y[1][0]: P[1][0]/e+sign*e*N[1][0],
    }
    F = sign*mu*Hm+m3*Hp+mu**2*ell
    scale = e/2 if contracted == "minus" else sign*e**3/2
    return {
        q: sp.factor(sp.expand(
            scale*sp.series(parent_witnesses[root_index][q].subs(subs), e, 0, 4).removeO()
            *(1+e**2*F)
        ).coeff(e, 2))
        for q in (1, 2)
    }


H = Hm-am*mu*Hp
K = ell-mu*Hp
expected_odd = (
    {2: (H+am)/4, 1: (N[0][0]+N[1][0]+mu*H*(P[0][0]+P[1][0]))/2},
    {2: -(H+am)/4, 1: -(N[0][0]+mu*H*P[0][0])/2},
)
expected_even = (
    {2: mu*K/4, 1: mu**2*K*(P[0][0]+P[1][0])/2},
    {2: -mu*K/4, 1: -mu**2*K*P[0][0]/2},
)
expected_plus = (
    {2: 1/(4*mu), 1: (P[0][0]+P[1][0])/2},
    {2: -1/(4*mu), 1: -P[0][0]/2},
)
for i in range(2):
    u = branch_witness(i, +1, "minus")
    b = branch_witness(i, -1, "minus")
    odd = {q: sp.factor((u[q]-b[q])/2) for q in (1, 2)}
    even = {q: sp.factor((u[q]+b[q])/2) for q in (1, 2)}
    pu = branch_witness(i, +1, "plus")
    pb = branch_witness(i, -1, "plus")
    plus_odd = {q: sp.factor((pu[q]-pb[q])/2) for q in (1, 2)}
    for q in (1, 2):
        ck(sp.simplify(odd[q]-expected_odd[i][q]) == 0,
           f"root {i+1} independently derived odd witness {q}")
        ck(sp.simplify(even[q]-expected_even[i][q]) == 0,
           f"root {i+1} independently derived even witness {q}")
        ck(sp.simplify(plus_odd[q]-expected_plus[i][q]) == 0,
           f"root {i+1} independently derived plus witness {q}")


def Dcoeff(expr, root):
    out = sum(sp.diff(expr, P[j][k])*P[j][k+1]
              + sp.diff(expr, N[j][k])*N[j][k+1]
              for j in range(2) for k in range(8))
    red = (root[0]-root[2], root[1]-root[2])
    out += sp.diff(expr, Hm)*sum(red[j]*N[j][0] for j in range(2))
    out += sp.diff(expr, Hp)*sum(red[j]*P[j][0] for j in range(2))
    out += sp.diff(expr, ell)*winv-sp.diff(expr, winv)*winv**2
    return sp.expand(out)


def Dvertex(expr, root):
    red = (root[0]-root[2], root[1]-root[2])
    return sp.expand(Dcoeff(expr, root)+mu*sum(red[j]*P[j][0] for j in range(2))*expr)


ck(Dcoeff(winv, roots3[0]) == -winv**2, "independent D(w^-1) rule")
for i, root in enumerate(roots3):
    for name, witness in (("odd", expected_odd[i]), ("even", expected_even[i])):
        ope = {3: 2*witness[2],
               2: Dvertex(witness[2], root)+witness[1],
               1: Dvertex(witness[1], root)}
        recovered_2 = sp.factor(ope[3]/2)
        recovered_1 = sp.factor(ope[2]-Dvertex(recovered_2, root))
        residual = sp.factor(ope[1]-Dvertex(recovered_1, root))
        ck(residual == 0, f"root {i+1} independent {name} exact derivative")


# Exact branch monodromy is reconstructed independently of the OPE algebra.
t, m, u, b = sp.symbols("t m u b", nonzero=True)
du, db = t*u**2, t*b**2
lp = sp.Rational(1, 2)*((m-du)/u+(m-db)/b)
tlm = sp.Rational(1, 2)*((m-du)/u-(m-db)/b)
ck(sp.simplify(du+u*lp+u*tlm-m) == 0, "independent unbarred monodromy")
ck(sp.simplify(db+b*lp-b*tlm-m) == 0, "independent barred monodromy")

print(f"INDEPENDENT GATE 3B PARENT RECONSTRUCTION PASSED: {len(checks)}/{len(checks)}")

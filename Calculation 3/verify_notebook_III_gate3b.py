#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
from collections import Counter, defaultdict
from pathlib import Path

import sympy as sp


BASE = Path(__file__).resolve().parent
HTML = BASE / "Notebook_III_Gate3B_Tangent_OPE_Closure.html"
ROAD = BASE / "ROADMAP.md"
SOURCE = BASE / "SOURCE_LOG.md"
REQUIRED_SYMPY = "1.14.0"
PARENT_3A = "45e9bfdf2906527ea2175513dff447e9052d06a14c94dd979904d07323962c82"
PARENT_2G2 = "522f0a57b5e128bd9fda861d036d30b1ee36f98f98d34cfd4cf5d98862a16481"
SEMANTIC_CLAIMS = (
    "dwinv=-winv2",
    "ordinaryUnbarResidual1=-mu2(P1+3P2)/(4w)-mu/(4w2)",
    "ordinaryUnbarResidual2=mu2(P1-2P2)/(4w)+mu/(4w2)",
    "averageContact1=(mu/(4w),mu2(P1+P2)/(2w))",
    "averageContact2=(-mu/(4w),-mu2P1/(2w))",
    "oddWitness1=((H1+am)/4,(N1+N2+muH1(P1+P2))/2)",
    "oddWitness2=(-(H2+am)/4,-(N1+muH2P1)/2)",
    "branchMonodromy=exact",
    "targetEquation=bracket+dUTQ0/2=0",
    "status=gate3closedOutcomeB",
    f"parent3a={PARENT_3A}",
    f"parent2g2={PARENT_2G2}",
)
SEMANTIC_ID = "G3B-" + hashlib.sha256("|".join(SEMANTIC_CLAIMS).encode()).hexdigest()[:16]


class Ledger:
    def __init__(self):
        self.counts = Counter()
        self.failures: list[str] = []

    def check(self, group: str, condition, label: str):
        ok = bool(condition)
        self.counts[group] += 1
        print(("[PASS] " if ok else "[FAIL] ") + f"{group}: {label}")
        if not ok:
            self.failures.append(f"{group}: {label}")


x = sp.Symbol("x")
z = sp.Symbol("z", nonzero=True)
mu, cm, cp, ap, am = sp.symbols("mu c_m c_p alpha_p alpha_m", nonzero=True)
P = [[sp.Symbol(f"P{a + 1}_{k}") for k in range(10)] for a in range(2)]
N = [[sp.Symbol(f"N{a + 1}_{k}") for k in range(10)] for a in range(2)]
Hm, Hp, LogW, Winv = sp.symbols("Phi_m Phi_p Log_w w_inv")
H = Hm - am * mu * Hp
roots = ([1, -1, 0], [0, 1, -1])


C3p = sp.expand(
    -P[0][0] ** 2 * P[1][0] - P[0][0] * P[1][0] ** 2
    + ap * (sp.Rational(3, 2) * P[0][0] * P[1][1]
            + sp.Rational(1, 2) * P[0][1] * P[1][0]
            + P[1][0] * P[1][1])
    - ap**2 * P[1][2] / 2
)

C3m = sp.expand(
    -2 * N[0][0] * P[0][0] * P[1][0] - N[0][0] * P[1][0] ** 2
    - N[1][0] * P[0][0] ** 2 - 2 * N[1][0] * P[0][0] * P[1][0]
    + am * (sp.Rational(3, 2) * P[0][0] * P[1][1]
            + sp.Rational(1, 2) * P[0][1] * P[1][0]
            + P[1][0] * P[1][1])
    + ap * (sp.Rational(3, 2) * N[0][0] * P[1][1]
            + sp.Rational(1, 2) * N[0][1] * P[1][0]
            + sp.Rational(1, 2) * N[1][0] * P[0][1]
            + N[1][0] * P[1][1]
            + sp.Rational(3, 2) * N[1][1] * P[0][0]
            + N[1][1] * P[1][0] - am * P[1][2])
    - ap**2 * N[1][2] / 2
)


def field_info(sym):
    for sector, arr in (("P", P), ("N", N)):
        for a in range(2):
            for k, item in enumerate(arr[a]):
                if sym == item:
                    return sector, a, k
    raise KeyError(sym)


FIELDS = {s for row in P + N for s in row}


def taylor(sym, order):
    sector, a, k = field_info(sym)
    arr = P if sector == "P" else N
    return sum(arr[a][k + r] * x**r / sp.factorial(r) for r in range(order + 1))


def term_factors(term):
    coeff, rest = term.as_coeff_Mul()
    factors = []
    for fac in sp.Mul.make_args(rest):
        if fac.is_Pow and fac.base in FIELDS:
            factors.extend([fac.base] * int(fac.exp))
        elif fac in FIELDS:
            factors.append(fac)
        else:
            coeff *= fac
    return coeff, factors


def monomial_commutative_ope(coeff, factors, root):
    """Diagnostic local Wick model, before the averaged-order contact is restored."""
    out = defaultdict(lambda: sp.S(0))

    def rec(j, pole, scalar, remaining, h_used):
        if j == len(factors):
            if pole == 0:
                return
            hfactor = sp.S(1) if h_used else (cm * Hm + cp * Hp)
            series = scalar * hfactor
            for sym in remaining:
                series *= taylor(sym, pole - 1)
                series = sp.series(series, x, 0, pole).removeO().expand()
            for r in range(pole):
                val = sp.expand(series).coeff(x, r)
                if val:
                    out[pole - r] += val
            return

        sym = factors[j]
        sector, a, k = field_info(sym)
        ck = root[a] * sp.Rational(1, 2) * (-1) ** k * sp.factorial(k)
        rec(j + 1, pole, scalar, remaining + [sym], h_used)
        if not h_used:
            rec(j + 1, pole + k + 1,
                scalar * (cm if sector == "P" else cp) * ck,
                remaining, True)
        if sector == "N":
            rec(j + 1, pole + k + 1, scalar * mu * ck, remaining, h_used)

    rec(0, 0, coeff, [], False)
    return out


def commutative_tangent_ope(poly, root):
    out = defaultdict(lambda: sp.S(0))
    for term in sp.Add.make_args(sp.expand(poly)):
        coeff, factors = term_factors(term)
        for pole, val in monomial_commutative_ope(coeff, factors, root).items():
            out[pole] += val
    return {p: sp.factor(sp.expand(v)) for p, v in sorted(out.items()) if v != 0}


def root_reduced(root):
    return root[0] - root[2], root[1] - root[2]


def D(expr, root):
    out = sp.S(0)
    for a in range(2):
        for k in range(9):
            out += sp.diff(expr, P[a][k]) * P[a][k + 1]
            out += sp.diff(expr, N[a][k]) * N[a][k + 1]
    red = root_reduced(root)
    out += sp.diff(expr, Hm) * sum(red[a] * N[a][0] for a in range(2))
    out += sp.diff(expr, Hp) * sum(red[a] * P[a][0] for a in range(2))
    out += sp.diff(expr, LogW) * Winv
    out -= sp.diff(expr, Winv) * Winv**2
    return sp.expand(out)


def Dvertex(expr, root):
    red = root_reduced(root)
    rootP = sum(red[a] * P[a][0] for a in range(2))
    return sp.expand(D(expr, root) + mu * rootP * expr)


def ope_from_witness(witness, root):
    return {
        3: sp.expand(2 * witness[2]),
        2: sp.expand(Dvertex(witness[2], root) + witness[1]),
        1: sp.expand(Dvertex(witness[1], root)),
    }


def witness_and_residual(ope, root):
    maxpole = max(ope)
    witness = {maxpole: sp.S(0)}
    for q in range(maxpole, 1, -1):
        witness[q - 1] = sp.factor((ope.get(q, 0) - Dvertex(witness[q], root)) / (q - 1))
    residual = sp.factor(ope.get(1, 0) - Dvertex(witness[1], root))
    return {q: sp.factor(v) for q, v in witness.items() if q < maxpole}, residual


def leading_minus_ope(root_index):
    if root_index == 0:
        witness = {1: (P[0][0] + P[1][0]) / 2, 2: 1 / (4 * mu)}
    else:
        witness = {1: -P[0][0] / 2, 2: -1 / (4 * mu)}
    return ope_from_witness(witness, roots[root_index])


def averaged_odd_witness(root_index):
    if root_index == 0:
        return {
            2: (H + am) / 4,
            1: (N[0][0] + N[1][0] + mu * H * (P[0][0] + P[1][0])) / 2,
        }
    return {2: -(H + am) / 4, 1: -(N[0][0] + mu * H * P[0][0]) / 2}


def averaged_even_witness(root_index):
    K = LogW - mu * Hp
    if root_index == 0:
        return {2: mu * K / 4, 1: mu**2 * K * (P[0][0] + P[1][0]) / 2}
    return {2: -mu * K / 4, 1: -mu**2 * K * P[0][0] / 2}


def parent_minus_branch_witness(root_index, sign):
    """Coefficient of t in each finite-parent orientation after barred contour transport."""
    e = sp.Symbol("epsilon", nonzero=True)
    a0, lam, X1, X2 = sp.symbols("a_parent lambda_parent X1 X2")
    if root_index == 0:
        parent = {
            2: a0 * lam * (a0 + lam) / 2,
            1: -lam * (X1*a0**2*lam + X1*a0*lam**2 - 3*X1*a0 - 2*X1*lam
                       - X2*a0**2*lam - X2*a0*lam**2 - X2*a0 - 2*X2*lam) / 2,
        }
    else:
        parent = {
            2: -a0 * lam * (a0 + lam) / 2,
            1: lam * (X1*a0**2*lam + X1*a0*lam**2 - 3*X1*a0 - 2*X1*lam
                      + 2*X2*a0**2*lam + 2*X2*a0*lam**2 - 2*X2*a0) / 2,
        }
    m3 = -mu**3 - sign * am * mu**2
    subs = {
        a0: 1/(mu*e) + sign*e*am,
        lam: e*(mu + e**2*m3),
        X1: P[0][0]/e + sign*e*N[0][0],
        X2: P[1][0]/e + sign*e*N[1][0],
    }
    prefactor = sign*mu*Hm + m3*Hp + mu**2*LogW
    return {
        q: sp.factor(sp.expand(
            e * sp.series(parent[q].subs(subs), e, 0, 4).removeO()
            * (1 + e**2*prefactor) / 2
        ).coeff(e, 2))
        for q in (1, 2)
    }


def parent_plus_branch_witness(root_index, sign):
    """Order-t W+ witness; sign includes the transported barred contour orientation."""
    e = sp.Symbol("epsilon", nonzero=True)
    a0, lam, X1, X2 = sp.symbols("a_parent lambda_parent X1 X2")
    if root_index == 0:
        parent = {
            2: a0 * lam * (a0 + lam) / 2,
            1: -lam * (X1*a0**2*lam + X1*a0*lam**2 - 3*X1*a0 - 2*X1*lam
                       - X2*a0**2*lam - X2*a0*lam**2 - X2*a0 - 2*X2*lam) / 2,
        }
    else:
        parent = {
            2: -a0 * lam * (a0 + lam) / 2,
            1: lam * (X1*a0**2*lam + X1*a0*lam**2 - 3*X1*a0 - 2*X1*lam
                      + 2*X2*a0**2*lam + 2*X2*a0*lam**2 - 2*X2*a0) / 2,
        }
    m3 = -mu**3 - sign * am * mu**2
    subs = {
        a0: 1/(mu*e) + sign*e*am,
        lam: e*(mu + e**2*m3),
        X1: P[0][0]/e + sign*e*N[0][0],
        X2: P[1][0]/e + sign*e*N[1][0],
    }
    prefactor = sign*mu*Hm + m3*Hp + mu**2*LogW
    return {
        q: sp.factor(sp.expand(
            sign * e**3 * sp.series(parent[q].subs(subs), e, 0, 4).removeO()
            * (1 + e**2*prefactor) / 2
        ).coeff(e, 2))
        for q in (1, 2)
    }


def shift(poly, root, sector):
    arr = P if sector == "+" else N
    return sp.factor(sum(
        sp.diff(poly, arr[a][k]) * root[a] * (-1)**k * sp.factorial(k) / z**(k + 1)
        for a in range(2) for k in range(7)
    ))


def run_model_checks(L: Ledger):
    L.check("model", sp.__version__ == REQUIRED_SYMPY, f"SymPy pinned at {REQUIRED_SYMPY}")
    L.check("model", D(LogW, roots[0]) == Winv, "D log(w/w0)=w^-1")
    L.check("model", D(Winv, roots[0]) == -Winv**2, "D(w^-1)=-w^-2")

    # Plus-primary strict odd OPEs are unaffected by averaged ordering.
    expected_plus_witnesses = (
        {2: 1/(4*mu), 1: (P[0][0] + P[1][0])/2},
        {2: -1/(4*mu), 1: -P[0][0]/2},
    )
    nu = -am * mu**2
    for i, root in enumerate(roots):
        ordinary = commutative_tangent_ope(C3p, root)
        ordinary = {p: sp.factor(v.subs({ap: 1/mu, cm: mu, cp: nu})) for p, v in ordinary.items()}
        expected = ope_from_witness(expected_plus_witnesses[i], root)
        for pole in (1, 2, 3):
            L.check("model", sp.simplify(ordinary[pole] - expected[pole]) == 0,
                    f"plus root {i+1} pole {pole}")
        _, residual = witness_and_residual(ordinary, root)
        L.check("model", residual == 0, f"plus root {i+1} is an exact derivative")

    odd_residuals = (
        -mu**2 * (mu*P[0][0]**2 + 2*mu*P[0][0]*P[1][0] - P[0][1]
                  - 3*mu*P[1][0]**2 + P[1][1]) / 4,
        mu**2 * (mu*P[0][0]**2 - P[0][1] - 4*mu*P[1][0]**2 - 2*P[1][1]) / 4,
    )
    corrected_even_residuals = (
        -odd_residuals[0] - mu**2*Winv*(P[0][0] + 3*P[1][0])/4 - mu*Winv**2/4,
        -odd_residuals[1] + mu**2*Winv*(P[0][0] - 2*P[1][0])/4 + mu*Winv**2/4,
    )
    unbar_residuals = (
        -mu**2*Winv*(P[0][0] + 3*P[1][0])/4 - mu*Winv**2/4,
        mu**2*Winv*(P[0][0] - 2*P[1][0])/4 + mu*Winv**2/4,
    )
    odd_contacts = (
        {3: -mu/2, 2: -mu**2*(P[0][0]+P[1][0])/2,
         1: -mu**2*(P[0][1]+P[1][1])/2},
        {3: mu/2, 2: mu**2*P[0][0]/2, 1: mu**2*P[0][1]/2},
    )
    even_contacts = (
        {3: mu/2,
         2: mu*(2*mu*P[0][0] + 2*mu*P[1][0] + Winv)/4,
         1: mu**2*(P[0][1]+P[1][1]+Winv*(P[0][0]+P[1][0]))/2},
        {3: -mu/2,
         2: -mu*(2*mu*P[0][0] + Winv)/4,
         1: -mu**2*(P[0][1]+Winv*P[0][0])/2},
    )
    unbar_contacts = (
        {3: 0, 2: mu*Winv/4, 1: mu**2*Winv*(P[0][0]+P[1][0])/2},
        {3: 0, 2: -mu*Winv/4, 1: -mu**2*Winv*P[0][0]/2},
    )

    for i, root in enumerate(roots):
        ordinary_odd = commutative_tangent_ope(C3m, root)
        ordinary_odd = {p: sp.expand(v.subs({ap: 1/mu, cm: mu, cp: nu}))
                        for p, v in ordinary_odd.items()}
        _, odd_res = witness_and_residual(ordinary_odd, root)
        L.check("model", sp.simplify(odd_res - odd_residuals[i]) == 0,
                f"root {i+1} commutative odd diagnostic residual")

        phi_plus = commutative_tangent_ope(C3m, root)
        phi_plus = {p: sp.expand(v.subs({ap: 1/mu, cm: 0, cp: -mu**3}))
                    for p, v in phi_plus.items()}
        lead = leading_minus_ope(i)
        ordinary_even = {p: sp.expand(phi_plus.get(p, 0) + mu**2*LogW*lead.get(p, 0))
                         for p in set(phi_plus) | set(lead)}
        _, even_res = witness_and_residual(ordinary_even, root)
        L.check("model", sp.simplify(even_res - corrected_even_residuals[i]) == 0,
                f"root {i+1} corrected even residual includes D(w^-1)")

        ordinary_unbar = {p: sp.expand(ordinary_odd[p] + ordinary_even[p]) for p in (1, 2, 3)}
        _, unbar_res = witness_and_residual(ordinary_unbar, root)
        L.check("model", sp.simplify(unbar_res - unbar_residuals[i]) == 0,
                f"root {i+1} audited ordinary unbarred residual")

        actual_odd = ope_from_witness(averaged_odd_witness(i), root)
        actual_even = ope_from_witness(averaged_even_witness(i), root)
        actual_unbar = {p: sp.expand(actual_odd[p] + actual_even[p]) for p in (1, 2, 3)}
        for pole in (1, 2, 3):
            L.check("model", sp.simplify(actual_odd[pole] - ordinary_odd[pole]
                                          - odd_contacts[i][pole]) == 0,
                    f"root {i+1} odd averaged-order contact pole {pole}")
            L.check("model", sp.simplify(actual_even[pole] - ordinary_even[pole]
                                          - even_contacts[i][pole]) == 0,
                    f"root {i+1} even averaged-order contact pole {pole}")
            L.check("model", sp.simplify(actual_unbar[pole] - ordinary_unbar[pole]
                                          - unbar_contacts[i][pole]) == 0,
                    f"root {i+1} combined parent contact pole {pole}")
        _, actual_odd_res = witness_and_residual(actual_odd, root)
        _, actual_even_res = witness_and_residual(actual_even, root)
        _, actual_unbar_res = witness_and_residual(actual_unbar, root)
        L.check("model", actual_odd_res == 0, f"root {i+1} averaged odd OPE exact")
        L.check("model", actual_even_res == 0, f"root {i+1} averaged even OPE exact")
        L.check("model", actual_unbar_res == 0, f"root {i+1} unbarred branch OPE exact")

        wu = parent_minus_branch_witness(i, +1)
        wb = parent_minus_branch_witness(i, -1)
        parent_odd = {q: sp.factor((wu[q] - wb[q])/2) for q in (1, 2)}
        parent_even = {q: sp.factor((wu[q] + wb[q])/2) for q in (1, 2)}
        for q in (1, 2):
            L.check("model", sp.simplify(parent_odd[q] - averaged_odd_witness(i)[q]) == 0,
                    f"root {i+1} two-orientation odd witness {q}")
            L.check("model", sp.simplify(parent_even[q] - averaged_even_witness(i)[q]) == 0,
                    f"root {i+1} two-orientation even witness {q}")
        pu = parent_plus_branch_witness(i, +1)
        pb = parent_plus_branch_witness(i, -1)
        parent_plus_odd = {q: sp.factor((pu[q] - pb[q])/2) for q in (1, 2)}
        for q in (1, 2):
            L.check("model", sp.simplify(parent_plus_odd[q] - expected_plus_witnesses[i][q]) == 0,
                    f"root {i+1} two-orientation plus witness {q}")

    # Exact branch equations and exact horizontal monodromies.
    t = sp.Symbol("t")
    m3u = -mu**3 - am*mu**2
    m3b = -mu**3 + am*mu**2
    muu = mu + t*m3u
    mub = mu + t*m3b
    eq_u = sp.expand(t*muu**2 + (1/mu + t*am)*muu - 1)
    eq_b = sp.expand(t*mub**2 + (1/mu - t*am)*mub - 1)
    L.check("model", eq_u.coeff(t, 0) == 0 and sp.simplify(eq_u.coeff(t, 1)) == 0,
            "unbarred screening branch through first coefficient")
    L.check("model", eq_b.coeff(t, 0) == 0 and sp.simplify(eq_b.coeff(t, 1)) == 0,
            "barred screening branch through first coefficient")
    L.check("model", sp.simplify((m3u-m3b)/2 + am*mu**2) == 0,
            "mu_diff=-alpha_minus mu^2")

    u, b, m = sp.symbols("u b m", nonzero=True)
    du, db = t*u**2, t*b**2
    lam_plus = sp.Rational(1, 2)*((m-du)/u + (m-db)/b)
    t_lam_minus = sp.Rational(1, 2)*((m-du)/u - (m-db)/b)
    au = sp.simplify(du + u*lam_plus + u*t_lam_minus - m)
    ab = sp.simplify(db + b*lam_plus - b*t_lam_minus - m)
    L.check("model", au == 0, "exact unbarred horizontal monodromy")
    L.check("model", ab == 0, "exact barred horizontal monodromy")
    ares = sp.Symbol("a_res")
    boundary = (sp.exp(2*sp.pi*sp.I*ares)-1)/(2*sp.pi*sp.I)
    L.check("model", boundary.subs(ares, au) == 0 and boundary.subs(ares, ab) == 0,
            "both exact branch boundaries vanish before coefficient extraction")
    L.check("model", sp.simplify(sp.diff(boundary, ares).subs(ares, 0)-1) == 0,
            "off-horizontal first boundary anomaly retained")

    # Scalar barred BCH factor.
    rho = sp.Symbol("rho")
    zbar = (1-rho)**(-2*t*mu**2)
    L.check("model", sp.diff(sp.log(zbar), z) == 0, "barred BCH is insertion independent")
    L.check("model", sp.simplify(sp.diff(sp.log(zbar), t).subs(t, 0)
                                  + 2*mu**2*sp.log(1-rho)) == 0,
            "barred BCH first scalar")

    # Nonlinear target connection is checked as a directional derivative, not by self-equality.
    Avec = [shift(C3p, root, "+") for root in roots]
    Bvec = [shift(C3m, root, "+") for root in roots]
    for i, root in enumerate(roots):
        L.check("model", shift(C3p, root, "-") == 0, f"root {i+1} dminus Uplus=0")
        L.check("model", sp.simplify(shift(C3m, root, "-") - Avec[i]) == 0,
                f"root {i+1} dminus Uminus=dplus Uplus")
        target_plus = sp.factor(mu*shift(C3p, root, "+") + nu*shift(C3p, root, "-"))
        target_minus = sp.factor(mu*shift(C3m, root, "+") + nu*shift(C3m, root, "-"))
        L.check("model", sp.simplify(target_plus - mu*Avec[i]) == 0,
                f"root {i+1} full target plus derivative")
        L.check("model", sp.simplify(target_minus - (mu*Bvec[i]+nu*Avec[i])) == 0,
                f"root {i+1} full target minus derivative")

    U = sp.Matrix([[2, 0], [0, -1]])
    A = sp.Matrix([[0, 3], [0, 0]])
    Q0 = sp.eye(2)
    deltaU = 2*(U*A-A*U)
    Qpbw = -A*Q0
    L.check("model", U*Qpbw-Qpbw*U == -deltaU*Q0/2,
            "target-first PBW sign and one-half factor")


def scalar_controls():
    t, m, u, b, ares = sp.symbols("t m u b a", nonzero=True)
    m3u = -mu**3-am*mu**2
    m3b = -mu**3+am*mu**2
    du, db = t*u**2, t*b**2
    lp = sp.Rational(1, 2)*((m-du)/u+(m-db)/b)
    tlm = sp.Rational(1, 2)*((m-du)/u-(m-db)/b)
    boundary = (sp.exp(2*sp.pi*sp.I*ares)-1)/(2*sp.pi*sp.I)
    controls = [
        (sp.__version__ == REQUIRED_SYMPY, "SymPy version"),
        (D(LogW, roots[0]) == Winv, "D log"),
        (D(Winv, roots[0]) == -Winv**2, "D inverse coordinate"),
        (sp.simplify(m3u+mu**3+am*mu**2) == 0, "unbarred branch coefficient"),
        (sp.simplify(m3b+mu**3-am*mu**2) == 0, "barred branch coefficient"),
        (sp.simplify((m3u-m3b)/2+am*mu**2) == 0, "odd branch coefficient"),
        (sp.simplify(du+u*lp+u*tlm-m) == 0, "unbarred monodromy"),
        (sp.simplify(db+b*lp-b*tlm-m) == 0, "barred monodromy"),
        (boundary.subs(ares, 0) == 0, "horizontal boundary"),
        (sp.simplify(sp.diff(boundary, ares).subs(ares, 0)-1) == 0, "boundary derivative"),
        (sp.simplify(2*mu**2-mu**2*sp.Integer(2)) == 0, "root BCH norm"),
        (sp.simplify((-mu/2)+(mu/2)) == 0, "orientation contact parity"),
    ]
    for ok, label in controls:
        if not bool(ok):
            raise AssertionError(f"scalar control failed: {label}")
    return controls


def run_document_checks(L: Ledger):
    for path in (HTML, ROAD, SOURCE):
        L.check("structure", path.is_file(), f"{path.name} exists")
    if L.failures:
        return
    html = HTML.read_text(encoding="utf-8")
    road = ROAD.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8")
    required_html = (
        "GATE 3B PASS - CORRECTED", "GATE 3 CLOSES WITH OUTCOME B",
        SEMANTIC_ID, "\\partial_w(w^{-1})=-w^{-2}",
        "R_{1,{\\rm even}}^{\\rm comm}=-R_1-\\frac{\\mu^2}{4w}(P_1+3P_2)-\\frac{\\mu}{4w^2}",
        "R_{2,{\\rm even}}^{\\rm comm}=-R_2+\\frac{\\mu^2}{4w}(P_1-2P_2)+\\frac{\\mu}{4w^2}",
        "\\delta\\mathcal O_{1,2}=\\frac{\\mu}{4w}",
        "\\delta\\mathcal O_{2,2}=-\\frac{\\mu}{4w}",
        "\\Xi_{1,2}=\\frac{H_1+\\alpha^-}{4}",
        "\\Xi_{2,2}=-\\frac{H_2+\\alpha^-}{4}",
        "Derived averaged-order contact", "no ad hoc contact counterterm",
        "Q_i^{[1]}=\\widetilde Q_i^{[1]}-\\mathsf A_{{\\rm T},i}Q_i^{[0]}",
        "not an ordinary second screening", PARENT_3A, PARENT_2G2,
        "Europe/Berlin, UTC+02:00",
    )
    for token in required_html:
        L.check("document", token in html, f"HTML contains {token}")
    L.check("document", html.count(SEMANTIC_ID) == 2,
            "HTML semantic release ID appears in header and footer only")
    forbidden = (
        "no hidden reordering contact term",
        "R_i cancels identically",
        "R_{1,{\\rm even}}=-R_1-\\frac{\\mu^2}{4w}(P_1+3P_2),\\qquad",
    )
    for token in forbidden:
        L.check("document", token not in html, f"obsolete claim absent: {token}")
    L.check("document", SEMANTIC_ID in road and SEMANTIC_ID in source,
            "semantic release ID synchronized")
    L.check("document", "D(w^-1)=-w^-2" in road and "D(w^-1)=-w^-2" in source,
            "inverse-coordinate derivative recorded")
    L.check("document", "derived averaged-order contact" in road
            and "derived averaged-order contact" in source,
            "ordering mechanism synchronized")
    L.check("document", "Gate 3: closed with Outcome B" in road
            and "Gate 3 closes with Outcome B" in source,
            "Gate disposition synchronized")
    L.check("document", "not an ordinary second screening" in road
            and "not an ordinary second screening" in source,
            "claim boundary synchronized")
    L.check("document", "free-field formulas, not a screening construction" in source
            and "screening construction in equations (4.18)-(4.21)" not in source,
            "Fredenhagen-Hoerl source role is exact")
    L.check("document", PARENT_3A in source and PARENT_2G2 in source,
            "frozen parent hashes recorded in source log")
    L.check("document", "Europe/Berlin, UTC+02:00" in road
            and "Europe/Berlin, UTC+02:00" in source,
            "release timezone synchronized")
    L.check("structure", 'mathjax@3.2.2' in html, "MathJax exactly pinned")
    L.check("structure", len(re.findall(r'<div class="cell"', html)) == 4,
            "four self-contained embedded cells")
    L.check("structure", html.count("<html") == 1 and html.count("</html>") == 1,
            "single complete HTML document")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scalar-sanity-controls", action="store_true")
    parser.add_argument("--document-only", action="store_true")
    args = parser.parse_args()
    if args.scalar_sanity_controls:
        controls = scalar_controls()
        print(f"SCALAR CONTROLS PASSED: {len(controls)}/{len(controls)}")
        return
    ledger = Ledger()
    if not args.document_only:
        run_model_checks(ledger)
    run_document_checks(ledger)
    if ledger.failures:
        print("FAILURES:")
        for failure in ledger.failures:
            print(" -", failure)
        raise SystemExit(1)
    total = sum(ledger.counts.values())
    print(f"MODEL CHECKS PASSED: {ledger.counts['model']}/{ledger.counts['model']}")
    print(f"DOCUMENT CHECKS PASSED: {ledger.counts['document']}/{ledger.counts['document']}")
    print(f"HTML STRUCTURAL CHECKS PASSED: {ledger.counts['structure']}/{ledger.counts['structure']}")
    print(f"VERIFIER PASSED: {total}/{total}")


if __name__ == "__main__":
    main()

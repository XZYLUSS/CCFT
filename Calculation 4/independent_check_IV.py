#!/usr/bin/env python3
"""Independent Notebook-IV reconstruction.

This program imports neither the main verifier nor any project helper.  It starts from
the two source normalizations, explicit weights, the frozen Miura polynomials, and the
bulk screening transformations.
"""
from __future__ import annotations

import sympy as S


checks: list[bool] = []


def ck(condition, name: str) -> None:
    ok = bool(condition)
    checks.append(ok)
    print(("[PASS] " if ok else "[FAIL] ") + name)


G = S.symbols("G", positive=True)
p = S.pi
k = 1 / (8 * p * G)

# 1. Central normalization, independently evaluated at several ranks.
for rank in (2, 3, 4, 7):
    trace = S.Rational(12, rank * (rank**2 - 1))
    scale2 = S.simplify(p * k * trace)
    ck(S.simplify(2 * rank * (rank**2 - 1) * scale2 - 3 / G) == 0, f"central triangle s={rank}")

# 2. Distributional Fourier sign and the FH factor i.
m = S.symbols("m", integer=True)
bulk_mode = S.simplify((8 * p * G) * m / (2 * p))
ck(bulk_mode == 4 * G * m, "bulk delta-prime Fourier coefficient")
a2 = S.symbols("a2", positive=True)
A = S.I * a2 / 2
fh_mode = S.simplify(-(A * A) * bulk_mode)
ck(S.simplify(fh_mode.subs(a2**2, 1 / (4 * G)) - m / 4) == 0, "FH N=2 mode bracket")
ck(S.simplify((-fh_mode).subs(a2**2, 1 / (4 * G)) + m / 4) == 0, "opposite barred sign is rejected")

# 3. General-to-explicit s=2 connection and row determinant.
weights2 = (1 / S.sqrt(2), -1 / S.sqrt(2))
conversion2 = -S.I * a2 / S.sqrt(2)
entries2 = tuple(S.simplify(S.I * w * conversion2 / a2) for w in weights2)
ck(entries2 == (S.Rational(1, 2), -S.Rational(1, 2)), "s=2 connection reduction")
x, x1, y, y1 = S.symbols("x x1 y y1")
u2 = S.expand((x / 2) * (-x / 2) - x1 / 2)
ubar2 = S.expand((y / 2) * (-x / 2) - y1 / 2 + (x / 2) * (-y / 2))
ck(S.simplify(u2 - (-x**2 / 4 - x1 / 2)) == 0, "s=2 unbarred row determinant")
ck(S.simplify(ubar2 - (-x * y / 2 - y1 / 2)) == 0, "s=2 tangent row determinant")

# 4. Full N=2 coefficient solve over complex constants.
AA, BB, CC, DD, rm, rl, rlm, a = S.symbols("AA BB CC DD rm rl rlm a")
system = [
    2 * AA**2 + rm / 4,
    2 * DD * a * AA + rm / 2,
    4 * AA * BB + rl / 2,
    2 * DD * a * BB + rl / 2,
    4 * AA * CC + rlm / 4,
    2 * DD * a * CC + rlm / 2,
    DD**2 + 1,
    AA * BB + a**2 / 4,
]
sols = S.solve(system, [AA, BB, CC, DD, rm, rl, rlm], dict=True)
plus = {AA: S.I * a / 2, BB: S.I * a / 2, CC: 0, DD: S.I, rm: 2 * a**2, rl: 2 * a**2, rlm: 0}
ck(len(sols) == 2, "N=2 solve has exactly two conjugate branches")
ck(plus in sols, "N=2 selected branch")
ck(all(S.simplify(eq.subs(plus)) == 0 for eq in system), "N=2 equations coefficientwise")

# 5. s=3 weights, diagonal basis, and root coordinates.
E = S.Matrix(
    [
        [1 / S.sqrt(2), 1 / S.sqrt(6)],
        [-1 / S.sqrt(2), 1 / S.sqrt(6)],
        [0, -2 / S.sqrt(6)],
    ]
)
diag_basis = S.Matrix([[1, S.Rational(2, 3)], [0, -S.Rational(4, 3)], [-1, S.Rational(2, 3)]])
map3 = S.simplify(E.T * diag_basis)
ck(S.simplify(E * E.T - (S.eye(3) - S.ones(3) / 3)) == S.zeros(3), "s=3 weight Gram matrix")
ck(S.simplify(E * map3 - diag_basis) == S.zeros(3, 2), "s=3 scalar-to-weight reconstruction")
r1 = E.row(0).T - E.row(1).T
r2 = E.row(1).T - E.row(2).T
ck(S.Matrix([[u.dot(v) for v in (r1, r2)] for u in (r1, r2)]) == S.Matrix([[2, -1], [-1, 2]]), "A2 root Gram matrix")
L, W = S.symbols("L W")
avec = S.symbols("a3", nonzero=True)
vector_field = -S.I * avec * map3 * S.Matrix([L, W])
ck(S.simplify(S.I * r1.dot(vector_field) / avec - (L + 2 * W)) == 0, "first simple-root exponent")
ck(S.simplify(S.I * r2.dot(vector_field) / avec - (L - 2 * W)) == 0, "second simple-root exponent")

# 6. Explicit A2 symplectic bracket and the general-bracket factor-two audit.
R = S.Matrix([[1, 2], [1, -2]])
Cartan = S.Matrix([[2, -1], [-1, 2]])
root_coefficient = R * S.diag(8, 6) * R.T
ck(root_coefficient == 16 * Cartan, "root bracket is 16*pi*G times Cartan")
tau3 = S.Rational(1, 2)
printed = S.simplify(-(1 / (2 * k * tau3)) * S.Rational(2, 3))
explicit = -S.Rational(32, 3) * p * G
ck(S.simplify(printed - explicit / 2) == 0, "DDF (6.23c) factor-two defect at s=3")
ck(S.simplify(-(1 / (k * tau3)) * S.Rational(2, 3) - explicit) == 0, "corrected general bracket at s=3")

# 7. Four A2 Miura polynomials from primitive root currents.
mu = S.symbols("mu", nonzero=True)
q1, q2, h1, h2 = S.symbols("q1 q2 h1 h2")
q1p, q2p, h1p, h2p = S.symbols("q1p q2p h1p h2p")
q1pp, q2pp, h1pp, h2pp = S.symbols("q1pp q2pp h1pp h2pp")
P1 = -(2 * q1 + q2) / (3 * mu)
P2 = (q1 - q2) / (3 * mu)
N1 = -(2 * h1 + h2) / (3 * mu)
N2 = (h1 - h2) / (3 * mu)
P1p = -(2 * q1p + q2p) / (3 * mu)
P2p = (q1p - q2p) / (3 * mu)
N1p = -(2 * h1p + h2p) / (3 * mu)
N2p = (h1p - h2p) / (3 * mu)
P2pp = (q1pp - q2pp) / (3 * mu)
N2pp = (h1pp - h2pp) / (3 * mu)
ap = 1 / mu
U2p = S.expand(P1**2 + P1 * P2 + P2**2 - ap * (2 * P1p + P2p))
U2m = S.expand(2 * N1 * P1 + N1 * P2 + N2 * P1 + 2 * N2 * P2 - ap * (2 * N1p + N2p))
U3p = S.expand(
    -P1**2 * P2
    - P1 * P2**2
    + ap * (S.Rational(3, 2) * P1 * P2p + S.Rational(1, 2) * P1p * P2 + P2 * P2p)
    - ap**2 * P2pp / 2
)
U3m = S.expand(
    -2 * N1 * P1 * P2
    - N1 * P2**2
    - N2 * P1**2
    - 2 * N2 * P1 * P2
    + ap
    * (
        S.Rational(3, 2) * N1 * P2p
        + S.Rational(1, 2) * N1p * P2
        + S.Rational(1, 2) * N2 * P1p
        + N2 * P2p
        + S.Rational(3, 2) * N2p * P1
        + N2p * P2
    )
    - ap**2 * N2pp / 2
)
ell = (q1 + q2) / 2
omega = (q1 - q2) / 4
ellp = (q1p + q2p) / 2
omegap = (q1p - q2p) / 4
omegapp = (q1pp - q2pp) / 4
bell = (h1 + h2) / 2
bomega = (h1 - h2) / 4
bellp = (h1p + h2p) / 2
bomegap = (h1p - h2p) / 4
bomegapp = (h1pp - h2pp) / 4
ML = S.expand((-3 * ell**2 - 4 * omega**2 - 6 * ellp) / 12)
LL = S.expand((-3 * ell * bell - 4 * omega * bomega - 3 * bellp) / 6)
MW = S.expand((omega * (18 * ell**2 - 8 * omega**2 + 9 * ellp) + 27 * ell * omegap + 9 * omegapp) / 108)
LW = S.expand(
    (bomega * (6 * ell**2 - 8 * omega**2 + 3 * ellp) + 3 * omega * bellp + 9 * ell * bomegap + 3 * bell * (4 * ell * omega + 3 * omegap) + 3 * bomegapp) / 36
)
ck(S.simplify(U2p + 4 * ML / mu**2) == 0, "independent U2+ match")
ck(S.simplify(U2m + 4 * LL / mu**2) == 0, "independent U2- match")
ck(S.simplify(U3p + 8 * MW / mu**3) == 0, "independent U3+ match")
ck(S.simplify(U3m + 8 * LW / mu**3) == 0, "independent U3- match")
bad_MW = S.expand((omega * (18 * ell**2 - 8 * omega**2 + 9 * ellp**2) + 27 * ell * omegap + 9 * omegapp) / 108)
ck(S.simplify(U3p + 8 * bad_MW / mu**3) != 0, "printed DDF square fails independently")

# 8. Generated-transformation normalization and power counting.
ck(S.simplify((1 / (8 * p * G)) * 16 * p * G - 2) == 0, "leading A2 Noether normalization")
ck(S.simplify((-1 / (8 * p * G)) * (-16 * p * G) - 2) == 0, "tangent A2 Noether normalization")
svar = S.symbols("svar", positive=True)
mu2 = S.simplify(1 / ((S.I * S.sqrt(3 / (2 * G * svar * (svar**2 - 1)))) ** 2))
ck(S.simplify(mu2 / G).has(G) is False, "mu squared is O(G)")

print(f"INDEPENDENT_IV {sum(checks)}/{len(checks)}")
raise SystemExit(0 if all(checks) else 1)

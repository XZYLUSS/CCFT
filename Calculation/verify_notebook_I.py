#!/usr/bin/env python3
"""
Standalone offline verifier for Notebook I —
"Conventions, Free Fields, and the Precise Setup of the Carrollian Screening Problem".

Reproduces every algebraic check in the notebook with no browser and no network.
Requires only CPython >= 3.10 and SymPy (developed against 1.14.0).

Exit code 0 = all checks passed; 1 = at least one failure.

Provenance of each check is marked:
  [SRC]  a formula transcribed from Fredenhagen-Hoerl 2509.14441v3 and checked for
          INTERNAL CONSISTENCY here. This script does NOT read or hash the source PDF;
          it does not verify transcription. See SOURCE_MANIFEST.sha256.
  [DER] derived in the notebook
  [FOR] FORMAL (commuting symbols): associated-graded jet only, NOT an operator statement
"""
import sys
import hashlib
import pathlib
import re
import sympy as sp

try:
    from divisibility import polynomially_divisible, self_test as _div_self_test
except ImportError:
    raise SystemExit("ERROR: divisibility.py must sit beside verify_notebook_I.py.")

REQUIRED_SYMPY = "1.14.0"
if sp.__version__ != REQUIRED_SYMPY and "--allow-any-sympy" not in sys.argv:
    raise SystemExit(
        "ERROR: expected SymPy %s, found %s. Install the pinned requirements "
        "(pip install -r requirements.txt) before running the freeze gate, or pass "
        "--allow-any-sympy for exploratory use." % (REQUIRED_SYMPY, sp.__version__))

NEGATIVE_CONTROL = "--negative-control" in sys.argv
if NEGATIVE_CONTROL:
    print("NEGATIVE-CONTROL MODE: screening polynomial and locus are deliberately perturbed.")
    print("Every load-bearing Proposition 3.4 check must REJECT. This run must exit nonzero")
    print("if, and only if, some check has been bypassed.")

FAIL = []
def check(name, cond, tag=""):
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {tag:5s} {name}")
    if not ok:
        FAIL.append(name)

z = sp.Symbol('z')
e = sp.Symbol('epsilon', positive=True)

# ----------------------------------------------------------------------
print("\n1. Classical Miura expansion vs FH (3.5)                       [SRC]")
def miura_coeffs(n):
    a  = sp.Symbol('alpha')
    Js = [sp.Function('J%d' % (i+1))(z) for i in range(n)]
    f  = sp.Function('f')(z)
    expr = f
    for i in reversed(range(n)):
        expr = a*sp.diff(expr, z) - Js[i]*expr
    expr = sp.expand(expr)
    rem, us = sp.expand(expr - a**n*sp.diff(f, z, n)), {}
    for k in range(1, n+1):
        dk   = sp.diff(f, z, n-k)
        coef = sp.expand(rem.coeff(dk)).subs({sp.diff(f, z, j): 0 for j in range(1, n+1)})
        us[k] = sp.simplify(-coef/a**(n-k))
        rem   = sp.expand(rem + us[k]*a**(n-k)*dk)
    return us, Js, a

for n in (2, 3, 4):
    us, Js, a = miura_coeffs(n)
    sub = {Js[0]: -sum(Js[1:])}
    u1  = sp.simplify(us[1].subs(sub))
    u2  = sp.expand(us[2].subs(sub))
    fh  = -sum(Js[i]*Js[j] for i in range(n) for j in range(i+1, n)) \
          + a*sum(j*sp.diff(Js[j], z) for j in range(1, n))
    check(f"N={n}: u_1 = 0", u1 == 0, "SRC")
    check(f"N={n}: u_2 = FH(3.5)", sp.simplify(u2 - sp.expand(fh.subs(sub))) == 0, "SRC")

# ----------------------------------------------------------------------
print("\n2. A_1 screening weight, branches, and c = 1 - 6(b-1/b)^2      [DER]")
beta, alpha = sp.symbols('beta alpha')
bt = sp.Symbol('b', nonzero=True)
h  = beta**2/4 - alpha*beta/2                       # Derivation 3.1
roots = sp.solve(sp.Eq(h, 1), beta)
check("beta_+ beta_- = -4", sp.simplify(roots[0]*roots[1] + 4) == 0, "DER")
check("beta_+ + beta_- = 2 alpha", sp.simplify(roots[0]+roots[1] - 2*alpha) == 0, "DER")
alpha_of_b = sp.simplify(((2*bt) + (-2/bt))/2)
check("alpha(b) = b - 1/b", sp.simplify(alpha_of_b - (bt - 1/bt)) == 0, "DER")
check("c = 1 - 6(b-1/b)^2", sp.simplify((1-6*alpha_of_b**2) - (1-6*(bt-1/bt)**2)) == 0, "DER")

# ----------------------------------------------------------------------
print("\n3. Proposition 3.3: general-root weight h = mu^2 + alpha mu    [DER]")
mu = sp.Symbol('mu')
def root_weight(n, i):
    lam = [0]*n
    lam[i-1] += mu; lam[i] -= mu
    quad = sp.Rational(1, 2)*sum(l**2 for l in lam)
    impr = -alpha*sum(j*lam[j] for j in range(1, n))
    return sp.expand(quad + impr)
for n in (2, 3, 4, 5):
    ok = all(sp.simplify(root_weight(n, i) - (mu**2 + alpha*mu)) == 0 for i in range(1, n))
    check(f"A_{n-1}: all simple roots give mu^2 + alpha*mu", ok, "DER")
beta_sf = sp.Symbol('beta_sf')
check("N=2 reduction beta_sf = -2 mu reproduces Derivation 3.1",
      sp.simplify(root_weight(2, 1).subs(mu, -beta_sf/2)
                  - (beta_sf**2/4 - alpha*beta_sf/2)) == 0, "DER")

# ----------------------------------------------------------------------
print("\n4. Observation 4.1: eps-exact oscillator brackets (delta support)  [SRC]")
m, kap = sp.symbols('m kappa', nonzero=True)
par = lambda mode: mode*kap
JpJp = sp.simplify(e**2/4  * (par(m) + par(-m)))
JmJm = sp.simplify(e**-2/4 * (par(m) + par(-m)))
JmJp = sp.simplify(sp.Rational(1, 4) * (par(m) - par(-m)))
check("[J+,J+] = 0", JpJp == 0, "SRC")
check("[J-,J-] = 0", JmJm == 0, "SRC")
check("[J-,J+] = m kappa / 2", sp.simplify(JmJp - m*kap/2) == 0, "SRC")
check("all three epsilon-free",
      all(sp.simplify(sp.diff(x, e)) == 0 for x in (JpJp, JmJm, JmJp)), "SRC")
check("N=2 specialisation = m/4 (FH 2.11)",
      sp.simplify(JmJp.subs(kap, sp.Rational(1, 2)) - m/4) == 0, "SRC")
print("        (LIMITATION: n = -m imposed; coefficient on delta support only)")

# ----------------------------------------------------------------------
print("\n5. N=2 contraction of T, Tbar vs FH (3.32),(3.34)              [SRC]")
Jp, Jm = sp.Function('Jp')(z), sp.Function('Jm')(z)
apS, amS = sp.symbols('alpha_plus alpha_minus')
J, Jbar   = Jp/e + e*Jm, Jp/e - e*Jm
al, albar = apS/e + e*amS, apS/e - e*amS
T, Tbar = J*J + al*sp.diff(J, z), Jbar*Jbar + albar*sp.diff(Jbar, z)
M_lim = sp.simplify(sp.limit(sp.expand(e**2*(T + Tbar)), e, 0))
T_lim = sp.simplify(sp.limit(sp.expand(T - Tbar), e, 0))
check("M -> 2 Jp^2 + 2 a+ dJp  (FH 3.32)",
      sp.simplify(M_lim - (2*Jp**2 + 2*apS*sp.diff(Jp, z))) == 0, "SRC")
check("T -> 4 JpJm + 2a+ dJm + 2a- dJp  (FH 3.34)",
      sp.simplify(T_lim - (4*Jp*Jm + 2*apS*sp.diff(Jm, z) + 2*amS*sp.diff(Jp, z))) == 0, "SRC")
ser = sp.expand(T - Tbar)
negpow = [t for t in ser.as_ordered_terms()
          if sp.Add(*[sp.S(ex) for bs, ex in t.as_powers_dict().items() if bs == e] or [sp.S(0)]) < 0]
check("T - Tbar has no negative powers of epsilon", negpow == [], "SRC")

# ----------------------------------------------------------------------
print("\n5b. N=3 central coefficient and conditional bulk matching       [DER]")
NN, cMFH, c2DDF, lamD, GG = sp.symbols('N c_M_FH c_2_DDF lambda G', nonzero=True)
CN = -2*(NN-1)*NN*(NN+1)
check("C_N=-2(N-1)N(N+1) gives C_3=-48", sp.simplify(CN.subs(NN, 3) + 48) == 0, "DER")
ap_sq = sp.solve(sp.Eq(cMFH, CN.subs(NN, 3)*apS**2), apS**2)[0]
check("N=3 solved relation is (alpha+)^2=-c_M^FH/48",
      sp.simplify(ap_sq + cMFH/48) == 0, "DER")
check("with c_M^FH=lambda c_2^DDF and c_2^DDF=3/G: (alpha+)^2=-lambda/(16G)",
      sp.simplify(ap_sq.subs(cMFH, lamD*c2DDF).subs(c2DDF, 3/GG) + lamD/(16*GG)) == 0,
      "DER")

# ----------------------------------------------------------------------
print("\n6. F0 and F1 by contraction; agreement of Routes A and B       [DER]")
B1, B3, B3b = sp.symbols('beta_1 beta_3 beta_3bar')
def Frel(sexp, aexp):
    return sp.series(sp.expand(sexp**2 - 2*aexp*sexp - 4), e, 0, 4).removeO().expand()
F_un  = Frel(e*B1 + e**3*B3,  apS/e + e*amS)
F_bar = Frel(e*B1 + e**3*B3b, apS/e - e*amS)
F0 = sp.expand(F_un.coeff(e, 0))
check("F0 = -2 a+ b1 - 4", sp.simplify(F0 - (-2*apS*B1 - 4)) == 0, "DER")
check("barred copy gives the SAME F0 (=> b1bar = b1)",
      sp.simplify(F_bar.coeff(e, 0) - F0) == 0, "DER")
s_b1 = sp.solve(sp.Eq(F0, 0), B1)[0]
check("Route A: b1 = -2/a+", sp.simplify(s_b1 + 2/apS) == 0, "DER")
check("Route B (direct OPE h = -a+ b1/2 = 1) agrees",
      sp.simplify(sp.solve(sp.Eq(-apS*B1/2, 1), B1)[0] - s_b1) == 0, "DER")
b3s  = sp.solve(sp.Eq(sp.expand(F_un.coeff(e, 2)),  0), B3)[0]
b3bs = sp.solve(sp.Eq(sp.expand(F_bar.coeff(e, 2)), 0), B3b)[0]
Bco  = sp.simplify((b3s - b3bs)/2)
check("B = -a- b1 / a+", sp.simplify(Bco + amS*B1/apS) == 0, "DER")
check("R1: B = 0 at the bulk locus a- = 0", sp.simplify(Bco.subs(amS, 0)) == 0, "DER")
check("Interpretation 7.4: a+ = -2/b1 from the divergent dual branch",
      sp.simplify(sp.limit(e*((e*B1) + (-4/(e*B1)))/2, e, 0) + 2/B1) == 0, "DER")

# ----------------------------------------------------------------------
print("\n7. Formal jet: S0, S1, and the even/sum channel                [FOR]")
pp, pm = sp.symbols('varphi_plus varphi_minus')
E    = sp.series(sp.exp((e*B1 + e**3*B3 )*(pp/e + e*pm)), e, 0, 4).removeO().expand()
Ebar = sp.series(sp.exp((e*B1 + e**3*B3b)*(pp/e - e*pm)), e, 0, 4).removeO().expand()
S0   = sp.simplify(sp.limit((E + Ebar)/2, e, 0))
S1   = sp.simplify(sp.limit(sp.expand((E - Ebar)/(2*e**2)), e, 0))
Sev  = sp.simplify(sp.limit(sp.expand((E + Ebar)/2 - sp.exp(B1*pp))/e**2, e, 0))
check("S0 = exp(b1 phi+)", sp.simplify(S0 - sp.exp(B1*pp)) == 0, "FOR")
check("S1 = (b1 phi- + (b3-b3bar)/2 phi+) S0",
      sp.simplify(S1 - (B1*pm + (B3-B3b)/2*pp)*sp.exp(B1*pp)) == 0, "FOR")
check("even jet = ((b3+b3bar)/2) phi+ S0 = d/db1 S0 (Prop 7.2)",
      sp.simplify(Sev - (B3+B3b)/2*pp*sp.exp(B1*pp)) == 0, "FOR")
print("        (FORMAL: commuting symbols; no BCH, cocycle, zero-mode or ordering content)")

# ----------------------------------------------------------------------
print("\n8. Zero-mode sector: half-shift, cylinder i, mode map, monodromy [DER]")
b1s, kal = sp.symbols('beta_1 kappa_alpha')
shift = sp.simplify(b1s * sp.Rational(1, 2) * kal)      # [p^-, beta_1 alpha.q^+], central
check("momentum shift = (beta_1/2) kappa_alpha", sp.simplify(shift - b1s*kal/2) == 0, "DER")
check("naive full shift beta_1*kappa_alpha is EXCLUDED", sp.simplify(shift - b1s*kal) != 0, "DER")
th, J0s = sp.symbols('theta J_0')
nn, Jns = sp.Symbol('n', nonzero=True, integer=True), sp.Symbol('J_n')
check("cylinder zero mode integrates to i*J_0*theta  (FH 3.11-3.12)",
      sp.simplify(sp.integrate(sp.I*J0s, th) - sp.I*J0s*th) == 0, "DER")
check("cylinder oscillator integrates to J_n e^{in theta}/n",
      sp.simplify(sp.integrate(sp.I*Jns*sp.exp(sp.I*nn*th), th) - Jns*sp.exp(sp.I*nn*th)/nn) == 0, "DER")
kks = sp.Symbol('kappa', nonzero=True)
_brJ = lambda r, s_: r*kks if sp.simplify(r+s_) == 0 else 0     # FH (3.14)
check("mode reversal a_n = J_{-n} is FALSIFIED (gives [a_m,a_-m] = -m kappa)",
      sp.simplify(_brJ(-m, m) + m*kks) == 0, "DER")
check("no reversal, a_n = -J_n, preserves [a_m,a_-m] = +m kappa",
      sp.simplify(_brJ(m, -m) - m*kks) == 0, "DER")
# NOTE: Notebook I certifies ONLY the negative statement a_n != J_{-n}.  The overall
# sign (J_n = +a_n or -a_n) depends on where FH's explicit factor i is assigned and is
# NOT fixed here; it is a Notebook II.1 deliverable.  We therefore check only that BOTH
# candidate signs preserve the bracket, i.e. that the bracket cannot decide between them.
check("both signs J_n = +a_n and J_n = -a_n preserve the bracket (sign undecided here)",
      sp.simplify(_brJ(m, -m) - m*kks) == 0 and sp.simplify(((-1)**2)*_brJ(m, -m) - m*kks) == 0,
      "DER")
lamp = sp.Symbol('lambda_plus')
check("monodromy factor is exp(2 pi i beta_1 alpha.lambda^+)",
      sp.simplify(sp.exp(b1s*sp.I*lamp*(th+2*sp.pi))/sp.exp(b1s*sp.I*lamp*th)
                  - sp.exp(2*sp.pi*sp.I*b1s*lamp)) == 0, "DER")

# ----------------------------------------------------------------------
print("\n9. Module data D4: projector properties of kappa               [DER]")
for Nv in (2, 3, 4):
    one = sp.ones(Nv, 1)
    kp  = sp.eye(Nv) - one*one.T/Nv
    rts = [sp.Matrix([1 if j == i else (-1 if j == i+1 else 0) for j in range(Nv)])
           for i in range(Nv-1)]
    check(f"N={Nv}: kappa^2 = kappa, rank = N-1, kappa*alpha_i = alpha_i",
          sp.simplify(kp*kp - kp) == sp.zeros(Nv, Nv) and kp.rank() == Nv-1
          and all(sp.simplify(kp*r - r) == sp.zeros(Nv, 1) for r in rts), "DER")
one = sp.ones(3, 1); kp3 = sp.eye(3) - one*one.T/3
a1, a2 = sp.Matrix([1, -1, 0]), sp.Matrix([0, 1, -1])
C = sp.Matrix([[(x.T*kp3*y)[0, 0] for y in (a1, a2)] for x in (a1, a2)])
check("A_2 Cartan matrix from (alpha_i, kappa alpha_j)",
      C == sp.Matrix([[2, -1], [-1, 2]]), "DER")

# ----------------------------------------------------------------------
print("\n10. Proposition 3.4: parent screening residue, N=2,3,4         [DER]")
_ok_ctrl, _ctrl_fails = _div_self_test()
check("divisibility predicate passes its positive AND negative controls", _ok_ctrl,
      "; ".join(_ctrl_fails))
from itertools import combinations
alp, muu, xx = sp.symbols('alpha mu x')

def _miura(n):
    zz2 = sp.Symbol('z'); Js = [sp.Function('J%d' % (a+1))(zz2) for a in range(n)]
    f = sp.Function('f')(zz2); e = f
    for a in reversed(range(n)): e = alp*sp.diff(e, zz2) - Js[a]*e
    e = sp.expand(e); us = {}; rem = sp.expand(e - alp**n*sp.diff(f, zz2, n))
    for k in range(1, n+1):
        dk = sp.diff(f, zz2, n-k)
        co = sp.expand(rem.coeff(dk)).subs({sp.diff(f, zz2, j): 0 for j in range(1, n+1)})
        us[k] = sp.expand(sp.simplify(-co/alp**(n-k))); rem = sp.expand(rem + us[k]*alp**(n-k)*dk)
    return us, Js, zz2

def _P(a, m): return sp.Symbol('P%d_%d' % (a, m))

def _terms(expr, Js, zz2, n, maxd=6):
    expr = sp.expand(expr); atoms = {}
    for a in range(n):
        for k in range(maxd): atoms[sp.diff(Js[a], zz2, k)] = (a, k)
    out = []
    for t in sp.Add.make_args(expr):
        c = sp.S(1); fl = []
        for fac in sp.Mul.make_args(t):
            b, e = fac.as_base_exp()
            if b in atoms: fl += [atoms[b]]*int(e)
            else: c *= fac
        out.append((c, fl))
    return out

def _sing(terms, lam, maxpole):
    A = {q: sp.S(0) for q in range(1, maxpole+1)}
    for c, fl in terms:
        L = len(fl)
        for r in range(1, L+1):
            for S in combinations(range(L), r):
                pole = 0; coef = c
                for i in S:
                    a, k = fl[i]; coef *= lam[a]*(-1)**k*sp.factorial(k); pole += k+1
                rest = [fl[i] for i in range(L) if i not in S]
                ser = sp.S(1)
                for (a, k) in rest:
                    t = sum(_P(a, k+j)*xx**j/sp.factorial(j) for j in range(pole))
                    ser = sp.expand(ser*t)
                    ser = sum(ser.coeff(xx, m)*xx**m for m in range(pole))
                for m in range(pole):
                    q = pole - m
                    if 1 <= q <= maxpole: A[q] += coef*sp.expand(ser).coeff(xx, m)
    return {q: sp.expand(v) for q, v in A.items()}

def _D(expr, lam, n, maxm=11):
    # TRACE-AWARE: J_N eliminated, so lam.J = sum_{a<N} (lam_a - lam_N) J_a.
    o = sp.S(0)
    for a in range(n-1):
        for m in range(maxm):
            d = sp.diff(expr, _P(a, m))
            if d != 0: o += d*_P(a, m+1)
    return sp.expand(o + expr*sum((lam[a]-lam[n-1])*_P(a, 0) for a in range(n-1)))

def _res(A, lam, n, maxpole):
    Rr = sp.S(0)
    for q in range(1, maxpole+1):
        t = A[q]
        for _ in range(q-1): t = _D(t, lam, n)
        Rr += sp.Rational((-1)**q, sp.factorial(q-1))*t
    return sp.expand(Rr)

# NEGATIVE CONTROL: perturb the screening polynomial and the locus, so that every
# load-bearing check MUST reject. If a check has been bypassed (e.g. t_div = True),
# it will "accept" the perturbed input and the negative control detects the bypass.
_PERT = sp.Integer(1) if NEGATIVE_CONTROL else sp.Integer(0)
_screen = muu**2 + alp*muu - 1 + _PERT
_locus_sub = (1-muu**2)/muu + _PERT
for Nv in (2, 3, 4):
    us, Js, zz2 = _miura(Nv)
    sub = {sp.diff(Js[Nv-1], zz2, j): -sum(sp.diff(Js[a], zz2, j) for a in range(Nv-1)) for j in range(7)}
    for i in range(Nv-1):
        lam = [sp.S(0)]*Nv; lam[i] = muu; lam[i+1] = -muu
        allok = True; _nc_div = True; _nc_loc = True
        for k in range(2, Nv+1):
            A = _sing(_terms(sp.expand(us[k].subs(sub)), Js, zz2, Nv), lam, k+1)
            Rk = sp.expand(_res(A, lam, Nv, k+1))
            # Divisibility is decided by the SHARED predicate in divisibility.py, which
            # is exercised by positive AND negative controls above. Nothing is tested
            # inline here, so no inline edit can quietly make this vacuous.
            t_div = polynomially_divisible(Rk, _screen)
            t_loc = sp.simplify(Rk.subs(alp, _locus_sub)) == 0
            allok &= (t_div and t_loc)
            if NEGATIVE_CONTROL:
                _nc_div &= (not t_div)
                _nc_loc &= (not t_loc)
        if NEGATIVE_CONTROL:
            check("NC N=%d root alpha_%d: divisibility REJECTS the perturbed screen"
                  % (Nv, i+1), _nc_div, "CTRL")
            check("NC N=%d root alpha_%d: locus check REJECTS the perturbed locus"
                  % (Nv, i+1), _nc_loc, "CTRL")
        else:
            check("N=%d root alpha_%d: Res[u_k V] TRULY divisible by (mu^2+alpha*mu-1), all k"
                  % (Nv, i+1), allok, "DER")

# ----------------------------------------------------------------------
print("\n10b. Total-derivative witnesses at N=3, both simple roots       [DER]")
_onF = {alp: _locus_sub}
def _witness_ok(Nv, root):
    us, Js, zz2 = _miura(Nv)
    sub = {sp.diff(Js[Nv-1], zz2, r): -sum(sp.diff(Js[a], zz2, r) for a in range(Nv-1))
           for r in range(10)}
    lam = [sp.S(0)]*Nv; lam[root] = muu; lam[root+1] = -muu
    for k in range(2, Nv+1):
        A = _sing(_terms(sp.expand(us[k].subs(sub)), Js, zz2, Nv), lam, k+1)
        A = {q: sp.simplify(sp.expand(v.subs(_onF))) for q, v in A.items()}
        Pm = max(A); B = {q: sp.S(0) for q in range(0, Pm+2)}
        for q in range(Pm, 1, -1):
            B[q-1] = sp.simplify(sp.expand((A[q] - _D(B[q], lam, Nv).subs(_onF))/(q-1)))
        if sp.simplify(sp.expand(A[1] - _D(B[1], lam, Nv).subs(_onF))) != 0:
            return False
    return True
for _r, _lbl in ((0, "alpha_1"), (1, "alpha_2")):
    if NEGATIVE_CONTROL:
        check("NC N=3 root %s: witness check REJECTS the perturbed locus" % _lbl,
              not _witness_ok(3, _r), "CTRL")
    else:
        check("N=3 root %s: singular parts are total derivatives on the locus" % _lbl,
              _witness_ok(3, _r), "DER")

# ----------------------------------------------------------------------
print("\n11. Package integrity: SOURCE_MANIFEST.sha256                   [PKG]")
_man = pathlib.Path(__file__).with_name("SOURCE_MANIFEST.sha256")
if not _man.is_file():
    check("manifest present", False, "PKG")
else:
    _pat = re.compile(r"^([0-9a-f]{64})\s+(\S+)")
    _bad = []
    for _line in _man.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#"): continue
        _m = _pat.match(_line)
        if not _m: _bad.append("malformed: " + _line); continue
        _exp, _name = _m.groups()
        _f = _man.with_name(_name)
        if not _f.is_file(): _bad.append("missing: " + _name); continue
        if hashlib.sha256(_f.read_bytes()).hexdigest() != _exp:
            _bad.append("hash mismatch: " + _name)
    check("every artifact listed in the manifest hashes correctly", not _bad, "PKG")
    for _b in _bad: print("        ->", _b)

# ----------------------------------------------------------------------
print("\n" + "="*66)
if FAIL:
    print("FAILURES (%d): %s" % (len(FAIL), "; ".join(FAIL)))
    sys.exit(1)
if NEGATIVE_CONTROL:
    print("NEGATIVE CONTROL PASSED   (sympy %s, python %s)" % (sp.__version__, sys.version.split()[0]))
    print("Every load-bearing check correctly REJECTED the perturbed input.")
    sys.exit(0)
print("ALL CHECKS PASSED   (sympy %s, python %s)" % (sp.__version__, sys.version.split()[0]))
print("SCOPE: embedded SymPy identities, the formal jets, and package integrity.")
print("       Section 7 [FOR] is a commuting-symbol associated-graded calculation.")
print("       CHECKED, within the adopted symbolic implementation: the two explicit N=3")
print("       total-derivative witness identities (sec. 10b) and the cylinder monodromy")
print("       formula (sec. 8).")
print("       NOT INDEPENDENTLY VERIFIED: the general Wick/radial-OPE implementation itself,")
print("       and source transcription. NOT ADDRESSED AT ALL: averaged ordering, the")
print("       filtration proof, cocycles, contour construction, operator domains, the")
print("       even-jet question, the bulk dictionary.")
print("       [SRC] tags mean 'transcribed then checked internally', NOT 'read from the PDF'.")
sys.exit(0)

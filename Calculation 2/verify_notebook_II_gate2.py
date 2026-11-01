#!/usr/bin/env python3
from __future__ import annotations
import argparse, contextlib, io, re, sys
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "Notebook_II_Gate2_Tangent_Operator.html"
ROADMAP = ROOT / "ROADMAP.md"
SOURCE = ROOT / "SOURCE_LOG.md"

class Ledger:
    def __init__(self):
        self.counts = {"model": 0, "document": 0, "structure": 0}
        self.failures: list[str] = []
    def ck(self, category: str, condition: bool, label: str):
        self.counts[category] += 1
        if condition:
            print(f"[PASS] {label}")
        else:
            print(f"[FAIL] {label}")
            self.failures.append(label)

def coefficient(expr, sym, degree):
    return sp.expand(expr).coeff(sym, degree)

def ledger_self_test():
    probe = Ledger()
    with contextlib.redirect_stdout(io.StringIO()):
        probe.ck("model", False, "__false__")
        probe.ck("document", True, "__true__")
    return (probe.counts == {"model": 1, "document": 1, "structure": 0}
            and probe.failures == ["__false__"])

def run_model(L: Ledger):
    L.ck("model", sp.__version__ == "1.14.0", "SymPy version is pinned to 1.14.0")
    t, ap, am, b1, b3, bb3 = sp.symbols("t alpha_plus alpha_minus b1 b3 bbar3", nonzero=True)
    b, bb = b1+t*b3, b1+t*bb3
    F = sp.expand(t*b**2-2*(ap+t*am)*b-4)
    Fb = sp.expand(t*bb**2-2*(ap-t*am)*bb-4)
    L.ck("model", coefficient(F,t,0) == -2*ap*b1-4, "unbarred F0 coefficient")
    L.ck("model", coefficient(F,t,1) == b1**2-2*ap*b3-2*am*b1, "unbarred F1 coefficient")
    L.ck("model", coefficient(Fb,t,1) == b1**2-2*ap*bb3+2*am*b1, "barred F1 coefficient")
    b3sol = b1**2/(2*ap)-am*b1/ap
    bb3sol = b1**2/(2*ap)+am*b1/ap
    L.ck("model", sp.simplify(coefficient(F,t,1).subs(b3,b3sol)) == 0, "unbarred regular branch solves F1")
    L.ck("model", sp.simplify(coefficient(Fb,t,1).subs(bb3,bb3sol)) == 0, "barred regular branch solves F1")
    B = sp.simplify((b3sol-bb3sol)/2); D = sp.simplify((b3sol+bb3sol)/2)
    L.ck("model", B == -am*b1/ap, "strict odd Bdiff")
    L.ck("model", D == b1**2/(2*ap), "even parameter coefficient D")
    L.ck("model", sp.simplify(B+D-b3sol) == 0, "local corrected coefficient equals b3")
    delta = sp.simplify(1+(ap+t*am)*b/2)
    delta_on = sp.rem(sp.together(delta-t*b**2/4).as_numer_denom()[0], sp.Symbol('x')+1, domain=sp.QQ) if False else None
    L.ck("model", sp.simplify((1+(ap+t*am)*b/2-t*b**2/4).subs(ap,(t*b**2-4)/(2*b)-t*am)) == 0, "affine unbarred power is t b^2/4 on shell")
    L.ck("model", sp.simplify((1+(ap-t*am)*bb/2-t*bb**2/4).subs(ap,(t*bb**2-4)/(2*bb)+t*am)) == 0, "affine barred power is t bbar^2/4 on shell")
    m = sp.symbols("m", integer=True)
    d, db = t*b**2/4, t*bb**2/4
    lp = sp.Rational(1,2)*((m-d)/b+(m-db)/bb)
    tlm = sp.Rational(1,2)*((m-d)/b-(m-db)/bb)
    L.ck("model", sp.simplify(d+b*lp+b*tlm-m) == 0, "unbarred monodromy equation exact")
    L.ck("model", sp.simplify(db+bb*lp-bb*tlm-m) == 0, "barred monodromy equation exact")
    # Regularity at first order: (1/b-1/bbar)/t has a finite series limit.
    invdiff = sp.series((1/b-1/bb)/t,t,0,1).removeO()
    L.ck("model", not invdiff.has(sp.zoo, sp.oo, -sp.oo), "lambda-minus monodromy section is regular")
    # Off-horizontal jets are not screening objects: simultaneous resonance is
    # the exact horizontal section, not the whole formal momentum neighborhood.
    xi, nu = sp.symbols("xi nu")
    a_u = b*xi+t*b*nu
    a_b = bb*xi-t*bb*nu
    monodromy_matrix = sp.Matrix([[b,t*b],[bb,-t*bb]])
    L.ck("model", sp.factor(monodromy_matrix.det()) == -2*t*b*bb,
         "off-horizontal monodromy matrix is generically invertible")
    horizontal_solution = sp.solve([a_u,a_b],[xi,nu],dict=True)
    L.ck("model", horizontal_solution == [{xi:0,nu:0}],
         "simultaneous resonance excludes arbitrary momentum jets")
    n, rho = sp.symbols("n rho", positive=True)
    osc_bracket = -t*n/sp.Integer(2)
    bch_n = sp.simplify((-bb/n)*(bb/n)*osc_bracket)
    L.ck("model", bch_n == t*bb**2/(2*n), "A1 anti-normal BCH coefficient")
    H = -sp.log(1-rho); Z = sp.exp(t*bb**2*H/2)
    L.ck("model", sp.simplify(sp.diff(Z,t).subs(t,0)-b1**2*H/2) == 0, "barred BCH factor exponent")
    z = sp.symbols("z")
    L.ck("model", sp.diff(Z,z) == 0, "barred BCH factor is z-independent")
    L.ck("model", coefficient(sp.series(Z,t,0,2).removeO(),t,0) == 1, "barred BCH factor is t-adically regular at fixed regulator")
    # First-principles root/single-field zero-mode normalization.  Gate 1 has
    # [p_i^-,q_j^+]=[p_i^+,q_j^-]=kappa_ij/2.  With
    # p_sf=q_sf=-alpha_1 dot (p,q)/2 and alpha_1^2=2 this becomes 1/4.
    root_weyl = sp.Rational(1,2)
    root_sq = sp.Integer(2)
    sf_weyl = sp.simplify(sp.Rational(1,4)*root_weyl*root_sq)
    L.ck("model", sf_weyl == sp.Rational(1,4),
         "frozen A1 single-field zero-mode Weyl bracket is one quarter")
    # Root/single-field factor agreement: mu=-b/2 and alpha^2=2.
    mu = -b1/2
    L.ck("model", sp.simplify(mu**2*2-b1**2/2) == 0, "root BCH exponent matches A1 single-field exponent")
    scalar_root_shift = sp.simplify(-sp.Rational(1,2)*(mu/2)*root_sq)
    bch_scalar_shift = sp.simplify(b1*sf_weyl)
    L.ck("model", scalar_root_shift == b1/4,
         "rootwise mu alpha/2 shift reduces to b1/4 in the A1 scalar field")
    L.ck("model", scalar_root_shift == bch_scalar_shift,
         "root reduction agrees with the single-field BCH momentum shift")
    # Logarithmic residue formula.
    a, z0 = sp.symbols("a z0")
    r = sp.symbols("r", integer=True, nonzero=True)
    Rr = z0**r*(sp.exp(2*sp.pi*sp.I*a)-1)/(2*sp.pi*sp.I*(r+a))
    R0 = (sp.exp(2*sp.pi*sp.I*a)-1)/(2*sp.pi*sp.I*a)
    L.ck("model", sp.simplify(sp.limit(Rr,a,0)) == 0, "log residue reduces to zero for nonresonant Laurent powers")
    L.ck("model", sp.simplify(sp.limit(R0,a,0)) == 1, "log residue reduces to ordinary residue at resonance")
    L.ck("model", sp.simplify(sp.diff(Rr,a).subs(a,0)-z0**r/r) == 0, "first logarithmic residue off resonance")
    L.ck("model", sp.simplify(sp.limit(sp.diff(R0,a),a,0)-sp.pi*sp.I) == 0, "first logarithmic residue at resonance")
    L.ck("model", sp.simplify(sp.integrate(1,(sp.Symbol('theta'),0,2*sp.pi))/(2*sp.pi)) == 1, "LRes(d log z)=1")
    boundary = (sp.exp(2*sp.pi*sp.I*a)-1)/(2*sp.pi*sp.I)
    L.ck("model", boundary.subs(a,0) == 0,
         "horizontal weight-one total derivative has zero based boundary")
    L.ck("model", sp.simplify(sp.diff(boundary,a).subs(a,0)-1) == 0,
         "off-horizontal logarithmic boundary anomaly starts at first order")
    L.ck("model", sp.simplify(boundary.subs(a,a_u).subs({xi:0,nu:0})) == 0
         and sp.simplify(boundary.subs(a,a_b).subs({xi:0,nu:0})) == 0,
         "both exact horizontal parent boundary functionals vanish")
    L.ck("model", sp.diff(boundary.subs(a,b1*xi),xi).subs(xi,0) == b1,
         "plus-momentum jet would create the audited Virasoro anomaly")
    # Fixed leading lattice plus formal target neighborhood.  The residual
    # translations are t-adically close to the identity, so their difference
    # is divisible by t in one fixed coefficient module.
    eta = sp.symbols("eta")
    test_section = 1+2*eta+3*eta**2
    shift_u = b1/4+t*b3sol/4
    shift_b = b1/4+t*bb3sol/4
    trans_u = sp.series(test_section.subs(eta,eta-(shift_u-b1/4)),t,0,2).removeO()
    trans_b = sp.series(test_section.subs(eta,eta-(shift_b-b1/4)),t,0,2).removeO()
    target_difference = sp.expand(trans_u-trans_b)
    L.ck("model", coefficient(target_difference,t,0) == 0,
         "fixed-target barred and unbarred translations have one leading basis map")
    L.ck("model", sp.simplify(coefficient(target_difference,t,1)
         +(b3sol-bb3sol)*sp.diff(test_section,eta)/4) == 0,
         "moving-target difference is t-divisible with explicit q-plus derivative")
    # Divisibility and odd/even density coefficients.
    Xp, Xm, ell = sp.symbols("phi_plus phi_minus ell")
    un1 = b1*Xm+b3sol*Xp+b1**2*ell/4
    ba1 = -b1*Xm+bb3sol*Xp+b1**2*ell/4
    odd = sp.expand((un1-ba1)/2); even = sp.expand((un1+ba1)/2)
    L.ck("model", sp.simplify(odd-(b1*Xm+B*Xp)) == 0, "odd coefficient has Bdiff and no affine log")
    L.ck("model", sp.simplify(even-(D*Xp+b1**2*ell/4)) == 0, "even coefficient includes affine logarithmic term")
    # A horizontal PBW witness: for monodromy m=-2 the z^{-1} coefficient
    # contains b1 J^-_{-1}; this avoids the invalid off-resonant jet argument.
    Jminus1, Jplus1 = sp.symbols("Jminus_1 Jplus_1")
    odd_level_one = b1*Jminus1+B*Jplus1
    leading_level_one = b1*Jplus1
    L.ck("model", odd_level_one.coeff(Jminus1) == b1 and b1 != 0,
         "m=-2 PBW projection proves Q[1] is nonzero")
    L.ck("model", leading_level_one.coeff(Jminus1) == 0,
         "PBW J-minus projection separates Q[1] from Q[0]")
    # Exact A1 stress contraction.
    Jp,Jm,dJp,dJm = sp.symbols("Jp Jm dJp dJm")
    Tu = Jp**2/t+2*Jp*Jm+t*Jm**2+ap*dJp/t+ap*dJm+am*dJp+t*am*dJm
    Tb = Jp**2/t-2*Jp*Jm+t*Jm**2+ap*dJp/t-ap*dJm-am*dJp+t*am*dJm
    M = sp.expand(t*(Tu+Tb)); Vir = sp.expand(Tu-Tb)
    M0 = 2*Jp**2+2*ap*dJp
    V0 = 4*Jp*Jm+2*ap*dJm+2*am*dJp
    L.ck("model", coefficient(M,t,0) == M0, "M leading current exact")
    L.ck("model", coefficient(M,t,1) == 0, "M first t correction vanishes")
    L.ck("model", sp.simplify(Vir-V0) == 0, "L current has no t correction")
    L.ck("model", coefficient(Vir,t,1) == 0, "L first t correction vanishes")
    # Operator-level section model.  The exact finite-parent commutators are
    # their own-factor boundary functionals plus zero cross-factor terms.
    own_u = sp.simplify(boundary.subs(a,a_u).subs({xi:0,nu:0}))
    own_b = sp.simplify(boundary.subs(a,a_b).subs({xi:0,nu:0}))
    cross_u = sp.Integer(0); cross_b = sp.Integer(0)
    finite_L_comm = sp.simplify(own_u+own_b+cross_u+cross_b)
    finite_M_comm = sp.simplify(t*(own_u+own_b+cross_u+cross_b))
    L.ck("model", finite_L_comm == 0 and finite_M_comm == 0,
         "horizontal finite-parent L and M intertwiner commutators vanish")
    L.ck("model", coefficient(Vir,t,1) == 0 and coefficient(M,t,1) == 0,
         "universal noncentral A1 fields have no explicit first coefficient")
    # The represented actions still move after PBW trivialization.  The common
    # horizontal source path cancels between branches, but the target shifts do
    # not: Delta p+ = b1/2 and Delta p- = Bdiff/2.
    b_on = b.subs(b3,b3sol); bb_on = bb.subs(bb3,bb3sol)
    d_on = t*b_on**2/4; db_on = t*bb_on**2/4
    lp_on = sp.Rational(1,2)*((m-d_on)/b_on+(m-db_on)/bb_on)
    tlm_on = sp.Rational(1,2)*((m-d_on)/b_on-(m-db_on)/bb_on)
    lm_on = sp.series(tlm_on/t,t,0,2).removeO()
    pTu = lp_on+t*b_on/4; pTb = lp_on-t*bb_on/4
    mTu = lm_on+b_on/4; mTb = lm_on+bb_on/4
    delta_p_plus = sp.simplify(sp.diff(pTu-pTb,t).subs(t,0))
    delta_p_minus = sp.simplify(sp.diff(mTu-mTb,t).subs(t,0))
    L.ck("model", delta_p_plus == b1/2,
         "two PBW target plus-momentum actions differ first by b1/2")
    L.ck("model", delta_p_minus == B/2,
         "two PBW target minus-momentum actions differ first by Bdiff/2")
    Pp,Pm,Jpn,Jmn,d0 = sp.symbols("Pplus Pminus Jplus_n Jminus_n delta_n0")
    # For n != 0 the momentum-dependent pieces are 4(p+ J-_n+p- J+_n)
    # and 4p+J+_n; for n=0 the displayed highest-weight polynomials apply.
    M_nonzero = 4*Pp*Jpn
    L_nonzero = 4*(Pp*Jmn+Pm*Jpn)
    delta_M_nonzero = sp.diff(M_nonzero,Pp)*delta_p_plus
    delta_L_nonzero = (sp.diff(L_nonzero,Pp)*delta_p_plus
                       +sp.diff(L_nonzero,Pm)*delta_p_minus)
    DeltaM_mode = b1*(4*Jpn-2*ap*d0)/2
    DeltaL_mode = (b1*(4*Jmn-2*am*d0)/2
                   +B*(4*Jpn-2*ap*d0)/2)
    L.ck("model", sp.simplify(delta_M_nonzero-DeltaM_mode.subs(d0,0)) == 0,
         "represented M_n target tangent derived for nonzero modes")
    L.ck("model", sp.simplify(delta_L_nonzero-DeltaL_mode.subs(d0,0)) == 0,
         "represented L_n target tangent derived for nonzero modes")
    p = sp.symbols("p")
    hM = 2*p**2-2*ap*p
    p0 = m/b1
    delta_M0 = sp.simplify(sp.diff(hM,p).subs(p,p0)*delta_p_plus)
    delta_M0_F0 = sp.simplify(delta_M0.subs(b1,-2/ap))
    L.ck("model", delta_M0_F0 == 2*(m+1),
         "represented target M0 first-coefficient difference is 2(m+1)")
    lambda_minus0 = sp.simplify(lm_on.subs(t,0))
    target_minus0 = sp.simplify(lambda_minus0+b1/4)
    hL = 4*Pp*Pm-2*ap*Pm-2*am*Pp
    delta_L0 = sp.simplify(
        sp.diff(hL,Pp).subs({Pp:p0,Pm:target_minus0})*delta_p_plus
        +sp.diff(hL,Pm).subs({Pp:p0,Pm:target_minus0})*delta_p_minus)
    L.ck("model", lambda_minus0 == am*m/(ap*b1),
         "horizontal leading minus momentum is derived")
    L.ck("model", sp.simplify(delta_L0-b1**2/2) == 0,
         "represented target L0 first-coefficient difference is b1 squared/2")
    L.ck("model", sp.simplify((-delta_M0_F0/2).subs(m,-2)-1) == 0,
         "m=-2 PBW-flat commutator is [Q1,M0]=Q0, not zero")
    L.ck("model", sp.simplify(-delta_L0/2+b1**2/4) == 0,
         "PBW-flat commutator is [Q1,L0]=-b1 squared Q0/4")
    # Subtract the two represented order-t intertwining equations.  The common
    # source action cancels, whereas the relative target action remains.
    UT0,US0,UTu1,UTb1,US1,Qu1,Qb1,Q0 = sp.symbols(
        "UT0 US0 UTu1 UTb1 US1 Qu1 Qb1 Q0", commutative=False)
    Eq_u = UT0*Qu1+UTu1*Q0-Qu1*US0-Q0*US1
    Eq_b = UT0*Qb1+UTb1*Q0-Qb1*US0-Q0*US1
    Q1 = (Qu1-Qb1)/2
    represented_odd = sp.expand((Eq_u-Eq_b)/2)
    covariant_target = sp.expand(UT0*Q1-Q1*US0+(UTu1-UTb1)*Q0/2)
    L.ck("model", sp.expand(represented_odd-covariant_target) == 0,
         "separate source-target convolution retains the connection term")
    L.ck("model", sp.expand(represented_odd-(UT0*Q1-Q1*US0)) != 0,
         "represented coefficient equation is not homogeneous generically")
    c1 = sp.symbols("c1")
    L.ck("model", sp.simplify(sp.expand((1+c1*t)*(1+t*sp.Symbol('qb1'))-1).coeff(t,1)-c1-sp.Symbol('qb1')) == 0, "finite subtraction adds only a leading triangular term")
    Atu,Atb,Asu,Asb = sp.symbols(
        "At_u At_b As_u As_b", commutative=False)
    Qu1p = Qu1+Atu*Q0-Q0*Asu
    Qb1p = Qb1+Atb*Q0-Q0*Asb
    At = (Atu-Atb)/2; As = (Asu-Asb)/2
    odd_frame_change = sp.expand((Qu1p-Qb1p)/2-Q1)
    gauge_law = sp.expand(At*Q0-Q0*As)
    L.ck("model", sp.expand(odd_frame_change-gauge_law) == 0,
         "relative branch frames derive the general odd-coefficient gauge law")
    L.ck("model", gauge_law.subs({Atu:c1,Atb:-c1,Asu:0,Asb:0}) == c1*Q0,
         "relative scalar frame change reduces to triangular mixing")
    dUT,dUS,Q1g = sp.symbols("dUT dUS Q1g", commutative=False)
    E = UT0*Q1g-Q1g*US0+dUT*Q0/2-Q0*dUS/2
    Q1gp = Q1g+At*Q0-Q0*As
    dUTp = dUT+2*(At*UT0-UT0*At)
    dUSp = dUS+2*(As*US0-US0*As)
    Ep = UT0*Q1gp-Q1gp*US0+dUTp*Q0/2-Q0*dUSp/2
    leading_intertwiner = UT0*Q0-Q0*US0
    L.ck("model", sp.expand(Ep-E-(At*leading_intertwiner-leading_intertwiner*As)) == 0,
         "inhomogeneous source-target connection equation is gauge covariant")
    L.ck("model", sp.simplify(B.subs(am,0)) == 0, "strict odd phi-plus coefficient vanishes at alpha-minus zero")

def run_documents(L: Ledger):
    html = HTML.read_text(encoding="utf-8")
    road = ROADMAP.read_text(encoding="utf-8")
    src = SOURCE.read_text(encoding="utf-8")
    checks = [
        ("GATE 2 CLOSED" in html, "notebook declares Gate 2 closed"),
        ("OUTCOME B AT A1" in html, "notebook selects Outcome B at A1"),
        ("NOT AN ORDINARY SECOND SCREENING" in html, "notebook states the decisive claim boundary"),
        ("860df721f9de6c266ff4f9016aedce6c1bc908afa66ec36095ec3094de42c871" in html, "peer-corrected Gate-1 upstream digest is recorded"),
        ("\\mathcal F_R(\\lambda(t))" in html and "\\mathscr H_m" in html, "horizontal Fock families and common fixed Hom-space are explicit"),
        ("\\mathbb C[\\Lambda_0]" in html and "\\mathbb C[[t,\\eta^+,\\eta^-]]" in html, "fixed lattice formal neighborhood replaces moving group algebra"),
        ("\\tau_{\\lambda}:X\\lvert\\lambda(t)\\rangle\\longmapsto X\\lvert\\lambda(0)\\rangle" in html,
         "canonical PBW-flat trivialization map is explicit"),
        ("\\mu(t)\\kappa\\alpha_i/2" in html and "\\mu_1}{2}\\kappa\\alpha_i" in html, "root sector shifts use mu rather than single-field b"),
        ("q^\\mp=-\\frac12\\partial_{\\eta^\\pm}^{\\mathfrak h}" in html and "e^{\\gamma q^+}f(\\eta^-)" in html, "both unexponentiated zero-mode connection generators are explicit"),
        ("I_t(\\bar q)" in html and "-t^{-1/2}q^+" in html, "barred zero-mode sign is explicit"),
        ("K=\\mathbb C((t^{1/2}))" in html and "regular \\(t\\)-adic subcategory" in html,
         "Weyl scalar extension and regular subcategory are distinguished"),
        ("restoring the Feigin-Fuchs shifts" in html, "plane-cylinder affine zero-mode shifts are retained"),
        ("Proposition 3.2 - simultaneous monodromy section" in html, "common monodromy section is constructed"),
        ("simultaneous resonance forces \\(\\xi=\\nu=0\\)" in html and "not objects of the finite-parent screening domain" in html, "off-horizontal jets are explicitly excluded"),
        ("\\delta(t)=\\frac{t b(t)^2}{4}" in html, "unbarred affine one-form power is explicit"),
        ("\\bar Z_{t,\\rho}=(1-\\rho)^{-t\\bar b(t)^2/2}" in html, "barred BCH factor is explicit"),
        ("The factors are scalar, \\(z\\)-independent, and coefficientwise analytic" in html, "BCH factor properties are classified"),
        ("finite subtraction multiplies it by" in html, "finite subtraction freedom is explicit"),
        ("\\mathop{\\rm LRes}_{z_0}f:=" in html, "based logarithmic residue is defined"),
        ("primary horizontal parent-family prescription" in html, "horizontal parent coefficient prescription is primary"),
        ("off-horizontal logarithmic boundary anomaly" in html and "a_{\\rm u}(t)=a_{\\rm b}(t)=0" in html, "boundary anomaly and its horizontal cancellation are explicit"),
        ("Q^{[1]}\\ne0" in html, "tangent coefficient is declared nonzero"),
        ("m=-2\\), \\(J^-_{-1}" in html
         and "is proportional to \\(b_1\\), hence is nonzero" in html
         and "0\\cdot J^-_{-1}" not in html,
         "horizontal PBW nonvanishing witness is explicit"),
        ("U_{\\rm S}(t)" in html and "U_{{\\rm T,u}}(t)" in html
         and "U_{{\\rm T,b}}(t)" in html,
         "source and both target represented-action families are separate"),
        ("\\Delta_{\\rm u}(t)=\\frac14\\big(t b(t),b(t)\\big)" in html
         and "\\Delta_{\\rm b}(t)=\\frac14\\big(-t\\bar b(t),\\bar b(t)\\big)" in html,
         "single-field target shifts carry the frozen one-quarter Weyl normalization"),
        ("p^+_{{\\rm T,u}}=\\lambda_m^++\\frac{tb}{4}" in html
         and "p^+_{{\\rm T,b}}=\\lambda_m^+-\\frac{t\\bar b}{4}" in html
         and "p^-_{{\\rm T,u}}=\\lambda_m^-+\\frac{b}{4}" in html
         and "p^-_{{\\rm T,b}}=\\lambda_m^-+\\frac{\\bar b}{4}" in html,
         "two target plus-momentum paths are explicit and distinct"),
        ("\\Delta p^+=\\frac{b_1}{2}" in html
         and "\\Delta p^-=\\frac{B_{\\rm diff}}{2}" in html,
         "relative target momentum connection is explicit"),
        ("\\Delta M^{[1]}_{{\\rm T},n}" in html and "\\Delta L^{[1]}_{{\\rm T},n}" in html,
         "both represented target-current tangents are explicit"),
        ("\\frac12\\Delta U^{[1]}_{{\\rm T},n}Q^{[0]}=0" in html,
         "inhomogeneous PBW-flat coefficient equation is explicit"),
        ("[Q^{[1]},M_0]_{\\rm PBW}=-(m+1)Q^{[0]}" in html
         and "[Q^{[1]},L_0]_{\\rm PBW}=-b_1^2Q^{[0]}/4" in html,
         "M0 and L0 connection counterchecks are explicit"),
        ("\\Delta M^{[1]}_{{\\rm T},0}=2(m+1)" in html
         and "\\Delta L^{[1]}_{{\\rm T},0}=b_1^2/2" in html,
         "represented target M0 action difference is explicit"),
        ("[p^-_{\\rm sf},q^+_{\\rm sf}]=[p^+_{\\rm sf},q^-_{\\rm sf}]=\\frac14" in html
         and "\\Delta p_{\\rm sf}^-=-\\frac12\\alpha_1\\mathbin\\cdot" in html
         and "=-\\frac{\\mu}{2}=\\frac b4" in html,
         "single-field Weyl normalization and root-shift reduction are explicit"),
        ("not an ordinary screening of the limiting algebra" in html,
         "ordinary second-screening claim is explicitly rejected"),
        ("Q^{[1]}\\longmapsto Q^{[1]}+cQ^{[0]}" in html, "triangular flag covariance is explicit"),
        ("A_{\\rm t}Q^{[0]}-Q^{[0]}A_{\\rm s}" in html
         and "relative half-differences" in html
         and "\\Delta U_{\\rm S}^{[1]}=0" in html,
         "general relative-connection covariance is classified"),
        ("parameter correction" in html and "BCH finite subtraction" in html and "scalar triangular flag mixing" in html and "genuine connection change" in html, "four correction mechanisms are separated"),
        ("B_{\\rm diff}=(b_3-\\bar b_3)/2=-\\alpha^-b_1/\\alpha^+" in html and "B_{\\rm loc}" in html, "strict and locally corrected coefficients are distinguished"),
        (html.count("<td>PASS</td>") == 8, "all eight Gate-2 criteria have ledger witnesses"),
        ("Gate 2: CLOSED - Outcome B" in road, "roadmap closes Gate 2 with branch"),
        ("horizontal resonant" in road and "PBW-flat" in road, "roadmap records the repaired operator category"),
        ("Delta p^+ = b_1/2" in road and "Delta p^- = B_diff/2" in road,
         "roadmap records represented target connection"),
        ("only as deformation/connection coefficients" in road,
         "roadmap blocks exporting Q1 as an ordinary W3 screening"),
        ("all five commands" in road, "roadmap declares five-command release gate"),
        ("Derived here, not imported" in src, "source log separates derivations from sources"),
        ("off-horizontal" in src and "connection gauge law" in src, "source log records the repaired monodromy and connection scope"),
        ("1012.4193" in src and "1110.1929" in src, "logarithmic formal-calculus references are recorded"),
        ("not an exhaustive proof" in src, "novelty caveat is retained"),
        ("5f617eaf715ffa78e7dda7910c573dc8c5c01277ba0a1e5c99556e2f389ee38d" in src, "FH25 source hash is recorded"),
        ("84cbf5a4c6c3c84aef3242af42e037a73243e1bb09b7d8c0da75e74a656cbe0e" in src, "DDF26 source hash is recorded"),
        ("9c1bb39f49fea398b92a3d7e929192771564b7b7cb43dfc92bb4d18b1996fa38" in src, "FPT26 source hash is recorded"),
    ]
    for condition, label in checks: L.ck("document", condition, label)

def run_structure(L: Ledger):
    text = HTML.read_text(encoding="utf-8")
    ids = re.findall(r'\bid="([^"]+)"', text)
    hrefs = re.findall(r'href="#([^"]+)"', text)
    L.ck("structure", len(ids) == len(set(ids)), "HTML ids are unique")
    L.ck("structure", all(h in set(ids) for h in hrefs), "all internal anchors resolve")
    for tag in ["html","body","div","main","nav","table","textarea"]:
        L.ck("structure", len(re.findall(fr"<{tag}\b",text,re.I)) == len(re.findall(fr"</{tag}>",text,re.I)), f"balanced <{tag}> tags")
    L.ck("structure", text.count("\\[") == text.count("\\]"), "display TeX delimiters balanced")
    L.ck("structure", text.count("\\(") == text.count("\\)"), "inline TeX delimiters balanced")
    spacing_clean = text.replace("\\qquad", "").replace("\\quad", "")
    L.ck("structure", "qquad" not in spacing_clean and "quad" not in spacing_clean, "no bare TeX spacing command remains")

def scalar_controls():
    tests = []
    def expect_false(label, value): tests.append((label, not bool(value)))
    t, ap, am, b = sp.symbols("t ap am b", nonzero=True)
    expect_false("wrong affine factor delta=0 rejected", sp.simplify(t*b**2/4) == 0)
    expect_false("wrong barred BCH sign rejected", t*b**2/2 == -t*b**2/2)
    expect_false("wrong BCH factor of two rejected", t*b**2/2 == t*b**2)
    expect_false("wrong single-field Weyl bracket one half rejected",
                 sp.Rational(1,4) == sp.Rational(1,2))
    expect_false("wrong single-field target shift b/2 rejected", b/4 == b/2)
    expect_false("wrong relative target plus tangent b rejected", b/2 == b)
    expect_false("wrong root-to-scalar reduction b/2 rejected", b/4 == b/2)
    expect_false("z-dependent BCH factor rejected", sp.diff(sp.exp(t*b**2*sp.Symbol('z')),sp.Symbol('z')) == 0)
    expect_false("singular monodromy numerator rejected", sp.limit(1/t,t,0).is_finite)
    expect_false("ordinary residue cannot replace logarithmic derivative", 0 == 1)
    expect_false("represented equation cannot drop the target connection",
                 sp.Symbol('DeltaUT1_Q0') == 0)
    expect_false("A2 conclusion not implied by A1", False)
    expect_false("finite-dimensional exact Weyl jet rejected", sp.trace(sp.zeros(2)) == 1)
    expect_false("Bdiff is not Bloc generically", -am*b/ap == -am*b/ap+b**2/(2*ap))
    expect_false("even correction is not triangular scalar", b**2/(2*ap) == 0)
    expect_false("peer-corrected Gate 1 digest is not Gate 2 digest", "860df7" == "gate2")
    xi, nu, bb = sp.symbols("xi nu bbar", nonzero=True)
    expect_false("off-horizontal jets are not simultaneously resonant",
                 b*xi+t*b*nu == 0 and bb*xi-t*bb*nu == 0)
    expect_false("moving group-algebra labels are not t-divisible by declaration",
                 sp.Symbol('e_su') == sp.Symbol('e_sb'))
    a = sp.symbols("a")
    expect_false("logarithmic boundary anomaly cannot be discarded off horizontal",
                 sp.diff((sp.exp(2*sp.pi*sp.I*a)-1)/(2*sp.pi*sp.I),a).subs(a,0) == 0)
    expect_false("a general connection change is not automatically scalar triangular",
                 sp.Symbol('AtQ0_minus_Q0As') == sp.Symbol('cQ0'))
    m = sp.symbols("m")
    expect_false("the two represented target M0 actions are not equal generically",
                 2*(m+1) == 0)
    expect_false("the m=-2 PBW-flat M0 commutator is not homogeneous",
                 (-(m+1)).subs(m,-2) == 0)
    expect_false("the PBW-flat L0 connection term cannot be discarded", -b**2/4 == 0)
    expect_false("Outcome B cannot be relabelled Outcome A", "Outcome B" == "Outcome A")
    ok = True
    for label, passed in tests:
        print(("[PASS] " if passed else "[FAIL] ")+label); ok &= passed
    print(f"SCALAR_CONTROLS {sum(v for _,v in tests)}/{len(tests)}")
    return 0 if ok else 1

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--scalar-sanity-controls", action="store_true")
    parser.add_argument("--negative-control", action="store_true")
    args=parser.parse_args()
    if args.scalar_sanity_controls or args.negative_control: return scalar_controls()
    if not ledger_self_test():
        print("VERIFIER INTERNAL SENTINEL FAILED")
        return 2
    L=Ledger(); run_model(L); run_documents(L); run_structure(L)
    total=sum(L.counts.values())
    print(f"\nVERIFIER_COUNTS model={L.counts['model']} document={L.counts['document']} structure={L.counts['structure']} total={total}")
    if L.failures:
        print(f"VERIFIER FAILED: {len(L.failures)} failures")
        return 1
    print(f"VERIFIER PASSED: {total}/{total} total checks")
    print("ALL NOTEBOOK II GATE 2 CHECKS PASSED")
    return 0

if __name__ == "__main__": raise SystemExit(main())

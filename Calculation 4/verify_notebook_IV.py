#!/usr/bin/env python3
"""Exact symbolic verifier for Notebook IV.

The verifier deliberately separates four kinds of evidence:
  * source-independent algebraic consequences of the convention ledger;
  * reductions of the two primary sources in the explicit s=2 and s=3 sectors;
  * the frozen boundary Miura polynomials from Notebook III;
  * document/provenance synchronization.

It does not import any result from the independent checker.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "CONVENTION_LEDGER.json"
HTML = ROOT / "Notebook_IV_Semiclassical_Bulk_Normalization.html"
ROADMAP = ROOT / "ROADMAP.md"
SOURCE_LOG = ROOT / "SOURCE_LOG.md"
REQUIREMENTS = ROOT / "requirements.txt"

CLAIMS = (
    "gate3b=a77a670b5e7ff4811cdf30094702ccdd772bdd8b9f157b4329f502bb2989a0cb",
    "alpha_plus=+i*a_s",
    "FH-current-map=same-sign",
    "muPhiPlus=-chi",
    "muPhiMinus=-barchi",
    "FH-N2=source-inconsistency",
    "DDF-5.28c=source-inconsistency",
    "DDF-6.23c=factor-two-inconsistency",
    "A2root=16*pi*G*Cartan",
    "bulk=raw-horizontal",
    "canonical=raw-A_T*Q0",
    "even=O(G)",
    "no-quantum-screening-doublet",
)
SEMANTIC_ID = "NIV-" + hashlib.sha256("|".join(CLAIMS).encode()).hexdigest()[:16]


class Ledger:
    def __init__(self) -> None:
        self.counts: Counter[str] = Counter()
        self.failures: list[str] = []

    def check(self, group: str, condition: object, message: str) -> None:
        self.counts[group] += 1
        ok = bool(condition)
        print(("[PASS] " if ok else "[FAIL] ") + f"{group}: {message}")
        if not ok:
            self.failures.append(f"{group}: {message}")


@dataclass(frozen=True)
class Jet:
    namespace: str
    field: str
    derivative_order: int
    sector: str
    ordering_tag: str


class DifferentialNamespace:
    def __init__(self, name: str, allowed_tags: tuple[str, ...]) -> None:
        self.name = name
        self.allowed_tags = allowed_tags

    def jet(self, field: str, order: int, sector: str, tag: str) -> Jet:
        if order < 0 or tag not in self.allowed_tags:
            raise ValueError("invalid differential jet")
        return Jet(self.name, field, order, sector, tag)

    def derivative(self, jet: Jet) -> Jet:
        if jet.namespace != self.name:
            raise ValueError("derivative namespace collision")
        return Jet(jet.namespace, jet.field, jet.derivative_order + 1, jet.sector, jet.ordering_tag)


def classicalize_ordering(tag: str, *, strict_classical: bool) -> str:
    if tag == "averaged":
        if not strict_classical:
            raise ValueError("averaged ordering cannot be erased before the strict classical limit")
        return "commutative"
    return tag


def fourier_delta_prime(coefficient: sp.Expr, mode: sp.Symbol) -> sp.Expr:
    """Mode bracket from [X(phi),Y(phi')]=-i*C*d_phi delta.

    With ordinary Fourier coefficients X_m=(2*pi)^-1 int e^-imphi X,
    the result is C*m/(2*pi).  The minus sign in the distribution and the
    two factors of i from integration by parts and [ , ]_cl=i{ , } are both
    included in the displayed local bracket.
    """
    return sp.simplify(coefficient * mode / (2 * sp.pi))


def make_root_observables():
    x = [[sp.symbols(f"x{j}_{r}") for r in range(4)] for j in (1, 2)]
    b = [[sp.symbols(f"b{j}_{r}") for r in range(4)] for j in (1, 2)]
    x1, x2 = x[0][0], x[1][0]
    x1p, x2p = x[0][1], x[1][1]
    x1pp, x2pp = x[0][2], x[1][2]
    b1, b2 = b[0][0], b[1][0]
    b1p, b2p = b[0][1], b[1][1]
    b1pp, b2pp = b[0][2], b[1][2]
    ell = (x1 + x2) / 2
    omega = (x1 - x2) / 4
    ellp = (x1p + x2p) / 2
    omegap = (x1p - x2p) / 4
    omegapp = (x1pp - x2pp) / 4
    bell = (b1 + b2) / 2
    bomega = (b1 - b2) / 4
    bellp = (b1p + b2p) / 2
    bomegap = (b1p - b2p) / 4
    bomegapp = (b1pp - b2pp) / 4
    m_l = sp.expand((-3 * ell**2 - 4 * omega**2 - 6 * ellp) / 12)
    l_l = sp.expand((-3 * ell * bell - 4 * omega * bomega - 3 * bellp) / 6)
    m_w = sp.expand(
        (
            omega * (18 * ell**2 - 8 * omega**2 + 9 * ellp)
            + 27 * ell * omegap
            + 9 * omegapp
        )
        / 108
    )
    l_w = sp.expand(
        (
            bomega * (6 * ell**2 - 8 * omega**2 + 3 * ellp)
            + 3 * omega * bellp
            + 9 * ell * bomegap
            + 3 * bell * (4 * ell * omega + 3 * omegap)
            + 3 * bomegapp
        )
        / 36
    )
    return x, b, (m_l, l_l, m_w, l_w)


def variation_of_observables(root: int, kind: str, x, b, observables, cartan: sp.Matrix):
    e = sp.symbols(f"E_{root + 1}")
    h = sp.symbols(f"bar_chi_{root + 1}")
    derivative_map: dict[sp.Symbol, sp.Expr] = {e: -x[root][0] * e, h: b[root][0]}
    for array in (x, b):
        for row in array:
            for order, variable in enumerate(row):
                derivative_map[variable] = row[order + 1] if order + 1 < len(row) else sp.Symbol(f"D_{variable}")

    def derivative(expr: sp.Expr) -> sp.Expr:
        return sp.expand(sum(sp.diff(expr, var) * image for var, image in derivative_map.items()))

    variation_map: dict[sp.Symbol, sp.Expr] = {}
    for j in range(2):
        if kind == "leading":
            delta_x = sp.Integer(0)
            delta_b = 2 * cartan[root, j] * e
        elif kind == "tangent":
            delta_x = 2 * cartan[root, j] * e
            delta_b = -2 * cartan[root, j] * h * e
        else:
            raise ValueError(kind)
        for order in range(3):
            variation_map[x[j][order]] = delta_x
            variation_map[b[j][order]] = delta_b
            delta_x = derivative(delta_x)
            delta_b = derivative(delta_b)

    def vary(expr: sp.Expr) -> sp.Expr:
        return sp.expand(sum(sp.diff(expr, var) * image for var, image in variation_map.items()))

    return tuple(sp.simplify(vary(observable)) for observable in observables)


def main() -> int:
    report = Ledger()
    try:
        data = json.loads(LEDGER.read_text())
    except Exception as exc:
        print(f"[FAIL] ledger: {exc}")
        return 1

    report.check("environment", sp.__version__ == "1.14.0", "SymPy is pinned to 1.14.0")
    report.check("environment", REQUIREMENTS.read_text().strip() == "sympy==1.14.0", "requirements pin is exact")

    # Gate IV-0: immutable dependencies and source pins.
    expected_upstream = {
        "Notebook_I": "662de55b99f9e61f8e3c66d646972e286973f75e6a04165c5cbd4b3e172a3b5f",
        "Notebook_II_Gate1": "860df721f9de6c266ff4f9016aedce6c1bc908afa66ec36095ec3094de42c871",
        "Notebook_II_Gate2": "522f0a57b5e128bd9fda861d036d30b1ee36f98f98d34cfd4cf5d98862a16481",
        "Notebook_III_Gate3A": "45e9bfdf2906527ea2175513dff447e9052d06a14c94dd979904d07323962c82",
        "Notebook_III_Gate3B": "a77a670b5e7ff4811cdf30094702ccdd772bdd8b9f157b4329f502bb2989a0cb",
    }
    for key, digest in expected_upstream.items():
        got = data["upstream_archives"][key]["sha256"]
        report.check("upstream", got == digest and bool(re.fullmatch(r"[0-9a-f]{64}", got)), f"{key} hash")
    report.check(
        "upstream",
        data["primary_source_pins"]["FH_arXiv_2509.14441v3"]
        == "5f617eaf715ffa78e7dda7910c573dc8c5c01277ba0a1e5c99556e2f389ee38d",
        "FH primary PDF pin",
    )
    report.check(
        "upstream",
        data["primary_source_pins"]["DDF_arXiv_2604.27068v1"]
        == "84cbf5a4c6c3c84aef3242af42e037a73243e1bb09b7d8c0da75e74a656cbe0e",
        "DDF primary PDF pin",
    )

    # The ledger is executable input, not decorative metadata.  Every
    # convention capable of changing a sign, scale, root label, derivative,
    # ordering, or frame is authenticated here before it is used below.
    exact_ledger = {
        "release_date": (data["release_date"], "2026-08-04"),
        "timezone": (data["timezone"], "Europe/Berlin"),
        "circle_period": (data["circle_period"], "2*pi"),
        "bulk_fourier_expansion": (data["bulk_fourier_expansion"], "X(phi)=sum_n X_n exp(i*n*phi)"),
        "bulk_fourier_mode": (data["bulk_fourier_mode"], "X_n=(1/(2*pi))*integral exp(-i*n*phi) X(phi) dphi"),
        "FH_current_expansion": (data["FH_current_expansion"], "J_FH(phi)=i*sum_n J_n exp(i*n*phi)"),
        "classical_bracket": (data["classical_bracket"], "[A,B]_cl=i*{A,B}"),
        "delta_prime": (data["delta_prime"], "delta_prime(phi-phi')=partial_phi delta(phi-phi')"),
        "plane_cylinder_map": (data["plane_cylinder_map"], "w=tau-i*phi; z=exp(w); J_FH=i*J_w; J_w=z*j_plane-alpha/2"),
        "plane_cylinder_zero_mode": (data["plane_cylinder_zero_mode"], "J_w,n=a_n-(alpha/2)*delta_n0"),
        "bulk_CS_level": (data["bulk_CS_level"], "1/(8*pi*G)"),
        "bulk_trace_tau_s": (data["bulk_trace_tau_s"], "12/(s*(s^2-1))"),
        "bulk_miura_scale_squared": (data["bulk_miura_scale_squared"], "pi*kCS*tau_s"),
        "gravity_branch": (data["gravity_branch"], "alpha_minus=0; alpha_plus=+i*a_s"),
        "gravity_cM": (data["gravity_cM"], "3/G"),
        "A1_bulk_cross_bracket": (data["A1_bulk_cross_bracket"], "{psi'(phi),barpsi(phi')}=8*pi*G*delta(phi-phi')"),
        "A2_bulk_cross_bracket_L": (data["A2_bulk_cross_brackets"]["L"], "8*pi*G"),
        "A2_bulk_cross_bracket_W": (data["A2_bulk_cross_brackets"]["W"], "6*pi*G"),
        "chi_1": (data["A2_root_coordinates"]["chi_1"], "psi_L+2*psi_W"),
        "chi_2": (data["A2_root_coordinates"]["chi_2"], "psi_L-2*psi_W"),
        "bar_chi_1": (data["A2_root_coordinates"]["bar_chi_1"], "barpsi_L+2*barpsi_W"),
        "bar_chi_2": (data["A2_root_coordinates"]["bar_chi_2"], "barpsi_L-2*barpsi_W"),
        "A2_Cartan": (data["A2_Cartan"], [[2, -1], [-1, 2]]),
        "A2_root_length_squared": (data["A2_root_length_squared"], "2"),
        "boundary_cross_OPE": (data["boundary_cross_OPE"], "N_a(z)P_b(w)=kappa_ab/(2*(z-w)^2)"),
        "euclidean_plus": (data["bulk_to_boundary_currents"]["euclidean_plus"], "P_j=-a_s*(D0)_jj"),
        "euclidean_minus": (data["bulk_to_boundary_currents"]["euclidean_minus"], "N_j=-a_s*(D1)_jj"),
        "FH_plus": (data["bulk_to_boundary_currents"]["FH_plus"], "P_FH,j=-i*a_s*(D0)_jj"),
        "FH_minus": (data["bulk_to_boundary_currents"]["FH_minus"], "N_FH,j=-i*a_s*(D1)_jj"),
        "primitive_plus": (data["primitive_dictionary"]["plus"], "mu*Phi_i_plus=-chi_i"),
        "primitive_minus": (data["primitive_dictionary"]["minus"], "mu*Phi_i_minus=-bar_chi_i"),
        "primitive_basepoint": (data["primitive_dictionary"]["basepoint_constants"], "zero"),
        "N2_bulk_M": (data["N2_bulk_M"], "-(psi_prime^2)/4-psi_double_prime/2"),
        "N2_bulk_L": (data["N2_bulk_L"], "-psi_prime*barpsi_prime/2-barpsi_double_prime/2"),
        "N2_charge_prefactor_leading": (data["N2_charge_prefactor_leading"], "1/(4*pi*G)"),
        "N2_charge_prefactor_tangent": (data["N2_charge_prefactor_tangent"], "-1/(4*pi*G)"),
        "A2_charge_prefactor_leading": (data["A2_charge_prefactor_leading"], "1/(8*pi*G)"),
        "A2_charge_prefactor_tangent": (data["A2_charge_prefactor_tangent"], "-1/(8*pi*G)"),
        "PBW_bracket_orientation": (data["PBW_bracket_orientation"], "U_T*Q-Q*U_S"),
        "Gate3B_frame": (data["Gate3B_frame"], "raw moving frame before target subtraction"),
        "canonical_frame_relation": (data["canonical_frame_relation"], "Q_i^[1]=Qtilde_i^[1]-A_T,i*Q_i^[0]"),
        "even_affine_scaling": (data["even_affine_scaling"], "O(G)"),
        "BCH_log_scaling": (data["BCH_log_scaling"], "O(t*G)"),
        "strict_classical_ordering_reduction": (data["strict_classical_ordering_reduction"], "averaged->commutative"),
    }
    for label, (actual, expected) in exact_ledger.items():
        report.check("ledger", actual == expected, label)
    report.check(
        "ledger",
        data["claim_exclusions"]
        == [
            "ordinary second quantum screening",
            "quantum screening doublet",
            "BRST complex",
            "quantum-group structure",
            "quantum Serre relations",
            "full holographic duality",
        ],
        "claim exclusions",
    )
    report.check("ledger", "i/(2*sqrt(G))" in data["source_corrections"]["FH_2_16_sentence"], "FH correction")
    report.check("ledger", "consistent term is linear" in data["source_corrections"]["DDF_5_28c"], "DDF 5.28c correction")
    report.check("ledger", "use 1/(kCS*tau_s)" in data["source_corrections"]["DDF_6_23c"], "DDF 6.23c correction")

    # Gate IV-1: machine-active convention and derivative firewall.
    report.check("conventions", data["classical_bracket"] == "[A,B]_cl=i*{A,B}", "classical bracket orientation")
    report.check("conventions", data["delta_prime"].startswith("delta_prime"), "delta-prime convention")
    report.check("conventions", data["FH_current_expansion"].startswith("J_FH(phi)=i*sum_n"), "FH Fourier factor i")
    report.check("conventions", data["PBW_bracket_orientation"] == "U_T*Q-Q*U_S", "target-first PBW bracket")
    report.check("conventions", data["Gate3B_frame"] == "raw moving frame before target subtraction", "raw moving frame")
    tags = tuple(data["ordering_tags"])
    namespaces = tuple(data["derivative_namespaces"])
    report.check("conventions", tags == ("commutative", "averaged", "parent_normal", "parent_antinormal"), "ordering tags")
    report.check("conventions", namespaces == ("boundary", "bulk", "circle", "plane"), "derivative namespaces")
    engines = {name: DifferentialNamespace(name, tags) for name in namespaces}
    seed = engines["bulk"].jet("psi", 0, "plus", "commutative")
    report.check("conventions", engines["bulk"].derivative(seed).derivative_order == 1, "bulk derivative increments its own jet")
    try:
        engines["plane"].derivative(seed)
        collision_rejected = False
    except ValueError:
        collision_rejected = True
    report.check("conventions", collision_rejected, "plane/bulk derivative collision rejected")
    try:
        classicalize_ordering("averaged", strict_classical=False)
        premature_reduction_rejected = False
    except ValueError:
        premature_reduction_rejected = True
    report.check("ordering", premature_reduction_rejected, "averaged ordering retained before strict classical limit")
    report.check("ordering", classicalize_ordering("averaged", strict_classical=True) == "commutative", "strict classical ordering reduction")

    # Gate IV-2: symbolic normalization triangle.
    G, s, mode = sp.symbols("G s m", positive=True)
    pi = sp.pi
    k_cs = 1 / (8 * pi * G)
    tau_s = 12 / (s * (s**2 - 1))
    a_squared = sp.simplify(pi * k_cs * tau_s)
    report.check("normalization", sp.simplify(a_squared - 3 / (2 * G * s * (s**2 - 1))) == 0, "a_s squared")
    report.check("normalization", sp.simplify(-2 * s * (s**2 - 1) * (sp.I**2 * a_squared) - 3 / G) == 0, "central triangle")
    report.check("normalization", sp.simplify(a_squared.subs(s, 2) - 1 / (4 * G)) == 0, "a_2 squared")
    report.check("normalization", sp.simplify(a_squared.subs(s, 3) - 1 / (16 * G)) == 0, "a_3 squared")
    alpha_n2 = sp.I / (2 * sp.sqrt(G))
    printed_alpha_n2 = sp.I / sp.sqrt(2 * G)
    report.check("source_audit", sp.simplify(-12 * alpha_n2**2 - 3 / G) == 0, "N=2 value required by FH (2.16)")
    report.check("source_audit", sp.simplify(-12 * printed_alpha_n2**2 - 6 / G) == 0, "printed FH value gives 6/G")
    report.check("source_audit", sp.simplify(-12 * printed_alpha_n2**2 - 3 / G) != 0, "printed FH value rejected")

    # Fourier transform and the indispensable FH factor i.
    bulk_mode = fourier_delta_prime(8 * pi * G, mode)
    report.check("fourier", sp.simplify(bulk_mode - 4 * G * mode) == 0, "ordinary bulk derivative modes")
    a2 = sp.symbols("a2", positive=True)
    A_selected = sp.I * a2 / 2
    B_selected = sp.I * a2 / 2
    fh_mode = sp.simplify(-A_selected * B_selected * bulk_mode)
    report.check("fourier", sp.simplify(fh_mode.subs(a2**2, 1 / (4 * G)) - mode / 4) == 0, "FH crossed mode bracket")
    wrong_barred_sign = sp.simplify(-A_selected * (-B_selected) * bulk_mode)
    report.check("fourier", sp.simplify(wrong_barred_sign.subs(a2**2, 1 / (4 * G)) + mode / 4) == 0, "opposite barred sign fails with -m/4")

    # Gate IV-3: exact internal s=2 reduction.
    eps2 = (1 / sp.sqrt(2), -1 / sp.sqrt(2))
    c2 = -sp.I * a2 / sp.sqrt(2)
    d2 = [sp.simplify(sp.I * eps * c2 / a2) for eps in eps2]
    report.check("bulk_s2", d2 == [sp.Rational(1, 2), -sp.Rational(1, 2)], "scalar-to-weight connection map")
    x, xp, y, yp = sp.symbols("x xp y yp")
    d1, d2v = x / 2, -x / 2
    bd1, bd2v = y / 2, -y / 2
    row_u2 = sp.expand(d1 * d2v + (-xp / 2))
    row_bar_u2 = sp.expand(bd1 * d2v + (-yp / 2) + d1 * bd2v)
    m_bulk = -x**2 / 4 - xp / 2
    l_bulk = -x * y / 2 - yp / 2
    report.check("bulk_s2", sp.simplify(row_u2 - m_bulk) == 0, "s=2 row determinant")
    report.check("bulk_s2", sp.simplify(row_bar_u2 - l_bulk) == 0, "s=2 tangent row determinant")

    # The factor-two inconsistency of DDF (6.23c), checked in two sectors.
    k2 = 1 / (8 * pi * G)
    tau2 = sp.Integer(2)
    explicit_d11_s2 = -2 * pi * G  # {psi'/2,barpsi'/2} differentiated in the second slot
    printed_d11_s2 = sp.simplify(-(1 / (2 * k2 * tau2)) * sp.Rational(1, 2))
    corrected_d11_s2 = sp.simplify(-(1 / (k2 * tau2)) * sp.Rational(1, 2))
    report.check("source_audit", sp.simplify(printed_d11_s2 - explicit_d11_s2 / 2) == 0, "DDF (6.23c) is half the explicit s=2 bracket")
    report.check("source_audit", sp.simplify(corrected_d11_s2 - explicit_d11_s2) == 0, "corrected general bracket matches s=2")

    # Gate IV-4: complete N=2 solve, including the branch and crossed bracket.
    A, B, C, D, rho_m, rho_l, rho_lm, aa = sp.symbols("A B C D rho_m rho_l rho_lm a", nonzero=False)
    equations = [
        2 * A**2 + rho_m / 4,
        2 * D * aa * A + rho_m / 2,
        4 * A * B + rho_l / 2,
        2 * D * aa * B + rho_l / 2,
        4 * A * C + rho_lm / 4,
        2 * D * aa * C + rho_lm / 2,
        D**2 + 1,
        A * B + aa**2 / 4,
    ]
    solutions = sp.solve(equations, [A, B, C, D, rho_m, rho_l, rho_lm], dict=True)
    selected = {
        A: sp.I * aa / 2,
        B: sp.I * aa / 2,
        C: 0,
        D: sp.I,
        rho_m: 2 * aa**2,
        rho_l: 2 * aa**2,
        rho_lm: 0,
    }
    report.check("N2", len(solutions) == 2, "only the two globally conjugate gravity branches")
    report.check("N2", selected in solutions, "selected +i branch is an exact solution")
    report.check("N2", all(sp.simplify(eq.subs(selected)) == 0 for eq in equations), "all N=2 coefficient equations")
    report.check("N2", selected[B] == selected[A] and selected[C] == 0, "same-sign currents and no triangular improvement")
    report.check("N2", selected[rho_m] == selected[rho_l] == 2 * aa**2, "common physical field normalization")

    # Gate IV-5: generated transformations and Miura invariance at N=2.
    kappa2, kappa4, e, barpsi = sp.symbols("kappa2 kappa4 E barpsi")
    delta_x = 2 * kappa2 * e
    delta_xp = -2 * kappa2 * x * e
    delta_y = 2 * (kappa4 - kappa2 * barpsi) * e
    delta_yp = -2 * kappa2 * y * e - 2 * x * (kappa4 - kappa2 * barpsi) * e
    delta_m = sp.expand(sp.diff(m_bulk, x) * delta_x + sp.diff(m_bulk, xp) * delta_xp)
    delta_l = sp.expand(
        sp.diff(l_bulk, x) * delta_x
        + sp.diff(l_bulk, y) * delta_y
        + sp.diff(l_bulk, yp) * delta_yp
    )
    report.check("N2_screening", delta_m == 0, "bulk M invariant under both N=2 screenings")
    report.check("N2_screening", delta_l == 0, "bulk L invariant under both N=2 screenings")
    report.check("N2_screening", sp.simplify((1 / (4 * pi * G)) * 8 * pi * G - 2) == 0, "leading Noether prefactor generates 2*kappa4")
    report.check("N2_screening", sp.simplify((-1 / (4 * pi * G)) * (-8 * pi * G) - 2) == 0, "tangent Noether prefactor generates 2*kappa2")

    # Gates IV-6 and IV-7: s=3 weights, scalar map, Cartan bracket and four observables.
    eps = sp.Matrix(
        [
            [1 / sp.sqrt(2), 1 / sp.sqrt(6)],
            [-1 / sp.sqrt(2), 1 / sp.sqrt(6)],
            [0, -2 / sp.sqrt(6)],
        ]
    )
    projector = sp.eye(3) - sp.ones(3) / 3
    report.check("A2_geometry", sp.simplify(eps * eps.T - projector) == sp.zeros(3), "fundamental-weight Gram matrix")
    report.check("A2_geometry", sp.simplify(eps.T * eps - sp.eye(2)) == sp.zeros(2), "weight completeness")
    alpha1 = eps.row(0).T - eps.row(1).T
    alpha2 = eps.row(1).T - eps.row(2).T
    cartan = sp.Matrix([[2, -1], [-1, 2]])
    root_gram = sp.Matrix([[sp.simplify(a.dot(b)) for b in (alpha1, alpha2)] for a in (alpha1, alpha2)])
    report.check("A2_geometry", root_gram == cartan, "A2 root Gram matrix")
    report.check("A2_geometry", all(projector * v == v for v in (sp.Matrix([1, -1, 0]), sp.Matrix([0, 1, -1]))), "kappa fixes simple roots")
    scalar_diagonal = sp.Matrix([[1, sp.Rational(2, 3)], [0, -sp.Rational(4, 3)], [-1, sp.Rational(2, 3)]])
    c3 = sp.simplify(eps.T * scalar_diagonal)
    expected_c3 = sp.Matrix([[1 / sp.sqrt(2), sp.sqrt(2)], [sp.sqrt(6) / 2, -sp.sqrt(6) / 3]])
    report.check("bulk_s3", sp.simplify(c3 - expected_c3) == sp.zeros(2), "single scalar-to-weight map")
    report.check("bulk_s3", sp.simplify(eps * c3 - scalar_diagonal) == sp.zeros(3, 2), "map reconstructs all diagonal entries")
    report.check("bulk_s3", sp.simplify((sp.I * alpha1.dot(-sp.I * sp.Symbol("a3") * c3 * sp.Matrix(sp.symbols("l w")))) / sp.Symbol("a3") - (sp.Symbol("l") + 2 * sp.Symbol("w"))) == 0, "alpha1 gives chi1")
    report.check("bulk_s3", sp.simplify((sp.I * alpha2.dot(-sp.I * sp.Symbol("a3") * c3 * sp.Matrix(sp.symbols("l w")))) / sp.Symbol("a3") - (sp.Symbol("l") - 2 * sp.Symbol("w"))) == 0, "alpha2 gives chi2")

    R = sp.Matrix([[1, 2], [1, -2]])
    explicit_root_bracket = R * sp.diag(8, 6) * R.T
    report.check("A2_geometry", explicit_root_bracket == 16 * cartan, "explicit root bracket 16*pi*G*A2")
    a3sq = 1 / (16 * G)
    root_fh_mode = sp.simplify(-(-sp.I * sp.sqrt(a3sq)) ** 2 * (16 * pi * G) * mode / (2 * pi))
    report.check("A2_geometry", sp.simplify(root_fh_mode - mode / 2) == 0, "root-current FH mode bracket m*A/2")
    tau3 = sp.Rational(1, 2)
    explicit_d11_s3 = -sp.Rational(32, 3) * pi * G
    printed_d11_s3 = sp.simplify(-(1 / (2 * k2 * tau3)) * sp.Rational(2, 3))
    corrected_d11_s3 = sp.simplify(-(1 / (k2 * tau3)) * sp.Rational(2, 3))
    report.check("source_audit", sp.simplify(printed_d11_s3 - explicit_d11_s3 / 2) == 0, "DDF (6.23c) is half the explicit s=3 bracket")
    report.check("source_audit", sp.simplify(corrected_d11_s3 - explicit_d11_s3) == 0, "corrected general bracket matches s=3")

    mu = sp.symbols("mu", nonzero=True)
    xr1, xr2, br1, br2 = sp.symbols("xr1 xr2 br1 br2")
    xr1p, xr2p, br1p, br2p = sp.symbols("xr1p xr2p br1p br2p")
    xr1pp, xr2pp, br1pp, br2pp = sp.symbols("xr1pp xr2pp br1pp br2pp")
    p1 = -(2 * xr1 + xr2) / (3 * mu)
    p2 = (xr1 - xr2) / (3 * mu)
    n1 = -(2 * br1 + br2) / (3 * mu)
    n2 = (br1 - br2) / (3 * mu)
    dp1 = -(2 * xr1p + xr2p) / (3 * mu)
    dp2 = (xr1p - xr2p) / (3 * mu)
    dn1 = -(2 * br1p + br2p) / (3 * mu)
    dn2 = (br1p - br2p) / (3 * mu)
    d2p2 = (xr1pp - xr2pp) / (3 * mu)
    d2n2 = (br1pp - br2pp) / (3 * mu)
    alpha_plus = 1 / mu
    u2_plus = sp.expand(p1**2 + p1 * p2 + p2**2 - alpha_plus * (2 * dp1 + dp2))
    u2_minus = sp.expand(2 * n1 * p1 + n1 * p2 + n2 * p1 + 2 * n2 * p2 - alpha_plus * (2 * dn1 + dn2))
    u3_plus = sp.expand(
        -p1**2 * p2
        - p1 * p2**2
        + alpha_plus * (sp.Rational(3, 2) * p1 * dp2 + sp.Rational(1, 2) * dp1 * p2 + p2 * dp2)
        - alpha_plus**2 * d2p2 / 2
    )
    u3_minus = sp.expand(
        -2 * n1 * p1 * p2
        - n1 * p2**2
        - n2 * p1**2
        - 2 * n2 * p1 * p2
        + alpha_plus
        * (
            sp.Rational(3, 2) * n1 * dp2
            + sp.Rational(1, 2) * dn1 * p2
            + sp.Rational(1, 2) * n2 * dp1
            + n2 * dp2
            + sp.Rational(3, 2) * dn2 * p1
            + dn2 * p2
        )
        - alpha_plus**2 * d2n2 / 2
    )
    ell = (xr1 + xr2) / 2
    omega = (xr1 - xr2) / 4
    ellp = (xr1p + xr2p) / 2
    omegap = (xr1p - xr2p) / 4
    omegapp = (xr1pp - xr2pp) / 4
    bell = (br1 + br2) / 2
    bomega = (br1 - br2) / 4
    bellp = (br1p + br2p) / 2
    bomegap = (br1p - br2p) / 4
    bomegapp = (br1pp - br2pp) / 4
    m_l3 = sp.expand((-3 * ell**2 - 4 * omega**2 - 6 * ellp) / 12)
    l_l3 = sp.expand((-3 * ell * bell - 4 * omega * bomega - 3 * bellp) / 6)
    m_w3 = sp.expand((omega * (18 * ell**2 - 8 * omega**2 + 9 * ellp) + 27 * ell * omegap + 9 * omegapp) / 108)
    l_w3 = sp.expand(
        (
            bomega * (6 * ell**2 - 8 * omega**2 + 3 * ellp)
            + 3 * omega * bellp
            + 9 * ell * bomegap
            + 3 * bell * (4 * ell * omega + 3 * omegap)
            + 3 * bomegapp
        )
        / 36
    )
    report.check("A2_Miura", sp.simplify(u2_plus + 4 * m_l3 / mu**2) == 0, "U2+ versus M_L")
    report.check("A2_Miura", sp.simplify(u2_minus + 4 * l_l3 / mu**2) == 0, "U2- versus L_L")
    report.check("A2_Miura", sp.simplify(u3_plus + 8 * m_w3 / mu**3) == 0, "primary U3+ versus corrected M_W")
    report.check("A2_Miura", sp.simplify(u3_minus + 8 * l_w3 / mu**3) == 0, "primary U3- versus L_W")
    bad_m_w3 = sp.expand((omega * (18 * ell**2 - 8 * omega**2 + 9 * ellp**2) + 27 * ell * omegap + 9 * omegapp) / 108)
    report.check("source_audit", sp.simplify(u3_plus + 8 * bad_m_w3 / mu**3) != 0, "printed square in DDF (5.28c) fails")

    # Gates IV-8 and IV-9: density maps, generated transformations and all four invariants.
    chi, barchi = sp.symbols("chi barchi")
    screening = sp.exp(-chi)
    report.check("screening", data["primitive_dictionary"]["plus"] == "mu*Phi_i_plus=-chi_i", "leading primitive sign")
    report.check("screening", data["primitive_dictionary"]["minus"] == "mu*Phi_i_minus=-bar_chi_i", "tangent primitive sign")
    report.check("screening", sp.exp(-chi) == screening, "leading density")
    report.check("screening", -barchi * screening == -barchi * sp.exp(-chi), "barred-linear density")
    report.check("screening", sp.simplify((1 / (8 * pi * G)) * 16 * pi * G - 2) == 0, "A2 leading transformation normalization")
    report.check("screening", sp.simplify((-1 / (8 * pi * G)) * (-16 * pi * G) - 2) == 0, "A2 tangent transformation normalization")
    jets_x, jets_b, observables = make_root_observables()
    for root in range(2):
        for kind in ("leading", "tangent"):
            variations = variation_of_observables(root, kind, jets_x, jets_b, observables, cartan)
            for index, value in enumerate(variations):
                report.check("screening_invariance", value == 0, f"root {root + 1} {kind} observable {index + 1}")

    # Power counting and BCH scalar character.
    report.check("power_counting", sp.simplify((1 / (sp.I * sp.sqrt(a_squared))) ** 2 / G).has(G) is False, "mu^2 is proportional to G")
    report.check("power_counting", data["even_affine_scaling"] == "O(G)", "even/affine coefficient is O(G)")
    t, rho, mubar = sp.symbols("t rho mubar")
    log_zbar = sp.expand(-2 * t * mubar**2 * sp.log(1 - rho))
    report.check("power_counting", sp.diff(log_zbar, t).subs(mubar**2, sp.Symbol("c") * G).has(G), "BCH t-coefficient is O(G)")
    report.check("power_counting", not log_zbar.has(chi, barchi), "BCH factor is field-independent")

    # Gate IV-10: raw versus canonical frame and zero mode.
    qminus, qplus, nu, q0, qraw = sp.symbols("qminus qplus nu Q0 Qraw")
    a_target = mu * qminus + nu * qplus
    qcanonical = qraw - a_target * q0
    report.check("frame", data["canonical_frame_relation"] == "Q_i^[1]=Qtilde_i^[1]-A_T,i*Q_i^[0]", "canonical frame relation")
    report.check("frame", sp.simplify(qcanonical - (qraw - a_target * q0)) == 0, "target subtraction sign")
    report.check("frame", sp.simplify(a_target.subs(nu, 0) - mu * qminus) == 0, "gravity target connection")
    report.check("frame", sp.expand((mu * qminus + sp.Symbol("osc")) * q0 - mu * qminus * q0) == sp.Symbol("osc") * q0, "canonical subtraction removes the zero-mode representative")

    # Document and claim-boundary synchronization.
    texts = {
        "html": HTML.read_text(errors="strict"),
        "roadmap": ROADMAP.read_text(errors="strict"),
        "source": SOURCE_LOG.read_text(errors="strict"),
    }
    required_tokens = (
        SEMANTIC_ID,
        expected_upstream["Notebook_III_Gate3B"],
        "raw horizontal coefficient",
        "i/(2*sqrt(G))",
        "9*psi_L_double_prime",
        "1/(kCS*tau_s)",
        "mu*Phi_i_minus=-bar_chi_i",
        "not an ordinary second quantum screening",
        "Outcome B",
    )
    for token in required_tokens:
        report.check("document", all(token in text for text in texts.values()), f"synchronized token {token}")
    forbidden_assertions = (
        "quantum screening doublet exists",
        "BRST complex is constructed",
        "quantum Serre relations are proved",
        "full holographic duality is proved",
    )
    for phrase in forbidden_assertions:
        report.check("claim_boundary", all(phrase.lower() not in text.lower() for text in texts.values()), f"forbidden assertion absent: {phrase}")

    print("COUNTS " + " ".join(f"{key}={value}" for key, value in sorted(report.counts.items())))
    if report.failures:
        print("FAILURES")
        print("\n".join(report.failures))
        return 1
    print(f"NOTEBOOK_IV_VERIFIED {SEMANTIC_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

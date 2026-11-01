#!/usr/bin/env python3
"""Adversarial release tests for the 38 roadmap failure modes."""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERIFY_SENTINEL = "NOTEBOOK_IV_VERIFIED NIV-36a2530aab4feb7d"
CHECKPOINT_SENTINEL = "CHECKPOINT_IV_PASS"
PAYLOAD = (
    "Notebook_IV.md",
    "notebook_iv_header.html",
    "Notebook_IV_Semiclassical_Bulk_Normalization.html",
    "Notebook_IV_Semiclassical_Bulk_Normalization_Static.pdf",
    "verify_notebook_IV.py",
    "scalar_controls_IV.py",
    "independent_check_IV.py",
    "derive_bulk_s2_anchor.py",
    "derive_bulk_s3_anchor.py",
    "test_notebook_IV_mutations.py",
    "checkpoint_check_IV.py",
    "CONVENTION_LEDGER.json",
    "ROADMAP.md",
    "SOURCE_LOG.md",
    "requirements.txt",
    "SOURCE_MANIFEST.sha256",
)


@dataclass(frozen=True)
class Mutation:
    number: int
    name: str
    filename: str
    old: str
    new: str


MODEL_MUTATIONS = (
    Mutation(1, "Chern-Simons level factor", "CONVENTION_LEDGER.json", '"bulk_CS_level": "1/(8*pi*G)"', '"bulk_CS_level": "1/(4*pi*G)"'),
    Mutation(2, "trace normalization", "CONVENTION_LEDGER.json", '"bulk_trace_tau_s": "12/(s*(s^2-1))"', '"bulk_trace_tau_s": "6/(s*(s^2-1))"'),
    Mutation(3, "remove gravity-branch i", "CONVENTION_LEDGER.json", "alpha_plus=+i*a_s", "alpha_plus=+a_s"),
    Mutation(4, "flip Miura scale squared", "CONVENTION_LEDGER.json", '"bulk_miura_scale_squared": "pi*kCS*tau_s"', '"bulk_miura_scale_squared": "-pi*kCS*tau_s"'),
    Mutation(5, "central charge 6/G", "CONVENTION_LEDGER.json", '"gravity_cM": "3/G"', '"gravity_cM": "6/G"'),
    Mutation(6, "N=2 M quadratic coefficient", "CONVENTION_LEDGER.json", '"N2_bulk_M": "-(psi_prime^2)/4-psi_double_prime/2"', '"N2_bulk_M": "-(psi_prime^2)/2-psi_double_prime/2"'),
    Mutation(7, "N=2 M improvement coefficient", "CONVENTION_LEDGER.json", '"N2_bulk_M": "-(psi_prime^2)/4-psi_double_prime/2"', '"N2_bulk_M": "-(psi_prime^2)/4-psi_double_prime/4"'),
    Mutation(8, "N=2 L coefficient", "CONVENTION_LEDGER.json", '"N2_bulk_L": "-psi_prime*barpsi_prime/2-barpsi_double_prime/2"', '"N2_bulk_L": "-psi_prime*barpsi_prime/4-barpsi_double_prime/2"'),
    Mutation(9, "symplectic sign", "CONVENTION_LEDGER.json", '"A1_bulk_cross_bracket": "{psi\'(phi),barpsi(phi\')}=8*pi*G*delta(phi-phi\')"', '"A1_bulk_cross_bracket": "{psi\'(phi),barpsi(phi\')}=-8*pi*G*delta(phi-phi\')"'),
    Mutation(10, "hidden square-root-two rescaling", "CONVENTION_LEDGER.json", "the consistent value is i/(2*sqrt(G))", "the consistent value is i/sqrt(2*G)"),
    Mutation(11, "delete FH Fourier i", "CONVENTION_LEDGER.json", "J_FH(phi)=i*sum_n", "J_FH(phi)=sum_n"),
    Mutation(12, "delta-prime sign", "CONVENTION_LEDGER.json", "=partial_phi delta", "=-partial_phi delta"),
    Mutation(13, "chi1 coefficient", "CONVENTION_LEDGER.json", '"chi_1": "psi_L+2*psi_W"', '"chi_1": "psi_L+sqrt(2)*psi_W"'),
    Mutation(14, "chi2 sign", "CONVENTION_LEDGER.json", '"chi_2": "psi_L-2*psi_W"', '"chi_2": "psi_L+2*psi_W"'),
    Mutation(15, "simple-root label swap", "CONVENTION_LEDGER.json", '"chi_1": "psi_L+2*psi_W"', '"chi_1": "psi_L-2*psi_W"'),
    Mutation(16, "Cartan off-diagonal sign", "CONVENTION_LEDGER.json", '"A2_Cartan": [[2, -1], [-1, 2]]', '"A2_Cartan": [[2, 1], [1, 2]]'),
    Mutation(17, "A2 W symplectic coefficient", "CONVENTION_LEDGER.json", '"W": "6*pi*G"', '"W": "8*pi*G"'),
    Mutation(18, "barred root-coordinate coefficient", "CONVENTION_LEDGER.json", '"bar_chi_1": "barpsi_L+2*barpsi_W"', '"bar_chi_1": "barpsi_L+barpsi_W"'),
    Mutation(19, "leading primitive exponent sign", "CONVENTION_LEDGER.json", '"plus": "mu*Phi_i_plus=-chi_i"', '"plus": "mu*Phi_i_plus=+chi_i"'),
    Mutation(20, "barred-linear primitive sign", "CONVENTION_LEDGER.json", '"minus": "mu*Phi_i_minus=-bar_chi_i"', '"minus": "mu*Phi_i_minus=+bar_chi_i"'),
    Mutation(21, "remove target-frame subtraction", "CONVENTION_LEDGER.json", '"canonical_frame_relation": "Q_i^[1]=Qtilde_i^[1]-A_T,i*Q_i^[0]"', '"canonical_frame_relation": "Q_i^[1]=Qtilde_i^[1]"'),
    Mutation(22, "even coefficient promoted to O(1)", "CONVENTION_LEDGER.json", '"even_affine_scaling": "O(G)"', '"even_affine_scaling": "O(1)"'),
    Mutation(23, "raw coefficient relabelled ordinary", "CONVENTION_LEDGER.json", '"Gate3B_frame": "raw moving frame before target subtraction"', '"Gate3B_frame": "ordinary O(1) second coefficient"'),
    Mutation(24, "BCH exponent promoted", "CONVENTION_LEDGER.json", '"BCH_log_scaling": "O(t*G)"', '"BCH_log_scaling": "O(t)"'),
    Mutation(25, "A2 tangent charge prefactor sign", "CONVENTION_LEDGER.json", '"A2_charge_prefactor_tangent": "-1/(8*pi*G)"', '"A2_charge_prefactor_tangent": "1/(8*pi*G)"'),
    Mutation(26, "restore erroneous spin-three square", "CONVENTION_LEDGER.json", "the consistent term is linear", "the consistent term is squared"),
    Mutation(27, "erase averaged ordering incorrectly", "CONVENTION_LEDGER.json", '"strict_classical_ordering_reduction": "averaged->commutative"', '"strict_classical_ordering_reduction": "averaged->parent_normal"'),
    Mutation(28, "authorize quantum screening doublet", "ROADMAP.md", "No quantum screening doublet", "A quantum screening doublet exists. No quantum screening doublet"),
    Mutation(29, "claim BRST construction", "ROADMAP.md", "No quantum screening doublet", "BRST complex is constructed. No quantum screening doublet"),
    Mutation(30, "promote canonical coefficient to ordinary screening", "SOURCE_LOG.md", "not an ordinary second quantum screening", "is an ordinary second quantum screening"),
)


def copy_release(target: Path) -> None:
    for name in PAYLOAD:
        shutil.copy2(ROOT / name, target / name)


def refresh_manifest(target: Path) -> None:
    lines = []
    for line in (target / "SOURCE_MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        _, name = line.split("  ", 1)
        lines.append(f"{hashlib.sha256((target / name).read_bytes()).hexdigest()}  {name}")
    (target / "SOURCE_MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(target: Path, command: list[str], *, timeout: float = 60.0, host_tz: str = "UTC") -> tuple[int, str, str, bool]:
    env = os.environ.copy()
    env["TZ"] = host_tz
    try:
        result = subprocess.run(command, cwd=target, env=env, text=True, capture_output=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr, False
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or "", True


def detected(returncode: int, stdout: str, sentinel: str) -> bool:
    return returncode != 0 and sentinel not in stdout


def model_mutation(case: Mutation) -> bool:
    with tempfile.TemporaryDirectory(prefix=f"notebook_iv_m{case.number:02d}_") as temp:
        target = Path(temp)
        copy_release(target)
        path = target / case.filename
        source = path.read_text(encoding="utf-8")
        if source.count(case.old) < 1:
            raise RuntimeError(f"mutation precondition M{case.number}: {case.old}")
        path.write_text(source.replace(case.old, case.new, 1), encoding="utf-8")
        code, stdout, _, timed_out = run(target, [sys.executable, "verify_notebook_IV.py"])
        if timed_out:
            print(f"[PASS] M{case.number:02d} {case.name}: fail-closed timeout")
            return True
        ok = detected(code, stdout, VERIFY_SENTINEL)
        print(("[PASS] " if ok else "[FAIL] ") + f"M{case.number:02d} {case.name}")
        return ok


def packaging_mutation(number: int, name: str) -> bool:
    with tempfile.TemporaryDirectory(prefix=f"notebook_iv_m{number:02d}_") as temp:
        target = Path(temp)
        copy_release(target)
        manifest = target / "SOURCE_MANIFEST.sha256"
        if number == 31:
            lines = manifest.read_text(encoding="utf-8").splitlines()
            lines[0] = "0" * 64 + lines[0][64:]
            manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        elif number == 32:
            (target / "CONVENTION_LEDGER.json").unlink()
        elif number == 33:
            text = manifest.read_text(encoding="utf-8")
            manifest.write_text(text.replace("  Notebook_IV.md", "  ../Notebook_IV.md", 1), encoding="utf-8")
        elif number == 34:
            lines = manifest.read_text(encoding="utf-8").splitlines()
            first_name = lines[0].split("  ", 1)[1]
            lines[1] = lines[1].split("  ", 1)[0] + "  " + first_name
            manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        elif number == 35:
            (target / "SOURCE_LOG.md").unlink()
        elif number == 36:
            (target / "Notebook_IV_Semiclassical_Bulk_Normalization_Static.pdf").write_bytes(
                (target / "Notebook_IV_Semiclassical_Bulk_Normalization.html").read_bytes()
            )
            refresh_manifest(target)
        elif number == 37:
            path = target / "Notebook_IV_Semiclassical_Bulk_Normalization.html"
            path.write_text(path.read_text(encoding="utf-8").replace("NIV-36a2530aab4feb7d", "NIV-0000000000000000", 1), encoding="utf-8")
            refresh_manifest(target)
        elif number == 38:
            path = target / "checkpoint_check_IV.py"
            source = path.read_text(encoding="utf-8")
            source = source.replace('env["TZ"] = "Europe/Berlin"', 'env["TZ"] = "UTC"', 1)
            source = source.replace(
                'gate.require(f"Author:          Semantic release {SEMANTIC_ID}" in info.stdout, "PDF semantic metadata")',
                'gate.require(f"Author:          Semantic release {SEMANTIC_ID}" in info.stdout and "CEST" in info.stdout, "PDF semantic metadata")',
                1,
            )
            path.write_text(source, encoding="utf-8")
            refresh_manifest(target)
        else:
            raise ValueError(number)
        code, stdout, _, timed_out = run(
            target,
            [sys.executable, "checkpoint_check_IV.py", "--skip-mutations", "--timeout", "90"],
            timeout=120,
            host_tz="UTC",
        )
        if timed_out:
            print(f"[PASS] M{number:02d} {name}: fail-closed timeout")
            return True
        ok = detected(code, stdout, CHECKPOINT_SENTINEL)
        print(("[PASS] " if ok else "[FAIL] ") + f"M{number:02d} {name}")
        return ok


def main() -> int:
    passed = sum(model_mutation(case) for case in MODEL_MUTATIONS)
    packaging = (
        (31, "corrupt manifest digest"),
        (32, "missing convention ledger"),
        (33, "manifest path traversal"),
        (34, "duplicate manifest member"),
        (35, "missing source log"),
        (36, "stale HTML substituted for PDF"),
        (37, "semantic release ID mismatch"),
        (38, "host-timezone CEST assertion"),
    )
    passed += sum(packaging_mutation(number, name) for number, name in packaging)

    controls = 0
    code, stdout, _, timed_out = run(ROOT, [sys.executable, "verify_notebook_IV.py"], timeout=90)
    if not timed_out and code == 0 and VERIFY_SENTINEL in stdout:
        controls += 1
        print("[PASS] control 1: unmutated verifier")
    else:
        print("[FAIL] control 1: unmutated verifier")
    code, stdout, _, timed_out = run(
        ROOT,
        [sys.executable, "checkpoint_check_IV.py", "--skip-mutations", "--timeout", "180"],
        timeout=210,
        host_tz="UTC",
    )
    if not timed_out and code == 0 and CHECKPOINT_SENTINEL in stdout:
        controls += 1
        print("[PASS] control 2: unmutated checkpoint under UTC host")
    else:
        print("[FAIL] control 2: unmutated checkpoint under UTC host")
    print(f"MUTATIONS_IV {passed}/38 controls={controls}/2")
    return 0 if passed == 38 and controls == 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())

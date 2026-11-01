#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


BASE = Path(__file__).resolve().parent
PAYLOADS = [
    "Notebook_III_Gate3B_Tangent_OPE_Closure.html",
    "Notebook_III_Gate3B_Tangent_OPE_Closure_Static.pdf",
    "verify_notebook_III_gate3b.py",
    "test_notebook_III_gate3b_mutations.py",
    "checkpoint_check_III_gate3b.py",
    "independent_check_III_gate3b.py",
    "ROADMAP.md",
    "SOURCE_LOG.md",
    "requirements.txt",
]


@dataclass(frozen=True)
class Case:
    label: str
    rel: str
    old: str
    new: str
    command: str = "document"


def write_manifest(path):
    lines = []
    for rel in PAYLOADS:
        data = (path/rel).read_bytes()
        lines.append(f"{hashlib.sha256(data).hexdigest()}  {rel}")
    (path/"SOURCE_MANIFEST.sha256").write_text("\n".join(lines)+"\n", encoding="utf-8")


def replace(path, rel, old, new):
    file = path/rel
    text = file.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"mutation source not found in {rel}: {old}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


def stage():
    temp = Path(tempfile.mkdtemp(prefix="gate3b-mutation-"))
    for name in PAYLOADS:
        shutil.copy2(BASE/name, temp/name)
    shutil.copy2(BASE/"SOURCE_MANIFEST.sha256", temp/"SOURCE_MANIFEST.sha256")
    return temp


def run(path, command, timeout=300):
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    return subprocess.run(command, cwd=path, text=True, capture_output=True,
                          timeout=timeout, env=env)


def must_fail(path, command, label):
    try:
        proc = run(path, command, timeout=60)
    except subprocess.TimeoutExpired:
        print(f"[CAUGHT] {label}: mutant timed out fail-closed", flush=True)
        return
    if proc.returncode == 0:
        raise AssertionError(f"mutation escaped: {label}")
    print(f"[CAUGHT] {label}: nonzero exit", flush=True)


cases = [
    Case("html_status", PAYLOADS[0], "GATE 3B PASS - CORRECTED", "GATE 3B FAIL"),
    Case("html_gate", PAYLOADS[0], "GATE 3 CLOSES WITH OUTCOME B", "GATE 3 REMAINS OPEN"),
    Case("html_dwinv", PAYLOADS[0], "\\partial_w(w^{-1})=-w^{-2}", "\\partial_w(w^{-1})=0"),
    Case("html_w2_root1", PAYLOADS[0], "-\\frac{\\mu}{4w^2}", "+\\frac{\\mu}{4w^2}"),
    Case("html_w2_root2", PAYLOADS[0], "+\\frac{\\mu}{4w^2}", "-\\frac{\\mu}{4w^2}"),
    Case("html_contact_root1", PAYLOADS[0], "\\delta\\mathcal O_{1,2}=\\frac{\\mu}{4w}", "\\delta\\mathcal O_{1,2}=-\\frac{\\mu}{4w}"),
    Case("html_contact_root2", PAYLOADS[0], "\\delta\\mathcal O_{2,2}=-\\frac{\\mu}{4w}", "\\delta\\mathcal O_{2,2}=+\\frac{\\mu}{4w}"),
    Case("html_odd_witness1", PAYLOADS[0], "\\Xi_{1,2}=\\frac{H_1+\\alpha^-}{4}", "\\Xi_{1,2}=\\frac{H_1+\\alpha^-+\\mu}{4}"),
    Case("html_odd_witness2", PAYLOADS[0], "\\Xi_{2,2}=-\\frac{H_2+\\alpha^-}{4}", "\\Xi_{2,2}=-\\frac{H_2+\\alpha^-+\\mu}{4}"),
    Case("html_target_frame", PAYLOADS[0], "Q_i^{[1]}=\\widetilde Q_i^{[1]}-\\mathsf", "Q_i^{[1]}=\\widetilde Q_i^{[1]}+\\mathsf"),
    Case("html_claim_boundary", PAYLOADS[0], "not an ordinary second screening", "an ordinary second screening"),
    Case("html_semantic_id", PAYLOADS[0], "G3B-aaef4dfef7d3880e", "G3B-0000000000000000"),
    Case("source_role", "SOURCE_LOG.md", "free-field formulas, not a screening construction", "screening construction in equations (4.18)-(4.21)"),
    Case("source_parent_hash", "SOURCE_LOG.md", "45e9bfdf2906527ea2175513dff447e9052d06a14c94dd979904d07323962c82", "05e9bfdf2906527ea2175513dff447e9052d06a14c94dd979904d07323962c82"),
    Case("source_derivative", "SOURCE_LOG.md", "D(w^-1)=-w^-2", "D(w^-1)=0"),
    Case("road_derivative", "ROADMAP.md", "D(w^-1)=-w^-2", "D(w^-1)=0"),
    Case("road_contact", "ROADMAP.md", "derived averaged-order contact", "discarded contact"),
    Case("road_gate", "ROADMAP.md", "Gate 3: closed with Outcome B", "Gate 3: open"),
    Case("code_dwinv", "verify_notebook_III_gate3b.py", "out -= sp.diff(expr, Winv) * Winv**2", "out += sp.diff(expr, Winv) * Winv**2", "model"),
    Case("code_even_w2_root1", "verify_notebook_III_gate3b.py", "- mu*Winv**2/4", "+ mu*Winv**2/4", "model"),
    Case("code_even_w2_root2", "verify_notebook_III_gate3b.py", "+ mu*Winv**2/4", "- mu*Winv**2/4", "model"),
    Case("code_odd_contact", "verify_notebook_III_gate3b.py", "{3: -mu/2, 2: -mu**2", "{3: mu/2, 2: -mu**2", "model"),
    Case("code_even_contact", "verify_notebook_III_gate3b.py", "{3: mu/2,\n         2: mu*", "{3: -mu/2,\n         2: mu*", "model"),
    Case("code_unbar_contact", "verify_notebook_III_gate3b.py", "{3: 0, 2: mu*Winv/4", "{3: 0, 2: -mu*Winv/4", "model"),
    Case("code_branch_coefficient", "verify_notebook_III_gate3b.py", "m3 = -mu**3 - sign * am * mu**2", "m3 = -mu**3 + sign * am * mu**2", "model"),
    Case("code_minus_orientation", "verify_notebook_III_gate3b.py", "e * sp.series(parent[q].subs(subs)", "-e * sp.series(parent[q].subs(subs)", "model"),
    Case("code_barred_contour", "verify_notebook_III_gate3b.py", "sign * e**3 * sp.series", "e**3 * sp.series", "model"),
    Case("code_monodromy", "verify_notebook_III_gate3b.py", "db + b*lam_plus - b*t_lam_minus - m", "db + b*lam_plus + b*t_lam_minus - m", "model"),
    Case("code_mu_diff", "verify_notebook_III_gate3b.py", "nu = -am * mu**2", "nu = am * mu**2", "model"),
    Case("independent_dwinv", "independent_check_III_gate3b.py", "-sp.diff(expr, winv)*winv**2", "+sp.diff(expr, winv)*winv**2", "independent"),
    Case("independent_screening", "independent_check_III_gate3b.py", "a*lam+lam**2-1", "a*lam-lam**2-1", "independent"),
]


# Two genuine unmutated controls.
controls = 0
temp = stage()
try:
    proc = run(temp, [sys.executable, "verify_notebook_III_gate3b.py"])
    if proc.returncode or "VERIFIER PASSED" not in proc.stdout:
        raise AssertionError("unmutated verifier control failed")
    controls += 1
finally:
    shutil.rmtree(temp)

temp = stage()
try:
    proc = run(temp, [sys.executable, "checkpoint_check_III_gate3b.py", "--skip-mutations"], timeout=360)
    if proc.returncode or "CHECKPOINT GATE 3B PASSED" not in proc.stdout:
        raise AssertionError("unmutated checkpoint control failed")
    controls += 1
finally:
    shutil.rmtree(temp)


caught = 0
for case in cases:
    temp = stage()
    try:
        replace(temp, case.rel, case.old, case.new)
        if case.command == "document":
            command = [sys.executable, "verify_notebook_III_gate3b.py", "--document-only"]
        elif case.command == "independent":
            command = [sys.executable, "independent_check_III_gate3b.py"]
        else:
            command = [sys.executable, "verify_notebook_III_gate3b.py"]
        must_fail(temp, command, case.label)
        caught += 1
    finally:
        shutil.rmtree(temp)


for label, rel in (
    ("missing_html", PAYLOADS[0]),
    ("missing_source", "SOURCE_LOG.md"),
    ("missing_road", "ROADMAP.md"),
    ("missing_independent", "independent_check_III_gate3b.py"),
):
    temp = stage()
    try:
        (temp/rel).unlink()
        must_fail(temp, [sys.executable, "checkpoint_check_III_gate3b.py", "--skip-mutations"], label)
        caught += 1
    finally:
        shutil.rmtree(temp)


temp = stage()
try:
    replace(temp, "requirements.txt", "sympy==1.14.0", "sympy>=1.14.0")
    write_manifest(temp)
    must_fail(temp, [sys.executable, "checkpoint_check_III_gate3b.py", "--skip-mutations"], "requirements")
    caught += 1
finally:
    shutil.rmtree(temp)

temp = stage()
try:
    (temp/PAYLOADS[1]).write_bytes(b"%PDF-1.4\n%%EOF\n")
    write_manifest(temp)
    must_fail(temp, [sys.executable, "checkpoint_check_III_gate3b.py", "--skip-mutations"], "stale_pdf")
    caught += 1
finally:
    shutil.rmtree(temp)

for label, extra in (
    ("unsafe_manifest", "0"*64+"  ../escape\n"),
    ("malformed_digest", "g"*64+"  extra.txt\n"),
):
    temp = stage()
    try:
        manifest = temp/"SOURCE_MANIFEST.sha256"
        manifest.write_text(manifest.read_text(encoding="utf-8")+extra, encoding="utf-8")
        must_fail(temp, [sys.executable, "checkpoint_check_III_gate3b.py", "--skip-mutations"], label)
        caught += 1
    finally:
        shutil.rmtree(temp)

temp = stage()
try:
    manifest = temp/"SOURCE_MANIFEST.sha256"
    first = manifest.read_text(encoding="utf-8").splitlines()[0]
    manifest.write_text(manifest.read_text(encoding="utf-8")+first+"\n", encoding="utf-8")
    must_fail(temp, [sys.executable, "checkpoint_check_III_gate3b.py", "--skip-mutations"], "duplicate_manifest")
    caught += 1
finally:
    shutil.rmtree(temp)

total = len(cases)+4+5
if controls != 2 or caught != total:
    raise AssertionError(f"mutation accounting failed: controls={controls}, caught={caught}, total={total}")
print(f"MUTATION GATE 3B PASSED: {caught}/{total} destructive mutations caught")
print(f"UNMUTATED CONTROLS: {controls}/2")

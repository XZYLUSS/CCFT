#!/usr/bin/env python3
"""Fail-closed end-to-end mutation regression for Notebook II, Gate 2."""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
PKG = [
    "Notebook_II_Gate2_Tangent_Operator.html",
    "Notebook_II_Gate2_Tangent_Operator_Static.pdf",
    "verify_notebook_II_gate2.py",
    "test_notebook_II_gate2_mutations.py",
    "freeze_check_II_gate2.py",
    "requirements.txt",
    "ROADMAP.md",
    "SOURCE_LOG.md",
]


def _positive_timeout(name, default):
    try:
        value = float(os.environ.get(name, default))
    except ValueError as exc:
        raise SystemExit(f"{name} must be numeric") from exc
    if value <= 0:
        raise SystemExit(f"{name} must be positive")
    return value


PER_PROCESS_TIMEOUT_S = _positive_timeout(
    "NOTEBOOK_II_GATE2_PER_PROCESS_TIMEOUT_S", 45)
PER_CASE_TIMEOUT_S = _positive_timeout(
    "NOTEBOOK_II_GATE2_PER_CASE_TIMEOUT_S", 60)
TOTAL_SUITE_TIMEOUT_S = _positive_timeout(
    "NOTEBOOK_II_GATE2_TOTAL_SUITE_TIMEOUT_S", 300)

MUTATIONS = {
    "H1 gate status corrupted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        "GATE 2 CLOSED", "GATE 2 OPEN"),
    "H2 fixed lattice deleted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"\mathbb C[\Lambda_0]\widehat\otimes",
        r"\mathbb C[\Gamma_t]\widehat\otimes"),
    "H3 PBW trivialization corrupted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"\tau_{\lambda}:X\lvert\lambda(t)\rangle\longmapsto X\lvert\lambda(0)\rangle",
        r"\tau_{\lambda}:X\lvert\lambda(t)\rangle\longmapsto0"),
    "H4 off-horizontal exclusion deleted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        "not objects of the finite-parent screening domain",
        "valid objects of the finite-parent screening domain"),
    "H5 boundary cancellation corrupted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"a_{\rm u}(t)=a_{\rm b}(t)=0",
        r"a_{\rm u}(t)=a_{\rm b}(t)=1"),
    "H6 PBW nonzero witness deleted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"m=-2\), \(J^-_{-1}",
        r"m=-2\), \(0\cdot J^-_{-1}"),
    "H7 connection gauge law corrupted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"A_{\rm t}Q^{[0]}-Q^{[0]}A_{\rm s}",
        r"A_{\rm t}+A_{\rm s}"),
    "H8 covariant target term deleted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"+\frac12\Delta U^{[1]}_{{\rm T},n}Q^{[0]}=0,",
        r"=0,"),
    "H9 q-plus generator sign corrupted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"q^\mp=-\frac12\partial_{\eta^\pm}^{\mathfrak h}",
        r"q^\mp=+\frac12\partial_{\eta^\pm}^{\mathfrak h}"),
    "H10 represented M0 correction erased": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"\Delta M^{[1]}_{{\rm T},0}=2(m+1)",
        r"\Delta M^{[1]}_{{\rm T},0}=0"),
    "H11 BCH factor sign corrupted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"(1-\rho)^{-t\bar b(t)^2/2}",
        r"(1-\rho)^{+t\bar b(t)^2/2}"),
    "H12 target action families collapsed": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"U_{{\rm T,u}}(t)\), and \(U_{{\rm T,b}}(t)",
        r"U_{{\rm T,u}}(t)\), and \(U_{{\rm T,u}}(t)"),
    "H13 target plus paths identified": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"p^+_{{\rm T,b}}=\lambda_m^+-\frac{t\bar b}{4}",
        r"p^+_{{\rm T,b}}=\lambda_m^++\frac{tb}{4}"),
    "H14 single-field target shift doubled": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"\Delta_{\rm u}(t)=\frac14\big(t b(t),b(t)\big)",
        r"\Delta_{\rm u}(t)=\frac12\big(t b(t),b(t)\big)"),
    "H15 relative target plus tangent doubled": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"\Delta p^+=\frac{b_1}{2},\qquad",
        r"\Delta p^+=b_1,\qquad"),
    "H16 relative target minus tangent doubled": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"\Delta p^-=\frac{B_{\rm diff}}{2}=",
        r"\Delta p^-=B_{\rm diff}="),
    "H17 root-to-single-field reduction corrupted": (
        "Notebook_II_Gate2_Tangent_Operator.html",
        r"=-\frac{\mu}{2}=\frac b4.",
        r"=-\mu=\frac b2."),
    "R1 roadmap horizontal category deleted": (
        "ROADMAP.md", "horizontal resonant Fock curves",
        "arbitrary logarithmic jet module"),
    "R2 roadmap timeout policy reversed": (
        "ROADMAP.md", "Every timeout is a failed test",
        "Every timeout is a caught mutation"),
    "S1 source connection scope deleted": (
        "SOURCE_LOG.md", "connection gauge law",
        "unclassified connection dependence"),
    "V1 verifier accumulator disabled": (
        "verify_notebook_II_gate2.py",
        "def ck(self, category: str, condition: bool, label: str):\n        self.counts[category] += 1",
        "def ck(self, category: str, condition: bool, label: str):\n        return  # MUTATION V1\n        self.counts[category] += 1"),
    "V2 verifier exits green early": (
        "verify_notebook_II_gate2.py", "class Ledger:",
        "print('ALL NOTEBOOK II GATE 2 CHECKS PASSED')\nsys.exit(0)  # MUTATION V2\nclass Ledger:"),
    "V3 horizontal determinant corrupted": (
        "verify_notebook_II_gate2.py",
        "sp.factor(monodromy_matrix.det()) == -2*t*b*bb",
        "sp.factor(monodromy_matrix.det()) == 0"),
    "V4 boundary restriction corrupted": (
        "verify_notebook_II_gate2.py",
        "boundary.subs(a,0) == 0",
        "boundary.subs(a,0) == 1"),
    "V5 target divisibility bypassed": (
        "verify_notebook_II_gate2.py",
        "shift_u = b1/4+t*b3sol/4",
        "shift_u = b1/4+t*bb3sol/4  # MUTATION V5"),
    "V6 PBW witness deleted": (
        "verify_notebook_II_gate2.py",
        "odd_level_one = b1*Jminus1+B*Jplus1",
        "odd_level_one = B*Jplus1  # MUTATION V6"),
    "V7 operator boundary corrupted": (
        "verify_notebook_II_gate2.py",
        "finite_L_comm = sp.simplify(own_u+own_b+cross_u+cross_b)",
        "finite_L_comm = sp.simplify(own_u+own_b+cross_u+cross_b)+1  # MUTATION V7"),
    "V8 stress contraction corrupted": (
        "verify_notebook_II_gate2.py",
        "M = sp.expand(t*(Tu+Tb))", "M = sp.expand(Tu+Tb)"),
    "V9 target momentum tangent erased": (
        "verify_notebook_II_gate2.py",
        "delta_p_plus = sp.simplify(sp.diff(pTu-pTb,t).subs(t,0))",
        "delta_p_plus = sp.Integer(0)  # MUTATION V9"),
    "V10 connection convolution deleted": (
        "verify_notebook_II_gate2.py",
        "covariant_target = sp.expand(UT0*Q1-Q1*US0+(UTu1-UTb1)*Q0/2)",
        "covariant_target = sp.expand(UT0*Q1-Q1*US0)  # MUTATION V10"),
    "V11 single-field Weyl bracket doubled": (
        "verify_notebook_II_gate2.py",
        "sf_weyl = sp.simplify(sp.Rational(1,4)*root_weyl*root_sq)",
        "sf_weyl = sp.Rational(1,2)  # MUTATION V11"),
    "V12 root shift reduction doubled": (
        "verify_notebook_II_gate2.py",
        "scalar_root_shift = sp.simplify(-sp.Rational(1,2)*(mu/2)*root_sq)",
        "scalar_root_shift = sp.simplify(-sp.Rational(1,2)*mu*root_sq)  # MUTATION V12"),
    "F1 freeze accumulator disabled": (
        "freeze_check_II_gate2.py",
        "def ck(cond,label):\n    global count",
        "def ck(cond,label):\n    return  # MUTATION F1\n    global count"),
    "F2 freeze checker fakes green": (
        "freeze_check_II_gate2.py", "count=0; failures=[]",
        "print('G_II_GATE2_mech GREEN -- 99/99 checks pass.')\n"
        "sys.exit(0)  # MUTATION F2\ncount=0; failures=[]"),
    "M1 mutation runner exits silently": (
        "test_notebook_II_gate2_mutations.py",
        "def main():\n    bad = []",
        "def main():\n    return 0  # MUTATION M1\n    bad = []"),
    "M2 mutation runner fakes sentinel": (
        "test_notebook_II_gate2_mutations.py",
        "def main():\n    bad = []",
        "def main():\n    print('MUTATION II GATE2 PASSED: 36/36 destructive mutations were caught.')\n"
        "    return 0  # MUTATION M2\n    bad = []"),
}


def _kill_process_group(pid):
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run(args, cwd, timeout_s=PER_PROCESS_TIMEOUT_S, start_new_session=True):
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as out_file, \
            tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as err_file:
        proc = subprocess.Popen(
            args, cwd=str(cwd), text=True, stdout=out_file, stderr=err_file,
            start_new_session=start_new_session)
        timed_out = False
        try:
            returncode = proc.wait(timeout=max(0.1, timeout_s))
        except subprocess.TimeoutExpired:
            timed_out = True
            if start_new_session:
                _kill_process_group(proc.pid)
            else:
                proc.kill()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if start_new_session:
                    _kill_process_group(proc.pid)
                else:
                    proc.kill()
                proc.wait()
            returncode = 124
        finally:
            if start_new_session and proc.poll() is not None:
                _kill_process_group(proc.pid)
        out_file.seek(0); err_file.seek(0)
        stdout, stderr = out_file.read(), err_file.read()
        if timed_out:
            stderr += f"\nTIMEOUT after {timeout_s:.1f}s"
        return subprocess.CompletedProcess(args, returncode, stdout, stderr)


def stage(dest):
    for name in PKG:
        shutil.copy(HERE/name, dest/name)
    shutil.copy(HERE/"SOURCE_MANIFEST.sha256", dest/"SOURCE_MANIFEST.sha256")


def regen_manifest(dest):
    path = dest/"SOURCE_MANIFEST.sha256"
    text = path.read_text(encoding="utf-8")
    for name in PKG:
        digest = hashlib.sha256((dest/name).read_bytes()).hexdigest()
        text = re.sub(rf"^[0-9a-f]{{64}}\s+{re.escape(name)}$",
                      f"{digest}  {name}", text, flags=re.M)
    path.write_text(text, encoding="utf-8")


def freeze_checker_green(result):
    hits = re.findall(
        r"G_II_GATE2_mech GREEN -- (\d+)/(\d+) checks pass\.",
        result.stdout)
    return (result.returncode == 0 and len(hits) == 1
            and hits[0][0] == hits[0][1]
            and int(hits[0][0]) == result.stdout.count("[PASS]")
            and int(hits[0][0]) > 0
            and "G_II_GATE2_mech RED" not in result.stdout)


def mutation_runner_green(result):
    """Independent success protocol for mutations of the runner itself."""
    nmut = len(MUTATIONS)
    expected = nmut+1
    sentinel = (
        f"MUTATION II GATE2 PASSED: {nmut}/{nmut} "
        "destructive mutations were caught.")
    counts = re.findall(
        r"MUTATION_COUNTS destructive=(\d+) scalar_controls=(\d+) total=(\d+)",
        result.stdout)
    return (result.returncode == 0
            and result.stdout.count(sentinel) == 1
            and counts == [(str(nmut), "1", str(expected))]
            and result.stdout.count("[PASS]") == expected
            and "[FAIL]" not in result.stdout
            and "MUTATION II GATE2 FAILED" not in result.stdout
            and "MUTATION II GATE2 PROTOCOL FAILED" not in result.stdout)


def run_case(target, old, new):
    with tempfile.TemporaryDirectory(prefix="gate2-case-") as td:
        dest = pathlib.Path(td)
        stage(dest)
        path = dest/target
        source = path.read_text(encoding="utf-8")
        if source.count(old) != 1:
            return False, f"mutation target count is {source.count(old)}, expected 1"
        path.write_text(source.replace(old,new,1), encoding="utf-8")
        regen_manifest(dest)
        auth = run(["sha256sum","-c","SOURCE_MANIFEST.sha256"], dest,
                   timeout_s=10, start_new_session=False)
        if auth.returncode != 0:
            return False, "mutated package failed its regenerated manifest"
        command = ("test_notebook_II_gate2_mutations.py"
                   if target == "test_notebook_II_gate2_mutations.py"
                   else "freeze_check_II_gate2.py")
        result = run([sys.executable,command], dest,
                     timeout_s=PER_PROCESS_TIMEOUT_S,
                     start_new_session=False)
        if result.returncode == 124 or "TIMEOUT after" in result.stderr:
            return False, "verification timed out; no mutation verdict was produced"
        green = (mutation_runner_green(result)
                 if command == "test_notebook_II_gate2_mutations.py"
                 else freeze_checker_green(result))
        if green:
            return False, "mutated package stayed behaviourally green"
        return True, f"caught (exit {result.returncode})"


def single_case_worker(label):
    if label not in MUTATIONS:
        print("MUTATION_CASE_RESULT status=FAIL detail=unknown-label")
        return 2
    try:
        ok, detail = run_case(*MUTATIONS[label])
    except Exception as exc:
        ok, detail = False, f"case failed: {exc}"
    print("MUTATION_CASE_RESULT status=%s detail=%s" %
          ("PASS" if ok else "FAIL", detail.replace("\n"," ")))
    return 0 if ok else 1


def main():
    bad = []
    print("NOTEBOOK II GATE 2 END-TO-END PACKAGE MUTATIONS")
    suite_deadline = time.monotonic()+TOTAL_SUITE_TIMEOUT_S
    for label in MUTATIONS:
        remaining = suite_deadline-time.monotonic()
        if remaining <= 0:
            ok, detail = False, "hard total-suite deadline exceeded"
        else:
            result = run(
                [sys.executable,str(HERE/"test_notebook_II_gate2_mutations.py"),
                 "--single-case",label], HERE,
                timeout_s=min(PER_CASE_TIMEOUT_S,remaining),
                start_new_session=True)
            passed = "MUTATION_CASE_RESULT status=PASS" in result.stdout
            failed = "MUTATION_CASE_RESULT status=FAIL" in result.stdout
            ok = (result.returncode == 0 and passed and not failed
                  and result.stdout.count("MUTATION_CASE_RESULT") == 1)
            match = re.search(
                r"MUTATION_CASE_RESULT status=(?:PASS|FAIL) detail=(.*)",
                result.stdout)
            detail = (match.group(1) if match else
                      (result.stdout+result.stderr)[-300:].replace("\n"," "))
        print("  [%s] %-42s %s" % ("PASS" if ok else "FAIL",label,detail))
        if not ok:
            bad.append(label)

    remaining = max(0.1,suite_deadline-time.monotonic())
    scalar = run([sys.executable,"verify_notebook_II_gate2.py",
                  "--scalar-sanity-controls"], HERE,
                 timeout_s=min(PER_PROCESS_TIMEOUT_S,remaining),
                 start_new_session=True)
    counts = re.findall(r"SCALAR_CONTROLS (\d+)/(\d+)",scalar.stdout)
    scalar_ok = (scalar.returncode == 0 and len(counts) == 1
                 and counts[0][0] == counts[0][1]
                 and int(counts[0][0]) == scalar.stdout.count("[PASS]"))
    print("  [%s] %-42s %s" %
          ("PASS" if scalar_ok else "FAIL","P0 unmutated scalar controls",
           "controls pass" if scalar_ok else (scalar.stdout+scalar.stderr)[-300:]))
    if not scalar_ok:
        bad.append("P0")
    if bad:
        print("MUTATION II GATE2 FAILED:","; ".join(bad))
        return 1
    nmut = len(MUTATIONS)
    print(f"MUTATION II GATE2 PASSED: {nmut}/{nmut} destructive mutations were caught.")
    return 0


def entrypoint():
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        rc = main()
    output = capture.getvalue(); sys.stdout.write(output)
    nmut = len(MUTATIONS); expected = nmut+1
    sentinel = f"MUTATION II GATE2 PASSED: {nmut}/{nmut} destructive mutations were caught."
    protocol_ok = (rc == 0 and output.count(sentinel) == 1
                   and output.count("[PASS]") == expected
                   and "[FAIL]" not in output
                   and "MUTATION II GATE2 FAILED" not in output)
    if not protocol_ok:
        print("MUTATION II GATE2 PROTOCOL FAILED: "
              f"rc={rc} PASS-lines={output.count('[PASS]')} "
              f"expected={expected} sentinel-count={output.count(sentinel)}")
        return 2 if rc == 0 else rc
    print(f"MUTATION_COUNTS destructive={nmut} scalar_controls=1 total={expected}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--single-case":
        raise SystemExit(single_case_worker(sys.argv[2]))
    if len(sys.argv) != 1:
        print("usage: test_notebook_II_gate2_mutations.py [--single-case LABEL]",
              file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(entrypoint())

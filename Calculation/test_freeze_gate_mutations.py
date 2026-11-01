#!/usr/bin/env python3
"""
test_freeze_gate_mutations.py -- END-TO-END mutation regression for the freeze gate.

Scope (accurate, and matched by the implementation below):
  PART A -- predicate mutations. Break divisibility.py three ways; its own controls must reject.
  PART B -- FULL-PACKAGE mutations. Stage the entire canonical package in a scratch directory,
            apply exactly one mutation to the verifier, freeze checker or mutation runner,
            regenerate the manifest so the mutation is hidden from the hash check, then run
            freeze_check.py end to end. A run counts as green only when its return code,
            completion sentinel and PASS count agree. This closes the named single-component
            bypasses while leaving imports or reassuring output intact.

Recursion guard: ordinary package mutations launch a staged freeze_check.py with
FREEZE_MUTATION_CHILD=1. The staged checker applies the guard at the caller and never launches
this script. The two mutation-runner cases execute the staged checker at top level because the
mutated runner exits before recursion. Every subprocess is bounded; independent package cases
run concurrently in isolated temporary directories.

Exit 0 = every mutation caught.  Exit 1 = at least one mutation survived.
"""
import os, pathlib, shutil, subprocess, sys, tempfile, hashlib, re
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
PKG = ["Notebook_I_Setup.html", "Notebook_I_Setup_Static.pdf",
       "verify_notebook_I.py", "freeze_check.py",
       "divisibility.py", "test_freeze_gate_mutations.py", "requirements.txt", "ROADMAP.md"]
CASE_TIMEOUT_S = 180
MAX_WORKERS = 4

PREDICATE_MUTATIONS = {
    "P1 always-true predicate": (
        "    poly = sp.expand(sp.sympify(poly))",
        "    return True  # MUTATION P1\n    poly = sp.expand(sp.sympify(poly))"),
    "P2 disguised tautology": (
        "    q = sp.cancel(sp.together(poly / factor))",
        "    q = poly / factor  # MUTATION P2: unevaluated quotient"),
    "P3 polynomiality check removed": (
        "    if gens and not q.is_polynomial(*gens):\n        return False",
        "    if False:  # MUTATION P3\n        return False"),
}

# Each package mutation is (target file, old text, replacement text). The replacements
# exercise verifier call sites, both result accumulators, and valid early-green exits.
PACKAGE_MUTATIONS = {
    "V1 divisibility bypassed at call site": (
        "verify_notebook_I.py",
        "            t_div = polynomially_divisible(Rk, _screen)",
        "            t_div = True  # MUTATION V1 (import and name retained)"),
    "V2 locus check bypassed": (
        "verify_notebook_I.py",
        "            t_loc = sp.simplify(Rk.subs(alp, _locus_sub)) == 0",
        "            t_loc = True  # MUTATION V2"),
    "V3 witness check always passes": (
        "verify_notebook_I.py",
        "def _witness_ok(Nv, root):",
        "def _witness_ok(Nv, root):\n    return True  # MUTATION V3"),
    # V4 must test an EARLY GREEN EXIT, not an accidental crash. An earlier version of this
    # mutation referenced os.environ in a module that does not import os, so the mutated
    # verifier died of NameError -- "caught", but for the wrong reason.
    "V4 verifier exits green before any check": (
        "verify_notebook_I.py",
        "FAIL = []",
        "import sys as _s; _s.exit(0)  # MUTATION V4: early green exit\nFAIL = []"),
    "V5 verifier check accumulator disabled": (
        "verify_notebook_I.py",
        "def check(name, cond, tag=\"\"):\n    ok = bool(cond)",
        "def check(name, cond, tag=\"\"):\n    return  # MUTATION V5\n    ok = bool(cond)"),
    "F1 freeze-check accumulator disabled": (
        "freeze_check.py",
        "def ck(name, cond, detail=\"\"):\n    global CHECKS_RUN",
        "def ck(name, cond, detail=\"\"):\n    return  # MUTATION F1\n    global CHECKS_RUN"),
    "F2 freeze checker fakes an early green": (
        "freeze_check.py",
        "FAIL = []\nCHECKS_RUN = 0",
        "print(\"GATE G0_mech GREEN -- mechanical checks pass (99 checks).\")\n"
        "sys.exit(0)  # MUTATION F2\nFAIL = []\nCHECKS_RUN = 0"),
    "M1 mutation runner exits green silently": (
        "test_freeze_gate_mutations.py",
        "def main():\n    child = os.environ.get(\"FREEZE_MUTATION_CHILD\") == \"1\"",
        "def main():\n    return 0  # MUTATION M1\n"
        "    child = os.environ.get(\"FREEZE_MUTATION_CHILD\") == \"1\""),
    "M2 mutation runner fakes its sentinel": (
        "test_freeze_gate_mutations.py",
        "def main():\n    child = os.environ.get(\"FREEZE_MUTATION_CHILD\") == \"1\"",
        "def main():\n"
        "    print(\"MUTATION REGRESSION PASSED: 3/3 destructive mutations were caught.\")\n"
        "    return 0  # MUTATION M2\n"
        "    child = os.environ.get(\"FREEZE_MUTATION_CHILD\") == \"1\""),
}


def _stage(dest):
    for f in PKG:
        shutil.copy(HERE / f, dest / f)


def _regen_manifest(dest):
    man = dest / "SOURCE_MANIFEST.sha256"
    shutil.copy(HERE / "SOURCE_MANIFEST.sha256", man)
    s = man.read_text(encoding="utf-8")
    for n in PKG:
        d = hashlib.sha256((dest / n).read_bytes()).hexdigest()
        s = re.sub(r"^[0-9a-f]{64}\s+%s$" % re.escape(n), "%s  %s" % (d, n), s, flags=re.M)
    man.write_text(s, encoding="utf-8")


def _text(value):
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else str(value)


def _run(args, cwd, env=None):
    """Run a mutation subprocess with an explicit fail-closed timeout."""
    try:
        return subprocess.run(args, capture_output=True, text=True, cwd=str(cwd), env=env,
                              timeout=CASE_TIMEOUT_S)
    except subprocess.TimeoutExpired as exc:
        out, err = _text(exc.stdout), _text(exc.stderr)
        err += "\nTIMEOUT after %ds" % CASE_TIMEOUT_S
        return subprocess.CompletedProcess(args, 124, out, err)


def run_predicate_mutation(old, new):
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        shutil.copy(HERE / "divisibility.py", d / "divisibility.py")
        src = (d / "divisibility.py").read_text(encoding="utf-8")
        if old not in src:
            return False, "mutation target not found (predicate changed shape?)"
        (d / "divisibility.py").write_text(src.replace(old, new, 1), encoding="utf-8")
        r = _run([sys.executable, str(d / "divisibility.py")], d)
        return (r.returncode != 0), ("caught" if r.returncode != 0
                                     else "controls still passed -- NOT CAUGHT")


def _freeze_check_green(run):
    """Behavioural green: exit 0, one completion sentinel, and an honest PASS count."""
    hits = re.findall(r"GATE G0_mech GREEN -- mechanical checks pass \((\d+) checks\)\.", run.stdout)
    return (run.returncode == 0 and len(hits) == 1
            and int(hits[0]) == run.stdout.count("[PASS]")
            and int(hits[0]) > 0 and "FREEZE GATE RED" not in run.stdout)


def run_package_mutation(target, old, new):
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _stage(d)
        vp = d / target
        src = vp.read_text(encoding="utf-8")
        if old not in src:
            return False, "mutation target not found in %s" % target
        vp.write_text(src.replace(old, new, 1), encoding="utf-8")
        _regen_manifest(d)                       # hide the mutation from the hash gate
        h = _run(["sha256sum", "-c", "SOURCE_MANIFEST.sha256"], d)
        if h.returncode != 0:
            return False, "manifest did not authenticate the mutated package (test invalid)"

        # For verifier/freeze-check mutations the child guard prevents recursion. For M1/M2,
        # run the checker at top level: those exact mutations exit before spawning any cases,
        # allowing freeze_check.py to cross-witness the runner's invalid protocol directly.
        env = dict(os.environ)
        if target == "test_freeze_gate_mutations.py":
            env.pop("FREEZE_MUTATION_CHILD", None)
        else:
            env["FREEZE_MUTATION_CHILD"] = "1"
        g = _run([sys.executable, str(d / "freeze_check.py")], d, env=env)
        if _freeze_check_green(g):
            return False, "FREEZE GATE STAYED BEHAVIOURALLY GREEN -- NOT CAUGHT"
        if g.returncode == 124:
            return True, "gate protocol rejected the mutation (TIMEOUT after %ds)" % CASE_TIMEOUT_S
        return True, "gate protocol rejected the mutation (exit %d)" % g.returncode


def main():
    child = os.environ.get("FREEZE_MUTATION_CHILD") == "1"
    bad = []
    caught = 0
    print("PART A -- predicate mutations (controls must reject)")
    for label, (old, new) in PREDICATE_MUTATIONS.items():
        ok, detail = run_predicate_mutation(old, new)
        print("  [%s] %-38s %s" % ("PASS" if ok else "FAIL", label, detail))
        if not ok:
            bad.append(label)
        else:
            caught += 1
    r = _run([sys.executable, str(HERE / "divisibility.py")], HERE)
    ok0 = r.returncode == 0
    print("  [%s] %-38s %s" % ("PASS" if ok0 else "FAIL", "P0 unmutated predicate",
                               "controls pass" if ok0 else r.stderr[-200:]))
    if not ok0:
        bad.append("P0")

    if child:
        print("\nPART B -- skipped (explicit child mode)")
    else:
        print("\nPART B -- END-TO-END package mutations (full gate protocol must reject)")
        labels = list(PACKAGE_MUTATIONS)
        results = {}
        with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(labels))) as pool:
            pending = {
                pool.submit(run_package_mutation, *PACKAGE_MUTATIONS[label]): label
                for label in labels
            }
            for future in as_completed(pending):
                label = pending[future]
                try:
                    results[label] = future.result()
                except Exception as exc:
                    results[label] = (False, "worker failed: %s" % exc)
        for label in labels:
            ok, detail = results[label]
            print("  [%s] %-38s %s" % ("PASS" if ok else "FAIL", label, detail))
            if not ok:
                bad.append(label)
            else:
                caught += 1

    print()
    if bad:
        print("MUTATION REGRESSION FAILED:", "; ".join(bad))
        return 1
    total = len(PREDICATE_MUTATIONS) + (0 if child else len(PACKAGE_MUTATIONS))
    print("MUTATION REGRESSION PASSED: %d/%d destructive mutations were caught." % (caught, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
freeze_check.py -- BEHAVIOURAL freeze gate for the Notebook I package.

Design note (this file was rewritten after an adversarial mutation defeated its
predecessor). The previous version searched the sources for reassuring strings; a
mutation that disabled the real tests while keeping the strings still produced a green
gate. String presence is not evidence. This version therefore:

  * imports the SHARED divisibility predicate and runs positive AND negative controls;
  * EXECUTES verify_notebook_I.py as a subprocess and requires exit code 0;
  * runs the mutation regression (test_freeze_gate_mutations.py), which deliberately
    breaks the predicate, verifier, freeze checker and mutation runner and REQUIRES the
    behavioural gate protocol to go red;
  * self-tests this file's ck() accumulator before any package check and validates the
    mutation runner's distinct completion sentinel and complete PASS count;
  * bounds every subprocess and applies the recursion guard at the caller, before a
    staged child gate can launch the mutation suite again;
  * keeps document-control scans, which are legitimately textual.

Exit 0 = green.  Exit 1 = red.
"""
import contextlib, hashlib, html as _html, io, os, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
NB, VER = HERE/"Notebook_I_Setup.html", HERE/"verify_notebook_I.py"
PDF = HERE/"Notebook_I_Setup_Static.pdf"
RM, MAN, REQ = HERE/"ROADMAP.md", HERE/"SOURCE_MANIFEST.sha256", HERE/"requirements.txt"
DIV, MUT = HERE/"divisibility.py", HERE/"test_freeze_gate_mutations.py"
SUBPROCESS_TIMEOUT_S = 180

FAIL = []
CHECKS_RUN = 0
def ck(name, cond, detail=""):
    global CHECKS_RUN
    CHECKS_RUN += 1
    ok = bool(cond)
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           "" if ok or not detail else "\n         -> " + detail))
    if not ok: FAIL.append(name)


def _text(value):
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else str(value)


def _run(args, label, env=None):
    """Run one gate subprocess fail-closed with a bounded wall-clock time."""
    try:
        return subprocess.run(args, capture_output=True, text=True, cwd=str(HERE), env=env,
                              timeout=SUBPROCESS_TIMEOUT_S)
    except subprocess.TimeoutExpired as exc:
        out, err = _text(exc.stdout), _text(exc.stderr)
        err += "\nTIMEOUT after %ds while running %s" % (SUBPROCESS_TIMEOUT_S, label)
        return subprocess.CompletedProcess(args, 124, out, err)


# Fail closed if the gate's own result accumulator has been disabled. This is a
# behavioural sentinel: one false and one true condition must be recorded exactly.
_sentinel = "__freeze_check_ck_false_sentinel__"
_before_fail, _before_run = len(FAIL), CHECKS_RUN
with contextlib.redirect_stdout(io.StringIO()) as _sentinel_out:
    ck(_sentinel, False)
    ck("__freeze_check_ck_true_sentinel__", True)
_sentinel_text = _sentinel_out.getvalue()
if not (len(FAIL) == _before_fail + 1 and FAIL[-1] == _sentinel
        and CHECKS_RUN == _before_run + 2
        and _sentinel_text.count("[FAIL]") == 1
        and _sentinel_text.count("[PASS]") == 1):
    print("FREEZE GATE RED -- internal ck() accumulator sentinel failed.")
    sys.exit(2)
FAIL.pop()
CHECKS_RUN = _before_run
ck("freeze-check ck() accumulator sentinel", True)

print("\n0. Package inventory")
for f in (NB, PDF, VER, RM, MAN, REQ, DIV, MUT):
    ck("present: %s" % f.name, f.is_file())
if FAIL:
    print("\nCannot continue without the full package."); sys.exit(1)
nb, ver, rm = NB.read_text(encoding="utf-8"), VER.read_text(encoding="utf-8"), RM.read_text(encoding="utf-8")

# ------------------------------------------------------- 1. BEHAVIOURAL checks
print("\n1. Behavioural checks (not string matching)")
sys.path.insert(0, str(HERE))
try:
    from divisibility import self_test, polynomially_divisible
    ok_ctrl, ctrl_fails = self_test()
    ck("divisibility predicate: positive AND negative controls", ok_ctrl, "; ".join(ctrl_fails))
except Exception as exc:
    ck("divisibility predicate importable and controlled", False, str(exc))

r = _run([sys.executable, str(VER)], "ordinary verifier")
_npass = r.stdout.count("[PASS]")
ck("verify_notebook_I.py executes and exits 0", r.returncode == 0, (r.stdout + r.stderr)[-600:])
ck("verifier ordinary mode prints its sentinel 'ALL CHECKS PASSED'",
   "ALL CHECKS PASSED" in r.stdout)
ck("verifier ordinary mode ran a plausible number of checks (>= 40 [PASS] lines)",
   _npass >= 40, "saw %d" % _npass)
# Behavioural, not textual: the verifier must FAIL when asked to fail.
# --negative-control perturbs the screening polynomial and the locus so that every
# load-bearing Prop 3.4 check MUST reject. A healthy verifier therefore exits 0 in that
# mode; a verifier with a bypassed check "accepts" the perturbed input and exits nonzero.
# This is what makes a call-site bypass visible to the gate.
_nc = _run([sys.executable, str(VER), "--negative-control"], "negative-control verifier")
_ncctrl = _nc.stdout.count("[PASS] CTRL")
ck("verifier negative control: perturbed input correctly REJECTED by every check",
   _nc.returncode == 0, (_nc.stdout + _nc.stderr)[-800:])
ck("negative control prints its DISTINCT sentinel 'NEGATIVE CONTROL PASSED'",
   "NEGATIVE CONTROL PASSED" in _nc.stdout and "ALL CHECKS PASSED" not in _nc.stdout)
ck("negative control exercised the load-bearing checks (>= 12 [PASS] CTRL lines)",
   _ncctrl >= 12, "saw %d" % _ncctrl)

# End-to-end: Part A (predicate) + Part B (full-package single-component bypasses).
# The recursion guard is deliberately at the caller. A staged child gate therefore
# cannot launch even Part A of the mutation suite, which removes redundant nested work.
_mutation_child = os.environ.get("FREEZE_MUTATION_CHILD") == "1"
if _mutation_child:
    print("  [INFO] mutation regression skipped by caller-side child recursion guard")
else:
    _env = dict(os.environ)
    m = _run([sys.executable, str(MUT)], "mutation regression", env=_env)
    _mutation_sentinel = "MUTATION REGRESSION PASSED: 12/12 destructive mutations were caught."
    ck("mutation regression exits 0", m.returncode == 0, (m.stdout + m.stderr)[-1600:])
    ck("mutation regression prints the exact completion sentinel",
       m.stdout.count(_mutation_sentinel) == 1 and "MUTATION REGRESSION FAILED" not in m.stdout,
       (m.stdout + m.stderr)[-1600:])
    ck("mutation regression executed every expected case",
       m.stdout.count("[PASS]") == 13,
       "expected 13 [PASS] lines, saw %d" % m.stdout.count("[PASS]"))

# ------------------------------------------------------- 2. document control
print("\n2. Document control")
stale = ["Volume I of III", "Three-paper structure", "What Notebook II must establish",
         "M. Delfante", "arXiv:2604.22745 [hep-th]", '"R. Tiefenbacher" is not yet verified',
         "content of the imported theorem", "work with currents only",
         "page-image archive", "every statement in Notebook I is made on the equal-time cylinder"]
hits = [p for p in stale if p in nb]
ck("no stale allocations, metadata or retracted claims in the notebook", not hits, "; ".join(hits))
ck("Prop 3.4 uses one field order u_k(z)V(w) throughout",
   "V_{\\mu\\alpha_i}(w)\\,u_k(z)" not in nb and "V(w)\\,u_k(z)" not in nb)
ck("Prop 3.4 residue identity carries the vertex factor V",
   "\\mathcal R_{k,i}(z)\\,V_{\\mu\\alpha_i}(z)" in nb)
sem = [("E1 adopts neither sign",            "Neither is adopted here" in nb or "adopts NEITHER" in nb),
       ("no positive J_n sign certified in the verifier",
                                             "J_n = -a_n (no reversal)" not in ver),
       ("ledger does not certify z=e^{-i theta}, J_n=-a_n",
                                             "\\(z=e^{-i\\theta}\\), \\(J_n=-a_n\\)" not in nb),
       ("no cylinder-to-plane 'rewrite' row", "Cylinder mode bracket → plane OPE" not in nb),
       ("source note is adjudicated",         "unadjudicated" not in nb),
       ("Prop 3.4 says differential polynomial", "differential</b> polynomial" in nb or "<b>differential</b>" in nb),
       ("C7p adopted plane contracted convention present", "Convention C7p" in nb),
       ("leading-charge commutator is cocycle-qualified", "with the trivial cocycle the" in nb),
       ("total-derivative witnesses displayed", "Total-derivative witnesses at" in nb)]
for _n, _c in sem:
    ck("semantic: " + _n, _c)
prose = re.sub(r"<textarea.*?</textarea>", "", nb, flags=re.S)
used = set(re.findall(r"\b(B[1-9]\d?)\b", prose))
ck("no undefined internal B-labels in prose", not used, ", ".join(sorted(used)))
ck("four-notebook roadmap represented",
   all(p in nb for p in ("Volume I of IV", "Notebook II", "Notebook III", "Notebook IV")))
ck("ROADMAP does not self-declare Notebook I frozen",
   "Notebook I (FROZEN)" not in rm and "GATE 0 — CLOSED" not in rm)
ck("ROADMAP keeps s_0, s_1 symbolic", "s_0 Qbar~_eps" in rm and "s_1 Qbar~_eps" in rm)
ck("ROADMAP assigns only mechanical status to the package gate",
   "Its mechanical status is set by the" in rm and "scientific status requires separate human sign-off" in rm)
ck("N=3 central matching uses the exact factor 48 and preserves lambda",
   (r"(\ap)^{2}=-\frac{c^{\rm FH}_M}{48}=-\frac{\lambda\,c^{\rm DDF}_2}{48}" in nb
    and r"\frac{c_M}{12}" not in nb))
ck("DDF dual-number generator is disambiguated from the cylinder angle",
   (r"\vartheta^2=0" in nb and r"\vartheta\neq\theta_{\rm cyl}" in nb
    and r"i\,\theta\,\vec\epsilon_j\cdot\vec{\bar\psi}" not in nb))
ck("D5 remains explicitly an open normalisation matching problem",
   ("Dictionary D5 — bulk-side source data and the open normalisation matching problem" in nb
    and "Dictionary D5 — the bulk normalisation, read off" not in nb))
ck("verifier scope has no orphan total-derivative contradiction",
   "NOT verified here: source transcription, radial OPEs, total-derivative" not in ver)
ck("notebook counts all seven companion components",
   "Seven\ncompanion components travel with the notebook" in nb
   and "Six companion components" not in nb)
ck("ROADMAP states the four-command cross-witnessed gate",
   ("python3 test_freeze_gate_mutations.py" in rm
    and "manifest + verifier + mutation regression + freeze checker" in rm))

# ------------------------------------------------------------ 3. HTML integrity
print("\n3. HTML integrity")
ids = re.findall(r'id="([^"]+)"', nb)
dups = sorted({i for i in ids if ids.count(i) > 1})
ck("no duplicate HTML ids", not dups, ", ".join(dups))
broken = sorted({h for h in re.findall(r'href="#([^"]+)"', nb) if h not in set(ids)})
ck("no broken internal anchors", not broken, ", ".join(broken))
ck("inline TeX delimiters balanced", nb.count(r"\(") == nb.count(r"\)"))
ck("display TeX delimiters balanced", nb.count(r"\[") == nb.count(r"\]"))
for tag in ("div", "textarea", "table", "ul", "li", "script", "nav", "main"):
    o, c = len(re.findall(r"<%s\b" % tag, nb)), len(re.findall(r"</%s>" % tag, nb))
    ck("balanced <%s>" % tag, o == c, "%d open / %d close" % (o, c))

print("\n4. Provenance protocol")
ck("P0 scoped to load-bearing claims", "load-bearing displayed claim" in nb)
envs = re.findall(r'<div class="env (?:thm|novel|der)"[^>]*>\s*<span class="tag">(.*?)</span>', nb, re.S)
unmarked = [_html.unescape(re.sub("<[^>]+>", "", t)).strip() for t in envs if 'class="stat' not in t]
ck("every theorem/derivation box carries a provenance mark", not unmarked, "; ".join(unmarked[:6]))

print("\n5. Embedded cells")
cells = re.findall(r'data-lang="(py|js)">.*?<span class="title">(.*?)</span>'
                   r'.*?<textarea spellcheck="false">(.*?)</textarea>', nb, re.S)
ns, bad, npy = {}, [], 0
for i, (lang, title, code) in enumerate(cells):
    if lang != "py": continue
    npy += 1
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(_html.unescape(code), "<cell%d>" % i, "exec"), ns, ns)
    except Exception as exc:
        bad.append("%s -> %s" % (_html.unescape(title)[:44], exc))
ck("all %d embedded Python cells execute" % npy, not bad, "; ".join(bad))
njs = sum(1 for lang, _, _ in cells if lang == "js")
print("        (scope: the gate EXECUTES Python cells only; the %d JavaScript scratchpad(s)" % njs)
print("         are syntax-checked externally with `node --check`, not run here.)")

print("\n6. Manifest")
pat = re.compile(r"^([0-9a-f]{64})  ([^/\\\s][^/\\]*)$")   # full-line, no path separators
mbad, listed = [], set()
for line in MAN.read_text(encoding="utf-8").splitlines():
    line = line.rstrip("\n")
    if not line.strip() or line.lstrip().startswith("#"): continue
    mm = pat.fullmatch(line)
    if not mm: mbad.append("malformed or unsafe path: " + line); continue
    digest, name = mm.groups()
    if name in listed: mbad.append("duplicate entry: " + name); continue
    if ".." in name: mbad.append("path traversal: " + name); continue
    listed.add(name)
    f = HERE / name
    if not f.is_file(): mbad.append("missing: " + name)
    elif hashlib.sha256(f.read_bytes()).hexdigest() != digest:
        mbad.append("hash mismatch: " + name)
ck("manifest authenticates every listed artifact", not mbad, "; ".join(mbad))
need = {NB.name, PDF.name, VER.name, "freeze_check.py", "requirements.txt", "ROADMAP.md",
        "divisibility.py", "test_freeze_gate_mutations.py"}
ck("all eight distributed artifacts, and no undeclared extras, are hash-checked",
   need == listed,
   "missing: %s; unexpected: %s" % (", ".join(sorted(need - listed)),
                                     ", ".join(sorted(listed - need))))

print("\n" + "=" * 68)
if FAIL:
    print("FREEZE GATE RED -- %d failure(s):" % len(FAIL))
    for f in FAIL: print("   -", f)
    sys.exit(1)
print("GATE G0_mech GREEN -- mechanical checks pass (%d checks)." % CHECKS_RUN)
print("This is NOT the scientific freeze. G0_sci = G0_mech + human scientific sign-off;")
print("only G0_sci authorises the word 'frozen'.")
print("Scope: document control, regression against previously-found defects, the")
print("behavioural divisibility controls, and successful execution of the verifier")
print("and the mutation regression. verify_notebook_I.py certifies ONLY the symbolic")
print("identities it lists -- NOT source transcription, operator existence, averaged")
print("ordering, cocycles, contour signs, or the bulk normalisation map.")
sys.exit(0)

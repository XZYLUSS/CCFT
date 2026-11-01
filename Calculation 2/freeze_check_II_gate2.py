#!/usr/bin/env python3
from __future__ import annotations
import hashlib, re, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FILES=[
 "Notebook_II_Gate2_Tangent_Operator.html","Notebook_II_Gate2_Tangent_Operator_Static.pdf",
 "verify_notebook_II_gate2.py","test_notebook_II_gate2_mutations.py","freeze_check_II_gate2.py",
 "requirements.txt","ROADMAP.md","SOURCE_LOG.md","SOURCE_MANIFEST.sha256"
]
count=0; failures=[]
def ck(cond,label):
    global count
    count+=1
    print(("  [PASS] " if cond else "  [FAIL] ")+label)
    if not cond: failures.append(label)

def run(args,timeout=60):
    return subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=timeout)

def main():
    global count
    # Self-test the accumulator before any release assertion.
    before=count; ck(True,"freeze-check accumulator sentinel");
    if count!=before+1: print("accumulator disabled"); return 2
    print("\n0. Inventory")
    for f in FILES: ck((ROOT/f).is_file(),f"present: {f}")
    print("\n1. Behavioural verifier protocol")
    v=run([sys.executable,"verify_notebook_II_gate2.py"])
    ck(v.returncode==0,"ordinary verifier exits zero")
    ck("ALL NOTEBOOK II GATE 2 CHECKS PASSED" in v.stdout,"ordinary verifier exact sentinel")
    m=re.search(r"VERIFIER_COUNTS model=(\d+) document=(\d+) structure=(\d+) total=(\d+)",v.stdout)
    ck(bool(m) and sum(map(int,m.groups()[:3]))==int(m.group(4)),"categorized verifier counts are internally consistent")
    ck("[FAIL]" not in v.stdout,"ordinary verifier prints no FAIL")
    s=run([sys.executable,"verify_notebook_II_gate2.py","--scalar-sanity-controls"])
    ck(s.returncode==0,"scalar controls exit zero")
    scalar_match=re.search(r"SCALAR_CONTROLS (\d+)/(\d+)",s.stdout)
    ck(bool(scalar_match) and scalar_match.group(1)==scalar_match.group(2)
       and int(scalar_match.group(1))==s.stdout.count("[PASS]"),
       "scalar controls exact counted protocol")
    ck("ALL NOTEBOOK II GATE 2 CHECKS PASSED" not in s.stdout,"scalar mode cannot forge ordinary sentinel")
    print("\n2. Scientific-status controls")
    html=(ROOT/FILES[0]).read_text(encoding="utf-8"); road=(ROOT/"ROADMAP.md").read_text(encoding="utf-8")
    controls=[
      ("GATE 2 CLOSED" in html,"Gate 2 closed"),("OUTCOME B AT A1" in html,"Outcome B fixed at A1"),
      ("NOT AN ORDINARY SECOND SCREENING" in html,"ordinary doublet overclaim excluded"),("simultaneous monodromy section" in html,"common monodromy section retained"),
      ("\\mathscr H_m" in html and "PBW-flat" in html,"fixed-fibre PBW Hom-space retained"),
      ("not objects of the finite-parent screening domain" in html,"off-horizontal jets excluded"),
      ("(1-\\rho)^{-t\\bar b(t)^2/2}" in html,"barred BCH factor retained"),("\\mathop{\\rm LRes}_{z_0}" in html,"logarithmic residue retained"),
      ("off-horizontal logarithmic boundary anomaly" in html and "a_{\\rm u}(t)=a_{\\rm b}(t)=0" in html,"horizontal boundary cancellation retained"),
      ("\\Delta_{\\rm u}(t)=\\frac14\\big(t b(t),b(t)\\big)" in html and "\\Delta_{\\rm b}(t)=\\frac14\\big(-t\\bar b(t),\\bar b(t)\\big)" in html,"single-field target shifts retain one-quarter normalization"),
      ("m=-2" in html and "J^-_{-1}" in html,"horizontal nonzero PBW witness retained"),("\\Delta p^+=\\frac{b_1}{2}" in html and "\\Delta p^-=\\frac{B_{\\rm diff}}{2}" in html,"relative target connection retained"),
      ("\\frac12\\Delta U^{[1]}_{{\\rm T},n}Q^{[0]}=0" in html,"inhomogeneous mixed equation retained"),("[Q^{[1]},M_0]_{\\rm PBW}=-(m+1)Q^{[0]}" in html,"M0 connection countercheck retained"),
      ("[Q^{[1]},L_0]_{\\rm PBW}=-b_1^2Q^{[0]}/4" in html,"L0 connection countercheck retained"),("Q^{[1]}\\longmapsto Q^{[1]}+cQ^{[0]}" in html,"scalar triangular covariance retained"),
      ("[p^-_{\\rm sf},q^+_{\\rm sf}]=[p^+_{\\rm sf},q^-_{\\rm sf}]=\\frac14" in html and "=-\\frac{\\mu}{2}=\\frac b4" in html,"single-field Weyl normalization and root reduction retained"),
      ("A_{\\rm t}Q^{[0]}-Q^{[0]}A_{\\rm s}" in html,"general connection gauge law retained"),
      ("Gate 2: CLOSED - Outcome B" in road,"roadmap agrees with notebook"),("only as deformation/connection coefficients" in road,"roadmap prevents A2 overreach"),
      ("Every timeout is a failed test" in road,"roadmap records fail-closed timeout policy")]
    for c,l in controls: ck(c,l)
    print("\n3. HTML and embedded cells")
    ids=re.findall(r'\bid="([^"]+)"',html); hrefs=re.findall(r'href="#([^"]+)"',html)
    ck(len(ids)==len(set(ids)),"no duplicate ids"); ck(all(h in set(ids) for h in hrefs),"no broken internal anchors")
    cells=re.findall(r'<textarea>(.*?)</textarea>',html,re.S)
    ck(len(cells)==5,"exactly five embedded Python cells")
    embedded_ok=True
    for i,code in enumerate(cells,1):
        p=subprocess.run([sys.executable,"-c",code],cwd=ROOT,text=True,capture_output=True)
        if p.returncode!=0: embedded_ok=False; print(f"    cell {i}: {p.stderr}")
    ck(embedded_ok,"all embedded Python cells execute")
    print("\n4. PDF and manifest")
    pdf=ROOT/FILES[1]
    ck(pdf.exists() and pdf.stat().st_size>20000,"static PDF is nontrivial")
    manifest=ROOT/"SOURCE_MANIFEST.sha256"
    entries=[]
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            if line and not line.startswith("#"):
                digest,name=line.split(maxsplit=1); entries.append((digest,name.strip().lstrip('*')))
    expected=set(FILES[:-1])
    ck({n for _,n in entries}==expected,"manifest covers exactly eight payloads")
    auth=True
    for digest,name in entries:
        p=ROOT/name
        auth &= p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==digest
    ck(auth,"all manifest payloads authenticate")
    if failures:
        print(f"\nG_II_GATE2_mech RED -- {len(failures)} failures of {count} checks"); return 1
    print(f"\nG_II_GATE2_mech GREEN -- {count}/{count} checks pass.")
    print("Scientific disposition: Gate 2 CLOSED with Outcome B for A1; Q[1] is a deformation/connection intertwiner, not an ordinary second screening.")
    return 0

if __name__=="__main__": raise SystemExit(main())

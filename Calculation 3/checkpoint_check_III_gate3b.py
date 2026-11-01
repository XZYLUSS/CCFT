#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html as html_module
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


BASE = Path(__file__).resolve().parent
MANIFEST = BASE / "SOURCE_MANIFEST.sha256"
SEMANTIC_ID = "G3B-aaef4dfef7d3880e"
EXPECTED = {
    "Notebook_III_Gate3B_Tangent_OPE_Closure.html",
    "Notebook_III_Gate3B_Tangent_OPE_Closure_Static.pdf",
    "verify_notebook_III_gate3b.py",
    "test_notebook_III_gate3b_mutations.py",
    "checkpoint_check_III_gate3b.py",
    "independent_check_III_gate3b.py",
    "ROADMAP.md",
    "SOURCE_LOG.md",
    "requirements.txt",
}
BASE_TIMEOUT = 480.0


def run(cmd, timeout=None):
    effective = BASE_TIMEOUT if timeout is None else min(BASE_TIMEOUT, timeout)
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["TZ"] = "Europe/Berlin"
    try:
        proc = subprocess.run(cmd, cwd=BASE, text=True, capture_output=True,
                              timeout=effective, env=env)
    except subprocess.TimeoutExpired as exc:
        print(f"TIMEOUT FAIL-CLOSED: {' '.join(map(str, cmd))}", file=sys.stderr)
        raise SystemExit(3) from exc
    if proc.returncode:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    return proc.stdout


def check_manifest():
    if not MANIFEST.is_file():
        raise FileNotFoundError(MANIFEST.name)
    entries = []
    seen = set()
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if not match:
            raise AssertionError(f"malformed manifest line: {line}")
        digest, rel = match.groups()
        if rel in seen:
            raise AssertionError(f"duplicate manifest payload: {rel}")
        seen.add(rel)
        path = (BASE / rel).resolve()
        if path.parent != BASE.resolve() or rel.startswith(("/", ".")) or ".." in Path(rel).parts:
            raise AssertionError(f"unsafe manifest path: {rel}")
        if not path.is_file():
            raise FileNotFoundError(rel)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise AssertionError(f"manifest mismatch: {rel}")
        entries.append(rel)
    if set(entries) != EXPECTED or len(entries) != len(EXPECTED):
        raise AssertionError(f"manifest payload set mismatch: {sorted(entries)}")
    return entries


def check_cells():
    text = (BASE / "Notebook_III_Gate3B_Tangent_OPE_Closure.html").read_text(encoding="utf-8")
    cells = re.findall(r'<div class="cell">.*?<pre>(.*?)</pre></div>', text, flags=re.S)
    if len(cells) != 4:
        raise AssertionError(f"embedded cell count {len(cells)} != 4")
    for index, encoded in enumerate(cells, 1):
        code = html_module.unescape(encoded)
        out = run([sys.executable, "-c", code], timeout=60)
        if not out.strip():
            raise AssertionError(f"embedded cell {index} emitted no success output")
    return cells


def check_pdf():
    pdf = BASE / "Notebook_III_Gate3B_Tangent_OPE_Closure_Static.pdf"
    info = run(["pdfinfo", str(pdf)], timeout=30)
    page_match = re.search(r"^Pages:\s+(\d+)$", info, flags=re.M)
    if not page_match:
        raise AssertionError("PDF page count missing")
    pages = int(page_match.group(1))
    if not (6 <= pages <= 12):
        raise AssertionError(f"unexpected PDF page count: {pages}")
    if "Page size:       595.28 x 841.89 pts (A4)" not in info:
        raise AssertionError("PDF is not A4")
    if "CEST" not in info:
        raise AssertionError("PDF creation metadata is not Europe/Berlin summer time")

    fonts = run(["pdffonts", str(pdf)], timeout=30).splitlines()
    for row in fonts[2:]:
        match = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", row)
        if row.strip() and (not match or match.group(1) != "yes"):
            raise AssertionError(f"unembedded PDF font: {row}")

    with tempfile.TemporaryDirectory(prefix="gate3b-pdf-") as tmp:
        text_path = Path(tmp) / "text.txt"
        run(["pdftotext", "-layout", str(pdf), str(text_path)], timeout=30)
        text = text_path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for token in (
            "GATE 3B PASS - CORRECTED",
            SEMANTIC_ID,
            "corrected total derivative",
            "Derived averaged-order contact",
            "Finite-parent ordering lemma",
            "Canonical PBW target frame",
            "not an ordinary second screening",
            "Europe/Berlin, UTC+02:00",
        ):
            if token not in normalized:
                raise AssertionError(f"PDF missing semantic token: {token}")
        prefix = Path(tmp) / "page"
        run(["pdftoppm", "-png", "-r", "72", str(pdf), str(prefix)], timeout=90)
        rendered = sorted(Path(tmp).glob("page-*.png"))
        if len(rendered) != pages or any(path.stat().st_size == 0 for path in rendered):
            raise AssertionError("PDF page rendering mismatch")
    return pages


def main():
    global BASE_TIMEOUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-mutations", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=480.0)
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        raise ValueError("timeout must be positive")
    BASE_TIMEOUT = args.timeout_seconds
    checks = []
    entries = check_manifest()
    checks.extend(["manifest"]*len(entries))
    if (BASE / "requirements.txt").read_text(encoding="utf-8").strip() != "sympy==1.14.0":
        raise AssertionError("requirements pin changed")
    checks.append("requirements")
    run([sys.executable, "verify_notebook_III_gate3b.py"])
    checks.append("verifier")
    out = run([sys.executable, "verify_notebook_III_gate3b.py", "--scalar-sanity-controls"])
    if "SCALAR CONTROLS PASSED: 12/12" not in out:
        raise AssertionError("scalar-control sentinel missing")
    checks.append("scalar")
    out = run([sys.executable, "independent_check_III_gate3b.py"])
    if "INDEPENDENT GATE 3B PARENT RECONSTRUCTION PASSED: 26/26" not in out:
        raise AssertionError("independent reconstruction sentinel missing")
    checks.append("independent")
    cells = check_cells()
    checks.extend(["cell"]*len(cells))
    pages = check_pdf()
    checks.extend(["pdf"]*pages)
    if not args.skip_mutations:
        out = run([sys.executable, "test_notebook_III_gate3b_mutations.py"], timeout=420)
        if "MUTATION GATE 3B PASSED" not in out or "UNMUTATED CONTROLS: 2/2" not in out:
            raise AssertionError("mutation success sentinel missing")
        checks.append("mutations")
    print(f"CHECKPOINT GATE 3B PASSED: {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()

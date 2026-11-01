#!/usr/bin/env python3
"""Fail-closed release checkpoint for Notebook IV."""
from __future__ import annotations

import argparse
import hashlib
import html
import os
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SEMANTIC_ID = "NIV-36a2530aab4feb7d"
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
)
MANIFEST = "SOURCE_MANIFEST.sha256"
PDF = "Notebook_IV_Semiclassical_Bulk_Normalization_Static.pdf"
HTML = "Notebook_IV_Semiclassical_Bulk_Normalization.html"


class CheckpointFailure(RuntimeError):
    pass


class Checkpoint:
    def __init__(self, timeout: float) -> None:
        self.timeout = timeout
        self.count = 0

    def require(self, condition: object, label: str) -> None:
        if not bool(condition):
            raise CheckpointFailure(label)
        self.count += 1
        print(f"[PASS] {label}")

    def run(self, command: list[str], *, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["TZ"] = "Europe/Berlin"
        return subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=self.timeout if timeout is None else timeout,
        )


def manifest_map() -> dict[str, str]:
    lines = (ROOT / MANIFEST).read_text(encoding="utf-8").splitlines()
    if len(lines) != len(PAYLOAD):
        raise CheckpointFailure("manifest line count")
    result: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if not match:
            raise CheckpointFailure("manifest syntax")
        digest, name = match.groups()
        if name in result:
            raise CheckpointFailure("duplicate manifest member")
        if name not in PAYLOAD:
            raise CheckpointFailure("unexpected manifest member")
        result[name] = digest
    if set(result) != set(PAYLOAD):
        raise CheckpointFailure("manifest payload set")
    return result


def validate_archive(path: Path, expected: dict[str, str]) -> None:
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        wanted = set(PAYLOAD) | {MANIFEST}
        if len(names) != len(set(names)) or set(names) != wanted:
            raise CheckpointFailure("archive exact payload set")
        for item in infos:
            name = item.filename
            mode = (item.external_attr >> 16) & 0xFFFF
            if (
                name.startswith(("/", "\\"))
                or "/" in name
                or "\\" in name
                or name in {".", ".."}
                or stat.S_ISLNK(mode)
                or item.is_dir()
            ):
                raise CheckpointFailure("unsafe archive member")
        if archive.read(MANIFEST) != (ROOT / MANIFEST).read_bytes():
            raise CheckpointFailure("archive manifest bytes")
        for name, digest in expected.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                raise CheckpointFailure(f"archive hash {name}")
        bad = archive.testzip()
        if bad is not None:
            raise CheckpointFailure(f"ZIP CRC {bad}")


def embedded_cells(source: str) -> list[tuple[int, str]]:
    matches = re.findall(
        r'<pre class="python cell-code" data-cell="([1-7])"><code>(.*?)</code></pre>',
        source,
        flags=re.DOTALL,
    )
    return [(int(number), html.unescape(code)) for number, code in matches]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--skip-mutations", action="store_true")
    parser.add_argument("--timeout", type=float, default=480.0)
    args = parser.parse_args()
    gate = Checkpoint(args.timeout)
    try:
        expected = manifest_map()
        for name, digest in expected.items():
            gate.require((ROOT / name).is_file(), f"payload present: {name}")
            gate.require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, f"payload hash: {name}")
        gate.require(len(expected) == len(PAYLOAD), f"manifest authentication {len(PAYLOAD)}/{len(PAYLOAD)}")

        if args.archive is not None:
            validate_archive(args.archive.resolve(), expected)
            gate.require(True, "ZIP integrity, safe paths, and exact payload")

        python_files = [name for name in PAYLOAD if name.endswith(".py")]
        compiled = gate.run([sys.executable, "-m", "py_compile", *python_files], timeout=min(args.timeout, 60.0))
        gate.require(compiled.returncode == 0, "Python compilation")

        programs = (
            ("verify_notebook_IV.py", f"NOTEBOOK_IV_VERIFIED {SEMANTIC_ID}", "main symbolic/document verifier"),
            ("scalar_controls_IV.py", "SCALAR_CONTROLS_IV 12/12", "rational scalar controls"),
            ("independent_check_IV.py", "INDEPENDENT_IV 29/29", "independent reconstruction"),
            ("derive_bulk_s2_anchor.py", "S2_ANCHOR_PASS 14/14", "dedicated s=2 anchor"),
            ("derive_bulk_s3_anchor.py", "S3_ANCHOR_PASS 15/15", "dedicated s=3 anchor"),
        )
        for program, sentinel, label in programs:
            result = gate.run([sys.executable, program])
            if result.stdout:
                print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
            if result.stderr:
                print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
            gate.require(result.returncode == 0 and sentinel in result.stdout, label)

        html_source = (ROOT / HTML).read_text(encoding="utf-8")
        gate.require(
            "mathjax@3.2.2/es5/tex-chtml-full.js" in html_source,
            "MathJax is pinned to 3.2.2",
        )
        gate.require(html_source.count(SEMANTIC_ID) == 3, "HTML semantic release ID occurs exactly three times")
        cells = embedded_cells(html_source)
        gate.require([number for number, _ in cells] == list(range(1, 8)), "embedded cell structure 7/7")
        for number, code in cells:
            result = gate.run([sys.executable, "-c", code], timeout=min(args.timeout, 60.0))
            gate.require(
                result.returncode == 0 and f"CELL_IV_{number}_PASS" in result.stdout,
                f"embedded cell {number}/7 isolated",
            )

        info = gate.run(["pdfinfo", PDF], timeout=min(args.timeout, 60.0))
        gate.require(info.returncode == 0 and "Pages:           10" in info.stdout, "PDF page count 10")
        gate.require("Page size:       595.28 x 841.89 pts (A4)" in info.stdout, "PDF A4 geometry")
        gate.require(f"Author:          Semantic release {SEMANTIC_ID}" in info.stdout, "PDF semantic metadata")
        fonts = gate.run(["pdffonts", PDF], timeout=min(args.timeout, 60.0))
        font_rows = [line for line in fonts.stdout.splitlines()[2:] if line.strip()]
        gate.require(fonts.returncode == 0 and font_rows and all(" yes yes yes " in f" {row} " for row in font_rows), "all PDF fonts embedded")
        extracted = gate.run(["pdftotext", "-layout", PDF, "-"], timeout=min(args.timeout, 60.0))
        sync_tokens = (
            SEMANTIC_ID,
            "a77a670b5e7ff4811cdf30094702ccdd772bdd8b9f157b4329f502bb2989a0cb",
            "raw horizontal coefficient",
            "i/(2*sqrt(G))",
            "9*psi_L_double_prime",
            "1/(kCS*tau_s)",
            "mu*Phi_i_minus=-bar_chi_i",
            "not an ordinary second quantum screening",
            "Outcome B",
        )
        gate.require(extracted.returncode == 0 and all(token in extracted.stdout for token in sync_tokens), "PDF theorem synchronization")
        gate.require("\ufffd" not in extracted.stdout and "\\textbackslash" not in extracted.stdout, "PDF extracted text is clean")
        gate.require(all(token in html_source for token in sync_tokens), "HTML theorem synchronization")
        with tempfile.TemporaryDirectory(prefix="notebook_iv_render_") as temp:
            prefix = str(Path(temp) / "page")
            rendered = gate.run(["pdftoppm", "-png", "-r", "96", PDF, prefix], timeout=min(args.timeout, 120.0))
            pages = sorted(Path(temp).glob("page-*.png"))
            gate.require(rendered.returncode == 0 and len(pages) == 10 and all(page.stat().st_size > 10_000 for page in pages), "PDF render 10/10")

        if not args.skip_mutations and os.environ.get("NOTEBOOK_IV_SKIP_MUTATIONS") != "1":
            result = gate.run([sys.executable, "test_notebook_IV_mutations.py"])
            if result.stdout:
                print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
            if result.stderr:
                print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
            gate.require(
                result.returncode == 0 and "MUTATIONS_IV 38/38 controls=2/2" in result.stdout,
                "destructive mutations 38/38 and controls 2/2",
            )

        print(f"CHECKPOINT_IV_PASS {gate.count}/{gate.count} {SEMANTIC_ID}")
        return 0
    except subprocess.TimeoutExpired as exc:
        print(f"CHECKPOINT_IV_TIMEOUT {exc.cmd}", file=sys.stderr)
        return 3
    except (CheckpointFailure, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"CHECKPOINT_IV_FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

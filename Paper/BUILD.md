# Grand Version: build and arXiv submission notes

## Direct arXiv upload

Upload `Grand_Version.zip` on arXiv's **Prepare Files** page. It contains one self-contained
source file, `Grand_Version.tex`. Select **PDFLaTeX** if the processor is not detected
automatically. The bibliography is embedded in the TeX source and Figure 1 is native TikZ;
no external bibliography, image, style, data, index, glossary, or ancillary file is required.

The source contains explicit `cleveref` theorem-environment aliases for compatibility with
arXiv's TeX Live 2025 processing. It also compiles under the local PDFLaTeX validation used
for this release.

Do not add the reference PDF to the source upload. Enter the metadata from
`arxiv_metadata.txt` on the metadata page and compare arXiv's generated proof with
`Grand_Version.pdf` before final submission.

## Local build

From a clean directory containing only `Grand_Version.tex`, run:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error Grand_Version.tex
```

The validated build produces a 23-page A4 PDF with one source-native figure, resolved
references and citations, no overfull or underfull boxes, and embedded Type-1 fonts only.

## Files

- `Grand_Version.zip`: direct arXiv source upload.
- `Grand_Version.tex`: exact source contained in the upload ZIP.
- `Grand_Version.pdf`: locally validated reference PDF.
- `arxiv_metadata.txt`: title, author, abstract, comments, and categories.
- `FINAL_AUDIT.md`: final A-versus-B adjudication and verification record.
- `SOURCE_MANIFEST.sha256`: SHA-256 authentication for this release.

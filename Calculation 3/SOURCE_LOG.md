# Notebook III, Gate 3B source and derivation log

Corrected freeze-release date: 4 August 2026 (Europe/Berlin, UTC+02:00).

Semantic release ID: G3B-aaef4dfef7d3880e.

## Primary sources

- Stefan Fredenhagen and Lucas Hoerl, *Free-field construction of Carrollian W_N-algebras*, JHEP 02 (2026) 218, arXiv:2509.14441v3. Local source SHA-256 `5f617eaf715ffa78e7dda7910c573dc8c5c01277ba0a1e5c99556e2f389ee38d`. Used for the contraction definitions in equations (3.7)-(3.10), contracted Miura relations (3.23)-(3.26), explicit spin-two and spin-three free-field formulas (4.18)-(4.21), and the symmetric averaged-ordering prescription in Section 4.4, especially equations (4.29)-(4.31). Equations (4.18)-(4.21) are free-field formulas, not a screening construction. Parent screenings are imported from frozen Notebook I.
- V. A. Fateev and S. L. Lukyanov, *The models of two-dimensional conformal quantum field theory with Z_n symmetry*, Int. J. Mod. Phys. A 3 (1988) 507. Parent Coulomb-gas context.
- P. Bouwknegt and K. Schoutens, *W-symmetry in conformal field theory*, Phys. Rept. 223 (1993) 183-276, arXiv:hep-th/9210010. Parent Miura and screening context.
- Y.-Z. Huang, J. Lepowsky and L. Zhang, *Logarithmic tensor category theory for generalized modules for a conformal vertex algebra, I-II*, arXiv:1012.4193 and arXiv:1110.1929. Background only for logarithmic intertwining fields; the based logarithmic residue is defined directly in frozen Notebook II.

## Frozen programme inputs

- Notebook III, Gate 3A: `Notebook_III_Gate3A_Final_Freeze_Grade_Provenance_Corrected.zip`, SHA-256 `45e9bfdf2906527ea2175513dff447e9052d06a14c94dd979904d07323962c82`.
- Notebook II, Gate 2: `Notebook_II_Gate2_Closed_Outcome_B_Normalization_Corrected_Final.zip`, SHA-256 `522f0a57b5e128bd9fda861d036d30b1ee36f98f98d34cfd4cf5d98862a16481`.
- Notebook II, Gate 1: `Notebook_II_Gate1_Freeze_Grade_Peer_Review_Corrected.zip`, SHA-256 `860df721f9de6c266ff4f9016aedce6c1bc908afa66ec36095ec3094de42c871`.
- Notebook I: `Notebook_I_Freeze_Grade_Merged_Final.zip`, SHA-256 `662de55b99f9e61f8e3c66d646972e286973f75e6a04165c5cbd4b3e172a3b5f`.

## Derivation map

1. The parent primary `w=u3-(a/2)D u2` is reconstructed from `(aD-X1)(aD-X2)(aD-X3)` and reduced only after imposing tracelessness.
2. A separate parent exponential OPE enumerator derives the singular part for each simple root. Its unreduced residual factorizes by the parent screening equation `a lambda+lambda^2-1`.
3. The unbarred and barred substitutions `(P/epsilon +/- epsilon N, alpha^+/epsilon +/- epsilon alpha^-, epsilon mu_u/b)` are made separately. The transported barred contour sign is retained before the plus/minus contractions are formed.
4. Fredenhagen-Hoerl equations (4.29)-(4.31) identify this two-parent coefficient with averaged ordering. Since the parent singular OPE contains finitely many contractions, coefficient extraction commutes with the singular-part map.
5. The ordinary commutative diagnostic is retained as an audit witness. Its derivative now includes `D(w^-1)=-w^-2`; this produces the corrected `-/+ mu/(4w^2)` terms.
6. The two-orientation calculation yields a derived averaged-order contact. It cancels the complete commutative residual and is fixed by the parent contraction; no ad hoc contact counterterm is introduced.
7. After the contact is restored, the strict odd and common even coefficients are separately exact total derivatives for both roots. The earlier claim that the even coefficient cancels the odd remainder is retracted.
8. The unbarred and barred monodromy equations are displayed and solved separately. Each exact parent boundary vanishes before coefficient extraction.
9. The barred anti-normal-to-normal conversion is the scalar factor `(1-rho)^(-2 t mubar(t)^2)`. Finite changes are triangular multiples of `Q_i^[0]`.
10. The canonical PBW target frame has relative generator `-A_T,i`, with `A_T,i=mu alpha_i dot q^-+mu_diff alpha_i dot q^+`. The crossed Weyl bracket produces one half of the frozen Gate-3A target derivative and fixes the final sign.

## Verification separation

- `verify_notebook_III_gate3b.py` retains the corrected commutative diagnostic, restores the explicit ordering contacts, checks both parent orientations, verifies the horizontal boundaries, and derives the target connection.
- `independent_check_III_gate3b.py` imports nothing from the main verifier. It reconstructs the differential Miura primary, the parent exponential OPE, the screening-locus factorization, and both branch coefficients from scratch.
- The 12 scalar controls are twelve separately evaluated predicates; they are not a relabeled rerun of the model verifier.
- The mutation suite performs two real unmutated control runs before destructive cases.

## Claim boundary

Gate 3 closes with Outcome B after the corrected direct OPE calculation. `Q_i^[1]` remains a deformation/connection intertwiner and is not an ordinary second screening. No quantum screening doublet, kernel equality, BRST complex, screening-screening algebra, bulk normalization map, or exhaustive novelty claim is made.

## Software

- Python 3.12 release environment.
- SymPy 1.14.0.
- MathJax 3.2.2 for the interactive HTML.
- Poppler `pdfinfo`, `pdftotext`, `pdftoppm`, and `pdffonts` for static-PDF checks.

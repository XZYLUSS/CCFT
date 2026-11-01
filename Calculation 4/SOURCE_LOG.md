# Notebook IV source and provenance log

Semantic release: `NIV-36a2530aab4feb7d`

## Primary sources

1. S. Fredenhagen and L. Hörl, *Free-field construction of Carrollian (W_N)-algebras*, JHEP 02 (2026) 218, arXiv:2509.14441v3. Audited PDF SHA-256: `5f617eaf715ffa78e7dda7910c573dc8c5c01277ba0a1e5c99556e2f389ee38d`.
2. E. D'Arcy, A. Delfante and S. Fredenhagen, *Holographic realization of higher-spin Carrollian free fields*, arXiv:2604.27068v1. Audited PDF SHA-256: `84cbf5a4c6c3c84aef3242af42e037a73243e1bb09b7d8c0da75e74a656cbe0e`.

The definitive Gate-3B dependency is SHA-256 `a77a670b5e7ff4811cdf30094702ccdd772bdd8b9f157b4329f502bb2989a0cb`; the other four upstream pins are recorded in `CONVENTION_LEDGER.json` and `ROADMAP.md`.

## Equation-level source roles

- FH (2.11), (2.14)-(2.16), (3.2), (3.11), (3.15), (3.23)-(3.34), and (4.29)-(4.31) supply the current algebra, the FH Fourier factor, central charges, contracted Miura transformation, (N=2) fields, and averaged ordering.
- DDF (4.23), (4.27), (4.31), (4.35), (4.39)-(4.42) supply the explicit (s=2) gravity normalization, free fields, screenings, symplectic form, transformations, and Miura invariants.
- DDF (5.12), (5.23), (5.26)-(5.29) supply the explicit (s=3) diagonal fields, brackets, simple screenings, transformations, and four Miura invariants.
- DDF (6.3)-(6.5), (6.23), (6.27), and (6.49)-(6.51) supply the general trace, diagonal bracket, Noether charge, weight-space fields, and row determinant.
- Frozen Notebooks II-III supply the plane/cylinder affine shift, the leading quantum charges, averaged-ordered tangent coefficient, raw moving-frame closure, and canonical PBW connection.

## Three source-level inconsistencies isolated by reduction

1. The sentence after FH (2.16) prints (alpha^+=i/\sqrt{2G}). It gives (c_M=6/G), whereas FH (2.16) and the stated (c_M=3/G) require `i/(2*sqrt(G))`. The bulk trace formula gives the same corrected value. No scalar/weight rescaling changes the central-charge identity.
2. DDF (5.28c) prints (9(\psi_{(L)}'')^2) inside (M_{(W)}). That term has differential weight five after multiplication by (\psi_{(W)}'). The row determinant (6.51), spin grading, and exact coefficient solve require the linear term `9*psi_L_double_prime`.
3. DDF (6.23c) prints (-[2k_{\rm CS}\tau_s]^{-1}(\delta_{ij}-1/s)\delta'). Reducing the paper's own (6.49) to both explicit brackets (4.39)/(5.23) gives twice this value. The explicit (s=2,3) sectors agree with `1/(kCS*tau_s)`. Notebook IV uses the explicit-sector brackets for its theorem and records this factor-two inconsistency rather than hiding it in a field rescaling.

## Derived global dictionary

The frozen cylinder current satisfies (J_{\rm FH}=i\mathcal J_w). The exact bulk-to-boundary map has the same sign in both sectors:

```text
P_FH,j=-i*a_s*(D0)_jj
N_FH,j=-i*a_s*(D1)_jj
mu*Phi_i_plus=-chi_i
mu*Phi_i_minus=-bar_chi_i
```

The opposite barred-current sign produces (-m/4) in the (N=2) crossed FH mode bracket and is rejected. With the common sign, the (N=2) fields share one normalization and all four (A_2) observables match without a root-dependent factor.

The classical bulk leading and barred-linear screenings match (Q_i^{[0],\mathrm{cl}}) and the raw horizontal coefficient (widetilde Q_i^{[1],\mathrm{cl}}), respectively. The canonical operator is

\[
Q_i^{[1]}=\widetilde Q_i^{[1]}-\mathsf A_{{\rm T},i}Q_i^{[0]}.
\]

It is a PBW-covariantized deformation intertwiner, not an ordinary second quantum screening. The disposition is Outcome B. No quantum screening doublet, BRST complex, quantum-group structure, quantum Serre relation, or full holographic duality is established.

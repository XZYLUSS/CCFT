# Notebook II, Gate 2 source and derivation log

Date: 2 August 2026 (Europe/Berlin).

## Immutable local primary sources

- Stefan Fredenhagen and Lucas Hörl, *Free-field construction of Carrollian W_N-algebras*, JHEP 02 (2026) 218, arXiv:2509.14441v3. Local SHA-256: `5f617eaf715ffa78e7dda7910c573dc8c5c01277ba0a1e5c99556e2f389ee38d`. Used at equations (2.11)-(2.15), (3.8)-(3.18), (3.23)-(3.34), (4.23)-(4.34), and Appendix B for the symmetric contraction, represented mode actions, barred mode reversal, averaged ordering and anti-normal-ordering mechanism.
- Ethan D'Arcy, Arnaud Delfante and Stefan Fredenhagen, *Holographic realization of higher-spin Carrollian free fields*, arXiv:2604.27068v1. Local SHA-256: `84cbf5a4c6c3c84aef3242af42e037a73243e1bb09b7d8c0da75e74a656cbe0e`. Context only for classical screening charges and the eventual bulk comparison.
- Stefan Fredenhagen, Stefan Prohazka and Robert Tiefenbacher, *Carrollian quantum states and flat space holography*, arXiv:2604.22745v2. Local SHA-256: `9c1bb39f49fea398b92a3d7e929192771564b7b7cb43dfc92bb4d18b1996fa38`. Context only for nonregular sectors.

The package does not redistribute these PDFs.

## Representation-theoretic background

- A. Tsuchiya and Y. Kanie, *Fock Space Representations of the Virasoro Algebra - Intertwining Operators -*, Publ. RIMS Kyoto Univ. 22 (1986) 259-327, DOI 10.2977/prims/1195178069.
- Y.-Z. Huang, J. Lepowsky and L. Zhang, *Logarithmic tensor category theory for generalized modules for a conformal vertex algebra, I*, arXiv:1012.4193, and *II: Logarithmic formal calculus and properties of logarithmic intertwining operators*, arXiv:1110.1929.
- D. Adamovic and G. Radobolja, *Self-dual and logarithmic representations of the twisted Heisenberg-Virasoro algebra at level zero*, Commun. Contemp. Math. 21 (2019) 1850008, arXiv:1703.00531.

These references motivate Hom-valued fields containing powers of a formal logarithm. They do not supply the Gate-2 theorem; the horizontal Fock category, PBW-flat comparison, fixed-lattice formal neighborhood, and based logarithmic residue used here are explicitly defined and checked in the notebook.

## Derived here, not imported

1. The exact affine powers `delta=t b^2/4` and `deltabar=t bbar^2/4` after transporting the plane screening one-forms.
2. The simultaneous regular monodromy section for both parent branches, together with the proof that generic off-horizontal momentum jets are not simultaneously resonant.
3. The regulated scalar BCH factor converting the transported barred anti-normal vertex to common normal order.
4. The fixed-leading-lattice/PBW-flat trivialization of the moving source and target Fock families, including an explicit unexponentiated `q^+` connection generator and genuine `t`-divisibility in one Hom-module. The parent Weyl embeddings use the scalar extension `C((t^(1/2)))`; the transported screening and current series used for the theorem are regular in `t`.
5. The based logarithmic residue formula, the off-horizontal Virasoro boundary anomaly, and its exact cancellation on the horizontal parent sections.
6. Finiteness and nonvanishing of the strict odd coefficient operator, with the nonzero `m=-2`, `J^-_{-1}` PBW projection as witness.
7. The separation between the universal current expansion and the PBW-trivialized represented actions. The frozen single-field Weyl brackets are `[p^-,q^+]=[p^+,q^-]=1/4`, so the transported unbarred and barred zero-mode exponentials shift the scalar target momenta by `(t b/4,b/4)` and `(-t bbar/4,bbar/4)`. This agrees with the reduction of the rootwise shift `mu kappa alpha_i/2`, with `mu=-b/2`, to the `A_1` scalar field. Although the noncentral universal fields have no explicit first `t` coefficient, the two target momentum paths differ by `Delta p^+=b_1/2` and `Delta p^-=B_diff/2`.
8. The resulting inhomogeneous A_1 connection/deformation-intertwiner equations for every `L_n` and `M_n`, including the explicit checks `[Q^[1],M_0]_PBW=-(m+1)Q^[0]` and `[Q^[1],L_0]_PBW=-(b_1^2/4) Q^[0]`.
9. The general first-order connection gauge law `Q^[1] -> Q^[1]+A_t Q^[0]-Q^[0]A_s`, where `A_t,A_s` are the relative half-differences of the two branch connections. A common branch frame leaves the odd coefficient unchanged. Only regulator, base-point and branch-relative relaxed vacuum-normalization changes reduce to `Q^[1] -> Q^[1]+cQ^[0]`; a momentum-differential connection change is not identified with this scalar ambiguity.

## Dated search snapshot and novelty caveat

Searches on 2 August 2026 for the exact FH and DDF titles, `Carrollian quantum screening W3`, `symmetric Carrollian screening doublet`, and `logarithmic Carrollian screening intertwiner` returned the two programme sources above but no directly matching construction of the finite-parameter quantum tangent operator. This is a dated inspected-result statement, not an exhaustive proof of absence, priority or novelty.

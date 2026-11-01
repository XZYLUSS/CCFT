# Carrollian Screening Programme - Notebook II, Gate 2 operative status

Date: 2 August 2026 (Europe/Berlin).

## Immutable upstream dependency

Gate 1 remains frozen as `Notebook_II_Gate1_Freeze_Grade_Peer_Review_Corrected.zip`, SHA-256 `860df721f9de6c266ff4f9016aedce6c1bc908afa66ec36095ec3094de42c871`. This Gate-2 continuation does not rewrite that archive.

## Scientific disposition

**Gate 2: CLOSED - Outcome B for the A_1 operator layer.**

The finite-`epsilon` parent screening families are defined on exact horizontal resonant Fock curves. Canonical PBW-flat source and target frames identify both moving Hom-spaces with one fixed leading Hom-space. The comparison does not use a moving direct-sum group algebra. The parent Weyl embeddings are formed over `C((t^(1/2)))`, while the transported vertices and contracted currents used for coefficient extraction lie in the regular `C[[t]]` subcategory.

The unbarred vertex is already normally ordered. The transported barred vertex is anti-normally ordered and has the regulated scalar conversion

`Zbar_(t,rho) = (1-rho)^(-t bbar(t)^2/2)`.

Minimal subtraction gives a continuous normal-ordered logarithmic field. Finite subtraction and base-point changes give `Q^[1] -> Q^[1] + c Q^[0]`. A relative change between the barred and unbarred source/target branch connections is distinct and obeys `Q^[1] -> Q^[1] + A_t Q^[0] - Q^[0] A_s`, with `A_t,A_s` the relative half-differences. A common frame change on both branches leaves the odd coefficient unchanged.

The transported plane one-form supplies the exact affine powers

`delta(t)=t b(t)^2/4`, `deltabar(t)=t bbar(t)^2/4`.

For every integral Fourier label `m`, the horizontal momentum section

`lambda_plus = ((m-delta)/b + (m-deltabar)/bbar)/2`,

`t lambda_minus = ((m-delta)/b - (m-deltabar)/bbar)/2`

is regular and makes both parent one-forms have monodromy `m`. An arbitrary perturbation `(xi,nu)` has residual monodromies `b xi+t b nu` and `bbar xi-t bbar nu`; simultaneous resonance forces `xi=nu=0`. Such off-horizontal jets are diagnostic target-neighborhood variables, not screening sources.

The based logarithmic residue is primary only as a representative of the finite-parent horizontal coefficient prescription. Off horizontal, the weight-one total-derivative integral has the boundary anomaly `(exp(2 pi i a)-1)/(2 pi i)`. On the exact horizontal curves `a_u(t)=a_b(t)=0` identically, so the anomaly vanishes before coefficient extraction.

The strict odd coefficient `Q^[1]` exists in the fixed PBW Hom-space, is finite, and is linearly independent from `Q^[0]`. Its nonvanishing is proved on the `m=-2` horizontal vacuum by the nonzero `b_1 J^-_{-1}` PBW projection, which is absent from `Q^[0]`.

## Decisive represented-action correction

The universal noncentral current expressions obey, up to commuting vacuum constants,

`M(t)=M^[0]+t^2 M^[2]`, `L(t)=L^[0]`.

This does not freeze the PBW-trivialized representations. The frozen single-field Weyl brackets are `[p^-,q^+]=[p^+,q^-]=1/4`. Hence the unbarred target shift is `(t b/4,b/4)` and the barred target shift is `(-t bbar/4,bbar/4)`. Equivalently, the rootwise shift `mu kappa alpha_i/2`, with `mu=-b/2`, reduces at `A_1` to the scalar shift `b/4`. The two target momentum paths therefore have relative first tangent

`Delta p^+ = b_1/2`, `Delta p^- = B_diff/2`.

Consequently,

`Delta M_T,n^[1] = (b_1/2)(4 J_n^+ - 2 alpha^+ delta_(n,0))`,

`Delta L_T,n^[1] = (b_1/2)(4 J_n^- - 2 alpha^- delta_(n,0)) + (B_diff/2)(4 J_n^+ - 2 alpha^+ delta_(n,0))`.

Subtracting the two exact finite-parent intertwining equations gives the PBW-flat deformation equation

`[Q^[1],U_n^[0]]_PBW + (1/2) Delta U_T,n^[1] Q^[0] = 0`, `U=L,M`.

The common source first correction cancels; the relative target correction does not. In particular,

`[Q^[1],M_0]_PBW = -(m+1) Q^[0]`,

so on the package's `m=-2` nonvanishing component it equals `Q^[0]`, not zero. Also `[Q^[1],L_0]_PBW = -(b_1^2/4) Q^[0]`. Therefore `Q^[1]` is a nonzero connection/deformation intertwiner, not an ordinary second screening in the canonical PBW-flat frame.

## Claim boundary and Notebook III

Notebook III may use `Q_i^[0]` as ordinary leading screenings. It may carry `Q_i^[1]` only as deformation/connection coefficients and must construct the separate source and target actions of the nonlinear `U_3^+` and `U_3^-` families before extracting their mixed equations. Notebook II does not authorize the phrase **quantum screening doublet**.

The viable title branch is therefore **Screening Jets and Deformation Intertwiners for the Symmetric Carrollian W_3 Algebra** unless Notebook III independently constructs a stronger covariant operator category.

## Release gate

In a clean extraction all five commands must return zero:

```text
sha256sum -c SOURCE_MANIFEST.sha256
python3 verify_notebook_II_gate2.py
python3 verify_notebook_II_gate2.py --scalar-sanity-controls
python3 test_notebook_II_gate2_mutations.py
python3 freeze_check_II_gate2.py
```

The mutation suite is a separate mandatory command and is not recursively launched by the top-level checker. Every timeout is a failed test, not a caught mutation. The budgets are overridable through `NOTEBOOK_II_GATE2_PER_PROCESS_TIMEOUT_S`, `NOTEBOOK_II_GATE2_PER_CASE_TIMEOUT_S`, and `NOTEBOOK_II_GATE2_TOTAL_SUITE_TIMEOUT_S` for forced-timeout auditing.

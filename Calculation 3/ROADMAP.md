# Carrollian Screening Programme - Notebook III, Gate 3B

Corrected freeze-release date: 4 August 2026 (Europe/Berlin, UTC+02:00).

Semantic release ID: G3B-aaef4dfef7d3880e.

## Frozen inputs

- Notebook III, Gate 3A: `Notebook_III_Gate3A_Final_Freeze_Grade_Provenance_Corrected.zip`, SHA-256 `45e9bfdf2906527ea2175513dff447e9052d06a14c94dd979904d07323962c82`.
- Notebook II, Gate 2: `Notebook_II_Gate2_Closed_Outcome_B_Normalization_Corrected_Final.zip`, SHA-256 `522f0a57b5e128bd9fda861d036d30b1ee36f98f98d34cfd4cf5d98862a16481`.
- Notebook II, Gate 1: `Notebook_II_Gate1_Freeze_Grade_Peer_Review_Corrected.zip`, SHA-256 `860df721f9de6c266ff4f9016aedce6c1bc908afa66ec36095ec3094de42c871`.
- Notebook I: `Notebook_I_Freeze_Grade_Merged_Final.zip`, SHA-256 `662de55b99f9e61f8e3c66d646972e286973f75e6a04165c5cbd4b3e172a3b5f`.

## Corrected Gate 3B theorem

The superseded archive omitted `D(w^-1)=-w^-2`. With the ordinary commutative diagnostic corrected, the unbarred residuals are

`Rcomm_1 = -mu^2(P1+3P2)/(4w) - mu/(4w^2)`,

`Rcomm_2 = +mu^2(P1-2P2)/(4w) + mu/(4w^2)`.

These are not discarded by horizontality. The two finite-parent normal-order orientations are evaluated before coefficient extraction. Their symmetric contraction produces the derived averaged-order contact

`alpha_1: delta O_2=mu/(4w), delta O_1=mu^2(P1+P2)/(2w)`,

`alpha_2: delta O_2=-mu/(4w), delta O_1=-mu^2 P1/(2w)`.

The contact accounts for the full corrected residual, including the `w^-2` pieces. It is fixed by the parent ordering and is not an ad hoc counterterm.

The strict odd averaged OPEs are separately exact total derivatives. Writing

`H_i=alpha_i dot phi^- - alpha^- mu alpha_i dot phi^+`,

their witnesses are

`Xi_1,2=(H_1+alpha^-)/4`,

`Xi_1,1=(N1+N2+mu H_1(P1+P2))/2`,

`Xi_2,2=-(H_2+alpha^-)/4`,

`Xi_2,1=-(N1+mu H_2 P1)/2`.

The common even/affine coefficient is also separately exact after the same two-orientation extraction. Thus the old explanation that the even coefficient cancels the odd algebraic remainder is retracted and replaced by the finite-parent averaged-order mechanism.

The exact rootwise horizontal source section solves both branch monodromy equations before coefficient extraction. Consequently the integrated raw moving-frame commutators vanish. The barred BCH factor is scalar and insertion-coordinate independent.

After the canonical target-frame derivative,

`[Q_i^[1], calU_3,n^{sigma,[0]}]_PBW + (1/2) Delta calU_T,3,n^{sigma,[1]} Q_i^[0] = 0`.

## Disposition

- Gate 3A: frozen upstream.
- Gate 3B: PASS after the derivative and averaged-order correction.
- Gate 3: closed with Outcome B.
- `Q_i^[1]`: finite deformation/connection intertwiner.
- `Q_i^[1]`: not an ordinary second screening.
- The phrase quantum screening doublet remains unauthorized.
- Kernel equality, a BRST complex, screening-screening closure, and the bulk normalization match remain unproved.

## Next step

Notebook IV: semiclassical bulk normalization and the `N=2` anchors. This corrected Gate 3B archive must be independently reviewed and frozen before Notebook IV depends on it.

## Reproducibility

Run under Python 3.12 with `sympy==1.14.0`:

1. `sha256sum -c SOURCE_MANIFEST.sha256`
2. `python3 verify_notebook_III_gate3b.py`
3. `python3 verify_notebook_III_gate3b.py --scalar-sanity-controls`
4. `python3 independent_check_III_gate3b.py`
5. `python3 test_notebook_III_gate3b_mutations.py`
6. `python3 checkpoint_check_III_gate3b.py`

# Notebook IV operative disposition

Semantic release: `NIV-36a2530aab4feb7d`

Notebook IV is the final normalization-and-interpretation checkpoint of the Carrollian screening programme. It does not reopen Gate 3. The definitive dependency is Gate 3B SHA-256 `a77a670b5e7ff4811cdf30094702ccdd772bdd8b9f157b4329f502bb2989a0cb`.

## Frozen upstream archives

1. Notebook I: `Notebook_I_Freeze_Grade_Merged_Final.zip`, SHA-256 `662de55b99f9e61f8e3c66d646972e286973f75e6a04165c5cbd4b3e172a3b5f`.
2. Notebook II Gate 1: `Notebook_II_Gate1_Freeze_Grade_Peer_Review_Corrected.zip`, SHA-256 `860df721f9de6c266ff4f9016aedce6c1bc908afa66ec36095ec3094de42c871`.
3. Notebook II Gate 2: `Notebook_II_Gate2_Closed_Outcome_B_Normalization_Corrected_Final.zip`, SHA-256 `522f0a57b5e128bd9fda861d036d30b1ee36f98f98d34cfd4cf5d98862a16481`.
4. Notebook III Gate 3A: `Notebook_III_Gate3A_Final_Freeze_Grade_Provenance_Corrected.zip`, SHA-256 `45e9bfdf2906527ea2175513dff447e9052d06a14c94dd979904d07323962c82`.
5. Notebook III Gate 3B: `Notebook_III_Gate3B_Definitive_Freeze_Grade_Portable.zip`, SHA-256 `a77a670b5e7ff4811cdf30094702ccdd772bdd8b9f157b4329f502bb2989a0cb`.

## Closed gate sequence

- IV-0: all five archive hashes and both primary-PDF hashes are pinned.
- IV-1: the FH factor `i`, Fourier sign, delta-prime sign, four derivative namespaces, averaged ordering, and target-first PBW orientation are machine-active.
- IV-2: `alpha_plus=+i*a_s` gives `cM=3/G`; the consistent special value is `i/(2*sqrt(G))`.
- IV-3: the general diagonal construction reduces to the explicit (s=2) connection and both row determinants.
- IV-4: the complete (N=2) solve has only two conjugate branches; the selected branch has equal unbarred and barred current signs and no triangular improvement.
- IV-5: the two (N=2) screening transformations and both Miura invariants match.
- IV-6: the (A_2) root bracket is (16\pi G A_{ij}), with one scalar-to-weight map.
- IV-7: all four observables (U_2^\pm,\mathcal U_3^\pm) match coefficientwise.
- IV-8: both leading simple-root charges match with one normalization rule.
- IV-9: both barred-linear charges match the raw horizontal coefficient; the common even/affine term is (O(G)).
- IV-10: the canonical coefficient is the target-frame covariantization of the raw coefficient.
- IV-11: composite charges remain a nonblocking, basepoint-sensitive diagnostic.
- IV-12: Outcome B is authorized after one global analytic continuation and plane/cylinder conversion.

## Machine-readable load-bearing tokens

- `mu*Phi_i_plus=-chi_i`
- `mu*Phi_i_minus=-bar_chi_i`
- DDF (5.28c): `9*psi_L_double_prime`
- DDF (6.23c) explicit-sector coefficient: `1/(kCS*tau_s)`
- frame: `raw horizontal coefficient`
- conclusion: `not an ordinary second quantum screening`

## Release protocol

Run, in order:

1. `.venv/bin/python verify_notebook_IV.py`
2. `.venv/bin/python scalar_controls_IV.py`
3. `.venv/bin/python independent_check_IV.py`
4. `.venv/bin/python derive_bulk_s2_anchor.py`
5. `.venv/bin/python derive_bulk_s3_anchor.py`
6. `.venv/bin/python test_notebook_IV_mutations.py`
7. `.venv/bin/python checkpoint_check_IV.py`

The bulk barred-linear Noether charge is the semiclassical image of the raw horizontal coefficient. The canonical (Q_i^{[1]}) is its PBW-covariantized deformation intertwiner and is not an ordinary second quantum screening. No quantum screening doublet, BRST complex, quantum-group structure, quantum Serre relation, or full holographic duality is claimed.

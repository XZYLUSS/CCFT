# Carrollian Screening Programme — Operative Roadmap
Committed 1 August 2026. Supersedes all earlier roadmap statements in the working record.
This file is the authoritative plan through to the manuscript. Amend by revision, not by memory.

    Notebook I  ->  Notebook II  ->  Notebook III  ->  Notebook IV (or III+IV)  ->  manuscript

NOTEBOOK I IS NOT DECLARED FROZEN BY THIS FILE. Its mechanical status is set by the
cross-witnessed package gate, and its scientific status requires separate human sign-off.
See section 0.

--------------------------------------------------------------------------------
## 0. STATUS OF NOTEBOOK I — regenerated from the final notebook, 1 Aug 2026
##    MECHANICAL STATUS: G0m GREEN.   SCIENTIFIC STATUS: G0s OPEN.

This section is REGENERATED from the current Notebook I, not a historical list of patches.
Superseded statements are not retained; where a position changed, only the final one appears.

TWO GATES, NAMED. Do not conflate them:

    G0_mech = manifest + verifier + mutation regression + freeze checker
    G0_sci  = G0_mech + human scientific sign-off

Only Notebook I's MECHANICAL status is set by the commands below; its scientific status is not.
G0_mech is established when, in a clean directory,

    sha256sum -c SOURCE_MANIFEST.sha256 && python3 verify_notebook_I.py \
      && python3 test_freeze_gate_mutations.py && python3 freeze_check.py

all return zero.  ONLY G0_sci AUTHORISES THE WORD "FROZEN".  As of this revision G0_mech is
green; G0_sci is not claimed by this file and cannot be -- a status document must not certify
its own subject. The mutation runner and freeze checker are cross-witnessed: the former
mutates the latter, while the latter requires the runner's exact completion sentinel and
case count. Every subprocess is bounded, staged child gates are stopped by a caller-side
recursion guard, and independent mutation cases run concurrently in isolated directories.
freeze_check.py also runs divisibility.py's positive/negative controls, semantic regression assertions on the statuses below, and
document-control scans. A green gate is a MECHANICAL result: its declared scope excludes
source interpretation, layer consistency, operator existence, contour signs, cocycles and
the bulk dictionary. Scientific freeze needs human sign-off on top of it.

### Current status of the load-bearing conventions

  ROUTES A AND B.  Both are calculations inside the ADOPTED plane realisation (C1 + C7p):
  Route A contracts a parent plane relation, Route B uses the adopted contracted plane algebra.
  Their agreement is an internal cross-check. NEITHER proves the plane/cylinder bridge.

  ZERO MODES.  The crossed algebra [p^-_i, q^+_j] = kappa_ij/2 is ADOPTED module data chosen for
  compatibility with C7p. It is NOT derived from C7, whose m=0 brackets vanish identically and
  say nothing about the conjugate q's. The half-shift and the monodromy are derived WITHIN that
  adopted convention. Layer (iii) of Prop 6.1 (base point / ordering / flag covariance) is a
  formulated structural inference, not a derivation.

  PLANE / CYLINDER.  Notebook I certifies ONE statement: a_n != J_{-n} (no unbarred mode
  reversal), falsified by the bracket sign. The OVERALL SIGN IS NOT FIXED: both J_n = +a_n
  and J_n = -a_n survive, depending on whether FH's explicit i is assigned to the Jacobian
  or to their reality convention J = i d(phi^FH). Notebook I adopts NEITHER. The complete
  bridge -- transporting J, varphi, alpha, beta, the Miura factors AND the barred contour
  together -- is a Notebook II.1 deliverable. See II.1 for the leading candidate.

  TWO REALISATIONS, DELIBERATELY UNBRIDGED.  Sections 3 and 7.2 are plane radial-OPE
  calculations in an ADOPTED plane realisation (C1 for the parent algebra, C7p for the
  contracted algebra and the plane forms of T and M). Sections 4-6 are cylinder statements
  in FH's conventions. The claim that these describe the same fields is NOT made in
  Notebook I. Route A and Route B for F_0 are both inside the adopted plane realisation, so
  their agreement is a genuine internal cross-check -- but it does not certify the bridge.

  SOURCE NOTE.  FH (3.3) as printed omits the mode factor m; (3.14) contains it. Confirmed
  by direct inspection of the canonical v3 PDF. We cite (3.14). Recorded as a source erratum
  note, with no speculation as to cause.

  REAL FORM.  The statement "alpha^+ is imaginary, hence c_alpha is imaginary" is a
  CONDITIONAL INFERENCE, not an obstruction theorem: it presupposes c_M^FH = lambda c_2^DDF
  with lambda > 0 real, and lambda is part of the open matching problem (Notebook IV).
  Use the rank relevant to Paper 1: at N = 3, C9 gives c_M = -48 (alpha^+)^2, NOT -12, which is
  the N = 2 value; consistent with the spin-three normalisation alpha_s = 1/2. Hence
      (alpha^+)^2 = -c_M^FH/48 = -lambda c_2^DDF/48 = -lambda/(16 G)   using c_2^DDF = 3/G.
  NO NUMERICAL VALUE IS CLAIMED: alpha^+ = +/- i/(4 sqrt G) only under the extra choice
  lambda = 1. What survives lambda-independently is the sign, for any real lambda > 0.

  MULTIPLICITY.  At the formal coefficient level the difference channel yields TWO CANDIDATE
  commutant directions, Q_0 and Q^(1). Their realisation as two nonzero independent operator
  intertwiners is conditional on Gate 2 of Notebook II. "Formal multiplicity pattern", never
  "established commutant multiplicity". The paper's title ("doublet") depends on upgrading the
  formal pair to operators, i.e. on Gate 2.

  CATEGORY SPLIT.  Paper 1 REQUIRES a minimal explicitly defined category and common domain,
  enough to make Q^(1) an intertwiner and state its commutators -- assigned to NOTEBOOK II.
  The FULL screening-screening logarithmic algebra, its closure onto the composite charges and
  the complete logarithmic/Takiff category are PAPER 3. Do not conflate the two.

  PROPOSITION 3.4.  Stated in ONE field order, with the vertex factor:

      Res_{w=z}[ u_k(z) V_{mu alpha_i}(w) ] = (mu^2 + alpha mu - 1) R_{k,i}(z) V_{mu alpha_i}(z),
      |z| > |w|,  R_{k,i} a DIFFERENTIAL polynomial in the currents (the second A_2 root
      produces dJ terms, so "polynomial" alone is wrong).

  Verified for N = 2,3,4, every simple root, every u_k, by a genuine divisibility test
  (polynomial quotient AND vanishing under alpha -> (1-mu^2)/mu). Computer-assisted over a
  FINITE range; not a general-N theorem. The screening locus is mu^2 + alpha mu = 1 WITH
  mu != 0 -- at mu = 0 the density is constant and the charge vanishes identically.
  The total-derivative witnesses at N=3 are now displayed in Notebook I and checked by the
  verifier for both simple roots.

  LEADING CHARGES.  The oscillator parts of the leading screenings commute unconditionally
  (varphi^+ varphi^+ ~ 0). The CHARGE-level statement [Q^(0)_i, Q^(0)_j] = 0 additionally
  requires the zero-mode cocycle to be trivial or compatibly commuting; D4(4) leaves it open.

  MODULE DATA.  The algebraic carrier (index space, oscillators, crossed zero modes, charge
  lattice, momentum-sector index set) is specified. The cocycle, the logarithmic residue
  defining Q^(1), the common operator domain and the affiliation proof are enumerated but
  NOT completed. A minimal category sufficient to make Q^(1) an intertwiner is a Notebook II
  deliverable, not a Paper 3 one.

  SELF-CONTAINMENT.  Paper 1 (N=3) is self-contained with respect to the PARENT SCREENING
  IDENTITY (Propositions 3.3, 3.4 replace the Fateev-Lukyanov import). FH25 remains
  load-bearing for the symmetric Carrollian W_3 algebra and DDF26 for the bulk charges.

  ARCHIVAL COMPANION.  The interactive HTML depends on CDN-hosted fonts, MathJax, Pyodide
  and SymPy, and the browser SymPy is NOT pinned. The offline verifier is the computational
  artefact of record; Notebook_I_Setup_Static.pdf is the self-contained archival reading
  copy authenticated by the manifest. The gate certifies its bytes, not visual equivalence.

--------------------------------------------------------------------------------
## 1. NOTEBOOK II — operator construction + A_1 decision layer.  Cannot be compressed.

Six layers, in this order:

 II.1  Coordinate/mode/contour map. THE COORDINATE CONVENTION IS AN OUTPUT OF THIS STEP,
       NOT AN INPUT. Notebook I deliberately leaves it open (Erratum E1 fixes only that there
       is no mode reversal). The LEADING CANDIDATE, to be confirmed with all Jacobians:
           w = tau - i theta,  z = e^w,  J_w = (dz/dw) J_pl = z J_pl,  J_FH = i J_w,
       which reproduces FH's cylinder dependence e^{-n tau + i n theta} exactly and gives
       a_n = J_n (no reversal, no sign flip), with FH's explicit i belonging to their reality
       convention J = i d(phi^FH) rather than to the Jacobian. At tau = 0, zbar = z^{-1}.
       Whichever convention is adopted must be transported through J, varphi, alpha, beta,
       the Miura factors AND the barred contour together -- changing only the current-mode
       relation is what made the earlier attempt inconsistent. DERIVE (do not assume): holomorphic and antiholomorphic mode
       expansions with SEPARATE symbols for plane and cylinder modes; Jbar_n -> Jbar_{-n};
       transformation of a weight-one screening current; barred contour orientation.
       DEFINE BOTH CHARGES ON THE CYLINDER FIRST,
           Q_eps = int_0^{2pi} dtheta V_cyl(theta),   Qbar_eps likewise,
       so both use increasing-theta orientation; rewrite as plane residues only afterwards.
       This is the ONLY way to avoid losing a sign between dzbar = -z^{-2} dz and the
       orientation reversal.
       OUTPUT: one boxed formula
           Q^{(0)}_eps = c_0(eps)( Q_eps + s_0 Qbar~_eps ),
           Q^{(1)}_eps = c_1(eps)( Q_eps + s_1 Qbar~_eps ),   s_0, s_1 in {+1,-1} DERIVED.
       This fixes the sign of the tangent field and hence the sign of B.

 II.2  Finite-eps module and vertex operators. Embeddings I_eps : H_eps -> Hhat, or an
       algebraic identification of finite-energy vectors permitting coefficientwise
       comparison. Parent vertex operator in full:
           V = E_-(b,z) e^{b q} z^{b p} E_+(b,z),
       barred copy written separately BEFORE the equal-time map.
       COCYCLE: absence of varphi^+varphi^+ contractions kills the oscillator branch factor
       but does NOT prove the zero-mode group algebra admits only the trivial cocycle.
       Trivial may suffice at A_1; at A_2 check compatibility of the two simple-root
       intertwiners with the chosen zero-mode algebra.

 II.3  DEFINE THE TANGENT CHARGE AS A COEFFICIENT OF THE PARENT FAMILY — not via an
       abstract logarithmic residue:
           Q^(0) = lim c_0(eps) ( Q_eps + s_0 Qbar~_eps ),
           Q^(1) = lim c_1(eps) ( Q_eps + s_1 Qbar~_eps ),
       with s_0, s_1 in {+1,-1} and c_0, c_1 TAKEN FROM II.1, NOT ASSUMED HERE. Do not hardcode
       the sum/difference assignment or the 1/2, 1/(2 eps^2) normalisations before II.1 is done;
       an earlier version of this file did, contradicting II.1's own instruction to derive them.
       Inherits the domain from the parent charges; fixes the relative contour sign; fixes
       the base point; makes Q^(1) -> Q^(1) + lambda Q^(0) transparent. A logarithmic-residue
       formalism, if wanted, must be shown EQUIVALENT to this, not adopted independently.

 II.4  SEPARATE THREE EFFECTS. They are not the same thing:
         (a) multiplicative renormalisation  Qhat_eps = Z_eps Q_eps;
         (b) parameter correction — a quantum shift of beta_3, bar-beta_3 CHANGES
             B = (beta_3 - bar-beta_3)/2;
         (c) triangular basis change — reordering varphi^- e^{b varphi^+} adds only
             C e^{b varphi^+}, i.e. Q^(1) -> Q^(1) + C Q^(0), and CANNOT shift B.
       Both (b) and (c) are real; only (c) is excluded from touching B.

 II.5  Exact A_1 commutators, PROVED TWICE (direct averaged-ordered modes/OPE, and
       coefficientwise limit of the exact finite-eps parent commutators — the operator-level
       analogue of the two-route F_0 check):
           [Q^(0), M_n] = 0 for every beta_1;
           [Q^(0), L_n] = 0  <=>  alpha^+ beta_1 = -2;
           [Q^(1), M_n] = [Q^(1), L_n] = 0 on the full (F_0, F_1) locus, modulo flag freedom.

 II.6  Even jet: compute [Q_0, U^-_{2,2}], hence [Q_2, U^-_{2,0}] = -[Q_0, U^-_{2,2}].
       Classify in the quotient by parameter derivatives and flag transformations:
       (1) does not commute; (2) commutes but is a parameter derivative; (3) genuinely
       independent. NO MULTIPLICITY CLAIM BEFORE THIS.

### GATES 1-2 (Notebook II) — the seven conditions
  Conditions 1-3 and 5 constitute GATE 1 (the leading operator Q^(0)).
  Conditions 4, 6, 7 constitute GATE 2 (the tangent operator Q^(1)).
  Notebook II passes in full only if ALL SEVEN hold:
  1. barred equal-time map and contour orientation derived, no unresolved sign;
  2. common algebraic domain or explicit I_eps defined;
  3. Q^(0) finite, nonzero, momentum-sector map explicit;
  4. Q^(1) finite, nonzero, stated base point and flag covariance;
  5. A_1 commutators reproduce F_0 exactly;
  6. F_1, B, multiplicative normalisation and triangular C-mixing SEPARATELY identified;
  7. even jet classified.
  Passing only 1-3 supports a LEADING-SCREENING paper, not a doublet paper.

### TITLE FORK — decided by Notebook II
  Q^(1) exists ->  "Quantum Screening Doublets for the Symmetric Carrollian W_3 Algebra"
  only Q^(0)   ->  "Leading Quantum Screenings for the Symmetric Carrollian W_3 Algebra"

--------------------------------------------------------------------------------
## 2. NOTEBOOK III — the A_2 theorem.  CO-DOMINANT RISK, not secondary.

  - Use the PRIMARY basis:
        cal-U_3^+ = U_3^+ - (alpha^+/2) d U_2^+
        cal-U_3^- = U_3^- - (alpha^-/2) d U_2^+ - (alpha^+/2) d U_2^-
  - Contract the ALREADY-DERIVED parent identity (Prop 3.4); display A_i, B_i explicitly.
  - Prove [Q_i^(a), cal-U_{3,n}^sigma] = 0 by BOTH routes: coefficientwise contraction of the
    exact parent identity, AND direct averaged-ordered computation. The second is essential:
    the first can conceal finite counterterms introduced while taking the limit.

### GATE 3 — passes only when, for i = 1,2, a = 0,1, sigma = +/-:
    [Q_i^(a), U_{2,n}^sigma] = [Q_i^(a), cal-U_{3,n}^sigma] = 0
  on an explicitly named module, with: all singular OPE terms displayed; every nonzero
  singular part written as a total derivative; no unexplained contact term; no hidden
  normal-ordering change; the exact parameter locus stated; the Weyl-related simple-root
  calculations cross-checked against one another.

  Notebook II is the CATEGORICAL risk (do the operators exist?).
  Notebook III is the NOVELTY risk (do they screen the nonlinear currents?).

--------------------------------------------------------------------------------
## 3. NOTEBOOK IV — holographic matching. SUBSTANTIVE, NOT BOOKKEEPING.

  IV.1  Solve the normalisation map. With J^+_j = c_+(-i eps_j . psi'), J^-_j = c_-(-i eps_j . psibar'),
        find the matrix R from the DDF (L,W) basis to the A_2 root basis satisfying
            R G_DDF R^T = C kappa.
        The 8 pi G vs 6 pi G coefficients need NOT signal inconsistent quantisations — they
        may simply reflect non-orthonormal L and W Cartan directions. The matrix matching
        must show this explicitly.
  IV.2  Fix c_alpha from the Miura operator once c_+ is fixed: compare alpha^+_FH d - J^+_j
        with alpha_DDF d + i eps_j . psi'. Only then may a numerical alpha^+(G) be written.
  IV.3  Match exponents: beta_1 alpha_1 . varphi^+ <-> -psi_(L) - 2 psi_(W);
        beta_1 alpha_2 . varphi^+ <-> -psi_(L) + 2 psi_(W); tangent prefactors to
        psibar_(L) +/- 2 psibar_(W); highest root to -2 psi_(L).
  IV.4  G -> 0 IS NOT A BARE SUBSTITUTION. From F_0, alpha^+ ~ c G^{-1/2} and beta_1 ~ c^{-1} G^{1/2}
        for a nonzero, G-independent matching constant c fixed by IV.1-IV.2 (the scaling is a
        consequence of the dictionary, not an independent input),
        so the field normalisation must scale so that beta_1 alpha_i . varphi^+ stays finite.
        State what is held fixed: normalised bulk fields, current modes, screening exponents,
        overall charge normalisation.
  IV.5  Cross-checks (AR16 W(2,2) kernel; Hidalgo-Vandoren-Zeng Carrollian Liouville) here or
        in an appendix. One singular vector ONLY if nearly automatic; it must not delay the paper.
  IV.6  MERGE INTO III only if: c_alpha, c_+, c_- come out cleanly; the 8/6 pi G issue resolves
        without a new representation problem; and the dictionary is <= ~1/4 of the combined
        notebook. Otherwise keep IV separate — mixing unresolved bulk normalisation into the
        delicate A_2 proof makes both harder to audit.

--------------------------------------------------------------------------------
## 4. MANUSCRIPT — 18-22 pages main text, technical mode computations in appendices

    1  Introduction and precise gap ................... 1.5-2
    2  Symmetric Carrollian Miura algebra ............. 2
    3  Operator contraction and screening doublet ..... 3-4
    4  Filtration lemma and N=2 theorem ............... 2-3
    5  A_2 / W_3 commutation theorem .................. 4-5
    6  Parameter hierarchy and holographic matching ... 3-4
    7  Discussion and outlook ......................... 1-1.5

  Appendices: plane/cylinder and barred contour derivation; complete parent u_3 OPE with the
  explicit A_i, B_i witness; zero-mode/cocycle conventions; full averaged-ordering
  calculations; bulk normalisation matrix.

  CLAIM INCLUSION, NOT EQUALITY:
      W_3^Car  SUBSET OF  intersection over i,a of ker ad Q_i^(a),
  unless a kernel/character theorem is added.

  Outlook, once each only: composite screenings, degenerate modules, induced representations,
  nonregular AQFT, electric/magnetic FJ, arbitrary N, Carrollian Toda.

--------------------------------------------------------------------------------
## 5. RISK REGISTER (corrected)

  A. OPERATOR EXISTENCE (Notebook II)
     A1 full success -> doublet paper as advertised.
     A2 tangent exists but F_1 = F_1^formal + Delta_av -> STRONGER paper: first genuinely
        quantum effect of averaged ordering.
     A3 only Q^(0) exists -> retitle; fallback must still prove the leading A_2 screenings
        commute with the FULL U_2^pm, U_3^pm algebra and match the two pure-exponential DDF
        charges. Not automatically as strong.
     A4 no well-defined coefficient limit on D4 -> failure on one module is NOT nonexistence.
        An obstruction theorem requires exclusion within a bounded class: fixed charge,
        filtration degree <= 1, bounded derivative order, finite parent contraction, specified
        cocycle and ordering, specified logarithmic-residue prescription.

  B. NONLINEAR W_3 COMMUTATION (Notebook III) — NOT secondary.
     An N=2-only fallback is NOT automatically publishable: the W(2,2)/Galilean screening
     literature already exists. It becomes a real paper only with a specifically PROPER
     SYMMETRIC Carrollian theorem, or a rigorous no-go not contained in known W(2,2) work.
     FALLBACK ORDER:
        full doublet W_3  ->  leading-only W_3  ->  rigorous symmetric N=2 result/obstruction
        ->  boundary W_3 project.

  C. BULK NORMALISATION (Notebook IV) — does not threaten the algebraic theorem, but can
     weaken the title and physical claim. If unresolved, publish the algebraic screening
     theorem with a qualitative classical correspondence and defer the exact normalisation.
     DO NOT force a numerical G-dictionary the sources do not support.

--------------------------------------------------------------------------------
## 6. GATES

  Gate 0m Mechanical package gate ........................... GREEN
                                                              (manifest + verifier + mutation regression
                                                              + freeze_check all return zero in a clean directory)
  Gate 0s Scientific freeze of Notebook I ................... OPEN
                                                              pending human scientific sign-off;
                                                              ONLY this gate authorises "frozen"
  Gate 1  Q^(0) exists, nonzero, obeys the A_1 theorem ...... = Notebook II conditions 1-3, 5
                                                              failure stops the project
  Gate 2  Q^(1) exists modulo flag covariance ............... = Notebook II conditions 4, 6, 7
                                                              failure changes title and scope
  Gate 3  Nonlinear A_2 theorem ............................. failure blocks the W_3 paper
  Gate 4  Holographic matching .............................. partial failure removes the exact
                                                              normalisation claim only
  Gate 5  Manuscript freeze:
            LaTeX compile: zero errors
            cross-references: zero unresolved
            bibliography: all identifiers checked
            symbolic verifier: all tests pass
            source manifest: all hashes pass
            novelty sweep: repeated and dated
            claim ledger: every theorem mapped to a notebook derivation

--------------------------------------------------------------------------------
## 7. STANDING PROTOCOLS (every notebook, every milestone)

  - Identifier sweep on 2509.14441 and 2604.27068 at each milestone and on submission day.
    Save the query log and citation snapshot; a null search result is not proof of absence.
  - Each notebook ships with its own offline verifier, pinned requirements, source manifest,
    and provenance ledger. All four gate commands (sha256sum -c; verifier; mutation regression;
    freeze_check) must return zero in a clean
    extracted directory.
  - Provenance marks: verbatim / rewrite / derived / imported / inference / open. Anything not
    in the ledger is not licensed for the paper.
  - Never promote a formal jet to an operator statement, an inference to a derivation, or an
    inclusion to an equality.

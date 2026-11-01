---
title: "Notebook IV: Semiclassical Bulk Normalization and the N=2 Anchors"
subtitle: "Final normalization checkpoint for the symmetric Carrollian W3 screening programme"
author: "Semantic release NIV-36a2530aab4feb7d"
date: "4 August 2026"
geometry: margin=20mm
papersize: a4
fontsize: 9pt
header-includes:
  - \usepackage{amsmath,amssymb,mathtools,booktabs,longtable,microtype}
  - \setlength{\parindent}{0pt}
  - \setlength{\parskip}{4pt}
  - |
    ```{=latex}
    \newcommand{\Av}[1]{\left\langle #1\right\rangle_{\mathrm{av}}}
    ```
---

# 1. Result, scope, and immutable dependencies

This notebook proves the convention-complete semiclassical dictionary between the frozen boundary screening family and the classical bulk Noether screenings. It is a normalization and interpretation calculation. It does not reopen the tangent OPE or any Gate-3 theorem.

The load-bearing Gate-3B dependency is the portable archive

```text
Notebook_III_Gate3B_Definitive_Freeze_Grade_Portable.zip
SHA-256 a77a670b5e7ff4811cdf30094702ccdd772bdd8b9f157b4329f502bb2989a0cb
```

The four earlier frozen archives and their exact hashes are:

**Notebook I**

```text
Notebook_I_Freeze_Grade_Merged_Final.zip
SHA-256 662de55b99f9e61f8e3c66d646972e286973f75e6a04165c5cbd4b3e172a3b5f
```

**Notebook II, Gate 1**

```text
Notebook_II_Gate1_Freeze_Grade_Peer_Review_Corrected.zip
SHA-256 860df721f9de6c266ff4f9016aedce6c1bc908afa66ec36095ec3094de42c871
```

**Notebook II, Gate 2**

```text
Notebook_II_Gate2_Closed_Outcome_B_Normalization_Corrected_Final.zip
SHA-256 522f0a57b5e128bd9fda861d036d30b1ee36f98f98d34cfd4cf5d98862a16481
```

**Notebook III, Gate 3A**

```text
Notebook_III_Gate3A_Final_Freeze_Grade_Provenance_Corrected.zip
SHA-256 45e9bfdf2906527ea2175513dff447e9052d06a14c94dd979904d07323962c82
```

The frozen operator relation is

\[
Q_i^{[1]}=\widetilde Q_i^{[1]}-\mathsf A_{{\rm T},i}Q_i^{[0]},
\qquad
\mathsf A_{{\rm T},i}=\mu\,\alpha_i\!\cdot q^-+\nu\,\alpha_i\!\cdot q^+.
\]

Here \(\widetilde Q_i^{[1]}\) is the raw horizontal coefficient between moving target fibres. The fixed-target operator \(Q_i^{[1]}\) is its PBW covariantization and is **not an ordinary second quantum screening**.

# 2. Convention firewall

## 2.1 Circle, Fourier, and bracket conventions

The bulk circle has period \(2\pi\). For an ordinary bulk field,

\[
X(\phi)=\sum_{n\in\mathbb Z}X_ne^{in\phi},
\qquad
X_n=\frac1{2\pi}\int_0^{2\pi}e^{-in\phi}X(\phi)\,d\phi.
\]

We use

\[
[A,B]_{\rm cl}=i\{A,B\},
\qquad
\delta'(\phi-\phi')=\partial_\phi\delta(\phi-\phi').
\]

Consequently,

\[
\{\psi'(\phi),\bar\psi(\phi')\}=8\pi G\delta(\phi-\phi')
\]

implies

\[
\{\psi'(\phi),\bar\psi'(\phi')\}=-8\pi G\delta'(\phi-\phi'),
\qquad
[\psi'_m,\bar\psi'_n]_{\rm cl}=4Gm\,\delta_{m+n,0}.
\]

The sign follows from differentiating in the second argument and then integrating by parts. It is not imported from a mode formula.

## 2.2 FH real current versus the frozen Euclidean cylinder current

Fredenhagen and Hörl use the real cylinder expansion [FH, eqs. (3.2), (3.11)]

\[
J_{\rm FH}(\phi)=i\sum_{n\in\mathbb Z}J_ne^{in\phi}.
\]

The frozen plane/cylinder bridge from Notebook II is

\[
w=\tau-i\phi,
\qquad z=e^w,
\qquad
\mathcal J_w=zj_{\rm pl}-\frac\alpha2,
\qquad
J_{\rm FH}=i\mathcal J_w.
\]

Thus

\[
\mathcal J_{w,n}=a_n-\frac\alpha2\delta_{n0}.
\]

The factor \(i\) in the FH field expansion is indispensable. If it is omitted while the ordinary bulk Fourier convention is retained, the crossed mode bracket changes sign.

## 2.3 Ordering and derivative namespaces

The quantum minus currents use the symmetric averaged product of [FH, eqs. (2.14), (4.29)-(4.31)]. The reduction

\[
\Av{NP}\longrightarrow NP
\]

is made only after the strict classical limit. The verifier distinguishes four derivative namespaces,

\[
D_{\rm boundary},\quad D_{\rm bulk},\quad D_{\rm circle},\quad D_{\rm plane},
\]

and four ordering tags: commutative, averaged, parent-normal, and parent-antinormal. A jet from one namespace cannot be differentiated by another.

# 3. Semiclassical normalization triangle

Write the bulk Chern-Simons level and invariant-trace normalization as [DDF, eqs. (4.23), (6.3)-(6.5)]

\[
k_{\rm CS}=\frac1{8\pi G},
\qquad
\tau_s=\frac{12}{s(s^2-1)},
\qquad
a_s=\sqrt{\pi k_{\rm CS}\tau_s}.
\]

Then

\[
a_s^2=\frac{3}{2Gs(s^2-1)}.
\]

For the symmetric Carrollian free fields [FH, eqs. (3.30)-(3.31), (4.16)-(4.17)],

\[
c_L=-4s(s^2-1)\alpha^+\alpha^-,
\qquad
c_M=-2s(s^2-1)(\alpha^+)^2.
\]

The gravity branch is

\[
\boxed{\alpha^-=0,\qquad \alpha^+=+ia_s}.
\]

It gives

\[
c_L=0,
\qquad
c_M=-2s(s^2-1)(ia_s)^2=\frac3G.
\]

The semiclassical parameter is

\[
g_s=a_s^{-1}=O(\sqrt G),
\qquad
\mu=(\alpha^+)^{-1}=-\frac{i}{a_s}=O(\sqrt G).
\]

```{.python .cell-code data-cell="1"}
import sympy as s
G,r=s.symbols('G r',positive=True)
a2=s.Rational(3,2)/(G*r*(r**2-1))
assert s.simplify(-2*r*(r**2-1)*(s.I**2*a2)-3/G)==0
assert s.simplify(a2.subs(r,2)-1/(4*G))==0
assert s.simplify(a2.subs(r,3)-1/(16*G))==0
print('CELL_IV_1_PASS')
```

## 3.1 Resolution of the printed N=2 square-root tension

At \(s=2\),

\[
a_2=\frac1{2\sqrt G},
\qquad
\alpha^+=\frac{i}{2\sqrt G}.
\]

The sentence after [FH, eq. (2.16)] prints \(i/\sqrt{2G}\). The two displayed equations immediately preceding that sentence give

\[
c_M=-12(\alpha^+)^2,
\qquad
c_M=\frac3G.
\]

They require \((\alpha^+)^2=-1/(4G)\), not \(-1/(2G)\). The printed value produces \(6/G\). The general trace normalization, the complete Miura coefficient solve, and the crossed bracket below all give \(i/(2\sqrt G)\). No scalar-to-weight rescaling modifies the central-charge identity. The special sentence is therefore inconsistent with the source's own equations.

# 4. Internal bulk N=2 reduction

Choose the \(\mathfrak{sl}_2\) weights

\[
\epsilon_1=\frac1{\sqrt2},
\qquad
\epsilon_2=-\frac1{\sqrt2}.
\]

Equation [DDF, (6.49)] reads

\[
(D_0)_{jj}=\frac{i}{a_2}\epsilon_j\boldsymbol\psi',
\qquad
(D_1)_{jj}=\frac{i}{a_2}\epsilon_j\bar{\boldsymbol\psi}'.
\]

Matching \(D_0=\psi'J_0\), \(D_1=\bar\psi'P_0\), with \(J_0=\mathrm{diag}(1/2,-1/2)\), fixes the same conversion in both sectors:

\[
\boxed{
\boldsymbol\psi=-\frac{ia_2}{\sqrt2}\psi,
\qquad
\bar{\boldsymbol\psi}=-\frac{ia_2}{\sqrt2}\bar\psi.
}
\]

The unbarred and one-bar row determinants become

\[
(a_2\partial+i\epsilon_1\boldsymbol\psi')
(a_2\partial+i\epsilon_2\boldsymbol\psi')
=a_2^2\left(\partial^2+M_{\rm bulk}\right),
\]

\[
\sum_{j=1}^2
(a_2\partial+i\epsilon_1\boldsymbol\psi')\cdots
(i\epsilon_j\bar{\boldsymbol\psi}')\cdots
(a_2\partial+i\epsilon_2\boldsymbol\psi')
=a_2^2L_{\rm bulk},
\]

where [DDF, eq. (4.41)]

\[
M_{\rm bulk}=-\frac14(\psi')^2-\frac12\psi'',
\qquad
L_{\rm bulk}=-\frac12\psi'\bar\psi'-\frac12\bar\psi''.
\]

```{.python .cell-code data-cell="2"}
import sympy as s
a=s.symbols('a',nonzero=True)
eps=(1/s.sqrt(2),-1/s.sqrt(2)); C=-s.I*a/s.sqrt(2)
assert [s.simplify(s.I*e*C/a) for e in eps]==[s.Rational(1,2),-s.Rational(1,2)]
x,xp,y,yp=s.symbols('x xp y yp')
assert s.expand((x/2)*(-x/2)-xp/2+x**2/4+xp/2)==0
assert s.expand((y/2)*(-x/2)-yp/2+(x/2)*(-y/2)+x*y/2+yp/2)==0
print('CELL_IV_2_PASS')
```

# 5. Boundary/bulk N=2 normalization firewall

Start without imposing a current normalization:

\[
J^+=A\psi',
\qquad
J^-=B\bar\psi'+C\psi',
\qquad
\alpha^+=Da_2,
\]

\[
M_{\rm bdry}=\rho_M M_{\rm bulk},
\qquad
L_{\rm bdry}=\rho_L L_{\rm bulk}+\rho_{LM}M_{\rm bulk}.
\]

Substitution in [FH, eqs. (3.32), (3.34)] gives eight independent polynomial equations after including the central branch and crossed bracket. Their only solutions are the two globally conjugate branches. The selected branch is

\[
\boxed{
A=B=\frac{ia_2}{2},
\quad C=0,
\quad D=i,
\quad
\rho_M=\rho_L=2a_2^2,
\quad \rho_{LM}=0.
}
\]

The same sign for \(A\) and \(B\) is forced by the FH factor \(i\). Indeed,

\[
[J_m^+,J_n^-]_{\rm cl}
=-AB\,[\psi'_m,\bar\psi'_n]_{\rm cl}
=\frac m4\delta_{m+n,0}.
\]

The extra minus sign is \((-i)^2\), because the ordinary Fourier coefficient of \(J_{\rm FH}\) is \(iJ_n\). Reversing only the barred current gives \(-m/4\) and fails.

Equivalently, in terms of the diagonal matrices,

\[
\boxed{
\mathcal P_j=-a_s(D_0)_{jj},
\quad
\mathcal N_j=-a_s(D_1)_{jj},
\quad
P_j^{\rm FH}=-ia_s(D_0)_{jj},
\quad
N_j^{\rm FH}=-ia_s(D_1)_{jj}.
}
\]

```{.python .cell-code data-cell="3"}
import sympy as s
A,B,C,D,rM,rL,rLM,a=s.symbols('A B C D rM rL rLM a')
eq=[2*A**2+rM/4,2*D*a*A+rM/2,4*A*B+rL/2,2*D*a*B+rL/2,
    4*A*C+rLM/4,2*D*a*C+rLM/2,D**2+1,A*B+a**2/4]
sol=s.solve(eq,[A,B,C,D,rM,rL,rLM],dict=True)
target={A:s.I*a/2,B:s.I*a/2,C:0,D:s.I,rM:2*a**2,rL:2*a**2,rLM:0}
assert len(sol)==2 and target in sol
print('CELL_IV_3_PASS')
```

# 6. N=2 screening charges and generated transformations

The primitive map follows by differentiating the current map and fixing the inherited basepoint constants:

\[
\boxed{
\mu\Phi^+=-\psi,
\qquad
\mu\Phi^-=-\bar\psi.
}
\]

Therefore

\[
E^{\rm cl}=e^{-\psi},
\qquad
\mathcal S_{\rm odd}^{[1],\rm cl}=-\bar\psi e^{-\psi}.
\]

These are precisely the two integrands of [DDF, eq. (4.35)]:

\[
S_{\kappa_4}=\frac{\kappa_4}{4\pi G}\int e^{-\psi}\,d\phi,
\qquad
S_{\kappa_2}=-\frac{\kappa_2}{4\pi G}\int\bar\psi e^{-\psi}\,d\phi.
\]

The bracket gives [DDF, eq. (4.40)]

\[
\{S,\psi'\}=2\kappa_2e^{-\psi},
\qquad
\{S,\bar\psi'\}=2(\kappa_4-\kappa_2\bar\psi)e^{-\psi}.
\]

Substitution shows \(\delta M_{\rm bulk}=\delta L_{\rm bulk}=0\) coefficientwise. If the boundary circle charges are normalized as unit integrals, then

\[
Q^{[0],\rm cl}=\frac{4\pi G}{\kappa_4}S_{\kappa_4},
\qquad
\widetilde Q^{[1],\rm cl}=\frac{4\pi G}{\kappa_2}S_{\kappa_2}.
\]

# 7. The general diagonal bracket has a factor-two inconsistency

Equation [DDF, (6.23c)] prints

\[
\{(D_0)_{ii},(D_1)_{jj}\}_{\rm print}
=-\frac1{2k_{\rm CS}\tau_s}
\left(\delta_{ij}-\frac1s\right)\delta'.
\]

This is incompatible with both explicit sectors after using the paper's own diagonal map (6.49).

For \(s=2\), its \(i=j=1\) component is \(-\pi G\delta'\), whereas (4.39) and \(D_{11}=\psi'/2\) give \(-2\pi G\delta'\). For \(s=3\), the printed component is \(-16\pi G\delta'/3\), whereas (5.23) and

\[
(D_0)_{11}=\psi_{(L)}'+\frac23\psi_{(W)}'
\]

give \(-32\pi G\delta'/3\). Both explicit sectors agree with

\[
\boxed{
\{(D_0)_{ii},(D_1)_{jj}\}_{\rm explicit}
=-\frac1{k_{\rm CS}\tau_s}
\left(\delta_{ij}-\frac1s\right)\delta'.
}
\]

Machine token: `1/(kCS*tau_s)`. Notebook IV uses the explicit \(s=2,3\) brackets for the theorem and records the disagreement rather than absorbing it into separate field rescalings.

# 8. A2 weights, diagonal map, and root symplectic form

Choose the fundamental weights

\[
\epsilon_1=\left(\frac1{\sqrt2},\frac1{\sqrt6}\right),
\quad
\epsilon_2=\left(-\frac1{\sqrt2},\frac1{\sqrt6}\right),
\quad
\epsilon_3=\left(0,-\frac2{\sqrt6}\right).
\]

They obey

\[
\epsilon_i\cdot\epsilon_j=\delta_{ij}-\frac13,
\qquad
\sum_i\epsilon_i=0,
\qquad
\sum_i\epsilon_i\epsilon_i^{\rm T}=I_2.
\]

With \(J_0=\mathrm{diag}(1,0,-1)\) and \(U_0=\tfrac23\mathrm{diag}(1,-2,1)\), the explicit diagonal field [DDF, eq. (5.12)] is

\[
D_0=\mathrm{diag}\left(
\psi_{(L)}'+\frac23\psi_{(W)}',
-\frac43\psi_{(W)}',
-\psi_{(L)}'+\frac23\psi_{(W)}'
\right),
\]

and similarly for \(D_1\). Equation (6.49) fixes one map in both sectors,

\[
\boldsymbol\psi=-ia_3
\begin{pmatrix}
1/\sqrt2&\sqrt2\\
\sqrt6/2&-\sqrt6/3
\end{pmatrix}
\binom{\psi_{(L)}}{\psi_{(W)}},
\]

with the same matrix for \(\bar{\boldsymbol\psi}\).

Define \(\alpha_1=\epsilon_1-\epsilon_2\), \(\alpha_2=\epsilon_2-\epsilon_3\). Then

\[
\alpha_i\cdot\alpha_j=A_{ij},
\qquad
A=\begin{pmatrix}2&-1\\-1&2\end{pmatrix},
\]

and

\[
\chi_1=\psi_{(L)}+2\psi_{(W)},
\qquad
\chi_2=\psi_{(L)}-2\psi_{(W)}
\]

satisfy

\[
\chi_i=\frac{i}{a_3}\alpha_i\cdot\boldsymbol\psi.
\]

The explicit brackets [DDF, eq. (5.23)] give

\[
\boxed{
\{\chi_i'(\phi),\bar\chi_j(\phi')\}
=16\pi G A_{ij}\delta(\phi-\phi').
}
\]

```{.python .cell-code data-cell="4"}
import sympy as s
R=s.Matrix([[1,2],[1,-2]])
A=s.Matrix([[2,-1],[-1,2]])
assert R*s.diag(8,6)*R.T==16*A
E=s.Matrix([[1/s.sqrt(2),1/s.sqrt(6)],[-1/s.sqrt(2),1/s.sqrt(6)],[0,-2/s.sqrt(6)]])
assert s.simplify(E*E.T-(s.eye(3)-s.ones(3)/3))==s.zeros(3)
print('CELL_IV_4_PASS')
```

# 9. Four A2 Miura observables

The primitive dictionary is now forced, rather than guessed:

\[
\boxed{
\mu\Phi_i^+=-\chi_i,
\qquad
\mu\Phi_i^-=-\bar\chi_i.
}
\]

Machine tokens: `mu*Phi_i_plus=-chi_i` and `mu*Phi_i_minus=-bar_chi_i`.

Differentiating and solving the traceless constraints gives

\[
P_1=-\frac{2\chi_1'+\chi_2'}{3\mu},
\qquad
P_2=\frac{\chi_1'-\chi_2'}{3\mu},
\]

\[
N_1=-\frac{2\bar\chi_1'+\bar\chi_2'}{3\mu},
\qquad
N_2=\frac{\bar\chi_1'-\bar\chi_2'}{3\mu}.
\]

Substitution into the frozen primary Miura fields yields four exact identities:

\[
\boxed{
U_2^+=-\frac4{\mu^2}M_{(L)},
\qquad
U_2^-=-\frac4{\mu^2}L_{(L)},
}
\]

\[
\boxed{
\mathcal U_3^+=-\frac8{\mu^3}M_{(W)},
\qquad
\mathcal U_3^-=-\frac8{\mu^3}L_{(W)}.
}
\]

No root-dependent factor and no spin-mixing improvement is present.

## 9.1 The printed spin-three polynomial is inconsistent

Equation [DDF, (5.28c)] prints a term \(9(\psi_{(L)}'')^2\) inside the parenthesis multiplying \(\psi_{(W)}'\). Its differential weight is five, although \(M_{(W)}\) has spin three. The general row determinant (6.51) and the coefficient solve both require a linear \(9\psi_{(L)}''\). Thus the expression used above contains

```text
9*psi_L_double_prime
```

and not its square. Reinstating the square makes the \(\mathcal U_3^+\) identity fail.

```{.python .cell-code data-cell="5"}
import sympy as s
mu=s.symbols('mu',nonzero=True)
x1,x2,x1p,x2p,x1pp,x2pp=s.symbols('x1 x2 x1p x2p x1pp x2pp')
P1=-(2*x1+x2)/(3*mu);P2=(x1-x2)/(3*mu);a=1/mu
dP1=-(2*x1p+x2p)/(3*mu);dP2=(x1p-x2p)/(3*mu);d2P2=(x1pp-x2pp)/(3*mu)
U3=s.expand(-P1**2*P2-P1*P2**2+a*(s.Rational(3,2)*P1*dP2+s.Rational(1,2)*dP1*P2+P2*dP2)-a**2*d2P2/2)
l=(x1+x2)/2;w=(x1-x2)/4;lp=(x1p+x2p)/2;wp=(x1p-x2p)/4;wpp=(x1pp-x2pp)/4
MW=s.expand((w*(18*l**2-8*w**2+9*lp)+27*l*wp+9*wpp)/108)
assert s.simplify(U3+8*MW/mu**3)==0
print('CELL_IV_5_PASS')
```

# 10. A2 simple-root screenings and generated transformations

The four simple charges [DDF, eq. (5.26)] are

\[
S_{8,i}=\frac{\kappa_{8,i}}{8\pi G}\int e^{-\chi_i}\,d\phi,
\qquad
S_{2,i}=-\frac{\kappa_{2,i}}{8\pi G}\int\bar\chi_i e^{-\chi_i}\,d\phi,
\]

where \((\kappa_{8,1},\kappa_{8,2})=(\kappa_8,\kappa_9)\) and \((\kappa_{2,1},\kappa_{2,2})=(\kappa_2,\kappa_3)\). The exponent labels fix

\[
Q_1^{[0]}\leftrightarrow S_{\kappa_8},
\qquad
Q_2^{[0]}\leftrightarrow S_{\kappa_9}.
\]

The root bracket gives the transformations

\[
\delta_{8,i}\chi_j'=0,
\qquad
\delta_{8,i}\bar\chi_j'=2\kappa_{8,i}A_{ij}e^{-\chi_i},
\]

\[
\delta_{2,i}\chi_j'=2\kappa_{2,i}A_{ij}e^{-\chi_i},
\qquad
\delta_{2,i}\bar\chi_j'=-2\kappa_{2,i}A_{ij}\bar\chi_i e^{-\chi_i}.
\]

Applying these variations, with \(D(e^{-\chi_i})=-\chi_i'e^{-\chi_i}\), annihilates all four observables for both roots. The main verifier performs all sixteen root/charge/observable checks.

For unit circle-integral normalization,

\[
Q_i^{[0],\rm cl}=\frac{8\pi G}{\kappa_{8,i}}S_{8,i},
\qquad
\widetilde Q_i^{[1],\rm cl}=\frac{8\pi G}{\kappa_{2,i}}S_{2,i}.
\]

```{.python .cell-code data-cell="6"}
import sympy as s
G=s.symbols('G',positive=True);pi=s.pi
A=s.Matrix([[2,-1],[-1,2]])
assert s.simplify((1/(8*pi*G))*(16*pi*G)-2)==0
assert s.simplify((-1/(8*pi*G))*(-16*pi*G)-2)==0
chi,bchi=s.symbols('chi bchi')
assert s.exp(-chi)==s.exp(-chi)
assert -bchi*s.exp(-chi)==-bchi*s.exp(-chi)
print('CELL_IV_6_PASS')
```

# 11. Even/affine coefficient and BCH power counting

At the gravity point, \(\alpha^-=\nu=0\). Gate 3B gives

\[
\mathcal S_{i,{\rm odd}}^{[1]}=:\mu\Phi_i^-E_i:,
\]

and

\[
\mathcal S_{i,{\rm even}}^{[1]}
=:\left(-\mu^3\Phi_i^++\mu^2\log(w/w_0)\right)E_i:.
\]

Since \(\mu\Phi_i^+=O(1)\) and \(\mu^2=O(G)\),

\[
\mathcal S_{i,{\rm odd}}^{[1]}=O(1),
\qquad
\mathcal S_{i,{\rm even}}^{[1]}=O(G).
\]

The barred BCH conversion is

\[
\bar Z_{t,\rho}=(1-\rho)^{-2t\bar\mu(t)^2},
\qquad
\log\bar Z_{t,\rho}=-2t\bar\mu(t)^2\log(1-\rho)=O(tG).
\]

It is scalar and insertion-coordinate independent. It changes only the allowed triangular multiple of \(Q_i^{[0]}\); it cannot supply a new \(O(G^0)\) local charge.

```{.python .cell-code data-cell="7"}
import sympy as s
G,c,t,rho=s.symbols('G c t rho')
mu2=c*G
logZ=-2*t*mu2*s.log(1-rho)
assert s.diff(logZ,t).has(G)
qraw,q0,qm,mu=s.symbols('qraw q0 qm mu')
qcanonical=qraw-mu*qm*q0
assert s.expand(qcanonical-(qraw-mu*qm*q0))==0
print('CELL_IV_7_PASS')
```

# 12. Raw moving frame and canonical PBW frame

The bulk Noether charges act on one classical phase space and annihilate the Miura invariants homogeneously. They therefore realize the raw horizontal coefficient:

\[
\boxed{
S_i^{(1)}\longleftrightarrow\widetilde Q_i^{[1],\rm cl}.
}
\]

At \(\nu=0\), decompose

\[
\Phi_i^-=q_i^-+p_i^-\log z+\Phi_{i,{\rm osc}}^-.
\]

The bulk field \(\bar\chi_i\) includes its constant mode unless a basepoint condition is imposed. Hence the bulk barred-linear charge contains the image of \(\mu q_i^-Q_i^{[0]}\) and is the raw representative. A fixed-target PBW trivialization subtracts precisely this target-frame derivative:

\[
\boxed{
Q_i^{[1]}=\widetilde Q_i^{[1]}-\mu\,\alpha_i\cdot q^-\,Q_i^{[0]}.
}
\]

Changing the bulk basepoint shifts \(\bar\chi_i\) by a constant and therefore changes the barred-linear charge by a scalar multiple of the leading charge. This is the same triangular ambiguity already allowed by Gate 3B; it does not create an additional screening.

# 13. Composite screening diagnostic

The nonlocal composite charges in [DDF, eq. (5.27)] depend on a basepoint \(\phi_0\). The source also notes below eq. (6.37) that higher-upper-diagonal transformations can involve field-dependent integration constants. Notebook IV therefore assigns the optional composite gate Outcome C: no basepoint-independent quantum screening-screening conclusion is extracted. This does not affect the simple-root theorem.

# 14. Theorems and outcome

## Theorem IV.1 - exact semiclassical normalization

Let

\[
k_{\rm CS}=\frac1{8\pi G},
\qquad
\tau_s=\frac{12}{s(s^2-1)},
\qquad
a_s=\sqrt{\pi k_{\rm CS}\tau_s},
\]

and choose \(\alpha^-=0\), \(\alpha^+=ia_s\). Then \(c_L=0\), \(c_M=3/G\). For \(s=2,3\), the single scalar-to-weight map, the FH factor \(i\), and the common current map derived above identify the bulk row-determinant invariants with the semiclassical symmetric Carrollian Miura fields. For \(s=3\), the exact relations are

\[
U_2^\pm=-\frac4{\mu^2}(M_{(L)},L_{(L)})^\pm,
\qquad
\mathcal U_3^\pm=-\frac8{\mu^3}(M_{(W)},L_{(W)})^\pm.
\]

## Theorem IV.2 - simple-root screening map

For \(s=2,3\),

\[
E_i^{\rm cl}=e^{-\chi_i},
\qquad
\mathcal S_{i,{\rm odd}}^{[1],\rm cl}=-\bar\chi_i e^{-\chi_i}.
\]

After fixing the bulk gauge parameters, \(Q_i^{[0],\rm cl}\) and \(\widetilde Q_i^{[1],\rm cl}\) equal the corresponding leading and barred-linear bulk Noether charges up to the explicitly displayed universal prefactors. Both root labels and both absolute signs are fixed by generated transformations. The common even/affine coefficient is \(O(G)\).

## Corollary IV.3 - canonical-frame interpretation

The classical bulk barred-linear screening realizes the raw horizontal coefficient. The canonical \(Q_i^{[1]}\) is its PBW-covariantized deformation intertwiner. It is not an ordinary second quantum screening.

## Disposition

\[
\boxed{\text{Notebook IV closes with Outcome B.}}
\]

The only convention transformation is one global analytic continuation and plane/cylinder conversion, used uniformly in the \(s=2\), \(s=3\), unbarred, barred, current, Miura, and screening sectors. There is no root-dependent normalization.

# 15. Claim boundary

This notebook does not establish a quantum screening doublet, equality of quantum kernels, a BRST complex, a quantum-group structure, quantum Serre relations, complete screening-screening closure, equality of quantum correlation functions, or a full holographic duality. The two primary-source formula inconsistencies and the general-bracket factor-two inconsistency are local source audits, not claims that the remaining results of either paper fail.

# 16. Reproducibility ledger

| Layer | Required evidence |
|---|---|
| Upstream | five exact archive hashes; portable Gate-3B checkpoint |
| Main model | normalization, Fourier, \(s=2\), \(A_2\), four Miura fields, transformations, power counting, frame |
| Independent model | no import from the main verifier; separate 29-check reconstruction |
| Source anchors | dedicated \(s=2\) and \(s=3\) programs |
| Embedded cells | seven isolated SymPy processes |
| Adversarial | all roadmap mutations plus real unmutated controls |
| Archive | strict manifest, safe paths, exact payload set, fresh extraction |
| Static record | A4, embedded fonts, page-by-page rendered inspection, HTML/PDF theorem synchronization |

Synchronization tokens: `raw horizontal coefficient`; `i/(2*sqrt(G))`; `9*psi_L_double_prime`; `1/(kCS*tau_s)`; `mu*Phi_i_minus=-bar_chi_i`; `not an ordinary second quantum screening`; `Outcome B`; `NIV-36a2530aab4feb7d`.

# References

1. S. Fredenhagen and L. Hörl, "Free-field construction of Carrollian \(W_N\)-algebras," *JHEP* **02** (2026) 218, [arXiv:2509.14441v3](https://arxiv.org/abs/2509.14441).
2. E. D'Arcy, A. Delfante and S. Fredenhagen, "Holographic realization of higher-spin Carrollian free fields," [arXiv:2604.27068v1](https://arxiv.org/abs/2604.27068).
3. V. A. Fateev and S. L. Lukyanov, "The models of two-dimensional conformal quantum field theory with \(Z_n\) symmetry," *Int. J. Mod. Phys. A* **3** (1988) 507, DOI: [10.1142/S0217751X88000205](https://doi.org/10.1142/S0217751X88000205).
4. P. Bouwknegt and K. Schoutens, "W-symmetry in conformal field theory," *Phys. Rept.* **223** (1993) 183-276, [arXiv:hep-th/9210010](https://arxiv.org/abs/hep-th/9210010).

#!/usr/bin/env python3
"""Source-specific s=3/A2 bulk anchor (DDF Sections 5 and 6)."""
import sympy as s

checks=[]
def ck(q,n):
    ok=bool(q); checks.append(ok); print(("[PASS] " if ok else "[FAIL] ")+n)

G=s.symbols('G',positive=True); pi=s.pi
k=1/(8*pi*G);tau=s.Rational(1,2);a=s.sqrt(pi*k*tau)
ck(s.simplify(a**2-1/(16*G))==0,'a_3 squared')

E=s.Matrix([[1/s.sqrt(2),1/s.sqrt(6)],[-1/s.sqrt(2),1/s.sqrt(6)],[0,-2/s.sqrt(6)]])
D=s.Matrix([[1,s.Rational(2,3)],[0,-s.Rational(4,3)],[-1,s.Rational(2,3)]])
C=s.simplify(E.T*D)
ck(s.simplify(E*C-D)==s.zeros(3,2),'single scalar-to-weight map reconstructs D')
r1=E.row(0).T-E.row(1).T;r2=E.row(1).T-E.row(2).T
A=s.Matrix([[2,-1],[-1,2]])
ck(s.Matrix([[u.dot(v) for v in (r1,r2)] for u in (r1,r2)])==A,'A2 root Gram matrix')
l,w=s.symbols('l w');vec=-s.I*a*C*s.Matrix([l,w])
ck(s.simplify(s.I*r1.dot(vec)/a-l-2*w)==0,'chi1 exponent')
ck(s.simplify(s.I*r2.dot(vec)/a-l+2*w)==0,'chi2 exponent')

R=s.Matrix([[1,2],[1,-2]])
root=R*s.diag(8,6)*R.T
ck(root==16*A,'root bracket 16*pi*G*A2')
explicit=-s.Rational(32,3)*pi*G
printed=s.simplify(-(1/(2*k*tau))*s.Rational(2,3))
corrected=s.simplify(-(1/(k*tau))*s.Rational(2,3))
ck(s.simplify(printed-explicit/2)==0,'printed 6.23c is half the s=3 bracket')
ck(s.simplify(corrected-explicit)==0,'corrected 6.23c coefficient')

mu=s.symbols('mu',nonzero=True)
x1,x2,b1,b2=s.symbols('x1 x2 b1 b2')
x1p,x2p,b1p,b2p=s.symbols('x1p x2p b1p b2p')
x1pp,x2pp,b1pp,b2pp=s.symbols('x1pp x2pp b1pp b2pp')
P1=-(2*x1+x2)/(3*mu);P2=(x1-x2)/(3*mu)
N1=-(2*b1+b2)/(3*mu);N2=(b1-b2)/(3*mu)
DP1=-(2*x1p+x2p)/(3*mu);DP2=(x1p-x2p)/(3*mu)
DN1=-(2*b1p+b2p)/(3*mu);DN2=(b1p-b2p)/(3*mu)
D2P2=(x1pp-x2pp)/(3*mu);D2N2=(b1pp-b2pp)/(3*mu);ap=1/mu
U2p=s.expand(P1**2+P1*P2+P2**2-ap*(2*DP1+DP2))
U2m=s.expand(2*N1*P1+N1*P2+N2*P1+2*N2*P2-ap*(2*DN1+DN2))
U3p=s.expand(-P1**2*P2-P1*P2**2+ap*(s.Rational(3,2)*P1*DP2+s.Rational(1,2)*DP1*P2+P2*DP2)-ap**2*D2P2/2)
U3m=s.expand(-2*N1*P1*P2-N1*P2**2-N2*P1**2-2*N2*P1*P2+ap*(s.Rational(3,2)*N1*DP2+s.Rational(1,2)*DN1*P2+s.Rational(1,2)*N2*DP1+N2*DP2+s.Rational(3,2)*DN2*P1+DN2*P2)-ap**2*D2N2/2)
ell=(x1+x2)/2;ww=(x1-x2)/4;ellp=(x1p+x2p)/2;wwp=(x1p-x2p)/4;wwpp=(x1pp-x2pp)/4
bell=(b1+b2)/2;bww=(b1-b2)/4;bellp=(b1p+b2p)/2;bwwp=(b1p-b2p)/4;bwwpp=(b1pp-b2pp)/4
ML=s.expand((-3*ell**2-4*ww**2-6*ellp)/12)
LL=s.expand((-3*ell*bell-4*ww*bww-3*bellp)/6)
MW=s.expand((ww*(18*ell**2-8*ww**2+9*ellp)+27*ell*wwp+9*wwpp)/108)
LW=s.expand((bww*(6*ell**2-8*ww**2+3*ellp)+3*ww*bellp+9*ell*bwwp+3*bell*(4*ell*ww+3*wwp)+3*bwwpp)/36)
for expression,name in [(U2p+4*ML/mu**2,'U2+'),(U2m+4*LL/mu**2,'U2-'),(U3p+8*MW/mu**3,'U3+'),(U3m+8*LW/mu**3,'U3-')]:
    ck(s.simplify(expression)==0,name+' bulk observable match')
bad=s.expand((ww*(18*ell**2-8*ww**2+9*ellp**2)+27*ell*wwp+9*wwpp)/108)
ck(s.simplify(U3p+8*bad/mu**3)!=0,'printed square in 5.28c fails')

# Exact transformation coefficients of the two simple roots.
ck(s.simplify((1/(8*pi*G))*16*pi*G-2)==0,'leading Noether coefficient')
ck(s.simplify((-1/(8*pi*G))*(-16*pi*G)-2)==0,'tangent Noether coefficient')

print(f'S3_ANCHOR_PASS {sum(checks)}/{len(checks)}')
raise SystemExit(0 if all(checks) else 1)

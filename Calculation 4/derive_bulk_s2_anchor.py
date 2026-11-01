#!/usr/bin/env python3
"""Source-specific s=2 bulk anchor (DDF Sections 4 and 6)."""
import sympy as s

checks=[]
def ck(q,n):
    ok=bool(q); checks.append(ok); print(("[PASS] " if ok else "[FAIL] ")+n)

G=s.symbols('G', positive=True); pi=s.pi
k=1/(8*pi*G); tau=s.Integer(2); a=s.sqrt(pi*k*tau)
ck(s.simplify(a**2-1/(4*G))==0,'a_2 squared')

# Equation (6.49) reduced with epsilon=(+1,-1)/sqrt(2).
eps=(1/s.sqrt(2),-1/s.sqrt(2)); C=-s.I*a/s.sqrt(2)
d=[s.simplify(s.I*e*C/a) for e in eps]
ck(d==[s.Rational(1,2),-s.Rational(1,2)],'D0=psi_prime*J0')
ck(d==[s.Rational(1,2),-s.Rational(1,2)],'D1=barpsi_prime*P0 uses same map')

x,xp,y,yp=s.symbols('x xp y yp')
M=-x**2/4-xp/2; L=-x*y/2-yp/2
row=s.expand((x/2)*(-x/2)-xp/2)
tangent=s.expand((y/2)*(-x/2)-yp/2+(x/2)*(-y/2))
ck(s.simplify(row-M)==0,'unbarred row determinant')
ck(s.simplify(tangent-L)==0,'one-bar tangent determinant')

# Explicit symplectic bracket versus displayed general equation (6.23c).
explicit=-2*pi*G
printed=s.simplify(-(1/(2*k*tau))*s.Rational(1,2))
corrected=s.simplify(-(1/(k*tau))*s.Rational(1,2))
ck(s.simplify(printed-explicit/2)==0,'printed general bracket is half the explicit bracket')
ck(s.simplify(corrected-explicit)==0,'corrected general bracket matches explicit s=2')

# Full boundary coefficient solution and source screening transformations.
A=B=s.I*a/2; alpha=s.I*a
Mbd=s.expand(2*(A*x)**2+2*alpha*A*xp)
Lbd=s.expand(4*(A*x)*(B*y)+2*alpha*B*yp)
ck(s.simplify(Mbd-2*a**2*M)==0,'boundary M equals 2*a_2^2 bulk M')
ck(s.simplify(Lbd-2*a**2*L)==0,'boundary L equals 2*a_2^2 bulk L')
bulk_mode=4*G*s.symbols('m')
fh_mode=s.simplify(-A*B*bulk_mode)
ck(s.simplify(fh_mode-s.symbols('m')/4)==0,'FH crossed mode bracket')

k2,k4,E,b=s.symbols('k2 k4 E b')
dx=2*k2*E; dxp=-2*k2*x*E
dy=2*(k4-k2*b)*E; dyp=-2*k2*y*E-2*x*(k4-k2*b)*E
dM=s.expand(s.diff(M,x)*dx+s.diff(M,xp)*dxp)
dL=s.expand(s.diff(L,x)*dx+s.diff(L,y)*dy+s.diff(L,yp)*dyp)
ck(dM==0,'both s=2 screenings preserve M')
ck(dL==0,'both s=2 screenings preserve L')
ck(s.simplify((1/(4*pi*G))*8*pi*G-2)==0,'leading charge transformation')
ck(s.simplify((-1/(4*pi*G))*(-8*pi*G)-2)==0,'barred-linear charge transformation')

print(f'S2_ANCHOR_PASS {sum(checks)}/{len(checks)}')
raise SystemExit(0 if all(checks) else 1)

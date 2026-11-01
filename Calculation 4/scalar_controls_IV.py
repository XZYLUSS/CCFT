#!/usr/bin/env python3
"""Twelve small exact controls, intentionally separate from both symbolic reconstructions."""
from fractions import Fraction

checks = []
def ck(condition, name):
    ok=bool(condition); checks.append(ok); print(("[PASS] " if ok else "[FAIL] ")+name)

# Coefficients are stored after stripping the common powers of pi and G.
ck(Fraction(1,8)*2 == Fraction(1,4), "a2^2 coefficient")
ck(Fraction(1,8)*Fraction(1,2) == Fraction(1,16), "a3^2 coefficient")
ck(2*2*(2**2-1)*Fraction(1,4) == 3, "s2 central triangle")
ck(2*3*(3**2-1)*Fraction(1,16) == 3, "s3 central triangle")
ck(Fraction(8,2) == 4, "Fourier delta-prime coefficient")
ck(-Fraction(-1,16)*4 == Fraction(1,4), "FH i-factor crossed bracket")
ck(Fraction(8,1)+4*Fraction(6,1) == 32, "A2 diagonal root bracket")
ck(Fraction(8,1)-4*Fraction(6,1) == -16, "A2 off-diagonal root bracket")
ck(Fraction(32,16) == 2, "A2 leading Noether action")
ck((-Fraction(1,8))*(-16) == 2, "A2 tangent Noether action")
ck(-12*Fraction(-1,4) == 3, "correct FH N2 alpha")
ck(-12*Fraction(-1,2) == 6, "printed FH N2 alpha gives six")

print(f"SCALAR_CONTROLS_IV {sum(checks)}/{len(checks)}")
raise SystemExit(0 if all(checks) and len(checks)==12 else 1)

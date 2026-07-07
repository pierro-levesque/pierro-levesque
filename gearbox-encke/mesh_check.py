import numpy as np, cadquery as cq
from gears import spur_gear, ring_gear

m, PA = 1.5, 20.0
Zs, Zp, Zr = 21, 21, 63
CR = m*(Zs+Zp)/2.0
BL = 0.014          # backlash angulaire (rad)

sun    = spur_gear(m, Zs, 16, PA, bore=0, bl=BL)
planet = spur_gear(m, Zp, 16, PA, bore=8, bl=BL)

half_ring_pitch = np.pi/Zr          # demi-pas couronne (rad)

def interf(rot_ring):
    ring = ring_gear(m, Zr, 16, 56, PA, bl=BL, rot=rot_ring)
    p0 = planet.translate((CR, 0, 0))
    # soleil <-> planete0
    v_sp = sun.intersect(p0).Volume() if sun.intersect(p0).Solids() else 0.0
    # planete0 <-> couronne
    int_pr = p0.intersect(ring)
    v_pr = int_pr.Volume() if int_pr.Solids() else 0.0
    return v_sp, v_pr

for rr in [0.0, half_ring_pitch, -half_ring_pitch]:
    v_sp, v_pr = interf(rr)
    print(f"ring_rot={np.degrees(rr):+6.3f} deg | overlap soleil-planete={v_sp:9.4f} mm3 | planete-couronne={v_pr:9.4f} mm3")

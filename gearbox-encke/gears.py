import numpy as np
import cadquery as cq

def involute_profile(m, z, pa_deg=20.0, add=1.0, ded=1.25, internal=False, seg=6):
    """Return list of (x,y) points of a closed involute spur gear profile.
    External: teeth point outward. Internal: material boundary of a ring bore
    (teeth point inward)."""
    a = np.radians(pa_deg)
    rp = m * z / 2.0
    rb = rp * np.cos(a)
    if not internal:
        ra = rp + add * m          # tip (outer)
        rf = rp - ded * m          # root (inner)
    else:
        ra = rp - add * m          # tip (inner)
        rf = rp + ded * m          # root (outer)

    def inv(al):
        return np.tan(al) - al

    inv_p = inv(a)
    s_half = np.pi / (2.0 * z)     # angular half tooth thickness at pitch

    def phi(r):
        r = np.maximum(r, rb + 1e-9)
        al_r = np.arccos(np.clip(rb / r, -1, 1))
        return s_half + inv_p - inv(al_r)

    # radii samples along a flank (from root to tip for external)
    r_lo, r_hi = (min(ra, rf), max(ra, rf))
    r_start = max(r_lo, rb)        # involute only valid above base circle
    rs = np.linspace(r_start, r_hi, seg * 6)

    pts = []
    pitch_ang = 2.0 * np.pi / z
    for k in range(z):
        c = k * pitch_ang
        # For external: go root->tip on left flank (angle c-phi), then tip arc,
        # then tip->root on right flank (angle c+phi). "left/right" & radial dir
        # differ for internal but the same construction yields a valid closed loop.
        if not internal:
            # left flank: root(rf) -> tip(ra)
            for r in np.linspace(rf, ra, seg * 3):
                ph = phi(r) if r >= rb else phi(rb)
                pts.append((r * np.cos(c - ph), r * np.sin(c - ph)))
            # tip arc ra: -phi(ra) -> +phi(ra)
            pa_t = phi(ra)
            for t in np.linspace(-pa_t, pa_t, seg):
                pts.append((ra * np.cos(c + t), ra * np.sin(c + t)))
            # right flank: tip(ra) -> root(rf)
            for r in np.linspace(ra, rf, seg * 3):
                ph = phi(r) if r >= rb else phi(rb)
                pts.append((r * np.cos(c + ph), r * np.sin(c + ph)))
            # root arc rf toward next tooth
            pf = phi(rf) if rf >= rb else phi(rb)
            next_c = (k + 1) * pitch_ang
            npf = phi(rf) if rf >= rb else phi(rb)
            for t in np.linspace(c + pf, next_c - npf, seg):
                pts.append((rf * np.cos(t), rf * np.sin(t)))
        else:
            # internal tooth (material pointing inward). root=rf(outer) tip=ra(inner)
            for r in np.linspace(rf, ra, seg * 3):
                ph = phi(r)
                pts.append((r * np.cos(c - ph), r * np.sin(c - ph)))
            pa_t = phi(ra)
            for t in np.linspace(-pa_t, pa_t, seg):
                pts.append((ra * np.cos(c + t), ra * np.sin(c + t)))
            for r in np.linspace(ra, rf, seg * 3):
                ph = phi(r)
                pts.append((r * np.cos(c + ph), r * np.sin(c + ph)))
            pf = phi(rf)
            next_c = (k + 1) * pitch_ang
            for t in np.linspace(c + pf, next_c - pf, seg):
                pts.append((rf * np.cos(t), rf * np.sin(t)))
    # remove consecutive duplicates (zero-length edges break the kernel)
    clean = [pts[0]]
    for p in pts[1:]:
        if (p[0] - clean[-1][0])**2 + (p[1] - clean[-1][1])**2 > 1e-8:
            clean.append(p)
    if (clean[0][0]-clean[-1][0])**2 + (clean[0][1]-clean[-1][1])**2 < 1e-8:
        clean.pop()
    return clean


def spur_gear(m, z, width, pa=20.0, bore=0.0):
    pts = involute_profile(m, z, pa, internal=False)
    wp = cq.Workplane("XY").polyline(pts).close()
    g = wp.extrude(width)
    if bore > 0:
        g = g.faces(">Z").workplane().hole(bore)
    return g.val()


def ring_gear(m, z, width, outer_r, pa=20.0):
    inner = involute_profile(m, z, pa, internal=True)
    face = (cq.Workplane("XY").circle(outer_r)
            .polyline(inner).close())
    # subtract the toothed bore polygon from the outer disk
    disk = cq.Workplane("XY").circle(outer_r).extrude(width)
    bore = cq.Workplane("XY").polyline(inner).close().extrude(width)
    return disk.cut(bore).val()


if __name__ == "__main__":
    m = 1.5
    sun = spur_gear(m, 21, 16, bore=10)
    planet = spur_gear(m, 21, 16, bore=8)
    ring = ring_gear(m, 63, 16, outer_r=56)
    print("sun vol", sun.Volume())
    print("planet vol", planet.Volume())
    print("ring vol", ring.Volume())
    a = cq.Assembly()
    a.add(sun, name="sun", color=cq.Color("steelblue"))
    a.add(ring, name="ring", color=cq.Color("red"))
    for i in range(3):
        ang = np.radians(i * 120)
        loc = cq.Location(cq.Vector(31.5*np.cos(ang), 31.5*np.sin(ang), 0))
        a.add(planet, name=f"planet{i}", color=cq.Color("green"), loc=loc)
    a.save("/tmp/claude-0/-home-user-pierro-levesque/86c17fdd-666a-5c8f-b19e-bafe50bbde97/scratchpad/test_train.step")
    print("saved test_train.step")

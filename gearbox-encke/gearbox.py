"""
ENCKE - Gearbox planetaire 2 rapports (train epicycloidal integre)
Modele parametrique detaille -> export STEP multi-corps.
Construit d'apres les planches techniques 1/4 .. 4/4.

Reperes :
  Axe machine = Z. Moteur cote -Z, sortie chaine cote +Z.
  Unites = mm.
"""
import numpy as np
import cadquery as cq
from gears import spur_gear, ring_gear, involute_profile

# --------------------------------------------------------------------------
# Parametres de conception (train epicycloidal simple, 2 modes de blocage)
# --------------------------------------------------------------------------
M      = 1.5          # module (mm)
PA     = 20.0         # angle de pression (deg)
Z_SUN  = 21           # dents soleil
Z_PL   = 21           # dents planete
Z_RING = 63           # dents couronne  (= Z_SUN + 2*Z_PL, contrainte coaxiale)
FW     = 16.0         # largeur de denture (face width)

RP_SUN  = M * Z_SUN / 2.0     # 15.75
RP_PL   = M * Z_PL  / 2.0     # 15.75
RP_RING = M * Z_RING / 2.0    # 47.25
CARRIER_R = RP_SUN + RP_PL    # 31.5  rayon cercle des axes de planetes
RING_OUTER = 56.0
BL = 0.030                    # jeu angulaire d'engrenement (rad) - engrene sans interference
RING_CLOCK = np.pi / Z_RING   # demi-pas couronne : phasage pour engrener les planetes

# Phasage (verifie par test d'interference booleen, overlap = 0 mm3) :
#  - planetes a 0/120/240 deg : 120 deg = 7 pas soleil (entier) => engrenent sans
#    rotation propre (Z_SUN impair => cote oppose = creux).
#  - couronne tournee d'un demi-pas (RING_CLOCK) pour presenter un creux a chaque planete.

# Rapport 1 (couronne bloquee) : i = 1 + Z_RING/Z_SUN = 4.0
# Rapport 2 (soleil bloque)    : i = 1 + Z_SUN/Z_RING = 1.33
# (valeurs de reduction donnees "a titre d'exemple" sur les planches)

COL = {
    "input":   cq.Color(0.20, 0.45, 0.80),   # bleu  - entree moteur / soleil
    "planet":  cq.Color(0.25, 0.65, 0.30),   # vert  - planetes
    "carrier": cq.Color(0.95, 0.70, 0.10),   # jaune - porte-planetes / sortie
    "ring":    cq.Color(0.80, 0.20, 0.20),   # rouge - couronne
    "steel":   cq.Color(0.62, 0.64, 0.67),
    "housing": cq.Color(0.75, 0.77, 0.80),
    "dark":    cq.Color(0.35, 0.37, 0.40),
    "black":   cq.Color(0.15, 0.15, 0.17),
}

# --------------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------------
def ball_bearing(d_in, d_out, w, n_balls=8):
    """Roulement a billes simplifie : bague ext + bague int + billes."""
    dm = (d_in + d_out) / 2.0          # diametre moyen
    race = (d_out - d_in) / 2.0
    ball_r = race * 0.30
    outer = (cq.Workplane("XY").circle(d_out/2).circle(d_out/2 - race*0.35)
             .extrude(w))
    inner = (cq.Workplane("XY").circle(d_in/2 + race*0.35).circle(d_in/2)
             .extrude(w))
    parts = [outer.val(), inner.val()]
    for i in range(n_balls):
        a = 2*np.pi*i/n_balls
        b = (cq.Workplane("XY").transformed(offset=cq.Vector(
                dm/2*np.cos(a), dm/2*np.sin(a), w/2)).sphere(ball_r))
        parts.append(b.val())
    return parts, ball_r


def roller_sprocket(z_t, pitch, roller_d, width, bore, hub_d, hub_len):
    """Pignon de sortie chaine (roue a rochet pour chaine a rouleaux)."""
    Rp = pitch / (2*np.sin(np.pi/z_t))          # rayon primitif
    r_out = Rp + 0.6*pitch - roller_d/2*0.0 + roller_d*0.0
    outer_r = Rp * 1.06 + roller_d*0.5
    disk = cq.Workplane("XY").circle(outer_r).extrude(width)
    # sieges de rouleaux
    for i in range(z_t):
        a = 2*np.pi*i/z_t
        disk = disk.cut(
            cq.Workplane("XY").transformed(offset=cq.Vector(
                Rp*np.cos(a), Rp*np.sin(a), 0)).circle(roller_d/2*1.05)
            .extrude(width))
    # creusage entre-dents (vallees) pour degager les flancs
    for i in range(z_t):
        a = 2*np.pi*(i+0.5)/z_t
        disk = disk.cut(
            cq.Workplane("XY").transformed(offset=cq.Vector(
                (outer_r+roller_d*0.2)*np.cos(a),
                (outer_r+roller_d*0.2)*np.sin(a), 0))
            .circle(roller_d*0.55).extrude(width))
    # moyeu + alesage
    hub = cq.Workplane("XY").workplane(offset=width).circle(hub_d/2).extrude(hub_len)
    spr = disk.union(hub)
    spr = spr.faces(">Z").workplane().hole(bore)
    # allegement : 5 trous
    for i in range(5):
        a = 2*np.pi*i/5
        spr = spr.cut(cq.Workplane("XY").transformed(offset=cq.Vector(
            Rp*0.55*np.cos(a), Rp*0.55*np.sin(a), 0)).circle(4).extrude(width))
    return spr.val()


def splined(d_pitch, z, length, bore=0.0, internal=False):
    """Cannelure (accouplement cannele) via micro-denture."""
    m_s = d_pitch / z
    if internal:
        # manchon cannele interieur
        prof = involute_profile(m_s, z, 30.0, add=0.6, ded=0.6, internal=True)
        outer = cq.Workplane("XY").circle(d_pitch/2 + 3).extrude(length)
        bore_s = cq.Workplane("XY").polyline(prof).close().extrude(length)
        return outer.cut(bore_s).val()
    else:
        prof = involute_profile(m_s, z, 30.0, add=0.6, ded=0.6, internal=False)
        g = cq.Workplane("XY").polyline(prof).close().extrude(length)
        if bore > 0:
            g = g.faces(">Z").workplane().hole(bore)
        return g.val()


# --------------------------------------------------------------------------
# Construction des composants
# --------------------------------------------------------------------------
def build():
    asm = cq.Assembly(name="ENCKE_Gearbox_Planetaire_2_Rapports")

    # --- 6. COURONNE INTERNE (ring) --------------------------------------
    ring = ring_gear(M, Z_RING, FW, RING_OUTER, PA, bl=BL, rot=RING_CLOCK)
    # dentelure exterieure de verrouillage (crabot) sur un cote de la couronne
    lockteeth = spur_gear(0.9, 60, 4.0)
    ring_lock = (cq.Workplane("XY").add(lockteeth).translate((0,0,FW))
                 .val())
    asm.add(ring, name="6_couronne_interne", color=COL["ring"],
            loc=cq.Location(cq.Vector(0, 0, 0)))

    # --- 4. SOLEIL (sun) + arbre d'entree --------------------------------
    sun = spur_gear(M, Z_SUN, FW, bore=0, bl=BL)
    sun = (cq.Workplane().add(sun)
           # moyeu arriere
           .union(cq.Workplane("XY").workplane(offset=FW).circle(9).extrude(6))
           # arbre d'entree traversant cote moteur
           .union(cq.Workplane("XY").workplane(offset=-40).circle(7).extrude(40))
           .val())
    # alesage cannele interieur pour accouplement moteur
    sun_bore = cq.Workplane("XY").workplane(offset=-40).circle(5).extrude(30)
    sun = sun.cut(sun_bore.val())
    asm.add(sun, name="4_soleil_arbre_entree", color=COL["input"])

    # --- 1+2. ARBRE MOTEUR + ACCOUPLEMENT CANNELE ------------------------
    motor_shaft = (cq.Workplane("XY").workplane(offset=-95).circle(6.5).extrude(48)
                   .val())
    asm.add(motor_shaft, name="1_arbre_moteur", color=COL["dark"],
            loc=cq.Location(cq.Vector(0, 0, 0)))
    coupler = splined(9.0, 12, 18)
    asm.add(coupler, name="2_accouplement_cannele", color=COL["steel"],
            loc=cq.Location(cq.Vector(0, 0, -55)))

    # --- 5. PLANETES (3x) ------------------------------------------------
    planet = spur_gear(M, Z_PL, FW, bore=8, bl=BL)
    for i in range(3):
        a = np.radians(120*i)
        loc = cq.Location(cq.Vector(CARRIER_R*np.cos(a), CARRIER_R*np.sin(a), 0))
        asm.add(planet, name=f"5_planete_{i+1}", color=COL["planet"], loc=loc)

    # --- 9. PORTE-PLANETES (carrier) + moyeu de sortie -------------------
    # plaque avant (cote moteur)
    front = (cq.Workplane("XY").workplane(offset=-8).circle(CARRIER_R+7)
             .circle(11).extrude(6))
    # plaque arriere (cote sortie)
    rear = (cq.Workplane("XY").workplane(offset=FW+2).circle(CARRIER_R+7)
            .extrude(6))
    # 3 axes de planetes
    pins = cq.Workplane("XY")
    carrier = front.union(rear)
    for i in range(3):
        a = np.radians(120*i)
        pin = cq.Workplane("XY").workplane(offset=-5).transformed(
            offset=cq.Vector(CARRIER_R*np.cos(a), CARRIER_R*np.sin(a), 0)
            ).circle(3.9).extrude(FW+10)
        carrier = carrier.union(pin)
    # moyeu de sortie coaxial (porte le pignon) cote +Z
    hub = (cq.Workplane("XY").workplane(offset=FW+8).circle(12).extrude(30)
           .faces(">Z").workplane().hole(14))
    carrier = carrier.union(hub)
    asm.add(carrier.val(), name="9_porte_planetes_sortie", color=COL["carrier"])

    # --- 3. BOITIER (housing) : tube + 2 flasques ------------------------
    tube = (cq.Workplane("XY").workplane(offset=-12).circle(RING_OUTER+8)
            .circle(RING_OUTER+0.5).extrude(FW+16))
    flasque_av = (cq.Workplane("XY").workplane(offset=-18).circle(RING_OUTER+8)
                  .extrude(6).faces("<Z").workplane().hole(30))
    flasque_ar = (cq.Workplane("XY").workplane(offset=FW+4).circle(RING_OUTER+8)
                  .extrude(6).faces(">Z").workplane().hole(28))
    housing = tube.union(flasque_av).union(flasque_ar)
    # oreilles de fixation
    for i in range(4):
        a = np.radians(45+90*i)
        ear = cq.Workplane("XY").workplane(offset=-2).transformed(
            offset=cq.Vector((RING_OUTER+9)*np.cos(a),(RING_OUTER+9)*np.sin(a),0)
            ).circle(6).extrude(FW).faces(">Z").workplane().hole(6.5)
        housing = housing.union(ear)
    asm.add(housing.val(), name="3_boitier_gearbox", color=COL["housing"])

    # --- 7. ROULEMENTS ---------------------------------------------------
    # roulement d'entree (soleil / arbre moteur)
    b1, _ = ball_bearing(14, 30, 8)
    for j, part in enumerate(b1):
        col = COL["black"] if j >= 2 else COL["steel"]
        asm.add(part, name=f"7_roulement_entree_p{j}", color=col,
                loc=cq.Location(cq.Vector(0, 0, -22)))
    # roulement de sortie (moyeu porte-planetes)
    b2, _ = ball_bearing(24, 44, 9)
    for j, part in enumerate(b2):
        col = COL["black"] if j >= 2 else COL["steel"]
        asm.add(part, name=f"7_roulement_sortie_p{j}", color=col,
                loc=cq.Location(cq.Vector(0, 0, FW+9)))

    # --- 10. PIGNON DE SORTIE CHAINE -------------------------------------
    sprocket = roller_sprocket(z_t=14, pitch=15.875, roller_d=10.16,
                               width=8, bore=14, hub_d=22, hub_len=8)
    asm.add(sprocket, name="10_pignon_sortie_chaine", color=COL["dark"],
            loc=cq.Location(cq.Vector(0, 0, FW+40)))

    # --- MANCHON COULISSANT (dog clutch) + FOURCHETTE --------------------
    sleeve = (cq.Workplane("XY").circle(20).circle(14).extrude(9)
              # gorge pour la fourchette
              .faces(">Z").workplane(offset=-9).circle(22).circle(20).extrude(3)
              )
    dog = spur_gear(0.9, 44, 4.0)  # crabots
    sleeve = sleeve.union(cq.Workplane().add(dog).translate((0,0,9)))
    asm.add(sleeve.val(), name="manchon_coulissant_crabot", color=COL["steel"],
            loc=cq.Location(cq.Vector(0, 0, FW+22)))

    # fourchette de selection : demi-anneau (fourche) engageant la gorge du
    # manchon + bras radial vers l'actionneur.
    yoke = (cq.Workplane("XY").workplane(offset=FW+22)
            .circle(24).circle(20.5)
            .extrude(3))
    # ne garder qu'un secteur (~230 deg) : retirer un coin cote actionneur
    cutwin = (cq.Workplane("XY").workplane(offset=FW+21)
              .moveTo(0, 0).lineTo(40, -18).lineTo(40, 18).close().extrude(5))
    yoke = yoke.cut(cutwin)
    arm = (cq.Workplane("XY").workplane(offset=FW+22)
           .moveTo(22, 0).lineTo(RING_OUTER+22, 0).rect(3, 6, centered=True)
           .extrude(3))
    arm = (cq.Workplane("XY").workplane(offset=FW+22)
           .center((RING_OUTER+22)/2 + 11, 0)
           .box(RING_OUTER, 5, 3, centered=(True, True, False)))
    fork = yoke.union(arm)

    # --- 8. ACTIONNEUR LINEAIRE (verrouillage) ---------------------------
    act_x = RING_OUTER + 22
    act_body = (cq.Workplane("XY").workplane(offset=-6).transformed(
        offset=cq.Vector(act_x, 0, 0)).circle(11).extrude(46))
    act_rod = (cq.Workplane("XY").workplane(offset=40).transformed(
        offset=cq.Vector(act_x, 0, 0)).circle(3.5).extrude(18))
    act_bracket = (cq.Workplane("XY").workplane(offset=-8).transformed(
        offset=cq.Vector(act_x, 0, 0)).box(10, 24, 6, centered=(True,True,False)))
    actuator = act_body.union(act_rod).union(act_bracket)
    # biellette reliant l'actionneur a la fourchette
    link = (cq.Workplane("XY").workplane(offset=FW+22).moveTo(act_x, 0)
            .lineTo(RING_OUTER+6, 0).rect(1, 6).extrude(4))
    asm.add(actuator.val(), name="8_actionneur_lineaire", color=COL["dark"])
    asm.add(fork.val(), name="fourchette_selection", color=COL["carrier"])

    return asm


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "gearbox_encke.step"
    asm = build()
    n = len(list(asm.traverse()))
    print("Composants dans l'assemblage:", n)
    asm.save(out)
    print("STEP ecrit:", out)

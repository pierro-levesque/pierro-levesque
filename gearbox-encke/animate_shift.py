"""
Simulation cinematique du changement de rapport - gearbox planetaire ENCKE.
Vue axiale (dans l'axe Z). Entrainee depuis l'arbre moteur (omega_in constant).
Ratios reels du train : R1 (couronne bloquee) i=4 ; R2 (soleil bloque) i=1.333.
Sortie -> GIF anime.
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle, FancyArrow
from matplotlib.animation import FuncAnimation, PillowWriter
from gears import involute_profile

m, PA = 1.5, 20.0
Zs, Zp, Zr = 21, 21, 63
CR = m*(Zs+Zp)/2.0
RING_CLOCK = np.degrees(np.pi/Zr)     # deg
BETA = [0, 120, 240]

# profils 2D de base (au repos, engrenes)
sun_p    = np.array(involute_profile(m, Zs, PA, bl=0.03))
planet_p = np.array(involute_profile(m, Zp, PA, bl=0.03))
ring_in  = np.array(involute_profile(m, Zr, PA, internal=True, bl=0.03,
                                     rot=np.radians(RING_CLOCK)))
R_OUT = 53.0
theta_c = np.linspace(0, 2*np.pi, 160)
ring_out = np.c_[R_OUT*np.cos(theta_c), R_OUT*np.sin(theta_c)]

C_SUN=(0.20,0.45,0.80); C_PL=(0.25,0.65,0.30); C_CAR=(0.95,0.70,0.10)
C_RING=(0.80,0.20,0.20); C_LOCK=(0.85,0.15,0.15); C_IN=(0.10,0.55,0.20)

def rot(pts, ang_deg):
    a=np.radians(ang_deg); c,s=np.cos(a),np.sin(a)
    return pts @ np.array([[c,s],[-s,c]])

# ---------------- cinematique par integration ------------------------------
OM = 4.0                                  # deg/frame de l'element d'entree
FR_R1, FR_SH, FR_R2 = 70, 26, 70
frames = FR_R1+FR_SH+FR_R2

def phase(i):
    if i < FR_R1: return "R1"
    if i < FR_R1+FR_SH: return "SHIFT"
    return "R2"

# vitesses (deg/frame) par element selon le mode
def rates(ph, prog=0.0):
    if ph=="R1":                          # soleil=entree, couronne bloquee
        return dict(sun=OM, ring=0.0, car=OM/4, pl=-OM/2)
    if ph=="R2":                          # couronne=entree, soleil bloque
        return dict(sun=0.0, ring=OM, car=3*OM/4, pl=1.5*OM)
    # SHIFT : coupure de couple -> tout ralentit (roue libre)
    k=0.12
    return dict(sun=OM*k, ring=0.0, car=OM/4*k, pl=-OM/2*k)

# integration des angles absolus
th=dict(sun=0.0, ring=0.0, car=0.0, pl=0.0)
ANG=[]
for i in range(frames):
    ANG.append(dict(th)); r=rates(phase(i))
    for kk in th: th[kk]+=r[kk]

# actuator position 0..1 (0=R1 couronne, 1=R2 soleil)
def act_pos(i):
    if i<FR_R1: return 0.0
    if i<FR_R1+FR_SH: return (i-FR_R1)/FR_SH
    return 1.0

# ---------------- rendu ----------------------------------------------------
fig=plt.figure(figsize=(15,8)); fig.patch.set_facecolor('white')
axg=fig.add_axes([0.02,0.05,0.60,0.9]); axg.set_aspect('equal'); axg.axis('off')
axg.set_xlim(-58,58); axg.set_ylim(-58,58)
axd=fig.add_axes([0.64,0.05,0.34,0.9]); axd.axis('off')

def ring_patch(ang):
    o=ring_out; ii=rot(ring_in, ang)
    verts=np.vstack([o, o[0], ii, ii[0]])
    codes=([Path.MOVETO]+[Path.LINETO]*(len(o)-1)+[Path.CLOSEPOLY]
           +[Path.MOVETO]+[Path.LINETO]*(len(ii)-1)+[Path.CLOSEPOLY])
    return PathPatch(Path(verts,codes), facecolor=C_RING, edgecolor='k',
                     lw=0.6, alpha=0.95)

def draw(i):
    axg.clear(); axg.set_aspect('equal'); axg.axis('off')
    axg.set_xlim(-58,58); axg.set_ylim(-58,58)
    a=ANG[i]; ph=phase(i)
    # couronne
    lockR = (ph in ("R1","SHIFT"))
    rp=ring_patch(a['ring']); axg.add_patch(rp)
    if lockR:
        axg.add_patch(Circle((0,0),R_OUT+2.5,fill=False,ec=C_LOCK,lw=4))
    # carrier (jaune) : bras + moyeu + axes
    for b in BETA:
        ang=np.radians(b+a['car']); cx,cy=CR*np.cos(ang),CR*np.sin(ang)
        axg.plot([0,cx],[0,cy],color=C_CAR,lw=9,solid_capstyle='round',zorder=2)
    axg.add_patch(Circle((0,0),8,facecolor=C_CAR,ec='k',lw=0.6,zorder=2))
    # planetes (vert)
    for b in BETA:
        ang=np.radians(b+a['car']); cx,cy=CR*np.cos(ang),CR*np.sin(ang)
        pp=rot(planet_p,a['pl'])+[cx,cy]
        axg.add_patch(plt.Polygon(pp,closed=True,facecolor=C_PL,ec='k',lw=0.5,zorder=3))
        axg.add_patch(Circle((cx,cy),3.5,facecolor=C_CAR,ec='k',lw=0.4,zorder=4))
    # soleil (bleu)
    sp=rot(sun_p,a['sun'])
    axg.add_patch(plt.Polygon(sp,closed=True,facecolor=C_SUN,ec='k',lw=0.5,zorder=5))
    if ph=="R2":
        axg.add_patch(Circle((0,0),13,fill=False,ec=C_LOCK,lw=4,zorder=6))
    # marqueur entree moteur (fleche sur l'element entraine)
    if ph=="R1" or ph=="SHIFT":
        axg.annotate("", xy=(0,17),xytext=(0,30),
            arrowprops=dict(arrowstyle='-|>',color=C_IN,lw=3))
        axg.text(0,33,"ENTREE MOTEUR",color=C_IN,ha='center',fontsize=9,weight='bold')
    else:
        axg.annotate("", xy=(0,R_OUT-2),xytext=(0,R_OUT+9),
            arrowprops=dict(arrowstyle='-|>',color=C_IN,lw=3))
        axg.text(0,R_OUT+11,"ENTREE MOTEUR",color=C_IN,ha='center',fontsize=9,weight='bold')
    # marqueur sortie (porte-planetes)
    axg.text(0,-52,"SORTIE = PORTE-PLANETES (pignon chaine)",ha='center',
             fontsize=9,color=(0.6,0.45,0.0),weight='bold')
    if ph=="SHIFT":
        axg.text(0,0,"CHANGEMENT\nDE RAPPORT",ha='center',va='center',
                 fontsize=15,weight='bold',color='k',
                 bbox=dict(boxstyle='round',fc='wheat',ec='k',alpha=0.85),zorder=9)

    # ---------- dashboard ----------
    axd.clear(); axd.axis('off'); axd.set_xlim(0,1); axd.set_ylim(0,1)
    gear = "1" if ph=="R1" else ("2" if ph=="R2" else "—")
    ratio= "4.0 : 1" if ph=="R1" else ("1.33 : 1" if ph=="R2" else "...")
    lockel= "Couronne" if ph in("R1","SHIFT") else "Soleil"
    inel = "Soleil" if ph in("R1","SHIFT") else "Couronne"
    out_speed = 0.25 if ph=="R1" else (0.75 if ph=="R2" else 0.12)
    axd.text(0.5,0.96,"GEARBOX PLANETAIRE ENCKE",ha='center',weight='bold',fontsize=13)
    axd.text(0.5,0.91,"Simulation changement de rapport",ha='center',fontsize=9,color='0.4')
    # gros numero de rapport
    axd.add_patch(plt.Rectangle((0.30,0.68),0.40,0.17,fc=(0.12,0.13,0.15)))
    axd.text(0.5,0.765,gear,ha='center',va='center',fontsize=40,color='w',weight='bold')
    axd.text(0.5,0.64,f"Reduction  {ratio}",ha='center',fontsize=12,weight='bold')
    # tableau etats
    rows=[("Entree moteur",inel,C_IN),
          ("Element bloque",lockel,C_LOCK),
          ("Sortie","Porte-planetes",C_CAR)]
    y=0.55
    for lab,val,col in rows:
        axd.text(0.06,y,lab,fontsize=10,color='0.3')
        axd.text(0.62,y,val,fontsize=10,weight='bold',color=col); y-=0.055
    # barres vitesse
    axd.text(0.06,0.36,"Vitesse arbre moteur (entree)",fontsize=9,color='0.3')
    axd.add_patch(plt.Rectangle((0.06,0.31),0.88,0.03,fc='0.85'))
    axd.add_patch(plt.Rectangle((0.06,0.31),0.88,0.03,fc=C_IN))
    axd.text(0.06,0.24,"Vitesse sortie (pignon chaine)",fontsize=9,color='0.3')
    axd.add_patch(plt.Rectangle((0.06,0.19),0.88,0.03,fc='0.85'))
    axd.add_patch(plt.Rectangle((0.06,0.19),0.88*out_speed,0.03,fc=C_CAR))
    axd.text(0.95,0.19,f"x{out_speed/0.25:.0f}" if ph!="SHIFT" else "",
             fontsize=9,ha='right',va='bottom',color=(0.6,0.45,0))
    # actionneur
    axd.text(0.06,0.11,"Actionneur lineaire",fontsize=9,color='0.3')
    axd.add_patch(plt.Rectangle((0.06,0.06),0.6,0.035,fc='0.85',ec='0.5'))
    axd.add_patch(plt.Rectangle((0.06+0.55*act_pos(i),0.055),0.06,0.045,fc='0.25'))
    axd.text(0.70,0.077,"R1" if act_pos(i)<0.5 else "R2",fontsize=9,va='center')
    return []

anim=FuncAnimation(fig,draw,frames=frames,interval=55,blit=False)
anim.save("shift_simulation.gif",writer=PillowWriter(fps=18),dpi=90)
print("shift_simulation.gif saved,",frames,"frames")

# Gearbox planétaire 2 rapports — intégration moto ENCKE (MotoStudent 2027)

Modèle CAO paramétrique du **train épicycloïdal 2 rapports** décrit dans les
planches techniques du projet ENCKE, exporté au format **STEP (AP214)** pour
import direct dans SolidWorks / CATIA / Fusion 360, etc.

## Fichier livrable

| Fichier | Description |
|---|---|
| `gearbox_encke.step` | Assemblage STEP multi-corps (32 solides, schéma AP214). Unités **mm**. |
| `gearbox.py` | Script paramétrique CadQuery qui construit tout l'assemblage. |
| `gears.py` | Générateur d'engrenages à profil en **développante de cercle** (extérieur + couronne intérieure). |
| `preview_composants.png` | Rendu de chaque composant isolé. |
| `preview_ensemble.png` | Vue d'ensemble assemblée + vue éclatée. |

## Composants modélisés (repères des planches 1/4 → 4/4)

| # | Composant | Détail modèle |
|---|---|---|
| 1 | Arbre moteur | Arbre d'entrée cylindrique côté moteur ENCKE |
| 2 | Accouplement cannelé | Cannelures (micro-denture à 30°) |
| 3 | Boîtier de gearbox | Carter tubulaire + 2 flasques + 4 oreilles de fixation |
| 4 | Soleil (entrée) | Engrenage développante Z=21, arbre + alésage cannelé |
| 5 | Planètes (3×) | Engrenages développante Z=21, alésage d'axe |
| 6 | Couronne interne | Denture **intérieure** développante Z=63 |
| 7 | Roulements | Roulement d'entrée + roulement de sortie (bagues + billes) |
| 8 | Actionneur linéaire | Corps + tige + patte de fixation (verrouillage) |
| 9 | Porte-planètes (sortie) | 2 plateaux + 3 axes de planètes + moyeu de sortie coaxial |
| 10 | Pignon de sortie chaîne | Roue à rouleaux (14 dents, pas 15,875 mm) |
| — | Manchon coulissant / crabot | Dog clutch de sélection de rapport |
| — | Fourchette de sélection | Fourche engageant la gorge du manchon |

## Paramètres du train épicycloïdal

- Module `m = 1.5 mm`, angle de pression `20°`
- `Z_soleil = 21`, `Z_planète = 21`, `Z_couronne = 63`
  (contrainte de coaxialité : `Z_couronne = Z_soleil + 2·Z_planète`, et
  `Z_soleil + Z_couronne = 84` divisible par 3 → 3 planètes équi-réparties)
- Largeur de denture `16 mm`, entraxe planètes `31,5 mm`
- **Rapport 1** (couronne bloquée) : `i = 1 + Z_couronne/Z_soleil = 4,0`
- **Rapport 2** (soleil bloqué) : `i = 1 + Z_soleil/Z_couronne ≈ 1,33`

> Les rapports de réduction indiqués sur les planches (4,10 / 2,15) sont donnés
> *« à titre d'exemple »*. Ils s'ajustent en changeant `Z_SUN` / `Z_RING` dans
> `gearbox.py` — le générateur recalcule automatiquement une denture valide.

## Code couleur (conforme aux planches)

- 🔵 Bleu — entrée moteur / soleil
- 🟢 Vert — planètes
- 🟡 Jaune — porte-planètes / sortie
- 🔴 Rouge — couronne interne (élément verrouillable)

## Régénérer / modifier le modèle

```bash
pip install cadquery
cd gearbox-encke
python3 gearbox.py mon_gearbox.step
```

Modifier les paramètres en tête de `gearbox.py` (module, nombres de dents,
largeurs, diamètres du carter…) puis relancer : le STEP est régénéré.

## Note sur le fichier source `Ass_Encke.SLDASM`

L'assemblage moto fourni est au format **binaire propriétaire SolidWorks**, non
lisible sans SolidWorks. Ce modèle de gearbox a donc été construit **d'après les
4 planches techniques** (architecture, agencement et fonctionnement). Les
interfaces (arbre d'entrée coaxial, pignon de sortie chaîne, axes alignés) sont
respectées pour permettre l'intégration coaxiale sur la moto ENCKE. Les cotes de
détail (diamètres exacts, longueurs) sont à recaler sur l'implantation réelle de
la moto — tout est paramétré pour cela.

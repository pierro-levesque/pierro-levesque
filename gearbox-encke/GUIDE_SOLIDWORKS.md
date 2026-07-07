# Guide SolidWorks — animer le gearbox planétaire ENCKE

Pas-à-pas pour importer `gearbox_encke.step`, le contraindre et **animer la
rotation + le changement de rapport** entraîné depuis l'arbre moteur.

Noms des composants dans le STEP :
`3_boitier_gearbox` (bâti) · `4_soleil_arbre_entree` (entrée) ·
`5_planete_1/2/3` · `6_couronne_interne` · `9_porte_planetes_sortie` (sortie) ·
`10_pignon_sortie_chaine` · `7_roulement_*` · `8_actionneur_lineaire`.

---

## 1. Importer le STEP comme ASSEMBLAGE (étape critique)

Un STEP importé « par défaut » devient **une seule pièce multicorps** → on ne
peut pas y mettre de contraintes. Il faut l'importer en **assemblage**.

1. `Fichier ▸ Ouvrir`, sélectionne `gearbox_encke.step`.
2. Dans la fenêtre d'ouverture, clique **Options** et coche :
   - *Importer comme* : **Assemblage**
   - *Corps multiples* : **importer les corps comme pièces**
   (ou : `Outils ▸ Options ▸ Importation ▸ STEP/IGES ▸ Assemblage`)
3. Ouvre. Tu obtiens un assemblage avec un composant par pièce (noms conservés).

> Si tu as déjà ouvert en pièce multicorps : clic droit sur le dossier
> *Solid Bodies* ▸ **Save Bodies** / **Insert into New Part**, ou
> `Insertion ▸ Fonction ▸ Diviser` puis crée l'assemblage. Le ré-import en
> assemblage reste le plus simple.

---

## 2. Fixer le bâti et libérer les pièces mobiles

À l'import, les composants sont souvent **fixes (f)**.

1. Clic droit sur `3_boitier_gearbox` ▸ **Fixe** (c'est le bâti, il ne bouge pas).
2. Clic droit sur chaque autre composant mobile ▸ **Flotter** :
   `4_soleil_arbre_entree`, `6_couronne_interne`, `9_porte_planetes_sortie`,
   `5_planete_1/2/3`.

---

## 3. Contraintes de position (concentricité + axial)

Objectif : ne laisser qu'**un degré de liberté en rotation** à chaque pièce.

| Pièce | Contrainte 1 | Contrainte 2 |
|---|---|---|
| `4_soleil_arbre_entree` | **Concentrique** à l'axe central du boîtier | **Coïncidence** d'une face (blocage axial) |
| `6_couronne_interne` | **Concentrique** à l'axe central | **Coïncidence** axiale |
| `9_porte_planetes_sortie` | **Concentrique** à l'axe central | **Coïncidence** axiale |
| `5_planete_1/2/3` | **Concentrique** à SON axe (le pion du porte-planètes) | **Coïncidence** axiale sur un plateau du porte-planètes |

Après ça : soleil, couronne et porte-planètes tournent autour de l'axe Z ;
chaque planète tourne sur son pion **et** est emportée par le porte-planètes.

---

## 4. Contraintes d'engrènement (Gear mates)

`Insertion ▸ Contrainte ▸ Mécaniques ▸ Engrenage`. Sélectionne deux entités
(faces cylindriques primitives ou arêtes circulaires, ou les deux axes) puis
saisis le rapport en **nombres de dents**.

| Engrènement | Rapport (dents) | Remarque |
|---|---|---|
| `4_soleil` ↔ `5_planete_1` | **21 : 21** | extérieur/extérieur, sens opposés → coche **Inverser** si besoin |
| `4_soleil` ↔ `5_planete_2` | **21 : 21** | idem |
| `4_soleil` ↔ `5_planete_3` | **21 : 21** | idem |
| `5_planete_1` ↔ `6_couronne` | **21 : 63** | engrènement intérieur |
| `5_planete_2` ↔ `6_couronne` | **21 : 63** | intérieur |
| `5_planete_3` ↔ `6_couronne` | **21 : 63** | intérieur |

> Les Gear mates de SolidWorks sont des rapports de vitesse autour de chaque axe.
> Combinés aux concentriques du §3 (dont les pions qui orbitent avec le
> porte-planètes), ils reproduisent correctement la cinématique épicycloïdale.
> Si une roue tourne « à l'envers », rouvre la contrainte et coche **Inverser**.

À ce stade, en bloquant un élément et en tournant l'entrée à la main, tout le
train doit tourner de façon cohérente.

---

## 5. Choisir le rapport (élément bloqué)

- **Rapport 1 (i = 4,0)** — couronne bloquée, entrée = soleil :
  clic droit `6_couronne_interne` ▸ **Fixe**. Le moteur entraîne le **soleil**.
  Sortie porte-planètes = **entrée ÷ 4**.
- **Rapport 2 (i = 1,33)** — soleil bloqué, entrée = couronne :
  clic droit `6_couronne_interne` ▸ **Flotter**, puis
  clic droit `4_soleil_arbre_entree` ▸ **Fixe**. Le moteur entraîne la
  **couronne**. Sortie porte-planètes = **entrée × 0,75**.

Astuce propre : au lieu de *Fixe*, crée une contrainte **Verrou (Lock)** entre
l'élément et le boîtier — tu peux la **supprimer/réactiver** pour changer de
rapport sans refaire les mates.

---

## 6. Étude de mouvement (Motion Study)

1. Onglet **Étude de mouvement 1** (en bas). Type : **Mouvement de base**
   (*Basic Motion*) ou **Analyse de mouvement** (add-in SolidWorks Motion, plus
   physique).
2. Ajoute un **Moteur rotatif** (icône moteur) :
   - Composant : la face de l'**arbre d'entrée** engagé (soleil en R1, couronne en R2).
   - Type : **Vitesse constante**, ex. **60 tr/min**.
3. Règle la durée sur la barre de temps (ex. 10 s) → place une clé à la fin.
4. Clique **Calculer**. ▶ Lecture.

Vérification des vitesses attendues (entrée 60 tr/min) :
- **Rapport 1** : sortie porte-planètes ≈ **15 tr/min**.
- **Rapport 2** : sortie porte-planètes ≈ **45 tr/min** (×3 plus rapide).

---

## 7. Animer LE CHANGEMENT de rapport

Le blocage d'un élément ne se « clé » pas dans le temps en Basic Motion. Deux
méthodes :

**Méthode A — deux études (recommandée, simple).**
1. `Étude de mouvement 1` = Rapport 1 (couronne fixe, moteur sur soleil).
2. Duplique l'onglet → `Étude de mouvement 2` = Rapport 2 (soleil fixe, moteur
   sur couronne).
3. Exporte chaque étude en vidéo (§8) puis assemble les deux clips + un plan du
   mécanisme (§ suivant) au montage.

**Méthode B — mécanisme de sélection (pour montrer le crabot).**
Anime séparément l'**actionneur** et le **manchon** :
- Moteur linéaire sur `8_actionneur_lineaire` (déplacement de la tige).
- Contrainte de coïncidence pilotée qui fait coulisser le manchon/fourchette.
Superpose ce plan « débrayage → sélection → embrayage » entre tes clips R1 et R2
pour reproduire la séquence de la **planche 3/4** (≈ 140–180 ms).

---

## 8. Exporter la vidéo

`Étude de mouvement ▸ Enregistrer l'animation` ▸ format **AVI** (ou images).
- Images/s : 30 ; qualité haute.
- Vue isométrique ou en coupe (`Affichage ▸ Vue en coupe`) pour montrer les
  planètes à l'intérieur de la couronne.

---

## 9. Problèmes fréquents

| Symptôme | Cause / solution |
|---|---|
| Impossible de mettre des contraintes | Importé en pièce multicorps → réimporter en **assemblage** (§1). |
| Une pièce ne tourne pas / bloquée | Elle est restée **Fixe** → *Flotter* ; ou sur-contrainte axiale. |
| Une roue tourne à l'envers | Rouvrir le Gear mate ▸ cocher **Inverser**. |
| Le train se coince | Trop de contraintes redondantes : garde 1 concentrique + 1 coïncidence par pièce, le reste = Gear mates. |
| Rotation saccadée | Augmente le nombre d'images de l'étude, ou passe en *Analyse de mouvement*. |
| Les dents s'interpénètrent | Le STEP est déjà engrené (interférence vérifiée = 0). Vérifie que tu n'as pas déplacé une pièce après import. |

---

### Rappel des ratios

- Base épicycloïdal : `k = Z_couronne / Z_soleil = 63/21 = 3`.
- **R1** couronne fixe : `i = 1 + k = 4,0` → sortie = entrée ÷ 4.
- **R2** soleil fixe, couronne entrée : sortie = entrée × 0,75 (`i = 1,33`).

import numpy as np
from parametres_spatiaux import calculer_position_pied_appui
from biomeca import get_joint_angles, evaluer_orientation_pied
from vitesses import calculer_vitesses_lineaires

# --------------------------------------------------
# 1. Notation du placement du pied d'appui
# --------------------------------------------------

def noter_placement_pied(dx, dy):
    if 20 <= dx <= 40 and 20 <= dy <= 112:
        return 10, "✅ Placement optimal [correct]"
    elif 15 <= dx <= 50 and 10 <= dy <= 130:
        return 6, "⚠️ Placement acceptable [partiel]"
    else:
        return 4, "❌ Placement incorrect [incorrect]"

# --------------------------------------------------
# 2. Notation des angles articulaires du membre frappant
# --------------------------------------------------

def noter_angles(angles):
    note = 10
    erreurs = []
    hanche = angles.get("hanche_droit")
    genou = angles.get("genou_droit")

    if hanche is None or not (25 <= hanche <= 40):
        note -= 4
        erreurs.append("Hanche hors plage (25°–40°)")
    if genou is None or not (45 <= genou <= 65):
        note -= 4
        erreurs.append("Genou hors plage (45°–65°)")

    if note == 10:
        return 10, "✅ Angles corrects [correct]"
    elif note >= 6:
        return 6, f"⚠️ {', '.join(erreurs)} [partiel]"
    else:
        return 4, f"❌ {', '.join(erreurs)} [incorrect]"

# --------------------------------------------------
# 3. Notation de la vitesse du pied (cheville)
# --------------------------------------------------

def noter_vitesse_pied(vitesse):
    if vitesse is None or np.isnan(vitesse):
        return 0, "❌ Donnée manquante [incorrect]"
    if vitesse >= 10:
        return 10, "✅ Vitesse suffisante [correct]"
    elif vitesse >= 6:
        return 6, "⚠️ Vitesse moyenne [partiel]"
    else:
        return 4, "❌ Vitesse insuffisante [incorrect]"

# --------------------------------------------------
# 4. Notation du contact médial (orientation pied / ballon)
# --------------------------------------------------

def noter_contact_medial(cheville_droite, pied, ballon):
    note, message = evaluer_orientation_pied(pied, cheville_droite, ballon)
    # On harmonise ici aussi le message final
    if "✅" in message:
        return note, f"{message} [correct]"
    elif "⚠️" in message:
        return note, f"{message} [partiel]"
    else:
        return note, f"{message} [incorrect]"

# --------------------------------------------------
# 5. Score global pondéré (pass kick sans élan)
# --------------------------------------------------

def calculer_score_global(notes):
    poids = {
        "placement": 0.25,
        "angles": 0.20,
        "vitesse": 0.15,
        "contact": 0.40
    }
    score = 0
    for k in notes:
        note = notes[k] if notes[k] is not None else 0
        score += note * poids.get(k, 0)
    return round(score, 1)

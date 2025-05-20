import numpy as np

# --------------------------------------------------
# 1. Notation amplitude articulaire (même logique que instep)
# --------------------------------------------------

def noter_amplitude(angle, moyenne, ecart):
    ecart_abs = abs(angle - moyenne)
    if ecart_abs <= ecart:
        return 10
    elif ecart_abs <= 2 * ecart:
        return 8
    elif ecart_abs <= 3 * ecart:
        return 6
    else:
        return 4

# --------------------------------------------------
# 2. Notation des amplitudes articulaires par côté (côté frappant)
# --------------------------------------------------

def noter_angles_par_cote_inside(moment, pied_frappe, angles, VALEURS_REF):
    notes = {}
    ref = VALEURS_REF[moment]["kick"]

    correspondance = {
        "epaule": "epaule_droit" if pied_frappe == "droit" else "epaule_gauche",
        "coude": "coude_droit" if pied_frappe == "droit" else "coude_gauche",
        "hanche": "hanche_droit" if pied_frappe == "droit" else "hanche_gauche",
        "genou": "genou_droit" if pied_frappe == "droit" else "genou_gauche",
        "cheville": "cheville_droit" if pied_frappe == "droit" else "cheville_gauche",
    }

    for articulation, (moyenne, ecart) in ref.items():
        art_mesuree = correspondance[articulation]
        angle_observe = angles.get(art_mesuree)
        if angle_observe is not None:
            notes[articulation] = noter_amplitude(angle_observe, moyenne, ecart)
        else:
            notes[articulation] = None

    return notes

# --------------------------------------------------
# 3. Notation qualitative (alignement, orientation, vitesses physiques)
# --------------------------------------------------

def convertir_alignement_en_note(alignement_result):
    if not alignement_result:
        return 4
    msg = alignement_result.lower()
    if "✅" in msg or "[correct]" in msg:
        return 10
    elif "⚠️" in msg or "[partiel]" in msg:
        return 6
    elif "❌" in msg or "[incorrect]" in msg:
        return 4
    return 4

def noter_orientation_pied(angle):
    ecart = abs(angle - 90)
    if ecart <= 10:
        return 10
    elif ecart <= 20:
        return 8
    elif ecart <= 30:
        return 6
    else:
        return 4

def noter_vitesse_lineaire_inside(v):  # en m/s
    if v is None:
        return 0
    if isinstance(v, (list, np.ndarray)):
        v = np.nanmean(v)
    if np.isnan(v):
        return 0
    if v >= 10:
        return 10
    elif v >= 8:
        return 8
    elif v >= 6:
        return 6
    else:
        return 4

def noter_vitesse_angulaire_inside(v):  # en rad/s
    if v is None:
        return 0
    if isinstance(v, (list, np.ndarray)):
        v = np.nanmean(v)
    if np.isnan(v):
        return 0
    if v <= 30:
        return 10
    elif v <= 40:
        return 8
    elif v <= 50:
        return 6
    else:
        return 4

# --------------------------------------------------
# 4. Notation par phase – spécifique au tir inside (suivi simplifié)
# --------------------------------------------------

def extraire_notes_par_moment_inside(notes_approche_angles, note_angle_approche, note_pied_appui,
                                     notes_kickstep_angles, vitesses_lineaires, vitesses_angulaires,
                                     orientation_angle, note_cheville_impact,
                                     suivi_eval, alignement_note):

    # Approche
    note_amp_approche = np.mean([n for n in notes_approche_angles.values() if n is not None]) if notes_approche_angles else 0
    note_approche = round(np.mean([note_amp_approche, note_angle_approche, note_pied_appui]), 2)

    # Kick Step
    note_amp_kick = np.mean([n for n in notes_kickstep_angles.values() if n is not None]) if notes_kickstep_angles else 0
    note_vit_lin = np.mean([noter_vitesse_lineaire_inside(v) for v in vitesses_lineaires.values()]) if vitesses_lineaires else 0
    note_vit_ang = np.mean([noter_vitesse_angulaire_inside(v) for v in vitesses_angulaires.values()]) if vitesses_angulaires else 0
    note_orientation = noter_orientation_pied(orientation_angle) if orientation_angle is not None else 4
    note_impact = round(np.mean([note_orientation, note_cheville_impact]), 2)
    note_kickstep = round(np.mean([note_amp_kick, note_vit_lin, note_vit_ang, note_impact]), 2)

    # Suivi simplifié : cheville uniquement, version vitesse linéaire
    v_cheville = suivi_eval.get("cheville")
    note_vit_suivi = noter_vitesse_lineaire_inside(v_cheville)
    note_suivi = round(np.mean([note_vit_suivi, alignement_note]), 2)

    return {
        "approche": note_approche,
        "kick_step": note_kickstep,
        "suivi": note_suivi
    }

# --------------------------------------------------
# 5. Notation qualitative textuelle vers score numérique
# --------------------------------------------------

def noter_evaluation_vitesse(message):
    message = message.lower()
    if "✅" in message or "[correct]" in message:
        return 10
    elif "⚠️" in message or "[partiel]" in message:
        return 6
    elif "❌" in message or "[incorrect]" in message:
        return 4
    return 4

# --------------------------------------------------
# 6. Score global pondéré (tir inside)
# --------------------------------------------------

def generer_score_global_inside(notes_par_phase):
    poids = {
        "approche": 0.25,
        "kick_step": 0.50,
        "suivi": 0.25
    }

    score = 0
    details = {}

    for phase, note in notes_par_phase.items():
        p = poids.get(phase, 0)
        note_eff = note if note is not None else 0
        contribution = note_eff * p
        details[phase] = f"{note_eff}/10 × {int(p*100)}% = {contribution:.2f}"
        score += contribution

    return round(score, 2), details

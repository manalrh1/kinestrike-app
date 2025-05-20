# noatation_instep.py
import numpy as np

# --------------------------------------------------
# 1. Notation d’un angle par rapport à une référence
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
# 2. Notation des amplitudes articulaires
# --------------------------------------------------

def noter_angles_par_cote(moment, pied_frappe, angles, VALEURS_REF):
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
# 3. Alignement tronc-bassin → note
# --------------------------------------------------

def convertir_alignement_en_note(alignement_result):
    if not alignement_result:
        return 4
    msg = alignement_result.lower()
    if "✅" in msg or "correct" in msg:
        return 10
    elif "⚠️" in msg or "partiel" in msg:
        return 6
    elif "❌" in msg or "incorrect" in msg:
        return 4
    return 4

# --------------------------------------------------
# 4. Message de vitesse → note
# --------------------------------------------------

def noter_evaluation_vitesse(message):
    if not message:
        return 0
    msg = message.lower()
    if "✅" in msg or "correct" in msg:
        return 10
    elif "⚠️" in msg or "partiel" in msg:
        return 6
    elif "❌" in msg or "incorrect" in msg:
        return 4
    return 6  # Fallback par défaut

# --------------------------------------------------
# 5. Extraction des notes par moment
# --------------------------------------------------

def extraire_notes_par_moment(notes_approche_angles, note_angle_approche, note_pied_appui,
                               notes_kickstep_angles, vit_eval_lin, vit_eval_ang,
                               note_cheville_impact, note_timing_impact,
                               suivi_eval, alignement_note):

    # Approche
    note_amplitudes_approche = np.mean([
        n for n in notes_approche_angles.values() if isinstance(n, (int, float))
    ]) if notes_approche_angles else 0

    note_approche = round(np.mean([
        note_amplitudes_approche,
        note_angle_approche,
        note_pied_appui
    ]), 2)

    # Kick Step
    note_amplitudes_kick = np.mean([
        n for n in notes_kickstep_angles.values() if isinstance(n, (int, float))
    ]) if notes_kickstep_angles else 0

    note_vit_lin = np.mean([
        noter_evaluation_vitesse(msg) for msg in vit_eval_lin.values()
    ]) if vit_eval_lin else 0

    note_vit_ang = np.mean([
        noter_evaluation_vitesse(msg) for msg in vit_eval_ang.values()
    ]) if vit_eval_ang else 0

    note_kickstep = round(np.mean([
        note_amplitudes_kick,
        note_vit_lin,
        note_vit_ang
    ]), 2)

    # Impact
    impact_notes = [
        n for n in [note_cheville_impact, note_timing_impact] if isinstance(n, (int, float))
    ]
    note_impact = round(np.mean(impact_notes), 2) if impact_notes else 0

    # Suivi
    note_vit_suivi = np.mean([
        noter_evaluation_vitesse(msg) for msg in suivi_eval.values()
    ]) if suivi_eval else 0

    note_suivi = round(np.mean([
        note_vit_suivi,
        alignement_note
    ]), 2)

    return {
        "approche": note_approche,
        "activation_transfert": note_kickstep,
        "impact": note_impact,
        "suivi": note_suivi
    }

# --------------------------------------------------
# 6. Score global pondéré
# --------------------------------------------------

def generer_score_global(notes_par_phase):
    poids = {
        "approche": 0.25,
        "activation_transfert": 0.40,
        "impact": 0.20,
        "suivi": 0.15
    }

    score = 0
    details = {}

    for phase, note in notes_par_phase.items():
        p = poids.get(phase, 0)
        note_eff = note if isinstance(note, (int, float)) else 0
        contribution = note_eff * p
        details[phase] = f"{note_eff}/10 × {int(p*100)}% = {contribution:.2f}"
        score += contribution

    return round(min(score, 10), 2), details

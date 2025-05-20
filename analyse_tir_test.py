import pickle
import numpy as np
import pandas as pd
import joblib

from biomeca import get_joint_angles, verifier_alignement_tronc_bassin, VALEURS_REF
from vitesses import (
    calculer_vitesses_lineaires,
    calculer_vitesses_angulaires,
    verifier_logique_vitesses_lineaires,
    verifier_logique_vitesses_angulaires,
    verifier_suivi,
    verifier_timing_impact
)
from notation_globale import (
    noter_angles_par_cote,
    convertir_alignement_en_note,
    extraire_notes_par_moment,
    generer_score_global
)
from recommandations import (
    generer_recommandations,
    generer_recommandation_globale,
    generer_analyse_qualitative
)

def analyser_tir(video_path, pied):
    # === 1. Chargement ===
    with open("keypoints_video1.pkl", "rb") as f:
        keypoints = pickle.load(f)
    with open("angles_video1.pkl", "rb") as f:
        angles = pickle.load(f)
    features_df = pd.read_csv("features_video1.csv")

    # === 2. Colonnes requises ===
    model_features = [
        "epaule_f", "coude_f", "hanche_f", "genou_f", "cheville_f",
        "epaule_nf", "coude_nf", "hanche_nf", "genou_nf", "cheville_nf",
        "v_ang_cuisse", "v_ang_jambe",
        "v_lin_hanche", "v_lin_genou", "v_lin_orteil",
        "dist_pied_ballon"
    ]
    features_df = features_df[[col for col in model_features if col in features_df.columns]]

    # === 3. Prédiction des phases ===
    model = joblib.load("modele_segmentateur.pkl")
    predictions = model.predict(features_df)

    # === 4. Identification des phases prédictes ===
    phase_indices = {phase: np.where(predictions == phase)[0] for phase in ["activation", "transfert", "impact", "suivi"]}
    indices = {}

    # Initialisation sécurisée
    if len(phase_indices["activation"]) > 0:
        indices["activation"] = phase_indices["activation"]
        indices["t1"] = int(phase_indices["activation"][0])
    else:
        indices["activation"] = []
        indices["t1"] = None

    if len(phase_indices["transfert"]) > 0:
        indices["transfert"] = phase_indices["transfert"]
    else:
        indices["transfert"] = []

    if len(phase_indices["impact"]) > 0:
        indices["impact"] = phase_indices["impact"]
        indices["t2"] = int(phase_indices["impact"][0])
    else:
        indices["impact"] = []
        indices["t2"] = None

    if len(phase_indices["suivi"]) > 0:
        indices["suivi"] = phase_indices["suivi"]
        indices["t3"] = int(phase_indices["suivi"][-1])
    else:
        indices["suivi"] = []
        indices["t3"] = None

    indices["t0"] = 0

    # === 5. Analyse biomécanique avec protection ===
    angles_frames = get_joint_angles(keypoints)
    notes_approche = noter_angles_par_cote("approche", "kick", angles_frames[0], VALEURS_REF) if indices["t1"] is not None else {}
    notes_kickstep = noter_angles_par_cote("kickstep", "kick", angles_frames[indices["t1"]], VALEURS_REF) if indices["t1"] is not None else {}
    note_cheville = notes_kickstep.get("cheville", 6)
    note_angle_approche = 8
    note_pied_appui = 8

    alignement_msg = verifier_alignement_tronc_bassin(keypoints, indices["suivi"], pied) if indices["t3"] is not None else "Alignement non mesuré"
    note_alignement = convertir_alignement_en_note(alignement_msg)

    vit_lin = calculer_vitesses_lineaires(keypoints, pied)
    vit_ang = calculer_vitesses_angulaires(angles, pied)

    eval_v_lin = verifier_logique_vitesses_lineaires(vit_lin, indices)
    eval_v_ang = verifier_logique_vitesses_angulaires(vit_ang, indices)
    eval_suivi = verifier_suivi(vit_ang, vit_lin, indices["suivi"]) if indices["t3"] is not None else {}
    timing_msg = verifier_timing_impact(vit_lin["cheville"], indices["t2"]) if indices["t2"] is not None else "Timing non mesuré"
    note_timing = 10 if "correctement" in timing_msg.lower() else 6 if "proche" in timing_msg.lower() else 4

    notes_par_phase = extraire_notes_par_moment(
        notes_approche, note_angle_approche, note_pied_appui,
        notes_kickstep, eval_v_lin, eval_v_ang,
        note_cheville, note_timing,
        eval_suivi, note_alignement
    )

    score_final, details_score = generer_score_global(notes_par_phase)

    eval_dict = {
        "angle_approche": 35,
        "dx": 30,
        "dy": 40,
        "eval_lin": eval_v_lin,
        "eval_ang": eval_v_ang,
        "timing_msg": timing_msg,
        "note_cheville": note_cheville,
        "suivi_eval": eval_suivi,
        "alignement_note": note_alignement
    }

    recommandations = generer_recommandations(eval_dict)
    reco_globale = generer_recommandation_globale(score_final)
    points_forts, points_a_ameliorer = generer_analyse_qualitative(notes_par_phase)

    return {
        "keypoints": keypoints,
        "angles": angles,
        "t2": indices["t2"] or 0,
        "notes_par_phase": notes_par_phase,
        "score_final": score_final,
        "details_score": details_score,
        "recommandations": recommandations,
        "reco_globale": reco_globale,
        "points_forts": points_forts,
        "points_a_ameliorer": points_a_ameliorer
    }

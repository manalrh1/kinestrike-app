import pickle
import numpy as np
import pandas as pd
from biomeca import get_joint_angles
from vitesses import calculer_vitesses_lineaires, calculer_vitesses_angulaires

# === PARAMÈTRES GÉNÉRAUX ===
WINDOW_SIZE = 10  # Taille de la fenêtre glissante
KEYPOINTS_PATH = "tir_segmentation_ml/data/keypoints_videos/keypoints_video72.pkl"
BALL_PATH = "tir_segmentation_ml/data/ball_positions/ball_positions72.pkl"
OUTPUT_CSV_PATH = "tir_segmentation_ml/data/Features_windowed/features_windowed72.csv"
PIED_FRAPPE = "gauche"  # Spécifie si le pied de frappe est le gauche ou le droit

# === Chargement des données ===
with open(KEYPOINTS_PATH, "rb") as f:
    keypoints_all = pickle.load(f)

with open(BALL_PATH, "rb") as f:
    ball_positions = pickle.load(f)

# === Fonction de calcul de la distance entre le pied de frappe et le ballon ===
def get_distance_pied_ballon(keypoints, ball_position, cote=PIED_FRAPPE):
    pied_idx = 31 if cote == "gauche" else 28  # Index du pied gauche ou droit dans la liste des keypoints
    pied = np.array(keypoints[pied_idx])
    if ball_position is None or (pied[0] == 0 and pied[1] == 0):
        return np.nan  # Valeur manquante si ballon ou pied non détecté
    return np.linalg.norm(pied - np.array(ball_position))  # Distance euclidienne

# === Calcul des vitesses linéaires du pied de frappe ===
vit_lin = calculer_vitesses_lineaires(keypoints_all, pied_frappe=PIED_FRAPPE)

# === Calcul des angles articulaires pour chaque frame ===
angles_par_frame = {
    f"hanche_{PIED_FRAPPE}": [],
    f"genou_{PIED_FRAPPE}": []
}
for frame in keypoints_all:
    angles = get_joint_angles(frame)
    angles_par_frame[f"hanche_{PIED_FRAPPE}"].append(angles.get(f"hanche_{PIED_FRAPPE}"))
    angles_par_frame[f"genou_{PIED_FRAPPE}"].append(angles.get(f"genou_{PIED_FRAPPE}"))

# === Calcul des vitesses angulaires à partir des angles ===
vit_ang = calculer_vitesses_angulaires(angles_par_frame, pied_frappe=PIED_FRAPPE)

# === Extraction des caractéristiques par fenêtre glissante ===
features = []

for i in range(len(keypoints_all) - WINDOW_SIZE + 1):
    window = keypoints_all[i:i + WINDOW_SIZE]

    # Initialisation des listes pour stocker les données
    angles_f = {k: [] for k in ["epaule", "coude", "hanche", "genou", "cheville"]}
    angles_nf = {k: [] for k in ["epaule", "coude", "hanche", "genou", "cheville"]}
    vit_ang_cuisse = []
    vit_ang_jambe = []
    vit_lin_hanche = []
    vit_lin_genou = []
    vit_lin_orteil = []
    distances = []

    for j in range(WINDOW_SIZE):
        frame_idx = i + j
        angles = get_joint_angles(window[j])
        
        # Récupération des angles du côté frappant et non-frappant
        for k in angles_f:
            angles_f[k].append(angles.get(f"{k}_gauche"))
            angles_nf[k].append(angles.get(f"{k}_droit"))

        # Extraction des vitesses linéaires et angulaires pour les frames > 0
        if frame_idx > 0:
            if frame_idx - 1 < len(vit_ang["cuisse"]):
                vit_ang_cuisse.append(vit_ang["cuisse"][frame_idx - 1])
                vit_ang_jambe.append(vit_ang["jambe"][frame_idx - 1])
            if frame_idx - 1 < len(vit_lin["hanche"]):
                vit_lin_hanche.append(vit_lin["hanche"][frame_idx - 1])
                vit_lin_genou.append(vit_lin["genou"][frame_idx - 1])
                vit_lin_orteil.append(vit_lin["cheville"][frame_idx - 1])

        # Calcul de la distance pied-ballon
        ball = ball_positions.get(frame_idx)
        dist = get_distance_pied_ballon(keypoints_all[frame_idx], ball, cote=PIED_FRAPPE)
        distances.append(dist)

    # Création d'une ligne de caractéristiques moyennées sur la fenêtre
    row = {
        "frame_centrale": i + WINDOW_SIZE // 2,
        "label": "unknown",  # À annoter manuellement ou automatiquement plus tard
        "epaule_f": np.nanmean(angles_f["epaule"]),
        "coude_f": np.nanmean(angles_f["coude"]),
        "hanche_f": np.nanmean(angles_f["hanche"]),
        "genou_f": np.nanmean(angles_f["genou"]),
        "cheville_f": np.nanmean(angles_f["cheville"]),
        "epaule_nf": np.nanmean(angles_nf["epaule"]),
        "coude_nf": np.nanmean(angles_nf["coude"]),
        "hanche_nf": np.nanmean(angles_nf["hanche"]),
        "genou_nf": np.nanmean(angles_nf["genou"]),
        "cheville_nf": np.nanmean(angles_nf["cheville"]),
        "v_ang_cuisse": np.nanmean(vit_ang_cuisse),
        "v_ang_jambe": np.nanmean(vit_ang_jambe),
        "v_lin_hanche": np.nanmean(vit_lin_hanche),
        "v_lin_genou": np.nanmean(vit_lin_genou),
        "v_lin_orteil": np.nanmean(vit_lin_orteil),
        "dist_pied_ballon": np.nanmean(distances)
    }
    features.append(row)

# === Enregistrement du fichier final CSV ===
df = pd.DataFrame(features)
df.to_csv(OUTPUT_CSV_PATH, index=False)

print(f"Fichier généré avec pied {PIED_FRAPPE} : {OUTPUT_CSV_PATH}")

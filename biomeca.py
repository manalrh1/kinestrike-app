#biomeca.py
import numpy as np

# --------------------------------------------------
# 1. Calcul d’angles à partir des keypoints 2D
# --------------------------------------------------

import numpy as np

def calculate_angle_2d(a, b, c):
    """
    Calcule l'angle formé par trois points 2D (x, y) avec b comme sommet.
    Angle retourné en degrés.
    """
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b

    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    # Vérification pour éviter division par zéro
    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 0.0

    cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)  # ⛔ éviter erreurs d'arrondi
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

import numpy as np

def calculate_angle_3d(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 0.0

    cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

def get_joint_angles(frame):
    """
    Calcule les angles genou, cheville, hanche, épaule pour une frame de keypoints 3D.
    """
    try:
        epaule_droite = frame[11]
        coude_droit = frame[13]
        poignet_droit = frame[15]

        epaule_gauche = frame[12]
        coude_gauche = frame[14]
        poignet_gauche = frame[16]

        hanche_droite = frame[23]
        genou_droit = frame[25]
        cheville_droite = frame[27]
        pied_droit = frame[31] if len(frame) > 31 else cheville_droite

        hanche_gauche = frame[24]
        genou_gauche = frame[26]
        cheville_gauche = frame[28]
        pied_gauche = frame[32] if len(frame) > 32 else cheville_gauche

        # Angles jambes
        angle_genou_droit = calculate_angle_3d(hanche_droite, genou_droit, cheville_droite)
        angle_cheville_droit = calculate_angle_3d(genou_droit, cheville_droite, pied_droit)
        angle_hanche_droit = calculate_angle_3d(epaule_droite, hanche_droite, genou_droit)

        angle_genou_gauche = calculate_angle_3d(hanche_gauche, genou_gauche, cheville_gauche)
        angle_cheville_gauche = calculate_angle_3d(genou_gauche, cheville_gauche, pied_gauche)
        angle_hanche_gauche = calculate_angle_3d(epaule_gauche, hanche_gauche, genou_gauche)

        # Angles bras
        angle_epaule_droite = calculate_angle_3d(coude_droit, epaule_droite, hanche_droite)
        angle_epaule_gauche = calculate_angle_3d(coude_gauche, epaule_gauche, hanche_gauche)

        # === Calcul des angles des coudes ===
        angle_coude_droit = calculate_angle_3d(epaule_droite, coude_droit, poignet_droit)
        angle_coude_gauche = calculate_angle_3d(epaule_gauche, coude_gauche, poignet_gauche)

        return {
            'genou_droit': round(angle_genou_droit, 1),
            'cheville_droit': round(angle_cheville_droit, 1),
            'hanche_droit': round(angle_hanche_droit, 1),
            'genou_gauche': round(angle_genou_gauche, 1),
            'cheville_gauche': round(angle_cheville_gauche, 1),
            'hanche_gauche': round(angle_hanche_gauche, 1),
            'epaule_droite': round(angle_epaule_droite, 1),
            'epaule_gauche': round(angle_epaule_gauche, 1),
            'coude_droit': round(angle_coude_droit, 1),
            'coude_gauche': round(angle_coude_gauche, 1)
        }

    except Exception as e:
        return {}

# --------------------------------------------------
# 2. Valeurs de référence biomécaniques (instep)
# --------------------------------------------------

VALEURS_REF_instep = {
    "approche": {
        "kick": {
            "epaule": (61, 5),
            "coude": (24, 3),
            "hanche": (93, 7),
            "genou": (80, 6),
            "cheville": (34, 5),
        },
        "non_kick": {
            "epaule": (63, 4),
            "coude": (22, 3),
            "hanche": (92, 8),
            "genou": (78, 7),
            "cheville": (35, 4),
        }
    },
    "kickstep": {
        "kick": {
            "epaule": (62, 7),
            "coude": (16, 6),
            "hanche": (130, 10),
            "genou": (108, 8),
            "cheville": (38, 5),
        },
        "non_kick": {
            "epaule": (158, 12),
            "coude": (22, 4),
            "hanche": (113, 11),
            "genou": (100, 7),
            "cheville": (37, 4),
        }
    }
}

# --------------------------------------------------
# 3. Valeurs de référence biomécaniques – tir intérieur (inside)
# --------------------------------------------------

VALEURS_REF_INSIDE = {
    "approche": {
        "kick": {
            "epaule": (58, 6),
            "coude": (22, 3),
            "hanche": (88, 7),
            "genou": (76, 6),
            "cheville": (32, 5),
        },
        "non_kick": {
            "epaule": (60, 5),
            "coude": (23, 3),
            "hanche": (91, 6),
            "genou": (79, 6),
            "cheville": (34, 4),
        }
    },
    "kickstep": {
        "kick": {
            "epaule": (56, 7),
            "coude": (14, 5),
            "hanche": (120, 10),
            "genou": (100, 8),
            "cheville": (35, 5),
        },
        "non_kick": {
            "epaule": (150, 12),
            "coude": (20, 4),
            "hanche": (110, 10),
            "genou": (95, 7),
            "cheville": (36, 4),
        }
    }
}

# --------------------------------------------------
# 4. Évaluation des amplitudes articulaires vs références
# --------------------------------------------------

def evaluer_amplitudes_par_côté(angles, moment, cote, VALEURS_REF):
    erreurs = []
    ref = VALEURS_REF[moment][cote]

    correspondance = {
        "epaule": "epaule_droit" if cote == "kick" else "epaule_gauche",
        "coude": "coude_droit" if cote == "kick" else "coude_gauche",
        "hanche": "hanche_droit" if cote == "kick" else "hanche_gauche",
        "genou": "genou_droit" if cote == "kick" else "genou_gauche",
        "cheville": "cheville_droit" if cote == "kick" else "cheville_gauche",
    }

    for articulation, (moyenne, ecart) in ref.items():
        art_mesuree = correspondance[articulation]
        angle_observe = angles.get(art_mesuree)
        if angle_observe is None:
            continue
        if abs(angle_observe - moyenne) > 2 * ecart:
            erreurs.append(
                f"❌ {articulation.title()} ({cote}, {moment}) = {angle_observe:.1f}° hors zone (réf : {moyenne} ± {ecart})"
            )
    return erreurs

# --------------------------------------------------
# 5. Vérification de l'alignement tronc-bassin (moment3)
# --------------------------------------------------

def verifier_alignement_tronc_bassin(keypoints_all, indices_moment3, pied_frappe='droit'):
    index = {
        'droit': {'epaule': 2, 'hanche': 9, 'genou': 10},
        'gauche': {'epaule': 5, 'hanche': 12, 'genou': 13}
    }

    ep_idx = index[pied_frappe]['epaule']
    ha_idx = index[pied_frappe]['hanche']
    ge_idx = index[pied_frappe]['genou']

    angles = []
    for i in indices_moment3:
        if i < len(keypoints_all):
            try:
                ep = keypoints_all[i][ep_idx]
                ha = keypoints_all[i][ha_idx]
                ge = keypoints_all[i][ge_idx]
                angle = calculate_angle_2d(ep, ha, ge)
                angles.append(angle)
            except:
                continue

    if len(angles) < 3:
        return "⚠️ Données insuffisantes pour évaluer l’alignement tronc-bassin."

    moyenne = np.mean(angles)
    tendance = np.polyfit(range(len(angles)), angles, 1)[0]

    if moyenne > 165 and tendance >= 0:
        return f"✅ Alignement postural progressif (moyenne = {moyenne:.1f}°)"
    elif moyenne < 150:
        return f"❌ Posture trop fermée (moyenne = {moyenne:.1f}°)"
    else:
        return f"⚠️ Retour incomplet ou instable (moyenne = {moyenne:.1f}°, pente = {tendance:.2f})"

# --------------------------------------------------
# 6. Orientation vectorielle – angle brut
# --------------------------------------------------

def get_vector_angle(a, b):
    vec = np.array(b) - np.array(a)
    angle_rad = np.arctan2(vec[1], vec[0])
    return np.degrees(angle_rad)

# --------------------------------------------------
# 7. Évaluation orientation pied – contact intérieur
# --------------------------------------------------

def evaluer_orientation_pied(pied, cheville, ballon, seuil_angle=60):
    vec_pied_cheville = np.array(cheville) - np.array(pied)
    vec_pied_ballon = np.array(ballon) - np.array(pied)

    norm1 = np.linalg.norm(vec_pied_cheville)
    norm2 = np.linalg.norm(vec_pied_ballon)
    if norm1 == 0 or norm2 == 0:
        return 4, "❌ Orientation non mesurable (vecteur nul)"

    cos_angle = np.dot(vec_pied_cheville, vec_pied_ballon) / (norm1 * norm2)
    angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
    ecart = abs(angle - 90)

    if ecart <= 10:
        return 10, f"✅ Orientation idéale ({angle:.1f}°)"
    elif ecart <= seuil_angle / 2:
        return 8, f"⚠️ Orientation acceptable ({angle:.1f}°)"
    else:
        return 4, f"❌ Orientation incorrecte ({angle:.1f}°)"

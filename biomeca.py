import numpy as np

# --------------------------------------------------
# 1. Calcul d’angles à partir des keypoints 2D
# --------------------------------------------------

def calculate_angle_2d(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def get_joint_angles(keypoints):
    angles = {}
    try:
        # Genoux
        angles['genou_droit'] = calculate_angle_2d(keypoints[8], keypoints[9], keypoints[10])
        angles['genou_gauche'] = calculate_angle_2d(keypoints[11], keypoints[12], keypoints[13])
        # Hanches
        angles['hanche_droit'] = calculate_angle_2d(keypoints[1], keypoints[8], keypoints[9])
        angles['hanche_gauche'] = calculate_angle_2d(keypoints[1], keypoints[11], keypoints[12])
        # Chevilles
        angles['cheville_droit'] = calculate_angle_2d(keypoints[9], keypoints[10], keypoints[22])
        angles['cheville_gauche'] = calculate_angle_2d(keypoints[12], keypoints[13], keypoints[19])
        # Coudes
        angles['coude_droit'] = calculate_angle_2d(keypoints[2], keypoints[3], keypoints[4])
        angles['coude_gauche'] = calculate_angle_2d(keypoints[5], keypoints[6], keypoints[7])
        # Épaules
        angles['epaule_droit'] = calculate_angle_2d(keypoints[1], keypoints[2], keypoints[3])
        angles['epaule_gauche'] = calculate_angle_2d(keypoints[1], keypoints[5], keypoints[6])
    except Exception as e:
        print("Erreur de calcul des angles :", e)
        angles = {k: None for k in [
            'genou_droit', 'genou_gauche', 'hanche_droit', 'hanche_gauche',
            'cheville_droit', 'cheville_gauche', 'coude_droit', 'coude_gauche',
            'epaule_droit', 'epaule_gauche'
        ]}
    return angles

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

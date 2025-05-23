import numpy as np

# ============================================================================
# 1. DÉTECTION DU PIED D’APPUI À PARTIR DU PIED DE FRAPPE
# ============================================================================

def detecter_pied_appui(keypoints_frame, pied_frappe):
    """
    Retourne les coordonnées du pied d’appui en fonction du pied de frappe.
    MediaPipe : 28 = cheville droite, 27 = cheville gauche
    """
    if pied_frappe == "droit":
        idx_appui = 27  # cheville gauche
    else:
        idx_appui = 28  # cheville droite

    if keypoints_frame[idx_appui][0] > 0 and keypoints_frame[idx_appui][1] > 0:
        return keypoints_frame[idx_appui]
    else:
        return None  # coordonnées invalides


# ============================================================================
# 2. ANGLE D’APPROCHE (course ↔ direction ballon-but)
# ============================================================================

def calculer_angle_approche(bassin_t0, bassin_t1, ballon, but):
    """
    Calcule l'angle entre la trajectoire de course (bassin_t0 → bassin_t1) et l'axe ballon → but.
    """
    vecteur_course = np.array(bassin_t1) - np.array(bassin_t0)
    vecteur_cible = np.array(but) - np.array(ballon)

    norm1 = np.linalg.norm(vecteur_course)
    norm2 = np.linalg.norm(vecteur_cible)
    if norm1 == 0 or norm2 == 0:
        return None

    cos_theta = np.dot(vecteur_course, vecteur_cible) / (norm1 * norm2)
    angle = np.arccos(np.clip(cos_theta, -1.0, 1.0))
    return np.degrees(angle)

def verifier_angle_approche(angle):
    """
    Vérifie si l'angle d'approche est dans l'intervalle optimal [30°, 45°] selon Isokawa & Lees (1988).
    """
    if angle is None:
        return  " Angle non mesurable"
    elif 30 <= angle <= 45:
        return " Angle optimal (30°–45°)"
    elif 25 <= angle < 30 or 45 < angle <= 50:
        return  " Légèrement dévié de l'optimal"
    else:
        return " Angle inapproprié"


# ============================================================================
# 3. POSITION DU PIED D’APPUI PAR RAPPORT AU BALLON
# ============================================================================

def calculer_position_pied_appui(pied_appui, ballon):
    """
    Retourne la distance latérale (dx) et arrière (dy) du pied d'appui par rapport au ballon (en px).
    Selon Hay (1985), distance idéale :
    - latérale : 5–10 cm (20–40 px)
    - arrière  : 5–28 cm (20–112 px)
    """
    pied = np.array(pied_appui)
    ball = np.array(ballon)
    dx = abs(pied[0] - ball[0])  # latéral
    dy = ball[1] - pied[1]       # arrière si positif
    return dx, dy

def verifier_placement_pied(dx, dy):
    """
    Vérifie si les distances dx et dy sont dans les fourchettes optimales définies par Hay (1985).
    """
    if 20 <= dx <= 40 and 20 <= dy <= 112:
        return " Placement optimal"
    elif 15 <= dx <= 50 and 10 <= dy <= 130:
        return " Placement acceptable"
    else:
        return " Placement incorrect"


# ============================================================================
# 4. TEST LOCAL
# ============================================================================

if __name__ == "__main__":
    # Exemple pour test
    bassin_t0 = [100, 200]
    bassin_t1 = [120, 190]
    ballon = [150, 170]
    but = [150, 50]  # cible = centre du but

    angle = calculer_angle_approche(bassin_t0, bassin_t1, ballon, but)
    print(f"📐 Angle d'approche (vers cible) = {angle:.2f}°")
    print("🔎", verifier_angle_approche(angle))

    # Pied appui test
    pied_appui = [140, 172]
    dx, dy = calculer_position_pied_appui(pied_appui, ballon)
    print(f"📏 Pied appui - Latéral: {dx:.1f}px, Arrière: {dy:.1f}px")
    print("🔎", verifier_placement_pied(dx, dy))

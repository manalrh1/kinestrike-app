import numpy as np
import cv2

# === A. FPS automatique ===
def get_fps_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps if fps and fps > 0 else 30

# === B. Échelle px→m automatique ===
def estimer_px_to_m_depuis_hanche_genou(keypoints, pied_frappe='droit', categorie='U17'):
    """
    Estime la conversion pixel → mètre en se basant sur la distance hanche-genou.
    Catégories possibles : U13, U15, U17, Seniors
    """
    tailles_reelles = {'U13': 0.32, 'U15': 0.36, 'U17': 0.41, 'Seniors': 0.45}

    if pied_frappe == 'droit':
        idx_hanche, idx_genou = 9, 10
    else:
        idx_hanche, idx_genou = 12, 13

    # Vérification de l'existence des points
    try:
        hanche = np.array(keypoints[idx_hanche])
        genou = np.array(keypoints[idx_genou])
    except IndexError:
        return None

    # Vérifie la validité des coordonnées
    if -1 in hanche or -1 in genou:
        return None

    # Distance en pixels
    pixels = np.linalg.norm(hanche - genou)
    if pixels == 0:
        return None

    taille_physique = tailles_reelles.get(categorie, 0.4)  # fallback 40 cm

    px_to_m = taille_physique / pixels

    # Contrôle de vraisemblance
    if not 0.001 <= px_to_m <= 0.05:
        return None

    return px_to_m

# === C. Vitesse linéaire (m/s) ===
import numpy as np

def calculer_vitesses_lineaires(keypoints_all, pied_frappe='droit', px_to_m=1.0, fps=30, max_vitesse_m_s=30, lissage=True):
    idx = {'droit': {'hanche': 9, 'genou': 10, 'cheville': 11},
           'gauche': {'hanche': 12, 'genou': 13, 'cheville': 14}}[pied_frappe]

    vitesses = {art: [] for art in idx}

    for i in range(1, len(keypoints_all)):
        for art, point_idx in idx.items():
            p1 = np.array(keypoints_all[i - 1][point_idx])
            p2 = np.array(keypoints_all[i][point_idx])

            if -1 in p1 or -1 in p2:
                vitesses[art].append(np.nan)
                continue

            v = np.linalg.norm(p2 - p1) * px_to_m * fps

            if v > max_vitesse_m_s:
                vitesses[art].append(np.nan)
            else:
                vitesses[art].append(v)

    if lissage:
        for art in vitesses:
            vitesses[art] = __smooth(vitesses[art], k=3)

    return vitesses

def __smooth(v, k=3):
    v = np.array(v)
    mask = ~np.isnan(v)
    v_filled = np.copy(v)
    v_filled[~mask] = np.interp(np.flatnonzero(~mask), np.flatnonzero(mask), v[mask])
    return np.convolve(v_filled, np.ones(k)/k, mode='same')


# === D. Vitesse angulaire (rad/s) ===
def calculer_vitesses_angulaires(angles_par_frame, pied_frappe='droit', fps=30):
    cuisse_key, jambe_key = f'hanche_{pied_frappe}', f'genou_{pied_frappe}'
    cuisse = [f.get(cuisse_key, np.nan) for f in angles_par_frame]
    jambe = [f.get(jambe_key, np.nan) for f in angles_par_frame]
    vit_ang = {'cuisse': [], 'jambe': []}
    for i in range(1, len(cuisse)):
        vit_ang['cuisse'].append(abs(cuisse[i] - cuisse[i - 1]) * np.pi / 180 * fps if not np.isnan(cuisse[i]) and not np.isnan(cuisse[i-1]) else np.nan)
        vit_ang['jambe'].append(abs(jambe[i] - jambe[i - 1]) * np.pi / 180 * fps if not np.isnan(jambe[i]) and not np.isnan(jambe[i-1]) else np.nan)
    return vit_ang

# === 2. Découpage phases ===
def decouper_activation_transfert(frames_kickstep, t2):
    if not frames_kickstep or t2 not in frames_kickstep:
        return {"activation": [], "transfert": [], "impact": []}
    idx = frames_kickstep.index(t2)
    pre = frames_kickstep[:idx]
    return {"activation": pre[:len(pre)//2], "transfert": pre[len(pre)//2:], "impact": [t2]}

# === 3. Logique des vitesses linéaires ===
def verifier_logique_vitesses_lineaires(vitesses, indices_par_phase):
    resultats = {}
    for art in vitesses:
        v = vitesses[art]
        act = np.nanmean([v[i] for i in indices_par_phase["activation"] if i < len(v)])
        tra = np.nanmean([v[i] for i in indices_par_phase["transfert"] if i < len(v)])
        imp = np.nanmean([v[i] for i in indices_par_phase["impact"] if i < len(v)])
        if art == "cheville":
            msg = "✅ Impact > Transfert > Activation [correct]" if imp > tra > act else f"❌ impact={imp:.2f}, tra={tra:.2f}, act={act:.2f} [incorrect]"
        elif art == "genou":
            msg = "✅ Transfert > Activation > Impact [correct]" if tra > act > imp else f"❌ tra={tra:.2f}, act={act:.2f}, imp={imp:.2f} [incorrect]"
        elif art == "hanche":
            msg = "✅ Activation ≥ Transfert > Impact [correct]" if act >= tra and act > imp else f"❌ act={act:.2f}, tra={tra:.2f}, imp={imp:.2f} [incorrect]"
        resultats[art] = msg
    return resultats

# === 4. Logique vitesses angulaires instep ===
def verifier_logique_vitesses_angulaires(vit_ang, indices_par_phase):
    resultats = {}
    for seg in vit_ang:
        v = vit_ang[seg]
        act = np.nanmean([v[i] for i in indices_par_phase["activation"] if i < len(v)])
        tra = np.nanmean([v[i] for i in indices_par_phase["transfert"] if i < len(v)])
        imp = np.nanmean([v[i] for i in indices_par_phase["impact"] if i < len(v)])
        if seg == "cuisse":
            msg = "✅ Pic au transfert [correct]" if tra > act and tra > imp else f"❌ tra={tra:.2f}, act={act:.2f}, imp={imp:.2f} [incorrect]"
        elif seg == "jambe":
            msg = "✅ Pic à l’impact [correct]" if imp > tra > act else f"❌ imp={imp:.2f}, tra={tra:.2f}, act={act:.2f} [incorrect]"
        resultats[seg] = msg
    return resultats

# === 5. Logique douce (inside) ===
def verifier_vitesses_lineaires_inside(vitesses, indices_par_phase):
    resultats = {}
    for art in vitesses:
        v = vitesses[art]
        act = np.nanmean([v[i] for i in indices_par_phase["activation"] if i < len(v)])
        tra = np.nanmean([v[i] for i in indices_par_phase["transfert"] if i < len(v)])
        imp = np.nanmean([v[i] for i in indices_par_phase["impact"] if i < len(v)])
        msg = "✅ Progression modérée [correct]" if imp >= tra >= act else f"❌ act={act:.2f}, tra={tra:.2f}, imp={imp:.2f} [incorrect]"
        resultats[art] = msg
    return resultats

def verifier_vitesses_angulaires_inside(vit_ang, indices_par_phase):
    resultats = {}
    for seg in vit_ang:
        v = vit_ang[seg]
        act = np.nanmean([v[i] for i in indices_par_phase["activation"] if i < len(v)])
        tra = np.nanmean([v[i] for i in indices_par_phase["transfert"] if i < len(v)])
        imp = np.nanmean([v[i] for i in indices_par_phase["impact"] if i < len(v)])
        msg = "✅ Séquence douce respectée [correct]" if tra >= act and imp >= tra else f"❌ act={act:.2f}, tra={tra:.2f}, imp={imp:.2f} [incorrect]"
        resultats[seg] = msg
    return resultats

# === 6. Suivi (follow-through) ===
def verifier_suivi(vit_ang, vit_lin, indices_moment3):
    resultats = {}
    for seg in ["cuisse", "jambe"]:
        v = [vit_ang[seg][i] for i in indices_moment3 if i < len(vit_ang[seg])]
        if len(v) >= 3:
            pente = np.polyfit(range(len(v)), v, 1)[0]
            msg = "✅ Diminution angulaire [correct]" if pente < 0 else f"❌ pente = {pente:.2f} [incorrect]"
        else:
            msg = "⚠️ Données insuffisantes [partiel]"
        resultats[seg] = msg
    for art in ["cheville"]:
        v = [vit_lin[art][i] for i in indices_moment3 if i < len(vit_lin[art])]
        if len(v) >= 3:
            pente = np.polyfit(range(len(v)), v, 1)[0]
            msg = "✅ Ralentissement pied [correct]" if pente < 0 else f"❌ pente = {pente:.2f} [incorrect]"
        else:
            msg = "⚠️ Données insuffisantes [partiel]"
        resultats[art] = msg
    return resultats

# === 7. Timing du pic de vitesse (impact) ===
def verifier_timing_impact(vitesses_pied, t2):
    if vitesses_pied is None or len(vitesses_pied) == 0 or not (2 <= t2 < len(vitesses_pied)):
        return "⚠️ Données insuffisantes [partiel]"

    attendu = t2 - 1
    pic_index = np.argmax(vitesses_pied[:t2 + 1])

    if pic_index == attendu:
        return "✅ Pic juste avant l’impact [correct]"
    elif abs(pic_index - attendu) == 1:
        return "⚠️ Pic proche mais décalé [partiel]"
    else:
        return f"❌ Pic à frame {pic_index}, attendu à {attendu} [incorrect]"

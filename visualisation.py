#visualisation.py
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip
import json

# === Connexions MediaPipe (pour squelette)
LIAISONS = [
    (11, 13), (13, 15),
    (12, 14), (14, 16),
    (11, 12), (23, 24),
    (11, 23), (12, 24),
    (23, 25), (25, 27),
    (24, 26), (26, 28)
]

COULEURS_PHASES = {
    "approche": (0, 255, 0),
    "kick_step": (255, 165, 0),
    "impact": (0, 0, 255),
    "suivi": (128, 0, 128)
}

# ----------------------------------------------------------
# 1. Vidéo avec squelette + phase (MediaPipe style)
# ----------------------------------------------------------

from moviepy.editor import ImageSequenceClip
import cv2
import numpy as np
import os

def generer_video_annotee1(video_path, keypoints_all, phases, pied_frappe, output_path="video_annotee_squelette.mp4", ralenti=3):
    # Définir les connexions pour squelette
    LIAISONS = [
        (11, 13), (13, 15),  # bras gauche
        (12, 14), (14, 16),  # bras droit
        (11, 12), (23, 24),  # tronc
        (11, 23), (12, 24),
        (23, 25), (25, 27),  # jambe gauche
        (24, 26), (26, 28)   # jambe droite
    ]

    COULEURS_PHASES = {
        "approche": (0, 255, 0),
        "kick_step": (255, 165, 0),
        "impact": (0, 0, 255),
        "suivi": (128, 0, 128)
    }

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frames = []

    for i in range(min(len(keypoints_all), len(phases))):
        ret, frame = cap.read()
        if not ret:
            break

        # Récupérer phase et couleur
        label = phases[i]
        color = COULEURS_PHASES.get(label, (255, 255, 255))

        # Tracer le squelette
        for a, b in LIAISONS:
            if a < len(keypoints_all[i]) and b < len(keypoints_all[i]):
                xa, ya = keypoints_all[i][a]
                xb, yb = keypoints_all[i][b]
                if xa > 0 and ya > 0 and xb > 0 and yb > 0:
                    cv2.line(frame, (int(xa), int(ya)), (int(xb), int(yb)), color, 2)

        # Tracer les points clés
        for (x, y) in keypoints_all[i]:
            if x > 0 and y > 0:
                cv2.circle(frame, (int(x), int(y)), 5, color, -1)

        # Texte explicatif
        cv2.putText(frame, f"Phase : {label}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.putText(frame, f"Pied de frappe : {pied_frappe}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 150, 255), 2)

        # Ajouter frame convertie
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame_rgb)

    cap.release()

    if not frames:
        return None

    clip = ImageSequenceClip(frames, fps=max(1, fps / ralenti))
    clip.write_videofile(output_path, codec="libx264", audio=False)

    return output_path


def generer_video_annotee(video_path, keypoints_all, phases, pied_frappe,
                          output_path="video_annotee_squelette.mp4",
                          ralenti=3,
                          frames_annotations=None):
    """
    Génère une vidéo annotée :
    - Affiche le squelette avec couleur de phase
    - Ajoute des symboles (+/-) sur les articulations avec erreurs
    - Utilise frames_annotations : {frame: [(index, color, symbol)]}
    """
    LIAISONS = [
        (11, 13), (13, 15),  # bras gauche
        (12, 14), (14, 16),  # bras droit
        (11, 12), (23, 24),  # tronc
        (11, 23), (12, 24),
        (23, 25), (25, 27),  # jambe gauche
        (24, 26), (26, 28)   # jambe droite
    ]

    COULEURS_PHASES = {
        "approche": (0, 255, 0),
        "kick_step": (255, 165, 0),
        "impact": (0, 0, 255),
        "suivi": (128, 0, 128)
    }

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frames = []

    for i in range(min(len(keypoints_all), len(phases))):
        ret, frame = cap.read()
        if not ret:
            break

        label = phases[i]
        color_phase = COULEURS_PHASES.get(label, (255, 255, 255))
        keypoints = keypoints_all[i]

        # Dessin du squelette
        for a, b in LIAISONS:
            if a < len(keypoints) and b < len(keypoints):
                xa, ya = keypoints[a]
                xb, yb = keypoints[b]
                if xa > 0 and ya > 0 and xb > 0 and yb > 0:
                    cv2.line(frame, (int(xa), int(ya)), (int(xb), int(yb)), color_phase, 2)

        # Points clés standards
        for (x, y) in keypoints:
            if x > 0 and y > 0:
                cv2.circle(frame, (int(x), int(y)), 5, color_phase, -1)

        # Postures annotées (si fournies)
        if frames_annotations and i in frames_annotations:
            for idx, couleur, symbole in frames_annotations[i]:
                if idx < len(keypoints):
                    x, y = keypoints[idx]
                    if x > 0 and y > 0:
                        cv2.circle(frame, (int(x), int(y)), 8, couleur, -1)
                        if symbole:
                            cv2.putText(frame, symbole, (int(x) + 5, int(y) - 5),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, couleur, 2)

        # Texte explicatif
        cv2.putText(frame, f"Phase : {label}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_phase, 3)
        cv2.putText(frame, f"Pied de frappe : {pied_frappe}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 150, 255), 2)

        # Convertir en RGB pour MoviePy
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame_rgb)

    cap.release()

    if not frames:
        return None

    clip = ImageSequenceClip(frames, fps=max(1, fps / ralenti))
    clip.write_videofile(output_path, codec="libx264", audio=False)

    return output_path

# ----------------------------------------------------------
# 2. Vidéo simple avec MoviePy (texte uniquement)
# ----------------------------------------------------------

def generer_video_phases_simple(video_path, phases, output_path="video_segmentee.mp4", ralenti=3):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    images = []
    for i in range(min(len(phases), total_frames)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        label = phases[i]
        color = COULEURS_PHASES.get(label, (255, 255, 255))
        cv2.putText(frame, f"Phase : {label}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        images.append(frame_rgb)

    cap.release()
    if not images:
        return None

    clip = ImageSequenceClip(images, fps=max(1, fps / ralenti))
    clip.write_videofile(output_path, codec="libx264", audio=False)

    return output_path if os.path.exists(output_path) else None

# ----------------------------------------------------------
# 3. Image de la pose à l’impact
# ----------------------------------------------------------
def enregistrer_image_pose(keypoints_all, frame_idx, video_path, output_path="impact_pose.png"):
    """
    Capture une image réelle (frame) de la vidéo à l’instant donné (frame_idx),
    avec superposition du squelette (MediaPipe-like) basé sur les keypoints.
    """
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return None

    # Dessiner les segments du squelette
    for a, b in LIAISONS:
        if a < len(keypoints_all[frame_idx]) and b < len(keypoints_all[frame_idx]):
            xa, ya = keypoints_all[frame_idx][a]
            xb, yb = keypoints_all[frame_idx][b]
            if xa > 0 and ya > 0 and xb > 0 and yb > 0:
                cv2.line(frame, (int(xa), int(ya)), (int(xb), int(yb)), (0, 255, 0), 2)

    # Dessiner les points clés
    for (x, y) in keypoints_all[frame_idx]:
        if x > 0 and y > 0:
            cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)

    # Sauvegarder l’image
    cv2.imwrite(output_path, frame)
    return output_path


def tracer_graphiques_vitesses(vitesses_lin_px, vitesses_ang, phases, pied_frappe, fps=30, px_to_m=1.0, output_dir="graphes"):
    import matplotlib.pyplot as plt
    import numpy as np
    import os

    os.makedirs(output_dir, exist_ok=True)
    jambe = "jambe droite" if pied_frappe == "droit" else "jambe gauche"

    # Convertir px/frame → m/s pour vitesses linéaires
    vitesses_lin = {
    art: [(v * px_to_m * fps) if not np.isnan(v) else np.nan for v in vitesses_lin_px[art]]
    for art in vitesses_lin_px
    }


    frames = np.arange(1, len(vitesses_lin["cheville"]) + 1)

    couleurs = {
        "approche": "#2a9d8f",
        "kick_step": "#f4a261",
        "impact": "#e76f51",
        "suivi": "#264653"
    }

    # === GRAPHE 1 : ANGULAIRE – Kick Step & Impact ===
    indices = [i for i, p in enumerate(phases) if p in ["kick_step", "impact"]]

    if indices:
        plt.figure(figsize=(10, 5))

        for seg in ["cuisse", "jambe"]:
            y_vals = [vitesses_ang[seg][i] if i < len(vitesses_ang[seg]) else np.nan for i in indices]
            plt.plot(indices, y_vals, label=f"{seg}", linewidth=2)

        labels_used = set()
        for i in indices:
            phase = phases[i]
            if phase in couleurs and phase not in labels_used:
                plt.axvspan(i - 0.5, i + 0.5, color=couleurs[phase], alpha=0.3, label=phase)
                labels_used.add(phase)
            elif phase in couleurs:
                plt.axvspan(i - 0.5, i + 0.5, color=couleurs[phase], alpha=0.3)

        plt.xlabel("Numéro de frame")
        plt.ylabel("Vitesse angulaire (rad/s)")
        plt.title(f"Vitesses angulaires de la {jambe} – Kick Step & Impact", fontsize=13, fontweight="bold")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/vitesses_angulaires_kick_impact.png")
        plt.close()

    # === GRAPHE 2 : Vitesse linéaire du pied (cheville) – Toutes phases ===
    plt.figure(figsize=(10, 5))
    plt.plot(frames, vitesses_lin["cheville"], color='red', label="Vitesse du pied (m/s)")

    for i in range(1, len(phases)):
        if phases[i] != phases[i - 1]:
            plt.axvline(x=i, color='gray', linestyle='--')
            plt.text(i, max(vitesses_lin["cheville"]) * 0.9, phases[i], rotation=90, verticalalignment='bottom')

    plt.xlabel("Numéro de frame")
    plt.ylabel("Vitesse du pied (m/s)")
    plt.title(f"Évolution de la vitesse du pied ({jambe}) – Toutes phases", fontsize=13, fontweight="bold")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/vitesse_pied_phases.png")
    plt.close()

    return [
        f"{output_dir}/vitesses_angulaires_kick_impact.png",
        f"{output_dir}/vitesse_pied_phases.png"
    ]

# Construction de la version finale de la fonction demandée

def detecter_postures_anotees(notes_approche_angles, notes_kickstep_angles, ref_angles,
                              t1, t2, pied_frappe="droit", threshold=8):
    """
    Détecte les écarts positifs ou négatifs pour chaque articulation côté frappant et non frappant.

    Retourne un dictionnaire : {frame: [(index_joint, couleur, symbole)]}
    - couleur : (0,255,0) si correct, (0,0,255) si mauvais
    - symbole : "+" si amplitude excessive, "-" si amplitude trop faible, "" sinon
    """
    mapping_keypoints = {
        "epaule": {"droit": 12, "gauche": 11},
        "coude": {"droit": 14, "gauche": 13},
        "hanche": {"droit": 24, "gauche": 23},
        "genou": {"droit": 26, "gauche": 25},
        "cheville": {"droit": 28, "gauche": 27}
    }

    frames_annotations = {t1: [], t2 - 1: []}

    def eval_note(articulation, note, observed_angle, moment):
        if note is None:
            return None
        ref_mean, ref_std = ref_angles[moment]["kick"][articulation]
        ecart = observed_angle - ref_mean
        if note >= threshold:
            return (0, 255, 0), "+" if ecart > ref_std else "-" if ecart < -ref_std else ""
        else:
            return (0, 0, 255), "+" if ecart > ref_std else "-" if ecart < -ref_std else ""

    for moment, frame_id, notes in [("approche", t1, notes_approche_angles), ("kickstep", t2 - 1, notes_kickstep_angles)]:
        for articulation in notes:
            for cote in ["droit", "gauche"]:
                idx = mapping_keypoints[articulation][cote]
                note = notes[articulation]
                # Choisir l'angle observé simulé (car non transmis ici)
                ref_mean, ref_std = ref_angles[moment]["kick"][articulation]
                # Pour la simulation, on suppose un angle à ref_mean ±1 selon le côté pour exemple
                simulated_angle = ref_mean + (2 if cote == pied_frappe else -2)
                result = eval_note(articulation, note, simulated_angle, moment)
                if result:
                    color, symbol = result
                    frames_annotations[frame_id].append((idx, color, symbol))

    frames_annotations[t2 - 1].sort()
    frames_annotations[t1].sort()
    frames_annotations_cleaned = {k: v for k, v in frames_annotations.items() if v}

    frames_annotations_cleaned_json = json.dumps(frames_annotations_cleaned, default=lambda o: list(o) if isinstance(o, tuple) else o)
    frames_annotations_cleaned_json[:300]  # Preview only


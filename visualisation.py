#visualisation.py
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip
import json
import plotly.graph_objects as go
import imageio

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

def generer_video_annotee(video_path, keypoints_all, phases, pied_frappe,
                          output_path="video_squelette.mp4", ralenti=3):
    import cv2
    from moviepy.editor import ImageSequenceClip
    import numpy as np
    import os

    # Liaisons du squelette
    LIAISONS = [
        (11, 13), (13, 15),   # Bras gauche
        (12, 14), (14, 16),   # Bras droit
        (11, 12),             # Épaules
        (11, 23), (23, 25), (25, 27),  # Tronc gauche
        (12, 24), (24, 26), (26, 28),  # Tronc droit
        (23, 24)              # Bassin
    ]

    # Couleurs des segments
    COLORS = {
        "bras": (255, 0, 255),    # Violet
        "jambes": (0, 255, 0),    # Vert
        "tronc": (255, 0, 0),     # Rouge
        "points": (0, 0, 255)     # Bleu pour les points
    }

    # Couleurs par phase
    COLORS_PHASES = {
        "approche": (0, 255, 0),       # Vert
        "kick_step": (255, 165, 0),    # Orange
        "impact": (255, 0, 0),         # Rouge
        "suivi": (0, 0, 255)           # Bleu
    }

    def get_color(a, b):
        bras = {11, 12, 13, 14, 15, 16}
        jambes = {23, 24, 25, 26, 27, 28}
        if a in bras and b in bras:
            return COLORS["bras"]
        elif a in jambes and b in jambes:
            return COLORS["jambes"]
        else:
            return COLORS["tronc"]

    if not os.path.exists(video_path):
        print(f"Erreur : Fichier vidéo introuvable : {video_path}")
        return None

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []

    for i in range(min(len(keypoints_all), len(phases))):
        ret, frame = cap.read()
        if not ret:
            break

        label = phases[i]
        keypoints = keypoints_all[i]

        # Détermine la couleur de phase actuelle
        couleur_phase = COLORS_PHASES.get(label, (200, 200, 200))  # Gris par défaut

        # Tracer les lignes du squelette
        for a, b in LIAISONS:
            if a < len(keypoints) and b < len(keypoints):
                xa, ya = keypoints[a]
                xb, yb = keypoints[b]
                if xa > 0 and ya > 0 and xb > 0 and yb > 0:
                    cv2.line(frame, (int(xa), int(ya)), (int(xb), int(yb)), get_color(a, b), 3)

        # Tracer les points
        for (x, y) in keypoints:
            if x > 0 and y > 0:
                cv2.circle(frame, (int(x), int(y)), 5, COLORS["points"], -1)

        # Ajouter le texte Phase + Pied de frappe
        cv2.putText(frame, f"Phase : {label}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, couleur_phase, 3)

        cv2.putText(frame, f"Pied de frappe : {pied_frappe}", (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 102, 204), 2)

        # Convertir frame pour MoviePy
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame_rgb)

    cap.release()

    if not frames:
        print("Erreur : Aucun frame valide généré.")
        return None

    clip = ImageSequenceClip(frames, fps=max(1, fps / ralenti))
    clip.write_videofile(output_path, codec="libx264", audio=False)

    return output_path

def detecter_postures_anotees(notes_approche_angles, notes_kickstep_angles,
                              angles_approche, angles_kickstep,
                              ref_angles, t1, t2, pied_frappe="droit"):
    import streamlit as st

    keypoints_all = st.session_state.donnees["keypoints_all"]
    angles_all = st.session_state.donnees["angles_all"]
    phases = st.session_state.donnees.get("phases") or ["kickstep"] * len(keypoints_all)
    frames_annotations = {}

    # Mapping articulations <-> index MediaPipe
    mapping_keypoints = {
        "epaule": {"droit": 12, "gauche": 11},
        "coude": {"droit": 14, "gauche": 13},
        "hanche": {"droit": 24, "gauche": 23},
        "genou": {"droit": 26, "gauche": 25},
        "cheville": {"droit": 28, "gauche": 27}
    }

    def verifier_correctitude(angle_mesure, ref_mean, ref_std):
        # Vérifie si angle dans [mean - std, mean + std]
        return abs(angle_mesure - ref_mean) <= ref_std

    cote_kick = pied_frappe
    cote_non_kick = "gauche" if pied_frappe == "droit" else "droit"

    for i, (keypoints, angles) in enumerate(zip(keypoints_all, angles_all)):
        phase = phases[i] if i < len(phases) else "kickstep"

        if phase == "approche":
            ref_moment = ref_angles.get("approche", {}).get("kick", {})
        elif phase in ["kickstep", "kick_step", "impact"]:
            ref_moment = ref_angles.get("kickstep", {}).get("kick", {})
        else:
            continue  # Ignore les phases "suivi" où il n'y a pas d'angles à vérifier

        for articulation in mapping_keypoints:
            for cote in ["droit", "gauche"]:
                nom_angle = f"{articulation}_{cote}"
                angle_mesure = angles.get(nom_angle)
                if angle_mesure is None:
                    continue

                ref = ref_moment.get(articulation)
                if ref is None:
                    continue

                ref_mean, ref_std = ref
                idx = mapping_keypoints[articulation][cote]

                if verifier_correctitude(angle_mesure, ref_mean, ref_std):
                    couleur = (0, 255, 0)  # Vert
                else:
                    couleur = (255, 0, 0)  # Rouge

                frames_annotations.setdefault(i, []).append((idx, couleur))

    return frames_annotations



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

from scipy.interpolate import make_interp_spline
import matplotlib.patches as mpatches


def tracer_graphiques_vitesses(
    vitesses_lin_px, vitesses_ang, phases,
    pied_frappe=None, fps=30,
    pas_affichage=30
):
    couleurs = {
        "approche": "blue",
        "kick_step": "orange",
        "impact": "red",
        "suivi": "green"
    }

    temps = np.arange(len(vitesses_lin_px["cheville"])) / fps

    # Définir légende externe des phases
    phase_colors = {
        "approche": "blue",
        "kick_step": "orange",
        "impact": "red",
        "suivi": "green"
    }
    patches = [mpatches.Patch(color=color, label=phase) for phase, color in phase_colors.items()]

    # === 1. VITESSES LINÉAIRES (px/s) ===
    fig1, ax1 = plt.subplots(figsize=(6, 2))

    for cle, couleur in zip(["cheville", "genou", "hanche"], ['red', 'green', 'blue']):
        vit_px_s = np.array([v if not np.isnan(v) else np.nan for v in vitesses_lin_px[cle]])
        temps_filtrés = temps[::pas_affichage]
        vit_filtrées = vit_px_s[::pas_affichage]

        mask = ~np.isnan(vit_filtrées)
        if np.sum(mask) >= 4:
            t_spline = temps_filtrés[mask]
            v_spline = vit_filtrées[mask]
            spline = make_interp_spline(t_spline, v_spline)
            t_dense = np.linspace(t_spline[0], t_spline[-1], 300)
            v_dense = spline(t_dense)
            ax1.plot(t_dense, v_dense, label=f"{cle}", linewidth=2, color=couleur)
        else:
            ax1.plot(temps_filtrés, vit_filtrées, label=f"{cle}", linewidth=2, color=couleur)

    for i, phase in enumerate(phases):
        t = i / fps
        ax1.axvspan(t - 0.5/fps, t + 0.5/fps, color=couleurs.get(phase, 'gray'), alpha=0.2)

    ax1.set_xlim(left=0)
    ax1.set_xlabel("Temps (s)", fontsize=10)
    ax1.set_yticks([])
    ax1.set_ylabel("")
    ax1.tick_params(axis='x', labelsize=8)  # ✅ Taille des ticks X réduite
    for spine in ax1.spines.values():
        spine.set_visible(False)

    # ✅ Légende biomécanique (courbes) avec taille réduite
    ax1.legend(loc="upper left", frameon=False, fontsize=8)

    # ✅ Légende des phases (externe)
    fig1.legend(handles=patches, loc='center left', bbox_to_anchor=(1, 0.5), frameon=False, fontsize=8)

    ax1.grid(True, color='lightgray', linestyle='--', linewidth=0.5)
    fig1.tight_layout()
    os.makedirs("graphes", exist_ok=True)
    fig1.savefig("graphes/graphe_vitesse_lineaire.png", bbox_inches='tight')

    # === 2. VITESSES ANGULAIRES (°/s) ===
    fig2, ax2 = plt.subplots(figsize=(6, 2))

    for seg, couleur in zip(["cuisse", "jambe"], ['purple', 'brown']):
        y_vals = []
        indices = []
        for i, val in enumerate(vitesses_ang[seg]):
            if val is not None:
                y_vals.append(val)
                indices.append(i)

        indices_filtrés = indices[::pas_affichage]
        y_filtrées = np.array(y_vals)[::pas_affichage]
        temps_filtrés = np.array(indices_filtrés) / fps

        if len(y_filtrées) >= 4:
            spline = make_interp_spline(temps_filtrés, y_filtrées)
            t_dense = np.linspace(temps_filtrés[0], temps_filtrés[-1], 300)
            y_dense = spline(t_dense)
            ax2.plot(t_dense, y_dense, label=f"{seg}", linewidth=2, color=couleur)
        else:
            ax2.plot(temps_filtrés, y_filtrées, label=f"{seg}", linewidth=2, color=couleur)

    for i, phase in enumerate(phases):
        t = i / fps
        ax2.axvspan(t - 0.5/fps, t + 0.5/fps, color=couleurs.get(phase, 'gray'), alpha=0.2)

    ax2.set_xlim(left=0)
    ax2.set_xlabel("Temps (s)", fontsize=10)
    ax2.set_yticks([])
    ax2.set_ylabel("")
    ax2.tick_params(axis='x', labelsize=8)  # ✅ Taille des ticks X réduite
    for spine in ax2.spines.values():
        spine.set_visible(False)

    ax2.legend(loc="upper left", frameon=False, fontsize=8)
    fig2.legend(handles=patches, loc='center left', bbox_to_anchor=(1, 0.5), frameon=False, fontsize=8)

    ax2.grid(True, color='lightgray', linestyle='--', linewidth=0.5)
    fig2.tight_layout()
    fig2.savefig("graphes/graphe_vitesse_angulaire.png", bbox_inches='tight')

    return fig1, fig2

from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import imageio

# Connexions MediaPipe-like pour squelette complet
LIAISONS_3D_COMPLET = [
    ("nez", "oeil_gauche"), ("nez", "oeil_droit"),
    ("epaule_gauche", "coude_gauche"), ("coude_gauche", "poignet_gauche"),
    ("epaule_droite", "coude_droit"), ("coude_droit", "poignet_droit"),
    ("epaule_gauche", "epaule_droite"),
    ("epaule_gauche", "hanche_gauche"), ("epaule_droite", "hanche_droite"),
    ("hanche_gauche", "genou_gauche"), ("genou_gauche", "cheville_gauche"),
    ("hanche_droite", "genou_droit"), ("genou_droit", "cheville_droit"),
    ("hanche_gauche", "hanche_droite")
]

COULEURS_PHASES_3D = {
    "approche": "green",
    "kick_step": "orange",
    "impact": "red",
    "suivi": "purple"
}

def tracer_radar_notes(notes_par_phase, output_path="graphes/radar_notes.png"):
    import numpy as np
    import matplotlib.pyplot as plt
    import os

    phases = {
        "approche": "approche",
        "activation_transfert": "phase de frappe",
        "impact": "impact",
        "suivi": "suivi"
    }

    labels = [phases.get(p, p) for p in notes_par_phase.keys()]
    scores = list(notes_par_phase.values())

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)

    # ✅ On ferme manuellement le polygone pour tracer
    scores += [scores[0]]
    angles_full = np.append(angles, angles[0])

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    
    # ✅ Couleurs correctes
    ax.plot(angles_full, scores, color='red', linewidth=2)
    ax.fill(angles_full, scores, color='red', alpha=0.25)

    # ✅ Labels sans duplication
    ax.set_thetagrids(np.degrees(angles), labels, fontsize=10, ha='center')

    ax.set_ylim(0, 10)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close(fig)

    return output_path


# squelette3d.py
import numpy as np
import plotly.graph_objects as go
<<<<<<< HEAD

=======
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
def generer_animation_plotly(keypoints_3d, angles_par_frame, phases=None):
    LIAISONS = [
        (11, 13), (13, 15),
        (12, 14), (14, 16),
        (11, 12),
        (11, 23), (12, 24),
        (23, 25), (25, 27),
        (24, 26), (26, 28),
        (23, 24)
    ]

    COULEURS_PHASES = {
        "approche": "green",
        "kick_step": "orange",
        "impact": "red",
        "suivi": "blue"
    }

    # Nettoyage : Ignorer les points aberrants (-1, etc.)
    all_points = []
    for frame in keypoints_3d:
        for pt in frame:
            if pt is not None and all([-0.5 < coord < 2 for coord in pt]):
                all_points.append(pt)
    all_points = np.array(all_points)

    x_min, x_max = np.min(all_points[:, 0]), np.max(all_points[:, 0])
    y_min, y_max = np.min(all_points[:, 1]), np.max(all_points[:, 1])
    z_min, z_max = np.min(all_points[:, 2]), np.max(all_points[:, 2])

    marge = 0.1
    x_range = [x_min - marge, x_max + marge]
    y_range = [y_min - marge, y_max + marge]
    z_range = [z_min - marge, z_max + marge]

    frames = []
    for i, frame in enumerate(keypoints_3d):
        traces = []
        x, y, z = zip(*frame)
        traces.append(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(size=5, color='red'),
            showlegend=False
        ))

        phase = phases[i] if phases and i < len(phases) else "autre"
        color = COULEURS_PHASES.get(phase, "gray")

        for a, b in LIAISONS:
            if a < len(frame) and b < len(frame):
                xa, ya, za = frame[a]
                xb, yb, zb = frame[b]
                if all([-0.5 < c < 2 for c in (xa, ya, za, xb, yb, zb)]):
                    traces.append(go.Scatter3d(
                        x=[xa, xb], y=[ya, yb], z=[za, zb],
                        mode='lines',
                        line=dict(color=color, width=3),
                        showlegend=False
                    ))

<<<<<<< HEAD
        # Affichage des angles : police grande, couleur noire, position très proche articulation
        angles = angles_par_frame[i]
        for articulation in ['genou_droit', 'genou_gauche', 'hanche_droit', 'hanche_gauche',
                             'cheville_droit', 'cheville_gauche', 'epaule_droite', 'epaule_gauche',
                             'coude_droit', 'coude_gauche']:
=======
        # ✅ Affichage des angles avec taille réduite et position fixe
        angles = angles_par_frame[i]
        for articulation in ['genou_droit', 'genou_gauche', 'hanche_droit', 'hanche_gauche',
                              'cheville_droit', 'cheville_gauche', 'epaule_droite', 'epaule_gauche',
                              'coude_droit', 'coude_gauche']:
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
            if articulation in angles:
                joint_idx = {
                    "genou_droit": 25, "genou_gauche": 26,
                    "hanche_droit": 23, "hanche_gauche": 24,
                    "cheville_droit": 27, "cheville_gauche": 28,
                    "epaule_droite": 11, "epaule_gauche": 12,
                    "coude_droit": 13, "coude_gauche": 14
                }[articulation]
                x_, y_, z_ = frame[joint_idx]
                if all([-0.5 < c < 2 for c in (x_, y_, z_)]):
                    angle = angles[articulation]
<<<<<<< HEAD

                    offset_y = 0.01 if 'gauche' in articulation else -0.01  # Collé à l'articulation
                    offset_z = 0.015  # Petit décalage vertical

                    traces.append(go.Scatter3d(
                        x=[x_], y=[y_ + offset_y], z=[z_ + offset_z],
=======
                    
                    # Offset pour éviter que le texte chevauche le point
                    offset_y = 0.05 if 'gauche' in articulation else -0.05
                    
                    traces.append(go.Scatter3d(
                        x=[x_], y=[y_ + offset_y], z=[z_ + 0.05],
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
                        mode='text',
                        text=[f"{int(angle)}°"],
                        textposition='middle center',
                        textfont=dict(
<<<<<<< HEAD
                            size=18,        # Plus grand (lisible)
                            color="black",  # Noir
                            family="Arial"
                        ),
                        showlegend=False,
                        hoverinfo='skip'
=======
                            size=10,  # Taille réduite à 10
                            color="white",
                            family="Arial"  # Police Arial standard
                        ),
                        showlegend=False,
                        # ✅ Stabiliser la taille du texte pendant l'animation
                        hoverinfo='skip'  # Éviter les interactions qui changent l'affichage
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
                    ))

        frames.append(go.Frame(data=traces, name=f"frame_{i}"))

    # Configuration de la scène avec dimensions fixes
    scene_settings = dict(
        xaxis=dict(
<<<<<<< HEAD
            title="X",
=======
            title="X", 
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
            range=x_range,
            showgrid=True,
            gridcolor="lightgray"
        ),
        yaxis=dict(
<<<<<<< HEAD
            title="Y",
=======
            title="Y", 
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
            range=y_range,
            showgrid=True,
            gridcolor="lightgray"
        ),
        zaxis=dict(
<<<<<<< HEAD
            title="Z",
=======
            title="Z", 
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
            range=z_range,
            showgrid=True,
            gridcolor="lightgray"
        ),
        aspectmode="cube",
        bgcolor="rgba(240,240,240,0.1)"
    )

    fig = go.Figure(
        data=frames[0].data,
        layout=go.Layout(
            title="Squelette 3D – Animation interactive avec angles",
            width=900,
            height=800,
            scene=scene_settings,
<<<<<<< HEAD
            margin=dict(l=0, r=0, b=0, t=60),
=======
            margin=dict(l=0, r=0, b=0, t=60),  # Plus de marge en haut pour les boutons
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
            updatemenus=[],
            sliders=[]
        ),
        frames=frames
    )

<<<<<<< HEAD
    # Play/Pause/Stop + slider
=======
    # ✅ Boutons Play et Pause améliorés
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
    fig.update_layout(
        updatemenus=[{
            "type": "buttons",
            "direction": "left",
            "x": 0.1,
            "y": 1.02,
            "xanchor": "left",
            "yanchor": "top",
            "buttons": [
                dict(
                    label="⏸️ Pause",
                    method="animate",
                    args=[[None], {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                ),
                dict(
                    label="▶️ Play",
                    method="animate",
                    args=[None, {
                        "frame": {"duration": 150, "redraw": True},
                        "fromcurrent": True,
                        "mode": "immediate",
                        "transition": {"duration": 50},
                    }]
                ),
                dict(
                    label="⏹️ Stop",
                    method="animate",
                    args=[[frames[0].name], {
                        "frame": {"duration": 0, "redraw": True},
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                )
            ]
        }]
    )

<<<<<<< HEAD
=======
    # ✅ Slider amélioré avec stabilité
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
    fig.update_layout(
        sliders=[{
            "steps": [dict(
                args=[[f.name], {
                    "frame": {"duration": 0, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 0}
                }],
<<<<<<< HEAD
                label=f"Frame {i+1}",
=======
                label=f"Frame {i+1}",  # Labels plus clairs
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
                method="animate"
            ) for i, f in enumerate(frames)],
            "active": 0,
            "currentvalue": {"prefix": "Frame: "},
            "len": 0.8,
            "x": 0.1,
            "y": 0,
            "xanchor": "left",
            "yanchor": "top"
        }]
    )

<<<<<<< HEAD
=======
    # ✅ Configuration pour maintenir la vue et taille stable
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
    fig.update_layout(
        scene_camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.2),
            center=dict(x=0, y=0, z=0),
            up=dict(x=0, y=0, z=1)
        ),
<<<<<<< HEAD
        scene=dict(
            **scene_settings,
            camera=dict(
                projection=dict(type="perspective")
            )
        ),
=======
        # ✅ Empêcher le redimensionnement automatique
        scene=dict(
            **scene_settings,
            camera=dict(
                projection=dict(type="perspective")  # Vue perspective fixe
            )
        ),
        # ✅ Configuration pour stabilité pendant l'animation
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)
        transition={
            'duration': 0,
            'easing': 'linear'
        }
    )
<<<<<<< HEAD

    return fig
=======
>>>>>>> 8f1c132 (🔧 Mise à jour complète du projet + fix requirements pour Streamlit Cloud)

    return fig
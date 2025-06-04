from extraction import extraire_keypoints_3d_plotly
from visualisation import generer_animation_plotly
from biomeca import get_joint_angles  # ⚡ important pour calculer les angles !

# === 1. Chemin vers ta vidéo ===
video_path = "video_segmentee.mp4"  # change ce chemin selon ta vidéo réelle

# === 2. Extraction des keypoints 3D
keypoints_3d = extraire_keypoints_3d_plotly(video_path)

# === 3. Calcul des angles pour chaque frame
angles_par_frame = []
for frame in keypoints_3d:
    angles = get_joint_angles(frame)  # ✅ calcul des angles genou, hanche, cheville
    angles_par_frame.append(angles)

# === 4. Génération de l’animation interactive
fig = generer_animation_plotly(keypoints_3d, angles_par_frame)
fig.show()

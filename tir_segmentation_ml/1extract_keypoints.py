import cv2
import mediapipe as mp
import numpy as np
import pickle
import os

# Initialisation du modèle MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils

# Chemin de la vidéo et du fichier de sortie
video_path = "Videos/video82.mp4"
output_path = "tir_segmentation_ml/data/keypoints_videos/keypoints_video82.pkl"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Ouverture de la vidéo
cap = cv2.VideoCapture(video_path)
keypoints_all = []  # Liste pour stocker tous les keypoints

# Initialakisation du suivi
last_center = None
max_distance = 60  # Distance maximale autorisée pour considérer qu'il s'agit de la même personne (en pixels)

print("Tracking automatique en cours...")

while True:
    ret, frame = cap.read()
    if not ret:
        break  # Fin de la vidéo

    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Conversion BGR → RGB pour MediaPipe
    results = pose.process(rgb)  # Détection des poses

    draw_skeleton = False  # Indicateur pour afficher le squelette

    if results.pose_landmarks:
        # Extraction des coordonnées normalisées et conversion en pixels
        lm = results.pose_landmarks.landmark
        keypoints = np.array([[p.x * w, p.y * h] for p in lm])
        center = (keypoints[23] + keypoints[24]) / 2  # Centre du bassin (moyenne des hanches gauche et droite)

        # Vérifie si le mouvement est continu (pas de saut brusque)
        if last_center is None or np.linalg.norm(center - last_center) < max_distance:
            keypoints_all.append(keypoints.tolist())
            last_center = center
            draw_skeleton = True
        else:
            keypoints_all.append([[0, 0]] * 33)  # Remplit avec zéros si la joueuse saute ou disparaît
    else:
        keypoints_all.append([[0, 0]] * 33)  # Aucun keypoint détecté pour cette frame

    # Affichage du squelette si valide
    if draw_skeleton and results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2))

    # Redimensionne la frame pour un affichage plus fluide
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5)

    # Affiche la vidéo avec squelette superposé
    cv2.imshow("Tracking de la joueuse", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Quitte l'affichage si la touche 'q' est pressée

# Libération des ressources vidéo
cap.release()
cv2.destroyAllWindows()

# Sauvegarde des keypoints dans un fichier .pkl
with open(output_path, "wb") as f:
    pickle.dump(keypoints_all, f)

print(f"Keypoints sauvegardés dans : {output_path}")

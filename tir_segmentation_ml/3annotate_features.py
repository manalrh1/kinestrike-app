import pandas as pd
import cv2
import numpy as np
import pickle
from biomeca import get_joint_angles  # Assurez-vous que le fichier biomeca.py est bien dans le dossier

# === PARAMÈTRES ===
CSV_PATH = "tir_segmentation_ml/data/Features_windowed/features_windowed72.csv"    # Fichier des features extraits
VIDEO_PATH = "Videos/video72.mp4"                                                  # Vidéo à annoter
KEYPOINTS_PATH = "tir_segmentation_ml/data/keypoints_videos/keypoints_video72.pkl"    # Keypoints 2D correspondants
OUTPUT_CSV_PATH = "tir_segmentation_ml/data/Features_annotated/features_annotated72.csv" # Fichier CSV de sortie annoté
WINDOW_SIZE = 10                                               # Taille de la fenêtre utilisée pour extraire les features

# === Chargement des données
df = pd.read_csv(CSV_PATH)
with open(KEYPOINTS_PATH, "rb") as f:
    keypoints_all = pickle.load(f)
cap = cv2.VideoCapture(VIDEO_PATH)

# === Fonction d’affichage des keypoints sur l’image
def draw_keypoints(frame, keypoints, color=(0, 255, 0)):
    for x, y in keypoints:
        if x != 0 and y != 0:
            cv2.circle(frame, (int(x), int(y)), 3, color, -1)  # Dessine un cercle aux coordonnées valides

# === Fonction d’ajout de la légende et numéro de frame
def draw_overlay_info(frame, frame_num):    
    h, w = frame.shape[:2]
    overlay = frame.copy()
    legend = "A: Approche | T: Activation | R: Transfert | I: Impact | S: Suivi | N: Ignorer | Q: Quitter"

    # Rectangle noir en haut + texte blanc
    cv2.rectangle(overlay, (0, 0), (w, 40), (0, 0, 0), -1)
    cv2.putText(overlay, legend, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    cv2.putText(overlay, f"Frame: {frame_num}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    return overlay

# === Fonction pour afficher la phase choisie
def show_labeled_frame(frame, label_text):
    confirmed = frame.copy()
    cv2.putText(confirmed, f"PHASE : {label_text.upper()}", (60, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
    return confirmed

print("Début de l’annotation – 1 frame centrale par fenêtre. Appuie sur A/T/R/I/S/N/Q pour annoter.")

# === Boucle d’annotation manuelle
for idx, row in df.iterrows():
    frame_central = int(row["frame_centrale"])  # Numéro de la frame centrale de la fenêtre
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_central)  # Positionner la vidéo sur cette frame
    ret, frame = cap.read()
    if not ret or frame_central >= len(keypoints_all):
        continue

    keypoints = keypoints_all[frame_central]
    draw_keypoints(frame, keypoints)  # Affiche les keypoints
    frame = draw_overlay_info(frame, frame_central)  # Affiche légende + numéro de frame

    # Redimensionnement pour un affichage plus rapide
    frame_resized = cv2.resize(frame, None, fx=0.5, fy=0.5)
    cv2.imshow("Annotation", frame_resized)

    # Attente de la touche utilisateur
    key = cv2.waitKey(0) & 0xFF
    label_text = ""
    if key == ord('a'):
        label_text = "approche"
    elif key == ord('t'):
        label_text = "activation"
    elif key == ord('r'):
        label_text = "transfert"
    elif key == ord('i'):
        label_text = "impact"
    elif key == ord('s'):
        label_text = "suivi"
    elif key == ord('n'):
        continue  # Passe à la fenêtre suivante sans modifier le label
    elif key == ord('q'):
        break  # Quitte la boucle d’annotation

    # Mise à jour du label dans la DataFrame et affichage de confirmation
    if label_text:
        df.at[idx, "label"] = label_text
        confirmation = show_labeled_frame(frame_resized, label_text)
        cv2.imshow("Annotation", confirmation)
        cv2.waitKey(500)  # Pause courte pour confirmer visuellement l’annotation

# === Sauvegarde des annotations
cap.release()
cv2.destroyAllWindows()
df.to_csv(OUTPUT_CSV_PATH, index=False)
print(f"Annotations sauvegardées dans : {OUTPUT_CSV_PATH}")

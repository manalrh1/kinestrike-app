import cv2
import pickle
import mediapipe as mp
import numpy as np
from biomeca import get_joint_angles
from vitesses import calculer_vitesses_lineaires, calculer_vitesses_angulaires

def extraire_donnees_biomecaniques(video_path,
                                    ball_positions_path=None,
                                    pied_frappe="droit"):
    """
    Extrait les keypoints, angles articulaires, vitesses biomécaniques et distance pied-ballon.

    Args:
        video_path (str): Chemin de la vidéo d'entrée.
        ball_positions_path (str or None): Chemin vers le fichier pickle contenant les positions du ballon.
        pied_frappe (str): 'droit' ou 'gauche'.

    Returns:
        dict: {
            "keypoints_all": keypoints par frame (list of list),
            "angles_all": angles articulaires par frame,
            "v_lin": vitesses linéaires hanche/genou/cheville,
            "v_ang": vitesses angulaires cuisse/jambe,
            "dist_pied_ballon": distance pied-ballon par frame
        }
    """
    mp_pose = mp.solutions.pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
    cap = cv2.VideoCapture(video_path)

    keypoints_par_frame = []
    angles_par_frame = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_pose.process(image)

        if results.pose_landmarks:
            h, w = frame.shape[:2]
            coords = [(lm.x * w, lm.y * h) if lm.visibility > 0.5 else (-1, -1)
                      for lm in results.pose_landmarks.landmark]
        else:
            coords = [(-1, -1)] * 33

        keypoints_par_frame.append(coords)
        angles_par_frame.append(get_joint_angles(coords))

    cap.release()
    mp_pose.close()

    # Chargement des positions du ballon
    if ball_positions_path is not None:
        with open(ball_positions_path, "rb") as f:
            ball_positions = pickle.load(f)
    else:
        ball_positions = {}

    # Calcul des vitesses biomécaniques
    vit_lin = calculer_vitesses_lineaires(keypoints_par_frame, pied_frappe)
    vit_ang = calculer_vitesses_angulaires(angles_par_frame, pied_frappe)

    # Calcul de la distance entre le pied et le ballon (par frame)
    dist_pied_ballon = []
    pied_idx = 28 if pied_frappe == "droit" else 27

    for i in range(len(keypoints_par_frame)):
        if i in ball_positions:
            pied = keypoints_par_frame[i][pied_idx]
            ballon = ball_positions[i]
            d = np.linalg.norm(np.array(pied) - np.array(ballon)) if pied != (-1, -1) else 0
            dist_pied_ballon.append(d)
        else:
            dist_pied_ballon.append(0)

    return {
        "keypoints_all": keypoints_par_frame,
        "angles_all": angles_par_frame,
        "v_lin": vit_lin,
        "v_ang": vit_ang,
        "dist_pied_ballon": dist_pied_ballon
    }

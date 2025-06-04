

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
    Extrait les keypoints 2D & 3D, angles articulaires, vitesses biomécaniques et distance pied-ballon.
    """
    mp_pose = mp.solutions.pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
    cap = cv2.VideoCapture(video_path)

    keypoints_2d_par_frame = []
    keypoints_3d_par_frame = []
    angles_par_frame = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_pose.process(image)

        if results.pose_landmarks:
            h, w = frame.shape[:2]

            coords_2d = [(lm.x * w, lm.y * h) if lm.visibility > 0.5 else (-1, -1)
                         for lm in results.pose_landmarks.landmark]

            coords_3d = [(lm.x, lm.y, lm.z) if lm.visibility > 0.5 else (-1, -1, -1)
                         for lm in results.pose_landmarks.landmark]
        else:
            coords_2d = [(-1, -1)] * 33
            coords_3d = [(-1, -1, -1)] * 33

        keypoints_2d_par_frame.append(coords_2d)
        keypoints_3d_par_frame.append(coords_3d)
        angles_par_frame.append(get_joint_angles(coords_2d))

    cap.release()
    mp_pose.close()

    # Chargement des positions du ballon
    if ball_positions_path is not None:
        with open(ball_positions_path, "rb") as f:
            ball_positions = pickle.load(f)
    else:
        ball_positions = {}

    # Calcul des vitesses biomécaniques
    vit_lin = calculer_vitesses_lineaires(keypoints_2d_par_frame, pied_frappe)
    vit_ang = calculer_vitesses_angulaires(angles_par_frame, pied_frappe)

    # Distance pied-ballon
    dist_pied_ballon = []
    pied_idx = 28 if pied_frappe == "droit" else 27
    for i in range(len(keypoints_2d_par_frame)):
        if i in ball_positions:
            pied = keypoints_2d_par_frame[i][pied_idx]
            ballon = ball_positions[i]
            d = np.linalg.norm(np.array(pied) - np.array(ballon)) if pied != (-1, -1) else 0
            dist_pied_ballon.append(d)
        else:
            dist_pied_ballon.append(0)

    return {
        "keypoints_all": keypoints_2d_par_frame,
        "keypoints_3d": keypoints_3d_par_frame,  # ✅ ici
        "angles_all": angles_par_frame,
        "v_lin": vit_lin,
        "v_ang": vit_ang,
        "dist_pied_ballon": dist_pied_ballon
    }

def extraire_keypoints_3d_plotly(video_path, max_frames=200):
    mp_pose = mp.solutions.pose
    keypoints_3d = []

    cap = cv2.VideoCapture(video_path)
    with mp_pose.Pose(static_image_mode=False, model_complexity=2) as pose:
        while cap.isOpened() and len(keypoints_3d) < max_frames:
            success, frame = cap.read()
            if not success:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)
            if results.pose_world_landmarks:
                keypoints_frame = [(lm.x, lm.y, lm.z) for lm in results.pose_world_landmarks.landmark]
                keypoints_3d.append(keypoints_frame)
    cap.release()
    return np.array(keypoints_3d)


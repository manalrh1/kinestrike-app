import cv2
import pickle
import os
from tempfile import gettempdir
from ultralytics import YOLO

def detect_ball_yolo(video_path, output_path=None, conf=0.4):
    """
    Utilise YOLOv8s pour détecter la position du ballon dans chaque frame d'une vidéo.
    Sauvegarde les positions dans un fichier .pkl.
    """
    model = YOLO("yolov8s.pt")

    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    ball_positions = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(source=frame, conf=conf, verbose=False)[0]

        for r in results.boxes.data:
            x1, y1, x2, y2, score, cls = r.tolist()
            if int(cls) == 0:
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                ball_positions[frame_idx] = (cx, cy)
                break

        frame_idx += 1

    cap.release()

    if output_path is None:
        output_path = os.path.join(gettempdir(), "ball_positions.pkl")

    with open(output_path, "wb") as f:
        pickle.dump(ball_positions, f)

    return output_path

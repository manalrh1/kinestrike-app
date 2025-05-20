import numpy as np

def filtrer_frames_apres_approche(frames, indices, pourcentage=0.25):
    """
    Ne garde que les frames à partir d’un certain pourcentage de la vidéo.
    """
    start_idx = int(len(frames) * pourcentage)
    return frames[start_idx:], indices[start_idx:]

def segmenter_kick(frames_total, frame_kick, frame_impact, frame_recontact):
    """
    Retourne une liste de labels de phase (approche, kick_step, impact, suivi) pour chaque frame.
    """
    phases = []
    for i in range(frames_total):
        if i < frame_kick:
            phases.append("approche")
        elif frame_kick <= i < frame_impact:
            phases.append("kick_step")
        elif frame_impact <= i < frame_recontact:
            phases.append("impact")
        else:
            phases.append("suivi")
    return phases

def sauvegarder_phases(phases, path="phases_segmentées.txt"):
    """
    Sauvegarde la liste des phases dans un fichier texte.
    """
    with open(path, "w") as f:
        for label in phases:
            f.write(label + "\n")
    return path

# Test (facultatif)
if __name__ == "__main__":
    total = 90
    phase = segmenter_kick(frames_total=total, frame_kick=22, frame_impact=35, frame_recontact=50)
    print(f"Phases générées : {len(phase)}")
    print("🔹 Exemple : ", phase[20:40])
    sauvegarder_phases(phase)

RECOMMANDATIONS_PASSKICK = {

    # -------------------------------
    # 📍 PLACEMENT DU PIED D’APPUI
    # -------------------------------
    "placement": [
        {
            "erreur": "Pied d’appui mal positionné (trop éloigné latéralement ou en arrière)",
            "condition": lambda dx, dy: dx is not None and dy is not None and (dx < 20 or dx > 40 or dy < 20 or dy > 112),
            "message": "Placement du pied d’appui incorrect",
            "recommandation": (
                "Le pied d’appui est mal placé par rapport au ballon : trop éloigné latéralement "
                "(<20 mm ou >40 mm) ou mal en retrait (<20 mm ou >112 mm), ce qui déséquilibre le corps. "
                "Pour un bon transfert d’énergie et une stabilité optimale, le pied doit être situé à "
                "environ **5–10 cm sur le côté** du ballon et **0–5 cm en arrière**. "
                "🧩 Astuce : Utiliser un marqueur au sol (cône, adhésif) pour apprendre ce repère visuel."
            )
        }
    ],

    # -------------------------------
    # 🦵 ANGLES ARTICULAIRES
    # -------------------------------
    "angles": [
        {
            "erreur": "Amplitude de hanche incorrecte (hors 25°–40°)",
            "condition": lambda angle_h: angle_h is not None and not (25 <= angle_h <= 40),
            "message": "Flexion de hanche inadéquate",
            "recommandation": (
                "La hanche est soit trop fermée, soit trop ouverte, ce qui nuit à la compacité du geste. "
                "Une bonne frappe passe par une flexion de **25° à 40°** de la hanche. "
                "🎯 Exercice : pratiquer des flexions dynamiques contrôlées, en se filmant de profil pour vérifier l’angle."
            )
        },
        {
            "erreur": "Amplitude de genou incorrecte (hors 45°–65°)",
            "condition": lambda angle_g: angle_g is not None and not (45 <= angle_g <= 65),
            "message": "Flexion de genou inadéquate",
            "recommandation": (
                "Le genou est trop tendu ou trop fléchi, ce qui rompt l’équilibre entre précision et fluidité. "
                "Il faut viser une flexion de **45° à 65°** au moment du contact. "
                "📏 Astuce : utiliser un miroir latéral ou un outil de mesure vidéo pour s’auto-corriger."
            )
        }
    ],

    # -------------------------------
    # ⚡ VITESSE DU PIED
    # -------------------------------
    "vitesse": [
        {
            "erreur": "Vitesse du pied inférieure à 10 m/s",
            "condition": lambda v: v is not None and v < 10,
            "message": "Vitesse du pied insuffisante",
            "recommandation": (
                "La vitesse du pied est trop faible pour une passe nette. Cela peut traduire un manque d’accélération en fin de geste. "
                "🎯 Objectif : atteindre au moins **10 m/s** sur le segment cheville au moment de la frappe. "
                "🔁 Exercice : faire des passes rapides en statique avec ballon suspendu ou élastique pour stimuler la vitesse terminale."
            )
        }
    ],

    # -------------------------------
    # 🦶 CONTACT MÉDIAL / ORIENTATION
    # -------------------------------
    "contact": [
        {
            "erreur": "Pied mal orienté (pas de contact avec la face interne)",
            "condition": lambda orientation_note: orientation_note is not None and orientation_note < 8,
            "message": "Orientation du pied incorrecte à l’impact",
            "recommandation": (
                "Le pied ne présente pas correctement la face interne au ballon, ce qui provoque des passes imprécises. "
                "Il faut viser une orientation à **90° ±10°** au moment du contact pour que le ballon parte droit. "
                "📌 Drill visuel : poser une ligne ou un plot devant le pied et s’assurer qu’il reste perpendiculaire à la cible."
            )
        }
    ]
}

RECOMMANDATIONS_GLOBALES_PASSKICK = {
    "<5": (
        "❌ Insuffisant",
        "Le geste est techniquement mal exécuté : le pied ne frappe pas avec la face interne, les angles sont inadaptés ou la vitesse est trop faible. Un travail fondamental est requis pour stabiliser le geste et retrouver un schéma moteur correct."
    ),
    "5-6.9": (
        "⚠️ À corriger",
        "La passe est fonctionnelle mais souffre de défauts techniques clairs (orientation, placement, vitesse ou posture). Des répétitions guidées et des corrections ciblées permettront d’améliorer la fluidité du geste."
    ),
    "7-8.9": (
        "✅ Correct",
        "Le geste est bien structuré avec quelques légers défauts (intensité, précision ou placement). Un entraînement de consolidation est recommandé pour viser une exécution optimale."
    ),
    "9-10": (
        "⭐ Excellent",
        "La passe est réalisée avec précision, stabilité et bon contrôle biomécanique. Le contact est propre, les vitesses sont adéquates, et le positionnement est optimal. Geste maîtrisé et reproductible."
    )
}

def generer_recommandations_passkick(eval_dict):
    recommandations = []

    dx = eval_dict.get("dx")
    dy = eval_dict.get("dy")
    for reco in RECOMMANDATIONS_PASSKICK["placement"]:
        if reco["condition"](dx, dy):
            recommandations.append(("Placement", reco["message"], reco["recommandation"]))

    angle_h = eval_dict.get("angle_hanche")
    angle_g = eval_dict.get("angle_genou")
    for reco in RECOMMANDATIONS_PASSKICK["angles"]:
        if "angle_h" in reco["condition"].__code__.co_varnames:
            if reco["condition"](angle_h):
                recommandations.append(("Angles", reco["message"], reco["recommandation"]))
        elif "angle_g" in reco["condition"].__code__.co_varnames:
            if reco["condition"](angle_g):
                recommandations.append(("Angles", reco["message"], reco["recommandation"]))

    v_cheville = eval_dict.get("v_cheville")
    for reco in RECOMMANDATIONS_PASSKICK["vitesse"]:
        if reco["condition"](v_cheville):
            recommandations.append(("Vitesse", reco["message"], reco["recommandation"]))

    orientation_note = eval_dict.get("note_orientation")
    for reco in RECOMMANDATIONS_PASSKICK["contact"]:
        if reco["condition"](orientation_note):
            recommandations.append(("Contact", reco["message"], reco["recommandation"]))

    return recommandations


def generer_recommandation_globale_passkick(note_finale):
    if note_finale < 5:
        return RECOMMANDATIONS_GLOBALES_PASSKICK["<5"]
    elif note_finale < 7:
        return RECOMMANDATIONS_GLOBALES_PASSKICK["5-6.9"]
    elif note_finale < 9:
        return RECOMMANDATIONS_GLOBALES_PASSKICK["7-8.9"]
    else:
        return RECOMMANDATIONS_GLOBALES_PASSKICK["9-10"]


def generer_analyse_qualitative_passkick(notes_dict):
    points_forts = []
    points_a_ameliorer = []

    descriptions = {
        "placement": {
            "fort": "Pied d’appui bien positionné, garantissant équilibre et précision.",
            "faible": "Pied d’appui mal aligné, entraînant perte de stabilité ou trajectoire incertaine."
        },
        "angles": {
            "fort": "Angles articulaires cohérents, geste compact et équilibré.",
            "faible": "Angles non maîtrisés, nécessitant un travail sur la posture et la mécanique du geste."
        },
        "vitesse": {
            "fort": "Bonne accélération du pied au contact, favorisant une passe dynamique.",
            "faible": "Vitesse insuffisante au moment du contact, limitant l’efficacité de la passe."
        },
        "contact": {
            "fort": "Contact médial bien orienté, garantissant une trajectoire précise.",
            "faible": "Orientation incorrecte du pied au contact, affectant la direction du ballon."
        }
    }

    for critere, note in notes_dict.items():
        if note >= 8:
            points_forts.append(f"Point fort : {descriptions[critere]['fort']}")
        elif note < 7:
            points_a_ameliorer.append(f"À améliorer : {descriptions[critere]['faible']}")

    return points_forts, points_a_ameliorer

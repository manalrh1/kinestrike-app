RECOMMANDATIONS_PAR_PHASE = {

    "approche": [
        {
            "erreur": "Angle d’approche trop fermé (< 30°)",
            "condition": lambda angle: angle is not None and angle < 30,
            "message": "Angle d’approche trop fermé (< 30°)",
            "recommandation": (
                "❌ Problème : La joueuse attaque le ballon trop de face, ce qui limite la rotation du bassin.\n\n"
                "🎯 Objectif : Améliorer l'angle de course pour favoriser une rotation plus fluide du tronc "
                "et un meilleur transfert d'énergie.\n\n"
                "🏋️‍♀️ Exercice : S’entraîner à varier l’angle de course en posant des plots à 30°–45° par rapport à la cible. "
                "Répéter des courses d’élan contrôlées vers le ballon en passant par ces repères."
            )
        },
        {
            "erreur": "Angle d’approche trop ouvert (> 45°)",
            "condition": lambda angle: angle is not None and angle > 45,
            "message": "Angle d’approche trop ouvert (> 45°)",
            "recommandation": (
                "❌ Problème : Un angle trop latéral désaxe la ligne de frappe et réduit la stabilité.\n\n"
                "🎯 Objectif : Ramener l’angle dans la zone efficace de 30° à 45° pour garantir précision et contrôle.\n\n"
                "🏋️‍♀️ Exercice : Placer deux cônes pour baliser une trajectoire d’approche entre 30° et 45°. "
                "Effectuer des courses courtes avec frappe sur ballon placé pour ancrer ce repère visuel."
            )
        },
        {
            "erreur": "Pied d’appui mal placé (dx ou dy hors zone)",
            "condition": lambda dx, dy: dx is not None and dy is not None and (dx < 20 or dx > 40 or dy < 20 or dy > 112),
            "message": "Placement du pied d’appui non optimal (latéral ou arrière)",
            "recommandation": (
                "❌ Problème : Le pied d’appui est mal positionné par rapport au ballon, ce qui déséquilibre le corps "
                "et compromet la transmission d’énergie.\n\n"
                "🎯 Objectif : Stabiliser le placement à **5–10 cm sur le côté** du ballon et **0–5 cm en arrière**.\n\n"
                "🏋️‍♀️ Exercice : Disposer des repères visuels (plots ou ruban adhésif) au sol autour du ballon. "
                "Travailler des frappes lentes en visant la zone cible définie autour du pied d’appui."
            )
        }
    ],

    "kick_step": [
        {
            "erreur": "Séquence proximale-distale non respectée (logique des vitesses)",
            "condition": lambda eval_lin, eval_ang: eval_lin and eval_ang and (
                any("incohérent" in v.lower() or "anomalie" in v.lower() for v in eval_lin.values()) or
                any("incohérent" in v.lower() or "anomalie" in v.lower() for v in eval_ang.values())
            ),
            "message": "Mauvaise coordination cuisse → jambe → pied",
            "recommandation": (
                "❌ Problème : Le mouvement n’est pas enchaîné dans le bon ordre, ce qui diminue la fluidité et la puissance.\n\n"
                "🎯 Objectif : Respecter la séquence proximale-distale (cuisse → jambe → pied).\n\n"
                "🏋️‍♀️ Exercice : Réaliser des frappes au ralenti, en mettant l'accent sur chaque segment. "
                "Filmer l'exécution pour vérifier que la jambe fouette après la cuisse, et que le pied arrive en dernier."
            )
        }
    ],

    "impact": [
        {
            "erreur": "Timing du pic de vitesse incorrect",
            "condition": lambda timing_msg: timing_msg and ("trop éloigné" in timing_msg.lower() or "aucun" in timing_msg.lower()),
            "message": "Pic de vitesse mal synchronisé avec l’impact",
            "recommandation": (
                "❌ Problème : Le pic de vitesse ne coïncide pas avec le moment de l’impact, réduisant l’efficacité de la frappe.\n\n"
                "🎯 Objectif : Synchroniser l'accélération maximale du pied avec le moment précis du contact.\n\n"
                "🏋️‍♀️ Exercice : Utiliser un ballon suspendu ou un signal sonore pour déclencher la frappe. "
                "Analyser le timing via des vidéos en ralenti pour affiner la synchronisation."
            )
        },
        {
            "erreur": "Cheville non verrouillée (amplitude faible)",
            "condition": lambda note: note is not None and note < 8,
            "message": "Cheville non verrouillée à l’impact",
            "recommandation": (
                "❌ Problème : Une cheville molle réduit la précision et la puissance du tir.\n\n"
                "🎯 Objectif : Maintenir une cheville verrouillée (rigide) au moment du contact.\n\n"
                "🏋️‍♀️ Exercice : Pratiquer des frappes pieds nus sur tapis souple pour renforcer les muscles stabilisateurs. "
                "Se concentrer sur la rigidité de la cheville pendant les répétitions lentes puis rapides."
            )
        }
    ],

    "suivi": [
        {
            "erreur": "Pas de ralentissement progressif après impact",
            "condition": lambda suivi_eval: suivi_eval and (
                "aucun ralentissement" in suivi_eval.get("cheville", "").lower() or
                "aucune diminution" in suivi_eval.get("jambe", "").lower()
            ),
            "message": "Ralentissement post-impact non maîtrisé",
            "recommandation": (
                "❌ Problème : Le geste s'arrête trop brutalement après impact, ce qui coupe la fluidité du mouvement.\n\n"
                "🎯 Objectif : Favoriser un ralentissement naturel et progressif du membre frappant après la frappe.\n\n"
                "🏋️‍♀️ Exercice : Utiliser des ballons mous pour s’exercer à prolonger le mouvement sans blocage. "
                "Filmer le geste pour observer la continuité du pied et du tronc après le contact."
            )
        },
        {
            "erreur": "Alignement tronc-bassin insuffisant",
            "condition": lambda note: note is not None and note < 8,
            "message": "Retour du tronc incomplet (alignement tronc-bassin)",
            "recommandation": (
                "❌ Problème : Le haut du corps ne suit pas la dynamique du geste, ce qui déséquilibre la posture post-frappe.\n\n"
                "🎯 Objectif : Réintégrer un recentrage naturel du tronc et des épaules après le tir.\n\n"
                "🏋️‍♀️ Exercice : Travailler la finition avec une consigne de relâchement des bras opposés. "
                "Filmer de face ou de dos pour ajuster l’alignement dans la phase de retour."
            )
        }
    ]
}


RECOMMANDATIONS_GLOBALES = {
    "<5": (
        "❌ Insuffisant",
        "Le geste est globalement mal structuré, avec un enchaînement peu fluide des phases, "
        "un manque de coordination cuisse-jambe-pied, et souvent un mauvais timing de l’impact. "
        "L’efficacité biomécanique est compromise, ce qui peut entraîner une perte de puissance, "
        "de contrôle ou un risque de blessure. Il est essentiel de retravailler les bases techniques "
        "avec un encadrement rigoureux."
    ),
    "5-6.9": (
        "⚠️ À corriger",
        "Le tir présente des défauts visibles, souvent liés à une coordination partielle ou à des erreurs "
        "dans le positionnement du pied d’appui, la gestion des vitesses ou l’alignement postural. "
        "Ces erreurs limitent la puissance, la précision ou la stabilité du geste. "
        "Un entraînement correctif par phase (notamment impact et suivi) est nécessaire pour revenir vers un geste performant."
    ),
    "7-8.9": (
        "✅ Correct",
        "Le tir est globalement bien réalisé, avec une structure technique cohérente. "
        "Quelques désajustements mineurs peuvent subsister "

        "Quelques désajustements mineurs peuvent subsister, "
        ", mais le geste reste fonctionnel et efficace dans la majorité des cas. "
        "Un travail ciblé sur certaines phases permettra de progresser rapidement."
    ),
    "9-10": (
        "⭐ Excellent",
        "Le geste est exécuté avec une grande fluidité et une très bonne coordination segmentaire. "
        "La technique est conforme aux standards du modèle élite, avec un bon enchaînement des phases, "
        "un timing optimal de l’impact, un bon verrouillage articulaire, et un mouvement de suivi bien maîtrisé. "
        "Très peu de corrections sont nécessaires, l’athlète peut viser la performance maximale."
    )
}

def generer_recommandations(eval_dict):
    recommandations = []

    # Approche
    angle = eval_dict.get("angle_approche")
    dx = eval_dict.get("dx")
    dy = eval_dict.get("dy")
    for reco in RECOMMANDATIONS_PAR_PHASE["approche"]:
        if "angle" in reco["condition"].__code__.co_varnames:
            if reco["condition"](angle):
                recommandations.append(("Approche", reco["message"], reco["recommandation"]))
        else:
            if reco["condition"](dx, dy):
                recommandations.append(("Approche", reco["message"], reco["recommandation"]))

    # Kick Step
    eval_lin = eval_dict.get("eval_lin", {})
    eval_ang = eval_dict.get("eval_ang", {})
    for reco in RECOMMANDATIONS_PAR_PHASE["kick_step"]:
        if reco["condition"](eval_lin, eval_ang):
            recommandations.append(("Kick Step", reco["message"], reco["recommandation"]))

    # Impact
    timing_msg = eval_dict.get("timing_msg")
    note_cheville = eval_dict.get("note_cheville")
    for reco in RECOMMANDATIONS_PAR_PHASE["impact"]:
        if "timing_msg" in reco["condition"].__code__.co_varnames:
            if reco["condition"](timing_msg):
                recommandations.append(("Impact", reco["message"], reco["recommandation"]))
        else:
            if reco["condition"](note_cheville):
                recommandations.append(("Impact", reco["message"], reco["recommandation"]))

    # Suivi
    suivi_eval = eval_dict.get("suivi_eval", {})
    alignement_note = eval_dict.get("alignement_note")
    for reco in RECOMMANDATIONS_PAR_PHASE["suivi"]:
        if "suivi_eval" in reco["condition"].__code__.co_varnames:
            if reco["condition"](suivi_eval):
                recommandations.append(("Suivi", reco["message"], reco["recommandation"]))
        else:
            if reco["condition"](alignement_note):
                recommandations.append(("Suivi", reco["message"], reco["recommandation"]))

    return recommandations

def generer_recommandation_globale(note_finale):
    note_finale = float(note_finale)  # Assure une comparaison sûre
    if note_finale < 5:
        return RECOMMANDATIONS_GLOBALES["<5"]
    elif 5 <= note_finale < 7:
        return RECOMMANDATIONS_GLOBALES["5-6.9"]
    elif 7 <= note_finale < 9:
        return RECOMMANDATIONS_GLOBALES["7-8.9"]
    else:
        return RECOMMANDATIONS_GLOBALES["9-10"]


def generer_analyse_qualitative(notes_par_phase):
    points_forts = []
    points_a_ameliorer = []

    descriptions = {
        "approche": {
            "fort": (
                "La trajectoire d’approche est optimale : l'angle choisi facilite l'ouverture du bassin, "
                "et le pied d’appui est positionné de manière stable, garantissant un élan fluide et équilibré vers le ballon."
            ),
            "faible": (
                "La trajectoire d’approche présente des défauts : l'angle d'attaque est inadapté, réduisant la capacité "
                "de rotation du bassin, et le positionnement du pied d’appui ne permet pas un bon équilibre avant la frappe."
            )
        },
        "kick_step": {
            "fort": (
                "La phase de kick step est bien maîtrisée : la coordination entre la cuisse, la jambe et le pied est progressive, "
                "permettant une montée efficace de la vitesse jusqu’au moment de l’impact."
            ),
            "faible": (
                "La phase de kick step révèle un manque de coordination : le transfert d'énergie entre la cuisse, la jambe "
                "et le pied est interrompu, ce qui limite la montée en puissance avant l’impact."
            )
        },
        "impact": {
            "fort": (
                "Le moment d'impact est techniquement réussi : la synchronisation du pic de vitesse avec le contact ballon-pied "
                "est efficace, et la cheville est verrouillée, maximisant la transmission de force."
            ),
            "faible": (
                "L’impact est mal maîtrisé : la synchronisation du pic de vitesse est décalée par rapport au contact, "
                "et l'absence de verrouillage de la cheville réduit la puissance et la précision de la frappe."
            )
        },
        "suivi": {
            "fort": (
                "Le suivi post-frappe est fluide : la jambe ralentit progressivement après l'impact et l'alignement "
                "tronc-bassin est bien conservé, assurant stabilité et équilibre en fin de geste."
            ),
            "faible": (
                "Le suivi post-frappe manque de fluidité : l'arrêt brutal du geste nuit à l’équilibre, et l’alignement "
                "tronc-bassin n’est pas correctement restauré après la frappe."
            )
        }
    }

    for phase, note in notes_par_phase.items():
        if phase in descriptions:
            if note >= 8:
                commentaire = descriptions[phase]["fort"]
                points_forts.append(f"🟢 {phase.capitalize()} : {commentaire}")
            elif note < 8:
                commentaire = descriptions[phase]["faible"]
                points_a_ameliorer.append(f"🔴 {phase.capitalize()} : {commentaire}")

    return points_forts, points_a_ameliorer

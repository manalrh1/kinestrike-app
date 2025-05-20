RECOMMANDATIONS_PAR_PHASE_INSIDE = {

    # -------------------------------
    # 🟢 PHASE D’APPROCHE
    # -------------------------------
    "approche": [
        {
            "erreur": "Angle d’approche non optimal (<20° ou >40°)",
            "condition": lambda angle: angle is not None and (angle < 20 or angle > 40),
            "message": "Angle d’approche non adapté",
            "recommandation": (
                "❌ Problème : L’angle d’approche est trop fermé ou trop ouvert, ce qui désaxe la trajectoire du pied.\n\n"
                "🎯 Objectif : Ajuster l’angle entre **20° et 40°** pour exposer correctement la face interne du pied au ballon.\n\n"
                "🏋️‍♀️ Exercice : Tracer deux lignes au sol formant un couloir d’approche. Effectuer des courses contrôlées dans cet intervalle "
                "et frapper un ballon fixe en respectant la trajectoire imposée."
            )
        },
        {
            "erreur": "Pied d’appui mal placé",
            "condition": lambda dx, dy: dx is not None and dy is not None and (dx < 5 or dx > 10 or dy < 0 or dy > 5),
            "message": "Placement du pied d’appui incorrect",
            "recommandation": (
                "❌ Problème : Le pied d’appui est trop proche, trop loin ou mal aligné, ce qui affecte l’équilibre et le contrôle.\n\n"
                "🎯 Objectif : Placer le pied à **5–10 cm sur le côté** du ballon, légèrement en retrait (**0–5 cm derrière**).\n\n"
                "🏋️‍♀️ Exercice : Délimiter une “zone cible” autour du ballon avec des cercles ou bandes adhésives. "
                "S’entraîner à positionner son pied d’appui dans cette zone lors de passes ou frappes statiques."
            )
        },
        {
            "erreur": "Amplitude articulaire insuffisante",
            "condition": lambda notes: any(n is not None and n < 6 for n in notes.values()),
            "message": "Amplitude insuffisante (hanche, genou ou cheville)",
            "recommandation": (
                "❌ Problème : Le geste est limité, manquant d’engagement articulaire, ce qui réduit sa fluidité.\n\n"
                "🎯 Objectif : Développer des amplitudes dynamiques suffisantes au niveau des hanches, genoux et chevilles.\n\n"
                "🏋️‍♀️ Exercice : Réaliser des séries de fentes dynamiques, montées de genoux et extensions talon-fesse avant les frappes. "
                "Inclure des exercices de mobilité articulaire active."
            )
        }
    ],

    # -------------------------------
    # 🟠 PHASE DE KICK STEP (FRAPPE)
    # -------------------------------
    "kick_step": [
        {
            "erreur": "Coordination segmentaire incorrecte",
            "condition": lambda eval_lin, eval_ang: eval_lin and eval_ang and (
                any("incohérent" in v.lower() or "anomalie" in v.lower() for v in eval_lin.values()) or
                any("incohérent" in v.lower() or "anomalie" in v.lower() for v in eval_ang.values())
            ),
            "message": "Séquence proximale-distale incorrecte",
            "recommandation": (
                "❌ Problème : Les segments (cuisse, jambe, pied) ne s’enchaînent pas correctement, altérant le transfert de vitesse.\n\n"
                "🎯 Objectif : Exécuter la séquence cuisse → jambe → pied de manière fluide et différée.\n\n"
                "🏋️‍♀️ Exercice : Travailler au ralenti avec des vidéos ou miroirs, en décomposant les mouvements. "
                "Privilégier les frappes à vide ou sur ballon suspendu pour se concentrer sur l’ordre d’activation."
            )
        },
        {
            "erreur": "Pied mal orienté à l’impact",
            "condition": lambda orientation_note: orientation_note is not None and orientation_note < 8,
            "message": "Orientation du pied au contact incorrecte",
            "recommandation": (
                "❌ Problème : Le pied n’est pas perpendiculaire à la trajectoire, ce qui perturbe la direction de la frappe.\n\n"
                "🎯 Objectif : Garder le pied perpendiculaire au ballon pour assurer un contact médial optimal.\n\n"
                "🏋️‍♀️ Exercice : Utiliser une cible visuelle au sol (ligne ou cercle). Répéter des frappes lentes en s’assurant que "
                "le pied reste bien aligné au moment du contact avec le ballon."
            )
        },
        {
            "erreur": "Cheville non verrouillée",
            "condition": lambda note: note is not None and note < 8,
            "message": "Cheville non verrouillée à l’impact",
            "recommandation": (
                "❌ Problème : Une cheville trop souple entraîne une perte de puissance et de précision.\n\n"
                "🎯 Objectif : Verrouiller la cheville pour une frappe stable et puissante.\n\n"
                "🏋️‍♀️ Exercice : Réaliser des frappes pieds nus sur tapis souple. Concentrer la tension dans le pied lors du contact. "
                "Ajouter des exercices de gainage du pied et de proprioception (équilibre unipodal)."
            )
        }
    ],

    # -------------------------------
    # 🔵 PHASE DE SUIVI
    # -------------------------------
    "suivi": [
        {
            "erreur": "Pas de ralentissement progressif après impact",
            "condition": lambda suivi_eval: suivi_eval and (
                "aucune diminution" in suivi_eval.get("cheville", "").lower()
            ),
            "message": "Ralentissement post-impact non maîtrisé",
            "recommandation": (
                "❌ Problème : Le geste s’arrête trop net, ce qui interrompt la dynamique globale du mouvement.\n\n"
                "🎯 Objectif : Maintenir un relâchement progressif après l’impact pour favoriser un geste fluide.\n\n"
                "🏋️‍♀️ Exercice : Utiliser des ballons légers ou dégonflés pour inciter à prolonger le mouvement. "
                "Répéter des frappes en insistant sur la continuité du geste au-delà du contact avec le ballon."
            )
        },
        {
            "erreur": "Alignement tronc-bassin insuffisant",
            "condition": lambda note: note is not None and note < 8,
            "message": "Retour du tronc incomplet (alignement tronc-bassin)",
            "recommandation": (
                "❌ Problème : Le tronc ne suit pas le mouvement, ce qui crée une perte d’équilibre après la frappe.\n\n"
                "🎯 Objectif : Réaligner le tronc et le bassin dans l’axe après l’impact.\n\n"
                "🏋️‍♀️ Exercice : Travailler des frappes lentes en s’imposant une phase de finition contrôlée, bras opposé levé. "
                "Analyser la vidéo de dos pour détecter les désalignements post-impact."
            )
        }
    ]
}

# --------------------------------------------------
# 2. Recommandations globales (selon note finale)
# --------------------------------------------------

RECOMMANDATIONS_GLOBALES_INSIDE = {
    "<5": (
        "❌ Insuffisant",
        "Le geste est mal structuré avec des défauts majeurs : positionnement, orientation ou coordination incorrects. Il est recommandé de reprendre les fondamentaux avec un encadrement personnalisé."
    ),
    "5-6.9": (
        "⚠️ À corriger",
        "Le geste présente des irrégularités qui nuisent à la précision ou à l’équilibre. Un travail ciblé sur la posture d’impact et la phase de suivi est recommandé."
    ),
    "7-8.9": (
        "✅ Correct",
        "Le geste est cohérent et fonctionnel, mais certains éléments peuvent être optimisés (fluidité, relâchement, orientation du pied). Des exercices spécifiques permettront d’élever la performance."
    ),
    "9-10": (
        "⭐ Excellent",
        "Le tir est fluide, stable et précis, avec une très bonne maîtrise technique. Seuls des réglages fins sont nécessaires pour atteindre un geste d’élite."
    )
}

# --------------------------------------------------
# 3. Fonctions d’analyse
# --------------------------------------------------

def generer_recommandations_inside(eval_dict):
    recommandations = []

    angle = eval_dict.get("angle_approche")
    dx = eval_dict.get("dx")
    dy = eval_dict.get("dy")
    notes_amplitudes = eval_dict.get("notes_approche_angles", {})
    for reco in RECOMMANDATIONS_PAR_PHASE_INSIDE["approche"]:
        if "notes" in reco["condition"].__code__.co_varnames:
            if reco["condition"](notes_amplitudes):
                recommandations.append(("Approche", reco["message"], reco["recommandation"]))
        elif "angle" in reco["condition"].__code__.co_varnames:
            if reco["condition"](angle):
                recommandations.append(("Approche", reco["message"], reco["recommandation"]))
        else:
            if reco["condition"](dx, dy):
                recommandations.append(("Approche", reco["message"], reco["recommandation"]))

    eval_lin = eval_dict.get("eval_lin", {})
    eval_ang = eval_dict.get("eval_ang", {})
    note_orientation = eval_dict.get("note_impact_orientation")
    note_cheville = eval_dict.get("note_cheville_impact")
    for reco in RECOMMANDATIONS_PAR_PHASE_INSIDE["kick_step"]:
        if "eval_lin" in reco["condition"].__code__.co_varnames:
            if reco["condition"](eval_lin, eval_ang):
                recommandations.append(("Kick Step", reco["message"], reco["recommandation"]))
        elif "orientation_note" in reco["condition"].__code__.co_varnames:
            if reco["condition"](note_orientation):
                recommandations.append(("Kick Step", reco["message"], reco["recommandation"]))
        else:
            if reco["condition"](note_cheville):
                recommandations.append(("Kick Step", reco["message"], reco["recommandation"]))

    suivi_eval = eval_dict.get("suivi_eval", {})
    alignement_note = eval_dict.get("alignement_note")
    for reco in RECOMMANDATIONS_PAR_PHASE_INSIDE["suivi"]:
        if "suivi_eval" in reco["condition"].__code__.co_varnames:
            if reco["condition"](suivi_eval):
                recommandations.append(("Suivi", reco["message"], reco["recommandation"]))
        else:
            if reco["condition"](alignement_note):
                recommandations.append(("Suivi", reco["message"], reco["recommandation"]))

    return recommandations

def generer_recommandation_globale_inside(note_finale):
    if note_finale < 5:
        return RECOMMANDATIONS_GLOBALES_INSIDE["<5"]
    elif note_finale < 7:
        return RECOMMANDATIONS_GLOBALES_INSIDE["5-6.9"]
    elif note_finale < 9:
        return RECOMMANDATIONS_GLOBALES_INSIDE["7-8.9"]
    else:
        return RECOMMANDATIONS_GLOBALES_INSIDE["9-10"]

def generer_analyse_qualitative_inside(notes_par_phase):
    points_forts = []
    points_a_ameliorer = []

    descriptions = {
        "approche": {
            "fort": "Approche maîtrisée avec bon placement du pied d’appui et orientation optimale.",
            "faible": "Approche à corriger : placement, angle ou posture déséquilibrée."
        },
        "kick_step": {
            "fort": "Coordination cuisse-jambe-pied fluide, contact intérieur bien orienté.",
            "faible": "Transfert ou impact mal enchaîné, perte de précision au contact."
        },
        "suivi": {
            "fort": "Relâchement post-impact et recentrage du tronc bien exécutés.",
            "faible": "Suivi incomplet ou perte d’équilibre, nécessitant une correction posturale."
        }
    }

    for phase, note in notes_par_phase.items():
        if phase in descriptions:
            if note >= 8:
                points_forts.append(f"Point fort : {descriptions[phase]['fort']}")
            elif note < 7:
                points_a_ameliorer.append(f"À améliorer : {descriptions[phase]['faible']}")

    return points_forts, points_a_ameliorer

def analyse_biomeca_inside():
    import os
    import tempfile
    from datetime import datetime
    import streamlit as st

    from biomeca import VALEURS_REF_INSIDE, verifier_alignement_tronc_bassin
    from vitesses import (
        get_fps_from_video,
        decouper_activation_transfert,
        verifier_logique_vitesses_lineaires,
        verifier_logique_vitesses_angulaires,
        estimer_px_to_m_depuis_hanche_genou
    )
    from extraction import extraire_donnees_biomecaniques
    from notation_inside import (
        noter_angles_par_cote_inside,
        extraire_notes_par_moment_inside,
        generer_score_global_inside,
        noter_orientation_pied,
        noter_evaluation_vitesse
    )
    from recommandations_inside import (
        generer_recommandations_inside,
        generer_analyse_qualitative_inside,
        generer_recommandation_globale_inside
    )
    from rapport import generer_rapport_pdf
    from segmentation_evenementielle import segmenter_kick
    from visualisation import (
        generer_video_annotee,
        enregistrer_image_pose,
        tracer_graphiques_vitesses,
        detecter_postures_anotees
    )

    st.markdown("<h2 style='text-align:center;'>📊 Étape 7 : Analyse biomécanique complète – Inside</h2>", unsafe_allow_html=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(st.session_state.video_bytes.getbuffer())
        video_path = tmp.name

    t1, t2, t3 = st.session_state.frame_kick, st.session_state.frame_impact, st.session_state.frame_postimpact
    pied = st.session_state.pied_frappe.lower()
    ball_path = st.session_state.get("ball_position_path", None)

    if "donnees" not in st.session_state:
        st.session_state.donnees = extraire_donnees_biomecaniques(video_path, ball_path, pied)
    donnees = st.session_state.donnees

    fps = get_fps_from_video(video_path)
    frames_kick = list(range(t1, t2 + 1))
    indices_par_phase = decouper_activation_transfert(frames_kick, t2)

    angles_approche = donnees["angles_all"][t1]
    angles_kick = donnees["angles_all"][t2 - 1]
    angles_impact = donnees["angles_all"][t2]
    angles_suivi = donnees["angles_all"][t3] if t3 < len(donnees["angles_all"]) else {}

    notes_approche = noter_angles_par_cote_inside("approche", pied, angles_approche, VALEURS_REF_INSIDE)
    notes_kickstep = noter_angles_par_cote_inside("kickstep", pied, angles_kick, VALEURS_REF_INSIDE)
    note_cheville_impact = noter_angles_par_cote_inside("kickstep", pied, angles_impact, VALEURS_REF_INSIDE).get("cheville", 0)

    vit_lin, vit_ang = donnees["v_lin"], donnees["v_ang"]
    eval_lin = verifier_logique_vitesses_lineaires(vit_lin, indices_par_phase)
    eval_ang = verifier_logique_vitesses_angulaires(vit_ang, indices_par_phase)
    alignement_msg = verifier_alignement_tronc_bassin(donnees["keypoints_all"], list(range(t2, t3)), pied)
    note_alignement = noter_evaluation_vitesse(alignement_msg)

    angle_approche, dx, dy = 30, 7, 2
    orientation_angle = 90
    note_angle_approche = noter_evaluation_vitesse("correct")
    note_pied_appui = noter_evaluation_vitesse("correct")
    note_orientation_impact = noter_orientation_pied(orientation_angle)

    notes_par_phase = extraire_notes_par_moment_inside(
        notes_approche, note_angle_approche, note_pied_appui,
        notes_kickstep, vit_lin, vit_ang,
        orientation_angle, note_cheville_impact,
        vit_ang.get("cheville", {}), note_alignement
    )
    score_global, details_score = generer_score_global_inside(notes_par_phase)
    points_forts, points_a_corriger = generer_analyse_qualitative_inside(notes_par_phase)
    recommandations = generer_recommandations_inside({
        "angle_approche": angle_approche, "dx": dx, "dy": dy,
        "notes_approche_angles": notes_approche,
        "eval_lin": eval_lin, "eval_ang": eval_ang,
        "note_impact_orientation": note_orientation_impact,
        "note_cheville_impact": note_cheville_impact,
        "suivi_eval": vit_ang.get("cheville", {}),
        "alignement_note": note_alignement
    })
    titre_global, synthese_globale = generer_recommandation_globale_inside(round(score_global, 1))

    st.success(f"🎯 Score final : **{score_global}/10**")
    st.subheader("📈 Notes par phase")
    for phase, note in notes_par_phase.items():
        st.write(f"- **{phase.capitalize()}** : {note}/10")

    st.subheader("📌 Synthèse globale")
    st.info(f"**{titre_global}**\n\n{synthese_globale}")

    if points_forts:
        st.markdown("✅ **Points forts**")
        for pf in points_forts:
            st.success(pf)

    if points_a_corriger:
        st.markdown("❗ **À améliorer**")
        for pa in points_a_corriger:
            st.warning(pa)

    st.markdown("🛠️ **Recommandations spécifiques**")
    for phase, erreur, reco in recommandations:
        st.markdown(f"**[{phase}]** {erreur} → _{reco}_")

    total = len(donnees["keypoints_all"])
    phases = segmenter_kick(total, t1, t2, t3)

    frames_annotations = detecter_postures_anotees(
        notes_approche_angles=notes_approche,
        notes_kickstep_angles=notes_kickstep,
        ref_angles=VALEURS_REF_INSIDE,
        t1=t1,
        t2=t2,
        pied_frappe=pied
    )

    video_out_path = generer_video_annotee(
        video_path,
        donnees["keypoints_all"],
        phases,
        pied,
        frames_annotations=frames_annotations
    )

    st.subheader("🎞️ Vidéo annotée avec squelette et postures")
    if os.path.exists(video_out_path):
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            with open(video_out_path, "rb") as f:
                st.video(f.read())
            with open(video_out_path, "rb") as f:
                st.download_button(
                    "⬇️ Télécharger la vidéo annotée",
                    f,
                    file_name="video_annotee_inside.mp4",
                    use_container_width=True
                )

    # Estimation px_to_m avec la vraie catégorie
    categorie = st.session_state.get("categorie_joueuse", "U17")
    px_to_m = None
    for kp in donnees["keypoints_all"]:
        px_to_m = estimer_px_to_m_depuis_hanche_genou(kp, pied_frappe=pied, categorie=categorie)
        if px_to_m:
            break
    if not px_to_m:
        px_to_m = 0.005  # Fallback réaliste

    pose_path = enregistrer_image_pose(donnees["keypoints_all"], t2, video_path)
    graph1, graph2 = tracer_graphiques_vitesses(
        vitesses_lin_px=vit_lin,
        vitesses_ang=vit_ang,
        phases=phases,
        pied_frappe=pied,
        fps=fps,
        px_to_m=px_to_m
    )

    st.subheader("📊 Visualisations graphiques")
    col1, col2, col3 = st.columns([3, 2, 3])
    with col1:
        st.image(graph1, caption="Kick Step & Impact", use_container_width=True)
    with col3:
        st.image(graph2, caption="Évolution du pied", use_container_width=True)

    st.markdown("### 📄 Rapport PDF")
    nom_joueuse = st.session_state.get("joueuse_selectionnee", "Nom non défini")
    type_long = st.session_state.type_geste.strip()
    GESTE_TO_LABEL = {
        "Tir de cou-de-pied": "Instep",
        "Tir intérieur du pied": "Inside",
        "Passe intérieure du pied": "Passe"
    }
    label_type_geste = GESTE_TO_LABEL.get(type_long, "Tir")

    nom_fichier_base = (
        nom_joueuse.replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("'", "")
        .lower()
    )
    date_str = datetime.now().strftime("%Y%m%d")
    nom_pdf = f"rapport_inside_{nom_fichier_base}_{date_str}.pdf"

    if st.button("📥 Télécharger le rapport PDF", use_container_width=True):
        rapport_path = generer_rapport_pdf(
            notes_par_phase=notes_par_phase,
            score_global=score_global,
            details_score=details_score,
            points_forts=points_forts,
            points_a_ameliorer=points_a_corriger,
            recommandations=recommandations,
            reco_globale=synthese_globale,
            image_path=pose_path,
            graphe1=graph1,
            graphe2=graph2,
            nom_fichier=nom_pdf,
            nom_joueuse=nom_joueuse,
            type_geste=label_type_geste
        )
        with open(rapport_path, "rb") as f:
            st.download_button(
                label="📤 Télécharger le rapport généré",
                data=f,
                file_name=nom_pdf,
                use_container_width=True
            )

def analyse_biomeca_instep():
    import os
    import tempfile
    from datetime import datetime
    import streamlit as st

    from biomeca import VALEURS_REF_instep, verifier_alignement_tronc_bassin
    from vitesses import (
        get_fps_from_video,
        decouper_activation_transfert,
        verifier_logique_vitesses_lineaires,
        verifier_logique_vitesses_angulaires,
        verifier_suivi,
        verifier_timing_impact,
        estimer_px_to_m_depuis_hanche_genou
    )
    from extraction import extraire_donnees_biomecaniques
    from notation_instep import (
        noter_angles_par_cote,
        noter_evaluation_vitesse,
        extraire_notes_par_moment,
        generer_score_global
    )
    from recommandations_instep import (
        generer_recommandations,
        generer_analyse_qualitative,
        generer_recommandation_globale
    )
    from rapport import generer_rapport_pdf
    from visualisation import (
        generer_video_annotee,
        enregistrer_image_pose,
        tracer_graphiques_vitesses,
        detecter_postures_anotees
    )
    from segmentation_evenementielle import segmenter_kick

    st.markdown("<h2 style='text-align:center;'>📊 Étape 7 : Analyse biomécanique complète – Instep</h2>", unsafe_allow_html=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(st.session_state.video_bytes.getbuffer())
        video_path = tmp.name

    t1, t2, t3 = st.session_state.frame_kick, st.session_state.frame_impact, st.session_state.frame_postimpact
    pied = st.session_state.pied_frappe.lower()
    ball_path = st.session_state.get("ball_position_path", None)

    if "donnees" not in st.session_state:
        st.session_state.donnees = extraire_donnees_biomecaniques(video_path, ball_path, pied)
    donnees = st.session_state.donnees

    fps = get_fps_from_video(video_path)
    frames_kick = list(range(t1, t2 + 1))
    indices_par_phase = decouper_activation_transfert(frames_kick, t2)

    angles_approche = donnees["angles_all"][t1]
    angles_kick = donnees["angles_all"][t2 - 1]
    angles_impact = donnees["angles_all"][t2]
    angles_suivi = donnees["angles_all"][t3] if t3 < len(donnees["angles_all"]) else {}

    notes_approche = noter_angles_par_cote("approche", pied, angles_approche, VALEURS_REF_instep)
    notes_kickstep = noter_angles_par_cote("kickstep", pied, angles_kick, VALEURS_REF_instep)
    note_cheville_impact = noter_angles_par_cote("kickstep", pied, angles_impact, VALEURS_REF_instep).get("cheville", 0)

    vit_lin, vit_ang = donnees["v_lin"], donnees["v_ang"]
    eval_lin = verifier_logique_vitesses_lineaires(vit_lin, indices_par_phase)
    eval_ang = verifier_logique_vitesses_angulaires(vit_ang, indices_par_phase)
    suivi_eval = verifier_suivi(vit_ang, vit_lin, list(range(t2, t3)))
    alignement_msg = verifier_alignement_tronc_bassin(donnees["keypoints_all"], list(range(t2, t3)), pied)
    note_alignement = noter_evaluation_vitesse(alignement_msg)
    timing_msg = verifier_timing_impact(vit_lin["cheville"], t2)
    note_timing_impact = noter_evaluation_vitesse(timing_msg)

    angle_approche, dx, dy = 40, 30, 35
    note_angle_approche = noter_evaluation_vitesse("correct")
    note_pied_appui = noter_evaluation_vitesse("correct")

    notes_par_phase = extraire_notes_par_moment(
        notes_approche, note_angle_approche, note_pied_appui,
        notes_kickstep, eval_lin, eval_ang,
        note_cheville_impact, note_timing_impact,
        suivi_eval, note_alignement
    )
    score_global, details_score = generer_score_global(notes_par_phase)
    points_forts, points_a_corriger = generer_analyse_qualitative(notes_par_phase)
    recommandations = generer_recommandations({
        "angle_approche": angle_approche, "dx": dx, "dy": dy,
        "eval_lin": eval_lin, "eval_ang": eval_ang,
        "timing_msg": timing_msg, "note_cheville": note_cheville_impact,
        "suivi_eval": suivi_eval, "alignement_note": note_alignement
    })
    titre_global, synthese_globale = generer_recommandation_globale(round(score_global, 1))

    st.success(f"🎯 Score final : **{score_global}/10**")
    st.subheader("📈 Notes par phase")
    for phase, note in notes_par_phase.items():
        st.write(f"- **{phase.capitalize()}** : {note}/10")

    st.subheader("📌 Synthèse globale")
    st.info(f"**{titre_global}**\n\n{synthese_globale}")

    if points_forts:
        st.markdown("✅ **Points forts**")
        for pf in points_forts:
            st.success(pf)

    if points_a_corriger:
        st.markdown("❗ **À améliorer**")
        for pa in points_a_corriger:
            st.warning(pa)

    st.markdown("🛠️ **Recommandations spécifiques**")
    for phase, erreur, reco in recommandations:
        st.markdown(f"**[{phase}]** {erreur} → _{reco}_")

    total = len(donnees["keypoints_all"])
    phases = segmenter_kick(total, t1, t2, t3)

    frames_annotations = detecter_postures_anotees(
        notes_approche_angles=notes_approche,
        notes_kickstep_angles=notes_kickstep,
        ref_angles=VALEURS_REF_instep,
        t1=t1,
        t2=t2,
        pied_frappe=pied
    )

    video_out_path = generer_video_annotee(
        video_path,
        donnees["keypoints_all"],
        phases,
        pied_frappe=pied,
        frames_annotations=frames_annotations
    )

    st.subheader("🎞️ Vidéo annotée avec squelette et erreurs d’articulations")
    if os.path.exists(video_out_path):
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            with open(video_out_path, "rb") as f:
                st.video(f.read())
            with open(video_out_path, "rb") as f:
                st.download_button("⬇️ Télécharger la vidéo annotée", f, file_name="video_annotee_instep.mp4")

    # Estimation px_to_m selon la catégorie joueuse
    categorie = st.session_state.get("categorie_joueuse", "U17")
    px_to_m = None
    for kp in donnees["keypoints_all"]:
        px_to_m = estimer_px_to_m_depuis_hanche_genou(kp, pied_frappe=pied, categorie=categorie)
        if px_to_m:
            break
    if not px_to_m:
        px_to_m = 0.005  # fallback réaliste : 1px = 5mm

    pose_path = enregistrer_image_pose(donnees["keypoints_all"], t2, video_path)
    graph1, graph2 = tracer_graphiques_vitesses(
        vitesses_lin_px=vit_lin,
        vitesses_ang=vit_ang,
        phases=phases,
        pied_frappe=pied,
        fps=fps,
        px_to_m=px_to_m
    )

    st.subheader("📊 Visualisations graphiques")
    col1, col2, col3 = st.columns([3, 2, 3])
    with col1:
        st.image(graph1, caption="Kick Step & Impact", use_container_width=True)
    with col3:
        st.image(graph2, caption="Évolution du pied", use_container_width=True)

    st.markdown("### 📄 Rapport PDF")
    nom_joueuse = st.session_state.get("joueuse_selectionnee", "Nom non défini")
    type_long = st.session_state.type_geste.strip()
    GESTE_TO_LABEL = {
        "Tir de cou-de-pied": "Instep",
        "Tir intérieur du pied": "Inside",
        "Passe intérieure du pied": "Passe"
    }
    label_type_geste = GESTE_TO_LABEL.get(type_long, "Tir")

    nom_fichier_base = (
        nom_joueuse.replace(" ", "_")
        .replace("(", "").replace(")", "").replace("'", "").lower()
    )
    date_str = datetime.now().strftime("%Y%m%d")
    nom_pdf = f"rapport_instep_{nom_fichier_base}_{date_str}.pdf"

    if st.button("📥 Télécharger le rapport PDF", use_container_width=True):
        rapport_path = generer_rapport_pdf(
            notes_par_phase=notes_par_phase,
            score_global=score_global,
            details_score=details_score,
            points_forts=points_forts,
            points_a_ameliorer=points_a_corriger,
            recommandations=recommandations,
            reco_globale=synthese_globale,
            image_path=pose_path,
            graphe1=graph1,
            graphe2=graph2,
            nom_fichier=nom_pdf,
            nom_joueuse=nom_joueuse,
            type_geste=label_type_geste
        )
        with open(rapport_path, "rb") as f:
            st.download_button("📤 Télécharger le rapport généré", f, file_name=nom_pdf)
    # Définir les chemins en sortie pour stockage DB
    chemin_rapport = f"rapports/{nom_pdf}"
    chemin_video = video_out_path if os.path.exists(video_out_path) else None

    return score_global, chemin_rapport, chemin_video

def analyse_biomeca_passe():
    import os
    import tempfile
    from datetime import datetime
    import streamlit as st

    from biomeca import evaluer_orientation_pied
    from extraction import extraire_donnees_biomecaniques
    from parametres_spatiaux import calculer_position_pied_appui
    from vitesses import calculer_vitesses_lineaires
    from segmentation_evenementielle import segmenter_kick
    from visualisation import (
        generer_video_annotee,
        enregistrer_image_pose,
        tracer_graphiques_vitesses
    )
    from rapport import generer_rapport_pdf

    from notation_passkick import (
        noter_placement_pied,
        noter_angles,
        noter_vitesse_pied,
        noter_contact_medial,
        calculer_score_global
    )
    from recommandations_passkick import (
        generer_recommandations_passkick,
        generer_analyse_qualitative_passkick,
        generer_recommandation_globale_passkick
    )

    st.markdown("<h2 style='text-align:center;'>📊 Étape 7 : Analyse biomécanique – Passe intérieure</h2>", unsafe_allow_html=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(st.session_state.video_bytes.getbuffer())
        video_path = tmp.name

    t1, t2, t3 = st.session_state.frame_kick, st.session_state.frame_impact, st.session_state.frame_postimpact
    pied = st.session_state.pied_frappe.lower()
    ball_path = st.session_state.get("ball_position_path", None)

    if "donnees" not in st.session_state:
        st.session_state.donnees = extraire_donnees_biomecaniques(video_path, ball_path, pied)
    donnees = st.session_state.donnees

    keypoints = donnees["keypoints_all"]
    angles = donnees["angles_all"][t2]
    v_lin = calculer_vitesses_lineaires(donnees["keypoints_all"])

    # PARAMÈTRES CLÉS
    dx, dy = calculer_position_pied_appui(keypoints[t2], pied)
    note_placement, msg_placement = noter_placement_pied(dx, dy)
    note_angles, msg_angles = noter_angles(angles)
    v_cheville = v_lin["cheville"][t2]
    note_vitesse, msg_vitesse = noter_vitesse_pied(v_cheville)

    pied_coord = keypoints[t2].get(f"pied_{pied}")
    cheville_coord = keypoints[t2].get(f"cheville_{pied}")
    ballon_coord = donnees["ball"][t2] if "ball" in donnees and t2 in donnees["ball"] else None
    note_contact, msg_contact = noter_contact_medial(cheville_coord, pied_coord, ballon_coord)

    # SCORE GLOBAL
    notes = {
        "placement": note_placement,
        "angles": note_angles,
        "vitesse": note_vitesse,
        "contact": note_contact
    }
    score_global = calculer_score_global(notes)

    # RECOMMANDATIONS + SYNTHÈSE
    recommandations = generer_recommandations_passkick({
        "dx": dx,
        "dy": dy,
        "angle_h": angles.get("hanche_droit"),
        "angle_g": angles.get("genou_droit"),
        "v_cheville": v_cheville,
        "note_orientation": note_contact
    })

    titre, synthese = generer_recommandation_globale_passkick(score_global)
    points_forts, points_a_corriger = generer_analyse_qualitative_passkick(notes)

    # AFFICHAGE
    st.success(f"🎯 Score final : **{score_global}/10**")
    st.subheader("📈 Notes par critère")
    st.write(f"- Placement du pied : {note_placement}/10 – {msg_placement}")
    st.write(f"- Angles articulaires : {note_angles}/10 – {msg_angles}")
    st.write(f"- Vitesse du pied : {note_vitesse}/10 – {msg_vitesse}")
    st.write(f"- Contact médial : {note_contact}/10 – {msg_contact}")

    st.subheader("📌 Synthèse globale")
    st.info(f"**{titre}**\n\n{synthese}")

    if points_forts:
        st.markdown("✅ **Points forts**")
        for pf in points_forts:
            st.success(pf)

    if points_a_corriger:
        st.markdown("❗ **À améliorer**")
        for pa in points_a_corriger:
            st.warning(pa)

    if recommandations:
        st.markdown("🛠️ **Recommandations spécifiques**")
        for phase, erreur, reco in recommandations:
            st.markdown(f"**[{phase}]** {erreur} → _{reco}_")

    # VISUALISATION
    phases = segmenter_kick(len(keypoints), t1, t2, t3)
    video_out_path = generer_video_annotee(video_path, keypoints, phases, pied)
    pose_path = enregistrer_image_pose(keypoints, t2, video_path)
    graph1, graph2 = tracer_graphiques_vitesses(v_lin, phases, pied)

    st.subheader("🎞️ Vidéo annotée avec squelette et phases")
    if os.path.exists(video_out_path):
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            with open(video_out_path, "rb") as f:
                st.video(f.read())
            with open(video_out_path, "rb") as f:
                st.download_button("⬇️ Télécharger la vidéo annotée", f, file_name="video_annotee_passe.mp4")

    st.subheader("📊 Visualisations graphiques")
    col1, col2, col3 = st.columns([3, 2, 3])
    with col1:
        st.image(graph1, caption="Phase de frappe", use_container_width=True)
    with col3:
        st.image(graph2, caption="Évolution du pied", use_container_width=True)

    # RAPPORT
    st.markdown("### 📄 Rapport PDF")
    nom_joueuse = st.session_state.joueuse_selectionnee
    type_long = st.session_state.type_geste.strip()
    GESTE_TO_LABEL = {
        "Tir de cou-de-pied": "Instep",
        "Tir intérieur du pied": "Inside",
        "Passe intérieure du pied": "Passe"
    }
    label_type_geste = GESTE_TO_LABEL.get(type_long, "Tir")

    nom_fichier_base = (
        nom_joueuse.replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("'", "")
        .lower()
    )
    date_str = datetime.now().strftime("%Y%m%d")
    nom_pdf = f"rapport_{label_type_geste.lower()}_{nom_fichier_base}_{date_str}.pdf"

    notes_par_phase = notes  # correspondance attendue par le générateur
    details_score = {}       # tu peux remplir si tu veux détailler par pondération
    synthese_globale = synthese

    if st.button("📥 Télécharger le rapport PDF", use_container_width=True):
        rapport_path = generer_rapport_pdf(
            notes_par_phase=notes_par_phase,
            score_global=score_global,
            details_score=details_score,
            points_forts=points_forts,
            points_a_ameliorer=points_a_corriger,
            recommandations=recommandations,
            reco_globale=synthese_globale,
            image_path=pose_path,
            graphe1=graph1,
            graphe2=graph2,
            nom_fichier=nom_pdf,
            nom_joueuse=nom_joueuse,
            type_geste=label_type_geste  # nouveau paramètre utilisé dans le rapport
        )
        with open(rapport_path, "rb") as f:
            st.download_button(
                label="📤 Télécharger le rapport généré",
                data=f,
                file_name=nom_pdf,
                use_container_width=True
            )

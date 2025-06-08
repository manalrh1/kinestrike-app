
import streamlit as st
from PIL import Image
import io
from auth import login
from data_storage import init_db, ajouter_joueuse, get_joueuses_par_coach
from moviepy.editor import VideoFileClip
import streamlit.components.v1 as components
import base64
from analyse import analyse_biomeca_instep
from analyse import analyse_biomeca_inside
from data_storage import enregistrer_analyse
from ui_utils import afficher_sidebar_profil

if "etape" not in st.session_state:
    st.session_state.etape = 0  # Accueil par défaut

# ⚙️ Configurer la page Streamlit
st.set_page_config(page_title="KinéStrike", page_icon="⚽", layout="wide")

# ✅ Protection connexion : protéger SEULEMENT les étapes >= 2
if st.session_state.get("etape", 0) not in [0, 1] and "name" not in st.session_state:
    st.session_state.etape = 1  # Connexion
    st.rerun()

# ✅ Afficher la sidebar uniquement si connecté
if st.session_state.etape != 0 and st.session_state.get("name"):
    from ui_utils import afficher_sidebar_profil
    afficher_sidebar_profil()

# --------------------
# ÉTAPE 0 : Accueil
# --------------------
if st.session_state.etape == 0:
    st.markdown("""
        <style>
            .centered-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                margin-top: 20px; /* ← Réduit la marge pour remonter */
            }
            .title {
                font-size: 40px;
                color: #cc4e4e;
                font-weight: bold;
                margin-top: 10px;
            }
            .desc {
                max-width: 600px;
                font-size: 18px;
                color: #444;
                margin: 20px 0;
            }
            .stButton>button {
                background-color: #cc4e4e;
                color: white;
                font-weight: bold;
                padding: 0.75em 2em;
                font-size: 18px;
                border-radius: 8px;
                border: none;
                transition: 0.3s;
                margin-top: 10px;
            }
            .stButton>button:hover {
                background-color: #b73737;
            }
        </style>

        <div class="centered-container">
            <img src="https://raw.githubusercontent.com/manalrh1/kinestrike-app/main/img.png" width="320">
            <div class="title">Analyse du Geste Sportif</div>
            <div class="desc">
                Bienvenue dans votre assistant d’analyse du mouvement :
                <ul style="text-align: left;">
                    <li>🎯 Détection automatique des phases</li>
                    <li>📐 Mesures biomécaniques précises</li>
                    <li>🤖 Identification des erreurs techniques</li>
                    <li>📄 Rapport PDF personnalisé</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ✅ Bouton centré sous la présentation
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        if st.button("🚀 Démarrer l’analyse", use_container_width=True):
            st.session_state.etape = 1
            st.rerun()

# --------------------
# ÉTAPE 1 : Connexion
# --------------------
elif st.session_state.etape == 1:
    # 🔙 Bouton retour en haut de la page
    col_retour, _ = st.columns([1, 5])
    with col_retour:
        if st.button("⬅️"):
            st.session_state.etape = 0
            st.rerun()

    st.markdown("<h2 style='text-align:center;'>🔐 Connexion Coach</h2>", unsafe_allow_html=True)
    st.markdown("Veuillez vous connecter avec vos identifiants.")
    if login():
        st.success(f"Bienvenue {st.session_state['name']} 👋")
        st.session_state.etape = 2
        st.rerun()

# --------------------
# ÉTAPE 2 : Gestion Joueuses
# --------------------
elif st.session_state.etape == 2:
    from data_storage import get_analyses_par_joueuse, get_joueuses_par_coach, supprimer_analyse
    import base64

    init_db()

    # 🔙 Bouton retour discret en haut à gauche
    col_retour, _ = st.columns([1, 6])
    with col_retour:
        if st.button("⬅️", key="retour_etape1"):
            st.session_state.etape = 1
            st.rerun()

    # 🎯 Titre centré
    st.markdown("<h2 style='text-align:center;'>👤 Gestion des joueuses</h2>", unsafe_allow_html=True)

    # ====== FORMULAIRE D’AJOUT ======
    with st.form("ajout_joueuse_form"):
        st.markdown("### ➕ Ajouter une nouvelle joueuse")
        nom = st.text_input("Nom", key="ajout_nom")
        prenom = st.text_input("Prénom", key="ajout_prenom")
        categorie = st.selectbox("Catégorie", st.session_state["categories_autorisees"], key="ajout_categorie")

        if st.form_submit_button("Ajouter"):
            if nom and prenom:
                st.session_state.new_joueuse_data = {
                    "nom": nom,
                    "prenom": prenom,
                    "categorie": categorie
                }
                st.session_state.etape = 2.5
                st.rerun()

    # ====== LISTE DES JOUEUSES PAR CATÉGORIE ======
    categorie = st.session_state.get("categorie_selectionnee", None)

    if categorie:
        st.markdown(f"### 📂 Joueuses de la catégorie **{categorie}**")
        joueuses = [
            j for j in get_joueuses_par_coach(st.session_state["username"])
            if j[3] == categorie and len(get_analyses_par_joueuse(j[0])) > 0
        ]

        if joueuses:
            joueuses_dict = {}
            for j in joueuses:
                joueuse_id, nom, prenom, cat, date = j
                key = (prenom, nom)
                if key not in joueuses_dict:
                    joueuses_dict[key] = {
                        "ids": [joueuse_id],
                        "categorie": cat
                    }
                else:
                    joueuses_dict[key]["ids"].append(joueuse_id)

            for (prenom, nom), infos in joueuses_dict.items():
                nom_complet = f"{prenom} {nom}"
                joueuse_ids = infos["ids"]
                cat = infos["categorie"]

                if st.button(f"👤 {nom_complet}", key=f"btn_joueuse_{nom_complet}"):
                    st.session_state.joueuse_affichee = nom_complet
                    st.session_state.analyse_selectionnee = None

                if st.session_state.get("joueuse_affichee") == nom_complet:
                    toutes_analyses = []
                    for jid in joueuse_ids:
                        analyses = get_analyses_par_joueuse(jid)
                        for a in analyses:
                            toutes_analyses.append((jid, *a))

                    toutes_analyses = sorted(toutes_analyses, key=lambda a: a[3], reverse=True)

                    for jid, id_analyse, technique, date, score, rapport, video in toutes_analyses:
                        label = f"📅 {date} – {technique}"
                        if st.button(label, key=f"btn_analyse_{id_analyse}"):
                            st.session_state.analyse_selectionnee = id_analyse

                        if st.session_state.get("analyse_selectionnee") == id_analyse:
                            st.write(f"**Score :** {score}/10")
                            if rapport:
                                st.markdown(f"[📄 Rapport PDF]({rapport})", unsafe_allow_html=True)
                            if video:
                                try:
                                    with open(video, "rb") as f:
                                        video_bytes = f.read()
                                        b64_video = base64.b64encode(video_bytes).decode("utf-8")
                                    video_html = f"""
                                    <video width="360" controls style="border-radius: 8px; margin-top:10px;">
                                        <source src="data:video/mp4;base64,{b64_video}" type="video/mp4">
                                    </video>
                                    """
                                    col1, col2, col3 = st.columns([3, 2, 3])
                                    with col2:
                                        st.markdown(video_html, unsafe_allow_html=True)
                                except:
                                    st.error("❌ Erreur de lecture de la vidéo.")

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🗑️ Supprimer l’analyse", key=f"del_{id_analyse}"):
                                    supprimer_analyse(id_analyse)
                                    st.success("Analyse supprimée.")
                                    st.session_state.analyse_selectionnee = None
                                    st.rerun()
                            with col2:
                                if st.button("➕ Nouvelle analyse", key=f"new_{id_analyse}_{jid}"):
                                    st.session_state.joueuse_id = jid
                                    st.session_state.joueuse_selectionnee = nom_complet
                                    st.session_state.categorie_joueuse = cat
                                    st.session_state.etape = 2.5
                                    st.rerun()
                            st.markdown("---")
        else:
            st.warning("Aucune joueuse avec analyse dans cette catégorie.")
    else:
        st.info("👉 Sélectionnez une catégorie dans la barre latérale.")

# --------------------
# ÉTAPE 2.5 : Instructions qualité vidéo
# --------------------
elif st.session_state.etape == 2.5:
    # 🔙 Bouton retour en haut à gauche
    col_retour, _ = st.columns([1, 6])
    with col_retour:
        if st.button("⬅️", key="retour_etape2"):
            st.session_state.etape = 2
            st.rerun()

    # 🎯 Titre centré
    st.markdown("<h2 style='text-align:center;'>🎯 Qualité requise pour la vidéo</h2>", unsafe_allow_html=True)

    # ✅ Consignes d'enregistrement
    st.markdown("""
    Pour garantir une analyse fiable et précise, merci de respecter **les conditions suivantes** lors de l’enregistrement :

    - 🎥 **La caméra doit rester fixe**, idéalement sur trépied ou support stable.
    - 📏 **Placez la caméra dans l’axe entre le ballon et la cible (le but)**.
    - ⚽ **Un seul ballon** doit apparaître dans le champ de vision.
    - 💡 **Bonne luminosité** : évitez les ombres fortes ou contre-jours.
    - 🧍‍♀️ **La joueuse doit être visible du début du geste jusqu’à la fin du suivi**, sans interruption.

    **Exemple de cadrage idéal :**
    """)

    # 🖼️ Image centrée
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("img_ref.png", caption="📸 Positionnement correct de la caméra", use_container_width=True)

    # ✅ Bouton centré pour valider
    colA, colB, colC = st.columns([2, 2, 2])
    with colB:
        if st.button("✅ Vidéo conforme – passer à la suite", key="btn_video_ok"):
            st.session_state.etape = 3
            st.rerun()

# --------------------
# ÉTAPE 3 : Vidéo – upload ou enregistrement direct
# --------------------

elif st.session_state.etape == 3:
    import io
    import base64
    import streamlit as st
    import streamlit.components.v1 as components

    # 🔙 Bouton retour discret en haut à gauche
    col_retour, _ = st.columns([1, 6])
    with col_retour:
        if st.button("⬅️", key="retour_etape_2_5"):
            st.session_state.etape = 2.5
            st.rerun()

    # 🎥 Titre centré
    st.markdown("<h2 style='text-align:center;'>🎥 Vidéo du tir</h2>", unsafe_allow_html=True)

    choix = st.radio(
        "Choisissez une méthode :",
        ["📁 Importer une vidéo", "🎥 Enregistrer avec la caméra"],
        horizontal=True
    )

    # ========= OPTION 1 : Importer une vidéo ========
    if choix == "📁 Importer une vidéo":
        video_file = st.file_uploader(
            "Importer une vidéo",
            type=["mp4", "webm", "avi", "mpeg", "mpg", "mkv", "mpeg4"],
            help="Formats pris en charge : MP4, AVI, WEBM, MKV, etc."
        )

        if video_file:
            if video_file.type == "video/quicktime":
                st.error("❌ Format non supporté : les fichiers `.mov` ne peuvent pas être lus ici.")
                st.info("💡 Convertissez votre vidéo ici : [cloudconvert.com/mov-to-mp4](https://cloudconvert.com/mov-to-mp4)")
            else:
                st.session_state.video_bytes = io.BytesIO(video_file.read())

                # ✅ Vidéo + bouton parfaitement centrés ensemble
                col1, col2, col3 = st.columns([3, 2, 3])
                with col2:
                    st.video(st.session_state.video_bytes)
                    st.markdown("<div style='margin-top: 20px; text-align: center;'>", unsafe_allow_html=True)
                    if st.button("➡️ Suivant : Moments clés", key="btn_suivant_moments"):
                        st.session_state.etape = 4
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Aucune vidéo sélectionnée.")

    # ========= OPTION 2 : Enregistrement direct via webcam =========
    elif choix == "🎥 Enregistrer avec la caméra":
        st.markdown("### 🎥 Enregistrez votre tir ci-dessous")
        st.markdown("Cliquez sur **Démarrer**, puis **Arrêter**, puis **➡️ Utiliser cette vidéo** pour analyser.")

        components.html("""<div style="text-align:center;">
                <video id="preview" width="320" height="240" autoplay muted></video><br>
                <button onclick="startRecording()">🔴 Démarrer</button>
                <button onclick="stopRecording()">⏹️ Arrêter</button><br><br>
                <video id="recording" width="320" height="240" controls></video><br>
                <textarea id="b64" style="display:none"></textarea>
                <button onclick="sendToStreamlit()">➡️ Utiliser cette vidéo</button>
            </div>
            <script>
                let mediaRecorder;
                let recordedBlobs;
                const preview = document.getElementById('preview');
                const recording = document.getElementById('recording');

                navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
                    preview.srcObject = stream;
                    window.stream = stream;
                });

                function startRecording() {
                    recordedBlobs = [];
                    const options = { mimeType: 'video/webm;codecs=vp9' };
                    mediaRecorder = new MediaRecorder(window.stream, options);
                    mediaRecorder.ondataavailable = e => {
                        if (e.data && e.data.size > 0) recordedBlobs.push(e.data);
                    };
                    mediaRecorder.onstop = () => {
                        const blob = new Blob(recordedBlobs, { type: 'video/webm' });
                        recording.src = URL.createObjectURL(blob);
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            const base64data = reader.result.split(',')[1];
                            const textarea = window.parent.document.querySelector("textarea[data-testid='stTextArea'] textarea");
                            if (textarea) {
                                textarea.value = base64data;
                                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        };
                        reader.readAsDataURL(blob);
                    };
                    mediaRecorder.start();
                }

                function stopRecording() {
                    mediaRecorder.stop();
                }

                function sendToStreamlit() {
                    stopRecording();
                }
            </script>
        """, height=700)

        base64_video = st.text_area("base64_video_webm", label_visibility="collapsed")

        if base64_video and "video_bytes" not in st.session_state:
            try:
                st.info("🎥 Traitement de la vidéo en cours...")
                video_data = base64.b64decode(base64_video)
                st.session_state.video_bytes = io.BytesIO(video_data)
                st.success("✅ Vidéo reçue. Passage à l’analyse.")
                st.session_state.etape = 4
                st.rerun()
            except Exception as e:
                st.error(f"Erreur de traitement vidéo : {e}")


# --------------------
# ÉTAPE 4 : Geste technique & Sélection frames
# --------------------
elif st.session_state.etape == 4:
    import tempfile
    import cv2
    from PIL import Image

    # 🔙 Bouton de retour en haut à gauche
    col_retour, _ = st.columns([1, 6])
    with col_retour:
        if st.button("⬅️", key="retour_etape3"):
            st.session_state.etape = 3
            st.rerun()

    # 🎯 Titre
    st.markdown("<h2 style='text-align:center;'>🧭 Étape 4 : Définir les moments clés du geste</h2>", unsafe_allow_html=True)

    if "video_bytes" not in st.session_state:
        st.error("❌ Aucune vidéo. Retournez à l'étape précédente.")
        st.stop()

    type_geste = st.radio("Quel type de geste technique a été réalisé ?", [
        "Tir de cou-de-pied",
        "Tir intérieur du pied",
        "Passe intérieure du pied"
    ], horizontal=True)

    pied_frappe = st.radio("Quel pied a été utilisé ?", ["Droit", "Gauche"], horizontal=True)

    if "Passe" in type_geste:
        st.info("""
        👉 Veuillez cliquer sur **l’image correspondant au moment de l’impact** du pied avec le ballon.

        Il ne faut choisir **qu’un seul moment clé** dans ce cas.
        """)
    else:
        st.info("""
        👉 Veuillez cliquer sur **3 images** correspondant aux **moments clés** suivants du geste :

        1. 🦶 **Début du geste** : quand la jambe commence à se balancer pour frapper  
        2. 💥 **Impact** : lorsque le pied frappe le ballon  
        3. 🌀 **Suivi** : juste après l’impact, quand la jambe continue son mouvement

        ⛔️ Choisissez les images qui vous semblent les plus proches de ces instants.
        """)

    def extraire_frames_filtrees(video_bytes, type_geste, step=5, max_frames=60):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(video_bytes.getbuffer())
            path = tmp.name

        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if "Passe" in type_geste:
            min_f, max_f = int(0.15 * total), int(0.85 * total)
        else:
            min_f, max_f = int(0.30 * total), int(0.90 * total)

        frames = []
        fno = 0
        while cap.isOpened() and len(frames) < max_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, fno)
            ret, frame = cap.read()
            if not ret:
                break
            if min_f <= fno <= max_f:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                frames.append((fno, pil_img))
            fno += step
        cap.release()
        return frames

    frames = extraire_frames_filtrees(st.session_state.video_bytes, type_geste)

    if "frame_selection" not in st.session_state:
        st.session_state.frame_selection = {"kick": None, "impact": None, "post": None}

    st.markdown("### 🎯 Cliquez sur les images pour définir les moments clés du geste")
    n_cols = 5
    rows = [frames[i:i + n_cols] for i in range(0, len(frames), n_cols)]
    for row in rows:
        cols = st.columns(len(row))
        for i, (fno, img) in enumerate(row):
            with cols[i]:
                if st.button(f"Frame {fno}", key=f"btn_{fno}"):
                    fs = st.session_state.frame_selection
                    if "Passe" in type_geste:
                        fs["impact"] = fno
                    else:
                        if fs["kick"] is None:
                            fs["kick"] = fno
                        elif fs["impact"] is None:
                            fs["impact"] = fno
                        elif fs["post"] is None:
                            fs["post"] = fno
                st.image(img, width=120)

    fs = st.session_state.frame_selection
    if "Passe" in type_geste:
        st.write("💥 Frame d’impact :", fs["impact"])
    else:
        st.write("🦶 Début du geste :", fs["kick"])
        st.write("💥 Impact :", fs["impact"])
        st.write("🌀 Suivi  :", fs["post"])

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔁 Corriger les sélections"):
            st.session_state.frame_selection = {"kick": None, "impact": None, "post": None}
            st.rerun()
    with col3:
        if st.button("✅ Valider les moments clés"):
            fs = st.session_state.frame_selection
            st.session_state.type_geste = type_geste
            st.session_state.pied_frappe = pied_frappe

            if "Passe" in type_geste:
                if fs["impact"] is None:
                    st.warning("Veuillez sélectionner le moment d’impact.")
                else:
                    st.session_state.frame_impact = fs["impact"]
                    st.session_state.frame_selection = {"kick": None, "impact": None, "post": None}
                    st.session_state.etape = 5
                    st.rerun()
            else:
                if fs["kick"] is None or fs["impact"] is None or fs["post"] is None:
                    st.warning("Veuillez sélectionner les 3 moments clés du tir.")
                else:
                    st.session_state.frame_kick = fs["kick"]
                    st.session_state.frame_impact = fs["impact"]
                    st.session_state.frame_postimpact = fs["post"]
                    st.session_state.frame_selection = {"kick": None, "impact": None, "post": None}
                    st.session_state.etape = 5
                    st.rerun()

    st.stop()

# --------------------
# ÉTAPE 5 : Vérification des phases
# --------------------
elif st.session_state.etape == 5:
    import tempfile
    import os
    import cv2
    from segmentation_evenementielle import segmenter_kick
    from visualisation import generer_video_phases_simple

    # 🔙 Bouton flèche en haut à gauche
    col_retour, _ = st.columns([1, 6])
    with col_retour:
        if st.button("⬅️", key="retour_etape4"):
            st.session_state.etape = 4
            st.rerun()

    # 🎯 Titre
    st.markdown("<h2 style='text-align:center;'>🧪 Étape 5 : Vérification des phases segmentées</h2>", unsafe_allow_html=True)
    st.markdown("La vidéo ci-dessous affiche les phases détectées automatiquement à partir des moments clés que vous avez sélectionnés.")

    if "video_bytes" not in st.session_state:
        st.error("❌ Aucune vidéo chargée.")
        st.stop()

    # 🎥 Préparation de la vidéo annotée
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(st.session_state.video_bytes.getbuffer())
        path_video = tmp.name

    cap = cv2.VideoCapture(path_video)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    frame_kick = st.session_state.get("frame_kick", 0)
    frame_impact = st.session_state.get("frame_impact", 0)
    frame_post = st.session_state.get("frame_postimpact", int(total_frames) - 1)

    phases = segmenter_kick(
        frames_total=total_frames,
        frame_kick=frame_kick,
        frame_impact=frame_impact,
        frame_recontact=frame_post
    )

    video_segmented_path = generer_video_phases_simple(
        path_video,
        phases,
        output_path="video_segmentee.mp4"
    )

    if video_segmented_path and os.path.exists(video_segmented_path):
        with open(video_segmented_path, "rb") as f:
            video_bytes = f.read()

        st.markdown("### 🎞️ Aperçu de la segmentation")
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            st.video(video_bytes)

        st.success("📹 Vidéo générée avec succès.")
    else:
        st.error("❌ La vidéo annotée n’a pas pu être générée.")
        st.stop()

    # ✅ Boutons de navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔁 Corriger les moments clés"):
            st.session_state.etape = 4
            st.rerun()
    with col3:
        if st.button("✅ C’est correct, passer à la détection du ballon"):
            st.session_state.etape = 6
            st.rerun()


# --------------------
# ÉTAPE 6 : Détection du ballon (coach-friendly)
# --------------------
elif st.session_state.etape == 6:
    import tempfile
    import os
    from detect_ball_yolo import detect_ball_yolo

    # 🔙 Bouton flèche en haut à gauche
    col_retour, _ = st.columns([1, 6])
    with col_retour:
        if st.button("⬅️", key="retour_etape5"):
            st.session_state.etape = 5
            st.rerun()

    # 🎯 Titre centré
    st.markdown("<h2 style='text-align:center;'>🎯 Étape 6 : Détection automatique du ballon</h2>", unsafe_allow_html=True)
    st.markdown("L’intelligence artificielle repère le ballon sur chaque image pour mesurer avec précision les distances et vitesses.")

    if "video_bytes" not in st.session_state:
        st.error("❌ Aucune vidéo détectée. Veuillez revenir à l'étape d'import.")
        st.stop()

    # 📍 Déclencher la détection YOLO
    if st.button("🎯 Lancer la détection", use_container_width=True):
        with st.spinner("Détection YOLOv8 en cours..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(st.session_state.video_bytes.getbuffer())
                video_path = tmp.name

            ball_path = detect_ball_yolo(video_path)

            if not ball_path or not os.path.exists(ball_path):
                st.error("❌ La détection du ballon a échoué. Vérifiez le modèle ou la vidéo.")
                st.stop()

            st.session_state.ball_position_path = ball_path
            st.session_state.ball_detected = True
            st.success("✅ Ballon détecté avec succès. Les données sont prêtes pour l’analyse biomécanique.")

    # ✅ Si détection ok → bouton pour passer à l’analyse
    if st.session_state.get("ball_detected", False):
        if st.button("➡️ Passer à l’analyse du geste", use_container_width=True):
            st.session_state.etape = 7
            st.rerun()


# -------------------------------
# ÉTAPE 7 : Analyse biomécanique complète
# -------------------------------
elif st.session_state.etape == 7:
    from analyse import (
        analyse_biomeca_instep,
        analyse_biomeca_inside,
        analyse_biomeca_passe
    )
    from data_storage import (
        ajouter_joueuse,
        get_joueuses_par_coach,
        enregistrer_analyse,
        existe_analyse
    )
    from datetime import datetime
    # 🔙 Bouton flèche retour en haut à gauche
    col_retour, _ = st.columns([1, 6])
    with col_retour:
        if st.button("⬅️", key="retour_etape6"):
            st.session_state.etape = 6
            st.rerun()

    # 🎯 Titre d’étape
    st.markdown("<h2 style='text-align:center;'>🧪 Étape 7 : Analyse biomécanique du geste</h2>", unsafe_allow_html=True)

    type_geste = st.session_state.type_geste.lower()

    # 1. Lancer l’analyse technique
    if "cou-de-pied" in type_geste:
        score_global, rapport_pdf_path, video_annotee_path = analyse_biomeca_instep()
    elif "intérieur" in type_geste and "passe" not in type_geste:
        score_global, rapport_pdf_path, video_annotee_path = analyse_biomeca_inside()
    elif "passe" in type_geste:
        score_global, rapport_pdf_path, video_annotee_path = analyse_biomeca_passe()
    else:
        st.error("❌ Type de geste non reconnu.")
        st.stop()

    # 2. Ajouter la joueuse si ajoutée via formulaire
    if "new_joueuse_data" in st.session_state:
        nom = st.session_state.new_joueuse_data["nom"]
        prenom = st.session_state.new_joueuse_data["prenom"]
        categorie = st.session_state.new_joueuse_data["categorie"]

        deja = any(
            j[1] == nom and j[2] == prenom and j[3] == categorie
            for j in get_joueuses_par_coach(st.session_state["username"])
        )

        if not deja:
            ajouter_joueuse(nom, prenom, categorie, st.session_state["username"])

        joueuses = get_joueuses_par_coach(st.session_state["username"])
        joueuse = next((j for j in joueuses if j[1] == nom and j[2] == prenom and j[3] == categorie), None)

        if joueuse:
            st.session_state.joueuse_id = joueuse[0]
            st.session_state.joueuse_selectionnee = f"{prenom} {nom}"
            st.session_state.categorie_joueuse = categorie

        del st.session_state["new_joueuse_data"]

    # 3. Enregistrer l’analyse si elle n’existe pas déjà
    joueuse_id = st.session_state.get("joueuse_id")
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not joueuse_id:
        st.error("❌ Joueuse introuvable. Analyse non enregistrée.")
        st.stop()

    if not existe_analyse(joueuse_id, st.session_state.type_geste, date_now):
        enregistrer_analyse(
            joueuse_id=joueuse_id,
            technique=st.session_state.type_geste,
            date_analyse=date_now,
            score_global=score_global,
            rapport_pdf_path=rapport_pdf_path,
            video_annotee_path=video_annotee_path
        )
        st.success("✅ Analyse enregistrée avec succès.")
    else:
        st.info("ℹ️ Une analyse identique vient d’être enregistrée.")

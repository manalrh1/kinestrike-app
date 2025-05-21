import streamlit as st
import io
import tempfile
import os
import shutil

def charger_video_convertie():
    st.markdown("#### 🎞️ Importer une vidéo (MP4 recommandé)")
    st.markdown("⚠️ Les fichiers `.mov` (iPhone) seront automatiquement convertis en `.mp4`.")

    video_file = st.file_uploader(
        "Importer une vidéo",
        type=None,  # accepter tous les types
        help="Formats pris en charge : MP4, MOV, AVI, etc."
    )

    if not video_file:
        return None

    suffix = os.path.splitext(video_file.name)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_input:
        temp_input.write(video_file.read())
        input_path = temp_input.name

    if video_file.type == "video/quicktime" or suffix.lower() != ".mp4":
        mp4_path = input_path.replace(suffix, ".mp4")
        ffmpeg_installed = shutil.which("ffmpeg") is not None

        if not ffmpeg_installed:
            st.error("❌ `ffmpeg` n’est pas installé sur le serveur. Impossible de convertir le fichier.")
            return None

        with st.spinner("♻️ Conversion vidéo en cours..."):
            result = os.system(f"ffmpeg -i \"{input_path}\" -vcodec libx264 -acodec aac \"{mp4_path}\" -y")

        if result != 0 or not os.path.exists(mp4_path):
            st.error("❌ La conversion de la vidéo a échoué.")
            return None

        with open(mp4_path, "rb") as f:
            st.success("✅ Conversion réussie.")
            return io.BytesIO(f.read())

    with open(input_path, "rb") as f:
        return io.BytesIO(f.read())

import streamlit as st

def afficher_sidebar_profil():
    from data_storage import get_joueuses_par_coach

    # 🌈 Appliquer style rouge clair à la sidebar
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                background-color: #ffe5e5;
                padding: 1rem;
            }
            .stButton>button {
                background-color: #cc4e4e;
                color: white;
                font-weight: bold;
                padding: 0.6em 1.5em;
                font-size: 16px;
                border-radius: 8px;
                border: none;
                margin-bottom: 8px;
            }
            .stButton>button:hover {
                background-color: #b73737;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## 👤 Profil")
        st.write(f"**Nom :** {st.session_state.get('name', 'Coach')}")

        st.markdown("### 📁 Catégories autorisées")

        for cat in st.session_state.get("categories_autorisees", []):
            if st.button(cat, key=f"cat_{cat}"):
                st.session_state.categorie_selectionnee = cat
                st.session_state.joueuse_id = None
                st.session_state.etape = 2
                st.rerun()

        st.markdown("---")

        # ✅ BOUTON DECONNEXION PROPRE
        if st.button("🔓 Se déconnecter"):
            # Ne pas clear() ! Supprimer seulement les variables d'utilisateur
            for key in ['name', 'username', 'categories_autorisees', 'categorie_selectionnee', 'joueuse_id']:
                if key in st.session_state:
                    del st.session_state[key]
            # Mettre l'étape 1 (page login)
            st.session_state.etape = 1
            st.rerun()

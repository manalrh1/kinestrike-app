import streamlit as st

def afficher_sidebar_profil():
    from data_storage import get_joueuses_par_coach

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
        # ✅ Ajout de clé unique ici
        if st.button("🔓 Se déconnecter", key="btn_logout"):
            st.session_state.clear()
            st.rerun()

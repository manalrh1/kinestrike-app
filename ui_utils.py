import streamlit as st

def afficher_sidebar_profil():
    with st.sidebar:
        st.markdown("## 👤 Profil")
        st.write(f"**Nom :** {st.session_state.get('name', 'Coach')}")

        st.write("### 📂 Catégories autorisées")
        for cat in st.session_state.get("categories_autorisees", []):
            if st.button(f"{cat}", key=f"cat_{cat}"):
                st.session_state.categorie_selectionnee = cat
                st.session_state.joueuse_id = None
                st.session_state.etape = 2
                st.rerun()

        st.markdown("---")
        if st.button("🔓 Se déconnecter"):
            st.session_state.clear()
            st.rerun()

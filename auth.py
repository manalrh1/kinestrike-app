import streamlit as st
import streamlit_authenticator as stauth

# =============================
# Définition des comptes autorisés
# =============================
# Chaque coach a :
# - un nom affiché
# - un mot de passe hashé (bcrypt)
# - une ou plusieurs catégories autorisées
# (U13, U15, U17, Senior)

USERS = {
    "ibtissam": {
        "name": "Coach Ibtissam",
        "password": "$2b$12$Eb7QbaF8JVcl0MV2EYgXvu9fp9YJ0yaO4YOm.zeX8rQ3D0w0E9gxa",  # ibt2024
        "categories": ["U15"]
    },
    "chaimaa": {
        "name": "Coach Chaimaa",
        "password": "$2b$12$TYjmr1FCyc5wSoA89VvYIeadamYXFLgpqlBBiaejNFiBURrzdNyAW",  # chaimaa2024
        "categories": ["U13", "U15"]
    },
    "oumaima": {
        "name": "Coach Oumaima",
        "password": "$2b$12$bmfviBKEJz69IlGDCgwIKuJNCIQ49KSv/tJa/bfNElJS7LurOqxMq",  # oumaima2024
        "categories": ["Senior"]
    },
    "mehdi": {
        "name": "Coach Mehdi",
        "password": "$2b$12$92uDNjztj56nGJajz0UNQefPJ5Ef9394g9pCB3Gx3vADUzVkyIr6O",  # mehdi2024
        "categories": ["Senior"]
    },
    "mohammed": {
        "name": "Coach Mohammed",
        "password": "$2b$12$DcWYbZzGwT30/Pyl74bFLOdJnA8ao09I1dChOLFUrqjcpxZVCXXpq",  # mohammed2024
        "categories": ["Senior"]
    },
    "redouan": {
        "name": "Coach Redouan",
        "password": "$2b$12$WSF01Q6RSunqF4pReXokbeDlXCPtyQe.LQfvpHToHoY.YjB8/yriG",  # redouan2024
        "categories": ["U17"]
    },
    "karam": {
        "name": "Président Karam",
        "password": "$2b$12$AoUviuYXZ9Es6YXUDpR1JOYnIo3kSlTvzX95cRIUK6HnUfOS.XenO",  # adminkaram
        "categories": ["U13", "U15", "U17", "Senior"]
    },
    "manal": {
        "name": "Manal",
        "password": "$2b$12$AuF3ZF83dKUw0GQCQ8cTGOIzHVJYhqy4jSoiZzYOKJsLjNJ.ZW6Tq",  # adminmanal
        "categories": ["U13", "U15", "U17", "Senior"]
    }
}

# =============================
# Fonction de login utilisée dans app.py
# =============================
def login():
    # Préparation des credentials pour streamlit_authenticator
    credentials = {"usernames": {}}
    for username, info in USERS.items():
        credentials["usernames"][username] = {
            "name": info["name"],
            "password": info["password"]
        }

    # Authentification via cookies
    authenticator = stauth.Authenticate(
        credentials,
        "kine_cookie",     # nom du cookie
        "kine_signature",  # clé de signature
        30                 # durée en jours
    )

    # Affiche le formulaire de connexion
    authenticator.login("main", "Connexion")

    # Vérifie le statut d’authentification
    username = st.session_state.get("username")
    if st.session_state.get("authentication_status"):
        st.session_state["username"] = username
        st.session_state["name"] = USERS[username]["name"]
        st.session_state["categories_autorisees"] = USERS[username]["categories"]
        return True
    elif st.session_state.get("authentication_status") is False:
        st.error("Identifiants incorrects.")
    else:
        st.info("Veuillez entrer vos identifiants.")
    return False

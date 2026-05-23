import streamlit as st
import requests
import re

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Configuration Maison", page_icon="🏠")
st.title("🏠 Configuration de la maison")
st.caption("Interface réservée à l'aidant — à configurer une seule fois")


# ================================
# INITIALISATION SESSION
# ================================

if "rooms" not in st.session_state:
    st.session_state.rooms = []
if "connections" not in st.session_state:
    st.session_state.connections = []


# ================================
# ÉTAPE 1 : Email utilisateur
# ================================

st.header("1. Email de l'utilisateur")
email = st.text_input("Email", placeholder="ex: farou@gmail.com")

email_valide = bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)) if email else False
if email and not email_valide:
    st.warning("Format d'email invalide.")


# ================================
# ÉTAPE 2 : Pièces de la maison
# ================================

st.header("2. Pièces de la maison")

col1, col2 = st.columns([3, 1])
with col1:
    new_room = st.text_input("Nom de la pièce", placeholder="ex: salon")
with col2:
    st.write("")
    st.write("")
    if st.button("Ajouter pièce") and new_room:
        if new_room.lower() not in st.session_state.rooms:
            st.session_state.rooms.append(new_room.lower())
        else:
            st.warning("Cette pièce existe déjà.")

if st.session_state.rooms:
    st.write("**Pièces ajoutées :**")
    cols = st.columns(min(len(st.session_state.rooms), 5))
    for i, room in enumerate(st.session_state.rooms):
        with cols[i % 5]:
            st.info(room)
            if st.button("❌", key=f"del_room_{i}"):
                st.session_state.rooms.remove(room)
                st.rerun()


# ================================
# ÉTAPE 3 : Connexions
# ================================

st.header("3. Connexions entre les pièces")

with st.expander("ℹ️ Comment choisir la direction ?"):
    st.markdown("""
    Les directions sont exprimées par rapport au plan de la maison :

    - ⬆️ **Nord (0°)** : la pièce est au-dessus
    - ➡️ **Est (90°)** : la pièce est à droite
    - ⬇️ **Sud (180°)** : la pièce est en dessous
    - ⬅️ **Ouest (270°)** : la pièce est à gauche

    **Exemple :**

    Si le salon est au centre :

    ```
           chambre
              ↑
              |
    cuisine ← salon → bureau
              |
              ↓
        salle de bain
    ```

    Les connexions seront :

    - salon → chambre : Nord (0°)
    - salon → bureau : Est (90°)
    - salon → salle de bain : Sud (180°)
    - salon → cuisine : Ouest (270°)

    ⚠️ Choisissez la direction selon la position réelle de la pièce sur le plan,
    et non selon l'orientation de la personne lorsqu'elle marche.
    """)

st.caption("Définissez la position relative des pièces sur le plan")

# Mapping cardinal → angle
CARDINAL_TO_ANGLE = {
    "Nord (0°)": 0,
    "Est (90°)": 90,
    "Sud (180°)": 180,
    "Ouest (270°)": 270
}

if len(st.session_state.rooms) >= 2:
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        room_from = st.selectbox(
            "De",
            st.session_state.rooms,
            key="from"
        )

    with col2:
        room_to = st.selectbox(
            "Vers",
            st.session_state.rooms,
            key="to"
        )

    with col3:
        cardinal = st.selectbox(
            "Direction (point cardinal)",
            list(CARDINAL_TO_ANGLE.keys()),
            key="dir"
        )

        angle = CARDINAL_TO_ANGLE[cardinal]

    with col4:
        st.write("")
        st.write("")

        if st.button("Ajouter"):
            if room_from == room_to:
                st.warning("Une pièce ne peut pas se connecter à elle-même.")
            else:
                exists = any(
                    c["from"] == room_from and c["to"] == room_to
                    for c in st.session_state.connections
                )

                if exists:
                    st.warning("Cette connexion existe déjà.")
                else:
                    st.session_state.connections.append({
                        "from": room_from,
                        "to": room_to,
                        "angle": angle
                    })

else:
    st.info("Ajoutez au moins 2 pièces pour définir des connexions.")

if st.session_state.connections:
    st.write("**Connexions définies :**")

    angle_icon = {
        0: "⬆️",
        90: "➡️",
        180: "⬇️",
        270: "⬅️"
    }

    angle_label = {
        0: "Nord",
        90: "Est",
        180: "Sud",
        270: "Ouest"
    }

    for i, conn in enumerate(st.session_state.connections):
        col1, col2 = st.columns([4, 1])

        with col1:
            icon = angle_icon.get(conn["angle"], "➡️")
            label = angle_label.get(conn["angle"], "")
            st.write(
                f"{icon} **{conn['from']}** → **{conn['to']}** ({label} - {conn['angle']}°)"
            )

        with col2:
            if st.button("❌", key=f"del_conn_{i}"):
                st.session_state.connections.pop(i)
                st.rerun()

# ================================
# ÉTAPE 4 : Aperçu JSON
# ================================

if st.session_state.rooms and st.session_state.connections:
    st.header("4. Aperçu de la configuration")
    house_data = {
        "rooms":       st.session_state.rooms,
        "connections": st.session_state.connections
    }
    st.json(house_data)

    # ================================
    # ÉTAPE 5 : Sauvegarder / Modifier
    # ================================

    st.header("5. Sauvegarder")

    if not email_valide:
        st.warning("Entrez un email valide avant de sauvegarder.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Sauvegarder", type="primary"):
                try:
                    r    = requests.post(
                        f"{BASE_URL}/house/save",
                        params={"device_id": email},
                        json=house_data
                    )
                    data = r.json()
                    if data.get("status") == "ok":
                        st.success(f"✅ Maison sauvegardée pour **{email}** !")
                        st.balloons()
                    else:
                        st.error(data.get("message", "Erreur lors de la sauvegarde."))
                except Exception as e:
                    st.error(f"Impossible de contacter le serveur : {e}")

        with col2:
            if st.button("✏️ Modifier config existante"):
                try:
                    r    = requests.put(
                        f"{BASE_URL}/house/update",
                        params={"device_id": email},
                        json=house_data
                    )
                    data = r.json()
                    if data.get("status") == "ok":
                        st.success(f"✅ Configuration mise à jour pour **{email}** !")
                    else:
                        st.error(data.get("message", "Erreur lors de la mise à jour."))
                except Exception as e:
                    st.error(f"Impossible de contacter le serveur : {e}")


# ================================
# CONSULTER / DUPLIQUER UNE CONFIG
# ================================

st.divider()
st.subheader("🔍 Consulter ou copier une configuration existante")

if "loaded_house" not in st.session_state:
    st.session_state.loaded_house = None

source_email = st.text_input(
    "Email de la configuration à charger",
    placeholder="ex: farou@gmail.com"
)

if st.button("Charger la configuration") and source_email:
    try:
        r = requests.get(
            f"{BASE_URL}/house",
            params={"device_id": source_email}
        )

        data = r.json()

        if data.get("status") == "ok":
            st.session_state.loaded_house = data["house"]
            st.success(f"Configuration trouvée pour **{source_email}**")
        else:
            st.error("Aucune configuration trouvée.")

    except Exception as e:
        st.error(f"Erreur : {e}")

if st.session_state.loaded_house:

    st.write("### Maison chargée")
    st.json(st.session_state.loaded_house)

    st.divider()

    st.write("### Copier cette configuration vers mon compte")

    target_email = st.text_input(
        "Mon email",
        placeholder="ex: monemail@gmail.com"
    )

    target_email_valid = bool(
        re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', target_email)
    ) if target_email else False

    if target_email and not target_email_valid:
        st.warning("Format d'email invalide.")

    if st.button("📋 Copier cette maison sur mon compte"):

        if not target_email_valid:
            st.error("Veuillez saisir un email valide.")
        else:
            try:
                r = requests.post(
                    f"{BASE_URL}/house/save",
                    params={"device_id": target_email},
                    json=st.session_state.loaded_house
                )

                data = r.json()

                if data.get("status") == "ok":
                    st.success(
                        f"✅ Configuration copiée avec succès vers **{target_email}**"
                    )
                else:
                    st.error(
                        data.get(
                            "message",
                            "Erreur lors de la copie."
                        )
                    )

            except Exception as e:
                st.error(f"Erreur : {e}")


# ================================
# RÉINITIALISER
# ================================

st.divider()
if st.button("🔄 Réinitialiser le formulaire"):
    st.session_state.rooms       = []
    st.session_state.connections = []
    st.rerun()
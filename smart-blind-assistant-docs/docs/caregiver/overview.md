# Interface Aidant — caregiver.py

## Pourquoi une interface séparée ?

La configuration de la maison est une tâche complexe qui nécessite de voir l'écran et de réfléchir au plan de la maison. Cette tâche est réalisée par un **aidant** (proche, personnel médical) **une seule fois**, pas par l'utilisateur malvoyant. Une interface web Streamlit séparée est donc plus adaptée qu'une fonctionnalité dans l'app mobile.

---

## Lancement

```bash
streamlit run caregiver.py
```

Interface accessible sur `http://localhost:8501`.

---

## Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| Identification par email | Email unique de l'utilisateur — validé par regex, converti en nom de fichier |
| Ajout de pièces | Ajout une par une avec bouton, suppression individuelle |
| Définition des connexions | De / Vers / Direction (Nord/Est/Sud/Ouest) avec icônes directionnelles |
| Aide contextuelle | Expander avec schéma ASCII expliquant les points cardinaux |
| Aperçu JSON | Visualisation en temps réel de la configuration générée |
| Sauvegarde | `POST /house/save` — refusé si email déjà utilisé |
| Modification | `PUT /house/update` — pour corriger une configuration existante |
| Consultation | `GET /house` — charger et afficher la config d'un utilisateur |
| Copie | Copier la maison d'un utilisateur vers un autre email |
| Réinitialisation | Vider le formulaire pour recommencer |

---

## Règle d'unicité par email

Un email ne peut être utilisé qu'**une seule fois** pour `POST /house/save`. Cette règle évite les écrasements accidentels. Pour modifier une configuration existante, l'aidant doit utiliser le bouton **Modifier** qui appelle `PUT /house/update`.

!!! info "Conversion email → fichier"
    `farou@gmail.com` est converti en `house_farou_gmail_com.json` via :
    ```python
    re.sub(r'[^\w]', '_', email.lower())
    ```
    Cette conversion est **identique** dans Streamlit et dans le backend — les deux pointent vers le même fichier.

---

## Schéma de configuration — Points cardinaux

```
         NORD (0°)
            ↑
OUEST ←─────┼─────→ EST
(270°)      │      (90°)
            ↓
         SUD (180°)
```

Exemple : si le salon est au nord de l'entrée, l'angle de connexion `entrée → salon` est `0°`.

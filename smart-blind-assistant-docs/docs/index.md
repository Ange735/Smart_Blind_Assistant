<div class="hero-banner" markdown>

# Smart Blind Assistant

<p class="subtitle">Système intelligent d'assistance aux personnes malvoyantes</p>

<div class="stack-badges">
  <span class="badge">⚡ FastAPI</span>
  <span class="badge">👁️ YOLOv8</span>
  <span class="badge">🧠 NLP</span>
  <span class="badge">📱 Flutter</span>
  <span class="badge">🗺️ Navigation BFS</span>
</div>

</div>

!!! success "Statut du projet"
    Tous les composants sont **opérationnels** et testés sur les cas d'usage principaux.
    Projet S6 — Mai 2026 · BADO Yipène Ange Cenacle · ISSOUG El Mehdi

---

## Vue d'ensemble

Smart Blind Assistant est un système complet qui permet à une personne malvoyante d'interagir de manière **autonome et sécurisée** avec son environnement intérieur, en utilisant uniquement sa voix et son smartphone.

### Composants du système

| Composant | Technologie | Rôle | Statut |
|-----------|-------------|------|--------|
| Backend API | Python / FastAPI | Intelligence artificielle | ✅ Terminé |
| Computer Vision | YOLOv8 + Depth Anything V2 | Détection et guidage | ✅ Terminé |
| NLP | SentenceTransformer + spaCy | Compréhension vocale | ✅ Terminé |
| Navigation | BFS + Graphe maison | Guidage pièce à pièce | ✅ Terminé |
| App Mobile | Flutter / Dart | Interface utilisateur | ✅ Terminé |
| Interface Aidant | Streamlit (Python) | Configuration maison | ✅ Terminé |

---

## Fonctionnalités principales

- 🔊 **Interaction 100% vocale** — aucun besoin de voir ou de toucher l'écran
- 🧠 **Compréhension du langage naturel** — « je ne retrouve pas mon lit » fonctionne aussi bien que « cherche le lit »
- 🏠 **Adaptabilité** — chaque maison est configurable, pas de plan prédéfini
- 🚨 **Sécurité active** — détection des dangers (feu, couteau, escaliers) en permanence
- 📐 **Architecture modulaire** — chaque fonctionnalité est indépendante et évolutive
- 📱 **Aucune dépendance matérielle spécifique** — fonctionne sur tout smartphone Android récent

---

## Navigation rapide

<div class="grid cards" markdown>

- :material-rocket-launch: **[Démarrage rapide](getting-started/prerequisites.md)**

    Installation, configuration et premier lancement du système.

- :material-sitemap: **[Architecture](architecture/overview.md)**

    Vue d'ensemble des trois couches et du principe de séparation des responsabilités.

- :material-eye: **[Computer Vision](modules/computer-vision.md)**

    YOLOv8, Depth Anything V2, détection d'obstacles et guidage.

- :material-brain: **[Module NLP](modules/nlp.md)**

    Compréhension sémantique avec SentenceTransformer et spaCy.

- :material-api: **[API REST](api/endpoints.md)**

    Référence complète des endpoints FastAPI.

- :material-cellphone: **[Application Flutter](mobile/architecture.md)**

    Architecture du client mobile vocal.

</div>

---

## Problématique résolue

> **Comment permettre à une personne malvoyante d'interagir de manière autonome et sécurisée avec son environnement intérieur, en utilisant uniquement sa voix et son smartphone, sans nécessiter de compétences techniques particulières ?**

Les solutions traditionnelles — canne blanche, chien guide — ne peuvent pas identifier un objet spécifique, lire l'environnement visuel ou guider vers une destination précise dans un espace intérieur. Les assistants vocaux existants (Alexa, Google Home) ne sont pas conçus pour la navigation spatiale et la détection d'obstacles en temps réel.

Smart Blind Assistant répond à ces limites en combinant trois domaines de l'IA : **vision par ordinateur**, **traitement du langage naturel** et **navigation par graphe**.

# Module Computer Vision

## Architecture des modèles

Le module CV utilise **deux types de modèles** d'intelligence artificielle complémentaires :

| Modèle | Type | Rôle |
|--------|------|------|
| YOLOv8n (COCO) | Détection d'objets — 80 classes | Usage général : meubles, personnes, appareils |
| YOLOv8n Custom (`best.pt`) | Détection d'objets — 4 classes | Dangers : fire, human-fire, knife, stairs |
| Depth Anything V2 Small | Estimation de profondeur monoculaire | Distance des obstacles sans capteur dédié |

---

## YOLOv8 — You Only Look Once

YOLO effectue une **seule passe** sur l'image entière et retourne simultanément la localisation (bounding box) et la classe de chaque objet détecté.

!!! note "Pourquoi YOLOv8n ?"
    La version « nano » (n) est la plus légère du framework — idéale pour un déploiement sans GPU dédié. Elle offre ~30ms par image sur CPU avec une précision suffisante pour l'assistance.

### Fine-tuning pour la détection de dangers

YOLOv8 standard ne détecte pas les éléments critiques pour la sécurité. Un modèle custom a été entraîné :

- **Dataset** : fusion de 3 datasets spécialisés sur Roboflow — 5 641 images, 4 classes (escaliers, feu, couteau)
- **Entraînement** : Google Colab (GPU Tesla T4), 50 epochs, YOLOv8n, `freeze=10`
- **Freeze=10** : les 10 premières couches sont gelées, préservant la connaissance générale tout en adaptant les couches supérieures aux nouvelles classes

!!! warning "Catastrophic Forgetting"
    Le fine-tuning initial a effacé les 80 classes COCO originales (*catastrophic forgetting*).

    **Solution retenue** : deux modèles en parallèle — `yolov8n.pt` pour les 80 classes COCO, `best.pt` pour les 4 classes de danger. Exécution simultanée via `ThreadPoolExecutor` (gain : 50–80ms vs 200ms en séquentiel).

---

## Depth Anything V2 — Estimation de distance

Connaître la distance d'un obstacle est crucial pour évaluer le danger. Le système utilise Depth Anything V2, un modèle de profondeur **monoculaire** qui estime la distance depuis une seule image (sans capteur LiDAR).

### Approches évaluées

| Approche | Description | Verdict |
|----------|-------------|---------|
| Table de référence (TAILLE_REF) | Taille connue par classe × pixels = distance estimée | ❌ Abandonnée — liste fermée |
| Hauteur bbox relative | Plus le bbox est grand = plus l'objet est proche | ⚠️ Fallback — universel mais imprécis |
| Modèle sténopé (pinhole) | Focale × taille réelle / pixels = distance métrique | ❌ Abandonnée — tailles requises |
| **Depth Anything V2 Small** | **Carte de profondeur complète par IA — ~50ms** | **✅ Retenue — universelle** |
| ARCore / ARKit | Profondeur native du smartphone | 🔮 Option future |

!!! tip "Stabilisation"
    Un filtre `GaussianBlur` est appliqué sur la carte de profondeur avant lecture pour stabiliser les valeurs et éviter les variations dues aux textures ou couleurs des objets.

---

## `detector.py` — Surveillance d'obstacles

Ce module analyse chaque frame envoyée par Flutter (toutes les 5 secondes).

### Système de priorité des alertes

| Priorité | Classes concernées | Message vocal généré |
|----------|--------------------|----------------------|
| 4 | fire | « Danger extrême ! Feu détecté, reculez immédiatement ! » |
| 3 | knife | « Danger ! Couteau détecté, soyez prudent ! » |
| 2 | stairs | « Attention ! Escaliers, arrêtez-vous ! » |
| 1 | tout obstacle proche | « Obstacle détecté, [objet_fr] à votre [direction]. » |
| 0 | objet loin | Aucune alerte générée |

### NMS inter-modèles

Les deux modèles YOLO peuvent détecter le même objet simultanément. Un algorithme de **NMS (Non-Maximum Suppression)** basé sur l'**IoU (Intersection over Union, seuil 0.5)** fusionne les détections redondantes en conservant uniquement celle avec la meilleure confiance.

---

## `finder.py` — Recherche et guidage d'objet

Ce module guide l'utilisateur pas à pas vers un objet spécifique. Il est appelé en boucle par Flutter toutes les 5 secondes.

### Système de 5 zones de direction

| Zone (ratio horizontal) | Instruction vocale générée |
|-------------------------|---------------------------|
| < 20% — extrême gauche | « Tournez franchement à gauche vers [objet]. » |
| 20–40% — légèrement gauche | « Tournez légèrement à gauche, [objet] est presque là. » |
| 40–60% — centre | « [objet] est droit devant vous, avancez. » / « Vous y êtes, tendez la main. » |
| 60–80% — légèrement droite | « Tournez légèrement à droite et avancez vers [objet]. » |
| > 80% — extrême droite | « Tournez franchement à droite vers [objet]. » |

**Condition d'arrivée** : `distance = "très proche"` ET `position = "centre"` → `reached=true` → Flutter arrête la boucle.

---

## `localizer.py` — Identification de pièce

Ce module identifie la pièce courante en analysant les objets visibles. Chaque pièce possède une « signature » d'objets caractéristiques avec des poids de confiance.

| Niveau de confiance | Message TTS généré | Exemple |
|---------------------|--------------------|---------|
| ≥ 70% | « Vous êtes dans la [pièce]. » | Lit, télé, horloge → chambre 85% |
| 40–69% | « Je pense que vous êtes dans la [pièce]. » | Ordinateur → bureau 55% |
| < 40% | « Vous êtes peut-être dans la [pièce], je ne suis pas certain. » | Chaise seule → 20% |

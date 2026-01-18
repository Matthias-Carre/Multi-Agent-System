# Multi-Agent Bridge Builder

Une simulation multi-agents en Python avec Pygame où des agents collaborent pour construire un pont et atteindre un objectif.

## Description

Dans cette simulation, trois types d'agents travaillent ensemble pour accomplir une mission : construire un pont au-dessus d'une rivière et atteindre la zone d'arrivée de l'autre côté.

## Les Agents

| Agent | Couleur | Rôle |
|-------|---------|------|
| **Gatherer** (Récolteur) | 🔴 Rouge | Récolte le bois des arbres et le ramène au woodstock |
| **Builder** (Constructeur) | 🔵 Bleu | Prend le bois du woodstock et construit le pont |
| **Manager** (Chef de projet) | 🟡 Jaune | Coordonne les agents et doit atteindre l'arrivée |

### Comportements des agents

- **Gatherers** : Cherchent du bois visible, le récoltent et le déposent au woodstock (case jaune)
- **Builders** : Récupèrent le bois du woodstock et construisent le pont section par section
- **Manager** : 
  - Communique les directions aux agents à proximité (portée de 2 cases)
  - Peut indiquer des ressources sur toute la carte
  - Se dirige vers l'arrivée une fois le pont construit
  - Privilégie d'aller vers la droite après avoir traversé le pont

## Objectif

La simulation se termine avec succès quand le **Manager** (agent jaune) atteint la case d'**arrivée** (case orange) de l'autre côté de la rivière.

## Contrôles

| Touche | Action |
|--------|--------|
| `ESPACE` | Pause / Reprendre |
| `R` | Redémarrer la simulation |
| `↑` / `↓` | Augmenter / Diminuer la portée de vision |
| `←` / `→` | Diminuer / Augmenter la vitesse (FPS) |

## Éléments de la carte

| Élément | Couleur | Description |
|---------|---------|-------------|
| Terre | 🟤 Marron | Zone traversable |
| Eau | 🔵 Bleu foncé | Infranchissable (nécessite un pont) |
| Bois | 🟢 Vert | Ressource à récolter |
| woodstock | 🟡 Jaune | Dépôt de ressources |
| Pont | ⬜ Gris clair | Construit par les builders |
| Arrivée | 🟠 Orange | Objectif final |
| Mur | ⬛ Gris foncé | Infranchissable |

## Structure du projet

```
Game/
├── main.py           # Point d'entrée
├── game.py           # Classe principale du jeu
├── agent.py          # Logique des agents
├── environment.py    # Gestion de l'environnement
├── renderer.py       # Rendu graphique
├── input_handler.py  # Gestion des entrées
├── config.py         # Configuration
├── map_loader.py     # Chargement des cartes
└── maps/             # Fichiers de cartes
    ├── example_map.txt
    └── test01_map.txt
```

## Configuration

Les paramètres peuvent être modifiés dans `config.py` :

```python
VISION_RANGE = 9          # Portée de vision des agents
WOOD_NEEDED_PER_BRIDGE_CELL = 2  # Bois nécessaire par section de pont
PREVENT_COLLISION = True  # Empêcher les collisions entre agents
STUCK_THRESHOLD = 3       # Seuil avant changement de direction
TREE_DENSITY = 0.1        # Densité d'arbres (0-1)
MAP_FILE = "./maps/example_map.txt"  # Carte à charger
```

## Créer une carte personnalisée

Créez un fichier `.txt` dans le dossier `maps/` avec le format suivant :

```
# Légende :
# 0 = Terre
# 1 = Eau
# 2 = woodstock
# 3 = Mur

0 0 0 0 1 1 1 0 0 0
0 0 2 0 1 1 1 0 0 0
0 0 0 0 1 1 1 0 0 0
```

Les arbres sont ajoutés automatiquement sur les cases de terre selon `TREE_DENSITY`.
L'arrivée est placée automatiquement à droite de la carte.

## Lancement

```bash
cd Game
python main.py
```

## Dépendances

- Python 3.x
- Pygame

```bash
pip install pygame
```


"""Configuration centrale du jeu"""

class Config:
    """Configuration centrale du jeu"""
    # Dimensions de base
    WIDTH, HEIGHT = 800, 400
    UI_HEIGHT = 130
    WINDOW_HEIGHT = HEIGHT + UI_HEIGHT
    CELL_SIZE = 20
    COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
    
    # Paramètres agents
    VISION_RANGE = 9  # Modifiable au runtime
    MANAGER_RANGE = 2
    
    # Nombre d'agents
    NUM_GATHERERS = 4   # Nombre de récolteurs (rouge)
    NUM_BUILDERS = 3    # Nombre de constructeurs (bleu)
    NUM_MANAGERS = 3    # Nombre de chefs de projet (jaune)
    
    # Couleurs
    WOOD = (34, 139, 34)
    WATER = (0, 105, 148)
    LAND = (139, 69, 19)
    BRIDGE = (200, 200, 200)
    woodstock = (255, 215, 0)
    ARRIVAL = (255, 165, 0)
    WALL = (50, 50, 50)  # Case infranchissable (gris foncé)
    GATHERER_COLOR = (255, 100, 100)
    BUILDER_COLOR = (100, 100, 255)
    MANAGER_COLOR = (255, 255, 100)
    
    # Paramètres jeu
    WOOD_NEEDED_PER_BRIDGE_CELL = 2
    RIVER_COL_START = COLS // 2 - 1
    RIVER_WIDTH = 4
    PREVENT_COLLISION = True  # Empêche 2 agents d'aller sur la même case
    STUCK_THRESHOLD = 3  # Nombre de tours avant qu'un agent bloqué change de direction (0 = désactivé)
    
    # Carte personnalisée (None = carte par défaut, sinon chemin vers le fichier)
    MAP_FILE = None #"./maps/test01_map.txt" # "./maps/example_map.txt"
    TREE_DENSITY = 0.1  # Densité d'arbres sur les cases simples (0-1)

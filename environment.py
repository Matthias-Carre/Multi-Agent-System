"""Gestion de l'environnement du jeu"""
import pygame
import random
from config import Config
from map_loader import MapLoader

class Environment:
    """Gère la grille de jeu, les ressources et le pont"""
    
    def __init__(self, map_file=None):
        self.woodstock = {"wood": 0}
        self.arrival_reached = False
        self.bridge_cells = []
        self.bridge_progress = {}
        self.bridge_row = None  # Ligne partagée pour la construction du pont
        
        # Charger la carte (personnalisée ou par défaut)
        map_path = map_file or Config.MAP_FILE
        if map_path:
            self._load_custom_map(map_path)
        else:
            self._setup_default_map()
    
    def _load_custom_map(self, filepath):
        """Charge une carte personnalisée depuis un fichier"""
        grid, woodstock_pos, arrival_pos = MapLoader.load_map(filepath)
        
        if grid is None:
            print("Chargement de la carte par défaut...")
            self._setup_default_map()
            return
        
        self.grid = grid
        
        # Stocker les dimensions
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        
        # woodstock
        if woodstock_pos:
            self.woodstock_pos = woodstock_pos
        else:
            self.woodstock_pos = (5, self.rows // 2)
            if 0 <= self.woodstock_pos[1] < self.rows and 0 <= self.woodstock_pos[0] < self.cols:
                self.grid[self.woodstock_pos[1]][self.woodstock_pos[0]] = Config.woodstock
        
        # Point d'arrivée
        if arrival_pos:
            self.arrival_pos = arrival_pos
        else:
            self.arrival_pos = (self.cols - 3, self.rows // 2)
            if 0 <= self.arrival_pos[1] < self.rows and 0 <= self.arrival_pos[0] < self.cols:
                self.grid[self.arrival_pos[1]][self.arrival_pos[0]] = Config.ARRIVAL
        
        # Ajouter des arbres aléatoirement
        self.grid = MapLoader.add_trees(self.grid, tree_density=Config.TREE_DENSITY)
        
        print(f"Carte chargée: {self.rows}x{self.cols}")
    
    def _setup_default_map(self):
        """Initialise la carte par défaut"""
        self.rows = Config.ROWS
        self.cols = Config.COLS
        self.grid = [[Config.LAND for _ in range(self.cols)] for _ in range(self.rows)]
        self.woodstock_pos = (5, self.rows // 2)
        self.arrival_pos = (self.cols - 3, self.rows // 2)
        self._setup_map_terrain()

    def _setup_map_terrain(self):
        """Ajoute le terrain par défaut (rivière, bois, etc.)"""
        # Créer une rivière au milieu
        for r in range(Config.ROWS):
            for c in range(Config.RIVER_COL_START, Config.RIVER_COL_START + Config.RIVER_WIDTH):
                self.grid[r][c] = Config.WATER
        
        # Ajouter des zones de bois à gauche
        for _ in range(30):
            r = random.randint(0, Config.ROWS-1)
            c = random.randint(0, Config.RIVER_COL_START - 2)
            if (c, r) != self.woodstock_pos:
                self.grid[r][c] = Config.WOOD
        
        # Marquer le woodstock et l'arrivée
        self.grid[self.woodstock_pos[1]][self.woodstock_pos[0]] = Config.woodstock
        self.grid[self.arrival_pos[1]][self.arrival_pos[0]] = Config.ARRIVAL

    def check_arrival(self, x, y):
        """Vérifie si l'agent a atteint l'arrivée"""
        if (x, y) == self.arrival_pos:
            self.arrival_reached = True

    def add_bridge_section(self, row, col):
        """Ajoute une section de pont si assez de bois"""
        if self.grid[row][col] != Config.WATER:
            return False
        
        # Définir la ligne de pont partagée si pas encore définie
        if self.bridge_row is None:
            self.bridge_row = row
        
        key = (row, col)
        if key not in self.bridge_progress:
            self.bridge_progress[key] = 0
        
        self.bridge_progress[key] += 1
        
        if self.bridge_progress[key] >= Config.WOOD_NEEDED_PER_BRIDGE_CELL:
            self.grid[row][col] = Config.BRIDGE
            self.bridge_cells.append(key)
            return True
        return False

    def is_bridge_complete(self):
        """Vérifie si le pont traverse toute la rivière (cherche une ligne complète de ponts)"""
        rows = len(self.grid)
        cols = len(self.grid[0]) if self.grid else 0
        
        # Trouver les colonnes d'eau
        water_cols = set()
        for r in range(rows):
            for c in range(cols):
                if self.grid[r][c] == Config.WATER:
                    water_cols.add(c)
        
        if not water_cols:
            return True  # Pas d'eau = pont "complet"
        
        min_water_col = min(water_cols)
        max_water_col = max(water_cols)
        
        # Vérifier si une ligne a un pont complet traversant toute l'eau
        for r in range(rows):
            has_bridge = all(
                self.grid[r][c] == Config.BRIDGE 
                for c in range(min_water_col, max_water_col + 1)
                if (r, c) in [(row, col) for row in range(rows) for col in range(cols) if self.grid[row][col] in [Config.WATER, Config.BRIDGE]]
            )
            # Simplification: vérifier si toutes les cases entre min et max water col sont des ponts
            row_complete = True
            for c in range(min_water_col, max_water_col + 1):
                if self.grid[r][c] == Config.WATER:
                    row_complete = False
                    break
            if row_complete and any(self.grid[r][c] == Config.BRIDGE for c in range(min_water_col, max_water_col + 1)):
                return True
        return False

    def draw(self, screen):
        """Dessine l'environnement"""
        rows = len(self.grid)
        cols = len(self.grid[0]) if self.grid else 0
        
        for r in range(rows):
            for c in range(cols):
                color = self.grid[r][c]
                pygame.draw.rect(screen, color, 
                               (c*Config.CELL_SIZE, r*Config.CELL_SIZE, 
                                Config.CELL_SIZE, Config.CELL_SIZE))
                pygame.draw.rect(screen, (0, 0, 0), 
                               (c*Config.CELL_SIZE, r*Config.CELL_SIZE, 
                                Config.CELL_SIZE, Config.CELL_SIZE), 1)
                
                # Indicateur visuel pour le woodstock
                if (c, r) == self.woodstock_pos:
                    pygame.draw.rect(screen, (255, 255, 255), 
                                   (c*Config.CELL_SIZE, r*Config.CELL_SIZE, 
                                    Config.CELL_SIZE, Config.CELL_SIZE), 3)

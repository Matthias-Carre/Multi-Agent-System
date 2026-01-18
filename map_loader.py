"""Chargement de cartes personnalisées depuis des fichiers texte"""
import random
from config import Config


class MapLoader:
    """Charge et parse des fichiers de carte"""
    
    # Correspondance entre les codes du fichier et les types de terrain
    TILE_CODES = {
        '0': 'LAND',       # Case simple
        '1': 'WATER',      # Eau
        '2': 'woodstock',  # Dépôt de bois
        '3': 'WALL',       # Case infranchissable
        '4': 'ARRIVAL',    # Point d'arrivée
    }
    
    @staticmethod
    def load_map(filepath):
        """
        Charge une carte depuis un fichier texte.
        
        Format du fichier:
        - 0 = case simple (land)
        - 1 = eau (water)
        - 2 = dépôt de bois (woodstock)
        - 3 = case infranchissable (wall)
        - 4 = point d'arrivée (arrival)
        
        Retourne: (grid, woodstock_pos, arrival_pos) ou (None, None, None) si erreur
        """
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            # Parser les lignes
            map_data = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):  # Ignorer les lignes vides et commentaires
                    continue
                # Supporter les formats: "0 1 0 1" ou "0101" ou "0,1,0,1"
                if ' ' in line:
                    row = line.split()
                elif ',' in line:
                    row = line.split(',')
                else:
                    row = list(line)
                map_data.append(row)
            
            if not map_data:
                print("Erreur: Fichier de carte vide")
                return None, None
            
            # Convertir en grille de couleurs
            rows = len(map_data)
            cols = len(map_data[0])
            
            grid = [[Config.LAND for _ in range(cols)] for _ in range(rows)]
            woodstock_pos = None
            arrival_pos = None
            
            for r, row in enumerate(map_data):
                for c, code in enumerate(row):
                    code = code.strip()
                    if code == '0':
                        grid[r][c] = Config.LAND
                    elif code == '1':
                        grid[r][c] = Config.WATER
                    elif code == '2':
                        grid[r][c] = Config.woodstock
                        woodstock_pos = (c, r)
                    elif code == '3':
                        grid[r][c] = Config.WALL
                    elif code == '4':
                        grid[r][c] = Config.ARRIVAL
                        arrival_pos = (c, r)
                    else:
                        print(f"Avertissement: Code inconnu '{code}' à la position ({r}, {c})")
                        grid[r][c] = Config.LAND
            
            return grid, woodstock_pos, arrival_pos
            
        except FileNotFoundError:
            print(f"Erreur: Fichier '{filepath}' introuvable")
            return None, None, None
        except Exception as e:
            print(f"Erreur lors du chargement de la carte: {e}")
            return None, None, None
    
    @staticmethod
    def add_trees(grid, tree_count=30, tree_density=0.1):
        """
        Ajoute des arbres aléatoirement sur les cases simples (LAND).
        
        Args:
            grid: La grille de jeu
            tree_count: Nombre d'arbres à ajouter (si tree_density=0)
            tree_density: Pourcentage de cases LAND qui deviennent des arbres (0-1)
        
        Retourne: La grille modifiée
        """
        rows = len(grid)
        cols = len(grid[0])
        
        # Trouver toutes les cases LAND
        land_cells = []
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == Config.LAND:
                    land_cells.append((r, c))
        
        if not land_cells:
            return grid
        
        # Calculer le nombre d'arbres à placer
        if tree_density > 0:
            num_trees = int(len(land_cells) * tree_density)
        else:
            num_trees = min(tree_count, len(land_cells))
        
        # Placer les arbres aléatoirement
        random.shuffle(land_cells)
        for i in range(num_trees):
            r, c = land_cells[i]
            grid[r][c] = Config.WOOD
        
        return grid
    
    @staticmethod
    def create_example_map(filepath):
        """Crée un fichier de carte exemple"""
        example_map = """# Exemple de carte
# 0 = case simple, 1 = eau, 2 = woodstock, 3 = mur
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 2 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0
"""
        with open(filepath, 'w') as f:
            f.write(example_map)
        print(f"Carte exemple créée: {filepath}")

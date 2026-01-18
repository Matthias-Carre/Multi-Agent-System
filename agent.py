"""Gestion des agents du jeu"""
import random
from config import Config

# Variable globale pour la portée de vision (modifiable au runtime)
vision_range = Config.VISION_RANGE

class Agent:
    """Représente un agent dans la simulation"""
    
    # Liste partagée de tous les agents (mise à jour par le jeu)
    all_agents = []
    
    def __init__(self, x, y, role):
        self.x = x
        self.y = y
        self.role = role  # "gatherer", "builder", "manager"
        self.inventory = None
        self.target = None
        self.state = "idle"
        self.last_pos = (x, y)  # Dernière position
        self.stuck_counter = 0  # Compteur de tours sur la même case
        self.ignore_target_turns = 0  # Compteur de tours à ignorer l'objectif
        self.manager_hint = None  # Direction donnée par le manager (x, y)
    
    def _check_stuck(self, env):
        """Vérifie si l'agent est bloqué et ignore l'objectif pendant 15 tours si nécessaire"""
        if Config.STUCK_THRESHOLD <= 0:
            return False
        
        # Si on ignore l'objectif, décrémenter le compteur
        if self.ignore_target_turns > 0:
            self.ignore_target_turns -= 1
            return True  # Continuer à ignorer
        
        if (self.x, self.y) == self.last_pos:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.last_pos = (self.x, self.y)
        
        if self.stuck_counter >= Config.STUCK_THRESHOLD:
            # Ignorer l'objectif pendant 15 tours
            self.ignore_target_turns = 15
            self.target = None
            self.stuck_counter = 0
            return True
        return False
    
    def _is_cell_occupied(self, x, y):
        """Vérifie si une case est occupée par un autre agent"""
        if not Config.PREVENT_COLLISION:
            return False
        for agent in Agent.all_agents:
            if agent is not self and agent.x == x and agent.y == y:
                return True
        return False
    
    def _is_walkable(self, env, x, y):
        """Vérifie si une case est traversable (pas d'eau, pas de mur)"""
        rows = len(env.grid) if env.grid else 0
        cols = len(env.grid[0]) if env.grid and env.grid[0] else 0
        if not (0 <= x < cols and 0 <= y < rows):
            return False
        cell = env.grid[y][x]
        return cell != Config.WATER and cell != Config.WALL

    def move_towards(self, env, target_x, target_y):
        """Déplace l'agent vers une cible en évitant l'eau, les murs et les collisions"""
        candidates = []
        if self.x < target_x:
            candidates.append((self.x + 1, self.y))
        elif self.x > target_x:
            candidates.append((self.x - 1, self.y))

        if self.y < target_y:
            candidates.append((self.x, self.y + 1))
        elif self.y > target_y:
            candidates.append((self.x, self.y - 1))

        for nx, ny in candidates:
            if self._is_walkable(env, nx, ny):
                if not self._is_cell_occupied(nx, ny):
                    self.x, self.y = nx, ny
                    env.check_arrival(self.x, self.y)
                    return

    def random_walk(self, env):
        """Déplacement aléatoire limité à la grille et évitant l'eau, les murs et les collisions"""
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if self._is_walkable(env, nx, ny):
                if not self._is_cell_occupied(nx, ny):
                    self.x, self.y = nx, ny
                    env.check_arrival(self.x, self.y)
                    return

    def _is_visible(self, x, y):
        """Vérifie si une position est visible"""
        global vision_range
        return abs(self.x - x) + abs(self.y - y) <= vision_range

    def _iter_visible_cells(self, env=None):
        """Itère sur toutes les cellules visibles"""
        global vision_range
        
        # Utiliser les dimensions réelles de la grille si disponible
        if env is not None and env.grid:
            rows = len(env.grid)
            cols = len(env.grid[0]) if env.grid else 0
        else:
            rows = Config.ROWS
            cols = Config.COLS
        
        for dy in range(-vision_range, vision_range + 1):
            for dx in range(-vision_range, vision_range + 1):
                if abs(dx) + abs(dy) > vision_range:
                    continue
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < cols and 0 <= ny < rows:
                    yield nx, ny

    def find_nearest_resource(self, env, resource_type):
        """Trouve la ressource la plus proche non occupée"""
        min_dist = float('inf')
        nearest = None

        for c, r in self._iter_visible_cells(env):
            if env.grid[r][c] == resource_type:
                # Vérifier si la case n'est pas occupée par un autre agent
                if self._is_cell_occupied(c, r):
                    continue
                dist = abs(self.x - c) + abs(self.y - r)
                if dist < min_dist:
                    min_dist = dist
                    nearest = (c, r)
        return nearest

    def _find_visible_bridge(self, env):
        """Trouve le pont le plus à droite visible dans le champ de vision"""
        rightmost_bridge = None
        for c, r in self._iter_visible_cells(env):
            if env.grid[r][c] == Config.BRIDGE:
                if rightmost_bridge is None or c > rightmost_bridge[0]:
                    rightmost_bridge = (c, r)
        return rightmost_bridge
    
    def _get_bridge_continuation(self, env, bridge_pos):
        """Trouve la prochaine case d'eau adjacente pour continuer un pont (priorité à droite)"""
        bx, by = bridge_pos
        cols = len(env.grid[0]) if env.grid else 0
        rows = len(env.grid)
        
        # Priorité 1: case d'eau à DROITE du pont
        nx, ny = bx + 1, by
        if 0 <= nx < cols and 0 <= ny < rows:
            if env.grid[ny][nx] == Config.WATER:
                if not self._is_cell_occupied(nx, ny):
                    return (nx, ny)
        
        # Priorité 2: autres directions (gauche, haut, bas) seulement si pas d'eau à droite
        for dx, dy in [(-1, 0), (0, -1), (0, 1)]:
            nx, ny = bx + dx, by + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if env.grid[ny][nx] == Config.WATER:
                    if not self._is_cell_occupied(nx, ny):
                        return (nx, ny)
        return None

    def find_bridge_location(self, env):
        """Trouve un emplacement pour construire le pont (priorité: à droite d'un pont existant)"""
        cols = len(env.grid[0]) if env.grid else 0
        rows = len(env.grid)
        
        # Priorité 1: Chercher le pont le plus à droite visible et continuer à sa droite
        rightmost_bridge = None
        for c, r in self._iter_visible_cells(env):
            if env.grid[r][c] == Config.BRIDGE:
                if rightmost_bridge is None or c > rightmost_bridge[0]:
                    rightmost_bridge = (c, r)
        
        if rightmost_bridge is not None:
            # Vérifier s'il y a de l'eau à droite de ce pont
            rx, ry = rightmost_bridge
            if rx + 1 < cols and env.grid[ry][rx + 1] == Config.WATER:
                if not self._is_cell_occupied(rx + 1, ry):
                    return (rx + 1, ry)
            
            # Sinon, chercher de l'eau adjacente à n'importe quel pont visible
            for c, r in self._iter_visible_cells(env):
                if env.grid[r][c] == Config.BRIDGE:
                    continuation = self._get_bridge_continuation(env, (c, r))
                    if continuation:
                        return continuation
            return None
        
        # Sinon, chercher n'importe quelle case d'eau visible non occupée
        for c, r in self._iter_visible_cells(env):
            if env.grid[r][c] == Config.WATER:
                if not self._is_cell_occupied(c, r):
                    return (c, r)
        return None

    def find_bridge_location_global(self, env):
        """Trouve un emplacement pour construire le pont dans toute la grille (priorité à droite)"""
        rows = len(env.grid)
        cols = len(env.grid[0]) if env.grid else 0
        
        # Priorité 1: Trouver le pont le plus à droite et chercher de l'eau à sa droite
        rightmost_bridge = None
        for r in range(rows):
            for c in range(cols):
                if env.grid[r][c] == Config.BRIDGE:
                    if rightmost_bridge is None or c > rightmost_bridge[0]:
                        rightmost_bridge = (c, r)
        
        if rightmost_bridge is not None:
            rx, ry = rightmost_bridge
            # Vérifier s'il y a de l'eau à droite
            if rx + 1 < cols and env.grid[ry][rx + 1] == Config.WATER:
                return (rx + 1, ry)
        
        # Priorité 2: Chercher de l'eau adjacente à n'importe quel pont (priorité droite)
        for r in range(rows):
            for c in range(cols):
                if env.grid[r][c] == Config.BRIDGE:
                    # D'abord à droite
                    if c + 1 < cols and env.grid[r][c + 1] == Config.WATER:
                        return (c + 1, r)
                    # Puis autres directions
                    for dx, dy in [(-1, 0), (0, -1), (0, 1)]:
                        nx, ny = c + dx, r + dy
                        if 0 <= nx < cols and 0 <= ny < rows:
                            if env.grid[ny][nx] == Config.WATER:
                                return (nx, ny)
        
        # Sinon, chercher une case d'eau au milieu de la carte
        middle_row = rows // 2
        # Chercher d'abord au milieu, puis s'éloigner progressivement
        for offset in range(rows):
            for r in [middle_row + offset, middle_row - offset]:
                if 0 <= r < rows:
                    for c in range(cols):
                        if env.grid[r][c] == Config.WATER:
                            return (c, r)
        return None

    def update(self, env, agents=None):
        """Met à jour l'agent selon son rôle"""
        # Vérifier si l'agent est bloqué
        is_ignoring = self._check_stuck(env)
        
        # Si on ignore l'objectif, faire du random walk
        if is_ignoring:
            self.random_walk(env)
            return
        
        if self.role == "gatherer":
            self._update_gatherer(env)
        elif self.role == "builder":
            self._update_builder(env)
        elif self.role == "manager":
            self._update_manager(env, agents or [])

    def _update_gatherer(self, env):
        """Logique du récolteur"""
        woodstock_x, woodstock_y = env.woodstock_pos
        
        if not self.inventory:
            # Utiliser l'indice du manager si disponible
            if self.manager_hint:
                self.target = self.manager_hint
                self.manager_hint = None
            
            if self.target and not self._is_visible(*self.target):
                self.target = None
            
            # Si la cible est occupée, en chercher une autre
            if self.target and self._is_cell_occupied(*self.target):
                self.target = None

            if not self.target:
                self.target = self.find_nearest_resource(env, Config.WOOD)

            if self.target:
                target_x, target_y = self.target
                self.move_towards(env, target_x, target_y)
                
                if self.x == target_x and self.y == target_y:
                    if env.grid[target_y][target_x] == Config.WOOD:
                        self.inventory = "wood"
                        env.grid[target_y][target_x] = Config.LAND
                        self.target = None
                        self.state = "returning"
            else:
                self.random_walk(env)
        else:
            # Utiliser l'indice du manager pour le woodstock si disponible
            if self.manager_hint:
                self.target = self.manager_hint
                self.manager_hint = None
            
            if self._is_visible(woodstock_x, woodstock_y):
                self.move_towards(env, woodstock_x, woodstock_y)
                if self.x == woodstock_x and self.y == woodstock_y:
                    env.woodstock["wood"] += 1
                    self.inventory = None
                    self.state = "idle"
            elif self.target:
                self.move_towards(env, *self.target)
            else:
                self.random_walk(env)

    def _update_builder(self, env):
        """Logique du constructeur"""
        woodstock_x, woodstock_y = env.woodstock_pos
        
        if not self.inventory:
            # Utiliser l'indice du manager si disponible - SET comme cible prioritaire
            if self.manager_hint:
                self.target = self.manager_hint
                self.manager_hint = None
            
            if env.woodstock["wood"] > 0 and self._is_visible(woodstock_x, woodstock_y):
                self.move_towards(env, woodstock_x, woodstock_y)
                
                if self.x == woodstock_x and self.y == woodstock_y:
                    env.woodstock["wood"] -= 1
                    self.inventory = "wood"
                    self.target = None
            elif self.target:
                self.move_towards(env, *self.target)
            else:
                self.random_walk(env)
        else:
            # PRIORITÉ 1: Chercher le pont le plus avancé VISIBLE (priorité sur le manager)
            visible_bridge = self._find_visible_bridge(env)
            if visible_bridge is not None:
                bridge_target = self._get_bridge_continuation(env, visible_bridge)
                if bridge_target:
                    self.target = bridge_target
                    self.manager_hint = None  # Ignorer l'indication du manager
            
            # PRIORITÉ 2: Utiliser l'indice du manager si pas de pont visible
            if not self.target and self.manager_hint:
                self.target = self.manager_hint
                self.manager_hint = None
            
            # PRIORITÉ 3: Chercher n'importe quelle eau visible
            if not self.target:
                self.target = self.find_bridge_location(env)
            
            if self.target:
                target_x, target_y = self.target
                self.move_towards(env, target_x, target_y)
                
                # Vérifier si on peut construire
                if abs(self.x - target_x) <= 1 and abs(self.y - target_y) <= 1:
                    success = env.add_bridge_section(target_y, target_x)
                    if success or env.grid[target_y][target_x] != Config.WATER:
                        self.inventory = None
                        self.target = None
                        self.state = "idle"
            else:
                self.random_walk(env)

    def _update_manager(self, env, agents):
        """Logique du chef de projet - communique les directions aux agents adjacents et va vers l'arrivée"""
        
        arrival_x, arrival_y = env.arrival_pos
        
        # Priorité 1: Si l'arrivée est visible, s'y diriger
        if self._is_visible(arrival_x, arrival_y):
            self.move_towards(env, arrival_x, arrival_y)
            # Vérifier si on a atteint l'arrivée
            if self.x == arrival_x and self.y == arrival_y:
                env.arrival_reached = True
        # Priorité 2: Si le pont est complet, trouver et traverser ce pont
        elif env.is_bridge_complete():
            # Trouver la position du pont complet
            complete_bridge_pos = self._find_complete_bridge(env)
            if complete_bridge_pos:
                bridge_row = complete_bridge_pos[1]
                # Vérifier si on est déjà passé de l'autre côté du pont complet
                if self._is_past_complete_bridge(env, bridge_row):
                    # Reprendre la marche aléatoire après avoir traversé
                    self.random_walk(env)
                else:
                    # Se diriger vers le pont complet (d'abord aller à la bonne ligne, puis traverser)
                    if self.y != bridge_row:
                        # D'abord aller à la ligne du pont
                        self.move_towards(env, self.x, bridge_row)
                    else:
                        # Ensuite traverser le pont (aller vers la droite du pont)
                        cols = len(env.grid[0]) if env.grid else 0
                        # Trouver la fin du pont (côté droit)
                        end_bridge_x = complete_bridge_pos[0]
                        for c in range(complete_bridge_pos[0], cols):
                            if env.grid[bridge_row][c] == Config.BRIDGE:
                                end_bridge_x = c
                            else:
                                break
                        self.move_towards(env, end_bridge_x + 1, bridge_row)
            else:
                # Pas de pont trouvé, random walk
                self.random_walk(env)
        else:
            # Sinon, se déplacer aléatoirement
            self.random_walk(env)
        
        # Communiquer avec les agents adjacents (distance <= 2)
        for other in agents:
            if other is self:
                continue
            
            # Vérifier si l'autre agent est à 2 cases de distance ou moins
            distance = abs(self.x - other.x) + abs(self.y - other.y)
            if distance > 2:
                continue

            # Communiquer avec les gatherers
            if other.role == "gatherer":
                if not other.inventory:
                    # Donner la direction vers le bois le plus proche (sur toute la carte)
                    target = self._find_nearest_resource_global(env, Config.WOOD)
                    if target:
                        other.manager_hint = target
                else:
                    # Donner la direction vers le woodstock
                    other.manager_hint = env.woodstock_pos

            # Communiquer avec les builders
            if other.role == "builder":
                if other.inventory:
                    # Donner la direction vers le pont le plus avancé (le plus à droite)
                    target = self.find_bridge_location_global(env)
                    if target:
                        other.manager_hint = target
                        other.target = target  # Forcer la cible immédiatement
                else:
                    # Donner la direction vers le woodstock
                    if env.woodstock["wood"] > 0:
                        other.manager_hint = env.woodstock_pos
    
    def _is_past_bridge(self, env):
        """Vérifie si l'agent est sur le pont ou l'a traversé (à droite de la rivière)"""
        # Vérifier si on est sur une case de pont
        if env.grid[self.y][self.x] == Config.BRIDGE:
            return True
        # Vérifier si on est à droite de la dernière case de pont
        for bx, by in env.bridge_cells:
            if self.x > bx:
                return True
        return False
    
    def _is_past_complete_bridge(self, env, bridge_row):
        """Vérifie si l'agent a traversé le pont complet sur la ligne donnée"""
        cols = len(env.grid[0]) if env.grid else 0
        
        # Trouver la colonne max d'eau
        max_water_col = 0
        for c in range(cols):
            if env.grid[bridge_row][c] == Config.WATER or env.grid[bridge_row][c] == Config.BRIDGE:
                max_water_col = max(max_water_col, c)
        
        # L'agent est passé s'il est à droite du pont ET sur la bonne ligne (ou proche)
        return self.x > max_water_col and abs(self.y - bridge_row) <= 2
    
    def _find_complete_bridge(self, env):
        """Trouve la position d'entrée du pont complet (le plus proche de l'agent)"""
        rows = len(env.grid)
        cols = len(env.grid[0]) if env.grid else 0
        
        # Trouver les colonnes d'eau
        water_cols = set()
        for r in range(rows):
            for c in range(cols):
                if env.grid[r][c] == Config.WATER:
                    water_cols.add(c)
        
        if not water_cols:
            return None
        
        min_water_col = min(water_cols)
        max_water_col = max(water_cols)
        
        # Trouver les lignes où le pont est complet
        complete_bridge_rows = []
        for r in range(rows):
            row_complete = True
            for c in range(min_water_col, max_water_col + 1):
                if env.grid[r][c] == Config.WATER:
                    row_complete = False
                    break
            if row_complete and any(env.grid[r][c] == Config.BRIDGE for c in range(min_water_col, max_water_col + 1)):
                complete_bridge_rows.append(r)
        
        if not complete_bridge_rows:
            return None
        
        # Trouver le pont complet le plus proche de l'agent
        best_row = None
        min_dist = float('inf')
        for r in complete_bridge_rows:
            dist = abs(self.y - r)
            if dist < min_dist:
                min_dist = dist
                best_row = r
        
        # Retourner la position d'entrée du pont (première case de pont sur cette ligne)
        if best_row is not None:
            return (min_water_col, best_row)
        
        return None
    
    def _move_right_priority(self, env):
        """Déplacement avec priorité vers la droite"""
        cols = len(env.grid[0]) if env.grid else 0
        rows = len(env.grid)
        
        # Priorité: droite, puis haut/bas aléatoire, puis gauche
        directions = [(1, 0)]  # Droite d'abord
        if random.random() < 0.5:
            directions.extend([(0, -1), (0, 1)])  # Haut puis bas
        else:
            directions.extend([(0, 1), (0, -1)])  # Bas puis haut
        directions.append((-1, 0))  # Gauche en dernier
        
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if self._is_walkable(env, nx, ny):
                if not self._is_cell_occupied(nx, ny):
                    self.x, self.y = nx, ny
                    env.check_arrival(self.x, self.y)
                    return
        
        # Si aucune direction n'est possible, rester sur place
        pass
    
    def _find_nearest_resource_global(self, env, resource_type):
        """Trouve la ressource la plus proche sur toute la carte"""
        rows = len(env.grid)
        cols = len(env.grid[0]) if env.grid else 0
        min_dist = float('inf')
        nearest = None

        for r in range(rows):
            for c in range(cols):
                if env.grid[r][c] == resource_type:
                    dist = abs(self.x - c) + abs(self.y - r)
                    if dist < min_dist:
                        min_dist = dist
                        nearest = (c, r)
        return nearest

import pygame
import random

# --- CONFIGURATION ---
class Config:
    """Configuration centrale du jeu"""
    # Dimensions
    WIDTH, HEIGHT = 800, 400
    UI_HEIGHT = 100
    WINDOW_HEIGHT = HEIGHT + UI_HEIGHT
    CELL_SIZE = 20
    COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
    
    # Paramètres agents
    VISION_RANGE = 9  # Modifiable au runtime
    MANAGER_RANGE = 2
    
    # Couleurs
    WOOD = (34, 139, 34)
    WATER = (0, 105, 148)
    LAND = (139, 69, 19)
    BRIDGE = (200, 200, 200)
    woodstock = (255, 215, 0)
    ARRIVAL = (255, 165, 0)
    GATHERER_COLOR = (255, 100, 100)
    BUILDER_COLOR = (100, 100, 255)
    MANAGER_COLOR = (255, 255, 100)
    
    # Paramètres jeu
    WOOD_NEEDED_PER_BRIDGE_CELL = 2
    RIVER_COL_START = COLS // 2 - 1
    RIVER_WIDTH = 3

# Alias pour compatibilité
WIDTH, HEIGHT = Config.WIDTH, Config.HEIGHT
UI_HEIGHT = Config.UI_HEIGHT
WINDOW_HEIGHT = Config.WINDOW_HEIGHT
CELL_SIZE = Config.CELL_SIZE
COLS, ROWS = Config.COLS, Config.ROWS
VISION_RANGE = Config.VISION_RANGE
MANAGER_RANGE = Config.MANAGER_RANGE
WOOD, WATER, LAND, BRIDGE = Config.WOOD, Config.WATER, Config.LAND, Config.BRIDGE
woodstock, ARRIVAL = Config.woodstock, Config.ARRIVAL
GATHERER_COLOR, BUILDER_COLOR, MANAGER_COLOR = Config.GATHERER_COLOR, Config.BUILDER_COLOR, Config.MANAGER_COLOR
WOOD_NEEDED_PER_BRIDGE_CELL = Config.WOOD_NEEDED_PER_BRIDGE_CELL
RIVER_COL_START, RIVER_WIDTH = Config.RIVER_COL_START, Config.RIVER_WIDTH

class Environment:
    def __init__(self):
        self.grid = [[LAND for _ in range(COLS)] for _ in range(ROWS)]
        self.woodstock = {"wood": 0}
        self.woodstock_pos = (5, ROWS // 2)  # Position du dépôt
        self.arrival_pos = (COLS - 3, ROWS // 2)
        self.arrival_reached = False
        self.bridge_cells = []  # Liste des cellules du pont construites
        self.bridge_progress = {}  # Progression par cellule {(row, col): wood_count}
        self._setup_map()

    def _setup_map(self):
        # Créer une rivière au milieu
        for r in range(ROWS):
            for c in range(RIVER_COL_START, RIVER_COL_START + RIVER_WIDTH):
                self.grid[r][c] = WATER
        
        # Ajouter des zones de bois à gauche (côté de départ)
        for _ in range(30):
            r = random.randint(0, ROWS-1)
            c = random.randint(0, RIVER_COL_START - 2)
            if (c, r) != self.woodstock_pos:
                self.grid[r][c] = WOOD
        
        # Marquer la zone du woodstock
        self.grid[self.woodstock_pos[1]][self.woodstock_pos[0]] = woodstock
        # Marquer le point d'arrivée
        self.grid[self.arrival_pos[1]][self.arrival_pos[0]] = ARRIVAL

    def check_arrival(self, x, y):
        if (x, y) == self.arrival_pos:
            self.arrival_reached = True

    def add_bridge_section(self, row, col):
        """Ajoute une section de pont si assez de bois"""
        if self.grid[row][col] != WATER:
            return False
        
        key = (row, col)
        if key not in self.bridge_progress:
            self.bridge_progress[key] = 0
        
        self.bridge_progress[key] += 1
        
        if self.bridge_progress[key] >= WOOD_NEEDED_PER_BRIDGE_CELL:
            self.grid[row][col] = BRIDGE
            self.bridge_cells.append(key)
            return True
        return False

    def is_bridge_complete(self):
        """Vérifie si le pont traverse toute la rivière"""
        # Pour chaque ligne, vérifier s'il y a un chemin de pont
        for r in range(ROWS):
            has_bridge = all(
                self.grid[r][c] == BRIDGE 
                for c in range(RIVER_COL_START, RIVER_COL_START + RIVER_WIDTH)
            )
            if has_bridge:
                return True
        return False

    def draw(self, screen):
        for r in range(ROWS):
            for c in range(COLS):
                color = self.grid[r][c]
                pygame.draw.rect(screen, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                # Bordures pour mieux voir
                pygame.draw.rect(screen, (0, 0, 0), (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
                
                # Indicateur visuel pour le woodstock
                if (c, r) == self.woodstock_pos:
                    pygame.draw.rect(screen, (255, 255, 255), (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

class Agent:
    def __init__(self, x, y, role):
        self.x = x
        self.y = y
        self.role = role # "gatherer" (récolteur) ou "builder" (bâtisseur)
        self.inventory = None
        self.target = None
        self.state = "idle"  # idle, moving, gathering, building

    def move_towards(self, env, target_x, target_y):
        """Déplace l'agent vers une cible en évitant l'eau"""
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
            if 0 <= nx < COLS and 0 <= ny < ROWS and env.grid[ny][nx] != WATER:
                self.x, self.y = nx, ny
                env.check_arrival(self.x, self.y)
                return

    def random_walk(self, env):
        """Déplacement aléatoire limité à la grille et évitant l'eau"""
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and env.grid[ny][nx] != WATER:
                self.x, self.y = nx, ny
                env.check_arrival(self.x, self.y)
                return
            # Si aucune case libre (entouré d'eau), ne bouge pas

    def _is_visible(self, x, y):
        return abs(self.x - x) + abs(self.y - y) <= VISION_RANGE

    def _iter_visible_cells(self):
        for dy in range(-VISION_RANGE, VISION_RANGE + 1):
            for dx in range(-VISION_RANGE, VISION_RANGE + 1):
                if abs(dx) + abs(dy) > VISION_RANGE:
                    continue
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < COLS and 0 <= ny < ROWS:
                    yield nx, ny

    def find_nearest_resource(self, env, resource_type):
        """Trouve la ressource la plus proche"""
        min_dist = float('inf')
        nearest = None

        for c, r in self._iter_visible_cells():
            if env.grid[r][c] == resource_type:
                dist = abs(self.x - c) + abs(self.y - r)
                if dist < min_dist:
                    min_dist = dist
                    nearest = (c, r)
        return nearest

    def find_bridge_location(self, env):
        """Trouve un emplacement pour construire le pont"""
        # Priorité 1: chercher une case d'eau à droite d'un pont existant
        for c, r in self._iter_visible_cells():
            if RIVER_COL_START <= c < RIVER_COL_START + RIVER_WIDTH:
                if env.grid[r][c] == BRIDGE:
                    # Vérifier d'abord à droite (dx=1)
                    nc, nr = c + 1, r
                    if RIVER_COL_START <= nc < RIVER_COL_START + RIVER_WIDTH:
                        if 0 <= nr < ROWS and env.grid[nr][nc] == WATER:
                            return (nc, nr)
        
        # Priorité 2: chercher n'importe quelle case d'eau adjacente à un pont
        for c, r in self._iter_visible_cells():
            if RIVER_COL_START <= c < RIVER_COL_START + RIVER_WIDTH:
                if env.grid[r][c] == BRIDGE:
                    # Autres directions (haut, bas, gauche)
                    for dx, dy in [(0, 1), (0, -1), (-1, 0)]:
                        nc, nr = c + dx, r + dy
                        if RIVER_COL_START <= nc < RIVER_COL_START + RIVER_WIDTH:
                            if 0 <= nr < ROWS and env.grid[nr][nc] == WATER:
                                return (nc, nr)
        
        # Priorité 3: n'importe quelle case d'eau dans la rivière
        for c, r in self._iter_visible_cells():
            if RIVER_COL_START <= c < RIVER_COL_START + RIVER_WIDTH:
                if env.grid[r][c] == WATER:
                    return (c, r)
        return None

    def find_bridge_location_global(self, env):
        """Trouve un emplacement pour construire le pont dans toute la grille"""
        # Cherche une cellule d'eau dans toute la rivière
        for r in range(ROWS):
            for c in range(RIVER_COL_START, RIVER_COL_START + RIVER_WIDTH):
                if env.grid[r][c] == WATER:
                    return (c, r)
        return None

    def update(self, env, agents=None):
        """Met à jour l'agent selon son rôle"""
        
        if self.role == "gatherer":
            self._update_gatherer(env)
        elif self.role == "builder":
            self._update_builder(env)
        elif self.role == "manager":
            self._update_manager(env, agents or [])

    def _update_gatherer(self, env):
        """Logique du récolteur: cherche du bois -> ramène au woodstock"""
        woodstock_x, woodstock_y = env.woodstock_pos
        
        if not self.inventory:
            # Chercher du bois
            if self.target and not self._is_visible(*self.target):
                self.target = None

            if not self.target:
                self.target = self.find_nearest_resource(env, WOOD)

            if self.target:
                target_x, target_y = self.target
                self.move_towards(env, target_x, target_y)
                
                # Si on atteint le bois
                if self.x == target_x and self.y == target_y:
                    if env.grid[target_y][target_x] == WOOD:
                        self.inventory = "wood"
                        env.grid[target_y][target_x] = LAND  # Consommer la ressource
                        self.target = None
                        self.state = "returning"
            else:
                self.random_walk(env)
        else:
            # Ramener au woodstock
            if self._is_visible(woodstock_x, woodstock_y):
                self.move_towards(env, woodstock_x, woodstock_y)
                if self.x == woodstock_x and self.y == woodstock_y:
                    env.woodstock["wood"] += 1
                    self.inventory = None
                    self.state = "idle"
            else:
                self.random_walk(env)

    def _update_builder(self, env):
        """Logique du constructeur: prend du bois -> construit le pont"""
        woodstock_x, woodstock_y = env.woodstock_pos
        
        if not self.inventory:
            # Aller chercher du bois au woodstock
            if env.woodstock["wood"] > 0 and self._is_visible(woodstock_x, woodstock_y):
                self.move_towards(env, woodstock_x, woodstock_y)
                
                if self.x == woodstock_x and self.y == woodstock_y:
                    env.woodstock["wood"] -= 1
                    self.inventory = "wood"
                    self.target = None
            else:
                self.random_walk(env)
        else:
            # Aller construire le pont
            if self.target and not self._is_visible(*self.target):
                self.target = None
 
            if not self.target:
                self.target = self.find_bridge_location(env)
            
            if self.target:
                target_x, target_y = self.target
                self.move_towards(env, target_x, target_y)
                
                # Si on est adjacent à l'emplacement du pont
                if abs(self.x - target_x) <= 1 and abs(self.y - target_y) <= 1:
                    # Construire seulement si c'est vraiment de l'eau
                    success = env.add_bridge_section(target_y, target_x)
                    if success or env.grid[target_y][target_x] != WATER:
                        # Vidé l'inventaire uniquement si construction réussie ou case déjà construite
                        self.inventory = None
                        self.target = None
                        self.state = "idle"
            else:
                self.random_walk(env)

    def _update_manager(self, env, agents):
        """Chef de projet: oriente les agents proches vers une cible utile"""
        for other in agents:
            if other is self:
                continue
            if abs(self.x - other.x) + abs(self.y - other.y) > MANAGER_RANGE:
                continue

            if other.role == "gatherer" and not other.inventory:
                # Oriente vers du bois visible par le chef
                target = self.find_nearest_resource(env, WOOD)
                if target:
                    other.target = target

            if other.role == "builder":
                if other.inventory:
                    # Le manager indique où construire même hors de sa vision
                    target = self.find_bridge_location_global(env)
                    if target:
                        other.target = target
                else:
                    sx, sy = env.woodstock_pos
                    if self._is_visible(sx, sy):
                        other.target = env.woodstock_pos

        # Patrouille simple
        self.random_walk(env)


class Renderer:
    """Gère tout l'affichage graphique"""
    
    def __init__(self, font):
        self.font = font
        self.victory_font = pygame.font.Font(None, 72)
    
    def draw_ui(self, screen, env, simulation_speed):
        """Affiche l'interface utilisateur"""
        # Fond pour le texte
        ui_bg = pygame.Surface((WIDTH, UI_HEIGHT))
        ui_bg.fill((0, 0, 0))
        ui_bg.set_alpha(180)
        screen.blit(ui_bg, (0, HEIGHT))
        
        # Statistiques
        self._draw_statistics(screen, env)
        self._draw_parameters(screen, simulation_speed)
        self._draw_victory_message(screen, env)
    
    def _draw_statistics(self, screen, env):
        """Affiche les statistiques du jeu"""
        base_y = HEIGHT + 10
        
        wood_text = self.font.render(f"Bois au woodstock: {env.woodstock['wood']}", True, (255, 255, 255))
        bridge_text = self.font.render(f"Sections de pont construites: {len(env.bridge_cells)}", True, (255, 255, 255))
        in_progress = sum(1 for prog in env.bridge_progress.values() if prog < WOOD_NEEDED_PER_BRIDGE_CELL)
        progress_text = self.font.render(f"Sections en construction: {in_progress}", True, (255, 255, 255))
        
        screen.blit(wood_text, (10, base_y))
        screen.blit(bridge_text, (10, base_y + 30))
        screen.blit(progress_text, (10, base_y + 60))
    
    def _draw_parameters(self, screen, simulation_speed):
        """Affiche les paramètres modifiables"""
        base_y = HEIGHT + 10
        vision_text = self.font.render(f"Portée de vision: {VISION_RANGE}", True, (255, 255, 255))
        speed_text = self.font.render(f"Vitesse: {simulation_speed} FPS", True, (255, 255, 255))
        
        screen.blit(vision_text, (WIDTH - 250, base_y))
        screen.blit(speed_text, (WIDTH - 250, base_y + 30))
    
    def _draw_victory_message(self, screen, env):
        """Affiche le message de victoire"""
        if env.arrival_reached:
            victory_text = self.victory_font.render("ARRIVEE ATTEINTE!", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(victory_text, text_rect)
        elif env.is_bridge_complete():
            victory_text = self.victory_font.render("PONT TERMINE!", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(victory_text, text_rect)
    
    def draw_agents(self, screen, agents):
        """Dessine tous les agents"""
        for agent in agents:
            # Couleur selon le rôle
            if agent.role == "manager":
                color = MANAGER_COLOR
            elif agent.role == "gatherer":
                color = GATHERER_COLOR
            else:
                color = BUILDER_COLOR
            
            # Dessiner l'agent
            pygame.draw.circle(screen, color,
                             (agent.x * CELL_SIZE + CELL_SIZE//2,
                              agent.y * CELL_SIZE + CELL_SIZE//2), 6)
            
            # Indicateur d'inventaire
            if agent.inventory:
                if agent.role == "builder":
                    pygame.draw.rect(screen, (255, 255, 255),
                                   (agent.x * CELL_SIZE + CELL_SIZE//2 - 3,
                                    agent.y * CELL_SIZE + CELL_SIZE//2 - 3, 6, 6))
                else:
                    pygame.draw.circle(screen, (34, 139, 34),
                                     (agent.x * CELL_SIZE + CELL_SIZE//2,
                                      agent.y * CELL_SIZE + CELL_SIZE//2), 3)
    
    def draw_instructions(self, screen):
        """Affiche les instructions"""
        instructions = self.font.render("ESPACE: Pause | R: Redémarrer | ↑↓: Vision | ←→: Vitesse", True, (255, 255, 255))
        screen.blit(instructions, (WIDTH - 550, 10))


class InputHandler:
    """Gère les entrées utilisateur"""
    
    @staticmethod
    def handle_events(events, game_state):
        """Traite les événements pygame"""
        global VISION_RANGE
        
        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                InputHandler._handle_keypress(event.key, game_state)
        return True
    
    @staticmethod
    def _handle_keypress(key, game_state):
        """Gère les touches clavier"""
        global VISION_RANGE
        
        if key == pygame.K_SPACE:
            game_state['paused'] = not game_state['paused']
        elif key == pygame.K_r:
            game_state['reset'] = True
        elif key == pygame.K_UP:
            VISION_RANGE = min(VISION_RANGE + 1, 20)
        elif key == pygame.K_DOWN:
            VISION_RANGE = max(VISION_RANGE - 1, 1)
        elif key == pygame.K_LEFT:
            game_state['speed'] = max(game_state['speed'] - 1, 1)
        elif key == pygame.K_RIGHT:
            game_state['speed'] = min(game_state['speed'] + 1, 60)


class Game:
    """Classe principale gérant la simulation"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Multi-Agent Bridge Builder")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        
        self.renderer = Renderer(self.font)
        self.env = None
        self.agents = []
        self.state = {
            'running': True,
            'paused': False,
            'reset': False,
            'speed': 10
        }
        
        self.reset_simulation()
    
    def reset_simulation(self):
        """Réinitialise la simulation"""
        self.env = Environment()
        self.agents = []
        
        # 4 récolteurs
        for i in range(4):
            self.agents.append(Agent(2, 2 + i * 3, "gatherer"))
        # 3 constructeurs
        for i in range(3):
            self.agents.append(Agent(2, 10 + i * 3, "builder"))
        # 1 chef de projet
        self.agents.append(Agent(6, ROWS // 2, "manager"))
        
        self.state['reset'] = False
    
    def update(self):
        """Met à jour la simulation"""
        if self.state['reset']:
            self.reset_simulation()
        
        if not self.state['paused'] and not self.env.arrival_reached:
            for agent in self.agents:
                agent.update(self.env, self.agents)
    
    def draw(self):
        """Dessine tout"""
        self.screen.fill((50, 50, 50))
        self.env.draw(self.screen)
        self.renderer.draw_agents(self.screen, self.agents)
        self.renderer.draw_ui(self.screen, self.env, self.state['speed'])
        self.renderer.draw_instructions(self.screen)
        pygame.display.flip()
    
    def run(self):
        """Boucle principale du jeu"""
        while self.state['running']:
            events = pygame.event.get()
            self.state['running'] = InputHandler.handle_events(events, self.state)
            
            self.update()
            self.draw()
            
            if self.env.arrival_reached:
                pygame.time.delay(1200)
                break
            
            self.clock.tick(self.state['speed'])
        
        pygame.quit()


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

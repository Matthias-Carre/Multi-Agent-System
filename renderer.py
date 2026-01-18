"""Gestion du rendu graphique"""
import pygame
from config import Config
import agent

class Renderer:
    """Gère tout l'affichage graphique"""
    
    def __init__(self, font):
        self.font = font
        self.victory_font = pygame.font.Font(None, 72)
    
    def draw_ui(self, screen, env, simulation_speed):
        """Affiche l'interface utilisateur"""
        ui_bg = pygame.Surface((Config.WIDTH, Config.UI_HEIGHT))
        ui_bg.fill((0, 0, 0))
        ui_bg.set_alpha(180)
        screen.blit(ui_bg, (0, Config.HEIGHT))
        
        self._draw_statistics(screen, env)
        self._draw_parameters(screen, simulation_speed)
        self._draw_victory_message(screen, env)
    
    def _draw_statistics(self, screen, env):
        """Affiche les statistiques du jeu"""
        base_y = Config.HEIGHT + 35
        
        wood_text = self.font.render(f"Bois dans la réserve: {env.woodstock['wood']}", True, (255, 255, 255))
        bridge_text = self.font.render(f"Sections de pont construites: {len(env.bridge_cells)}", True, (255, 255, 255))
        in_progress = sum(1 for prog in env.bridge_progress.values() if prog < Config.WOOD_NEEDED_PER_BRIDGE_CELL)
        #progress_text = self.font.render(f"Sections en construction: {in_progress}", True, (255, 255, 255))
        
        screen.blit(wood_text, (10, base_y))
        screen.blit(bridge_text, (10, base_y + 30))
        #screen.blit(progress_text, (10, base_y + 60))
    
    def _draw_parameters(self, screen, simulation_speed):
        """Affiche les paramètres modifiables"""
        base_y = Config.HEIGHT + 35
        vision_text = self.font.render(f"Portée de vision: {agent.vision_range}", True, (255, 255, 255))
        speed_text = self.font.render(f"Vitesse: {simulation_speed} ", True, (255, 255, 255))
        
        screen.blit(vision_text, (Config.WIDTH - 250, base_y))
        screen.blit(speed_text, (Config.WIDTH - 250, base_y + 30))
    
    def _draw_victory_message(self, screen, env):
        """Affiche le message de victoire"""
        if env.arrival_reached:
            victory_text = self.victory_font.render("ARRIVEE ATTEINTE!", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(Config.WIDTH // 2, Config.HEIGHT // 2))
            screen.blit(victory_text, text_rect)
    
    def draw_agents(self, screen, agents):
        """Dessine tous les agents"""
        for ag in agents:
            if ag.role == "manager":
                color = Config.MANAGER_COLOR
            elif ag.role == "gatherer":
                color = Config.GATHERER_COLOR
            else:
                color = Config.BUILDER_COLOR
            
            pygame.draw.circle(screen, color,
                             (ag.x * Config.CELL_SIZE + Config.CELL_SIZE//2,
                              ag.y * Config.CELL_SIZE + Config.CELL_SIZE//2), 6)
            
            if ag.inventory:
                if ag.role == "builder":
                    pygame.draw.rect(screen, (255, 255, 255),
                                   (ag.x * Config.CELL_SIZE + Config.CELL_SIZE//2 - 3,
                                    ag.y * Config.CELL_SIZE + Config.CELL_SIZE//2 - 3, 6, 6))
                else:
                    pygame.draw.circle(screen, (34, 139, 34),
                                     (ag.x * Config.CELL_SIZE + Config.CELL_SIZE//2,
                                      ag.y * Config.CELL_SIZE + Config.CELL_SIZE//2), 3)
    
    def draw_instructions(self, screen):
        """Affiche les instructions en haut du panneau UI"""
        instructions = self.font.render("ESPACE: Pause | R: Redémarrer | up down: Vision | left right: Vitesse", 
                                       True, (255, 255, 255))
        # Centrer horizontalement en haut du panneau UI
        text_rect = instructions.get_rect(center=(Config.WIDTH // 2, Config.HEIGHT + 15))
        screen.blit(instructions, text_rect)

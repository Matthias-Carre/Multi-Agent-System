"""Classe principale du jeu"""
import pygame
from config import Config
from environment import Environment
from agent import Agent
from renderer import Renderer
from input_handler import InputHandler

class Game:
    """Classe principale gérant la simulation"""
    
    def __init__(self):
        pygame.init()
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
        
        # Créer la fenêtre après avoir chargé l'environnement pour adapter la taille
        self._resize_window()
    
    def _resize_window(self):
        """Redimensionne la fenêtre en fonction de la carte"""
        width = self.env.cols * Config.CELL_SIZE
        height = self.env.rows * Config.CELL_SIZE + Config.UI_HEIGHT
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Multi-Agent Bridge Builder")
    
    def reset_simulation(self):
        """Réinitialise la simulation"""
        self.env = Environment()
        self.agents = []
        
        rows = self.env.rows
        cols = self.env.cols
        
        # Récolteurs (positions adaptées à la taille de la carte)
        for i in range(Config.NUM_GATHERERS):
            y = min(2 + i * 2, rows - 1)
            self.agents.append(Agent(min(2, cols - 1), y, "gatherer"))
        # Constructeurs
        for i in range(Config.NUM_BUILDERS):
            y = min(2 + i * 2, rows - 1)
            self.agents.append(Agent(min(3, cols - 1), y, "builder"))
        # Chefs de projet (managers)
        for i in range(Config.NUM_MANAGERS):
            y = min(rows // 2 + i * 2, rows - 1)
            self.agents.append(Agent(min(4, cols - 1), y, "manager"))
        
        # Mettre à jour la liste partagée des agents pour la détection de collision
        Agent.all_agents = self.agents
        
        self.state['reset'] = False
    
    def update(self):
        """Met à jour la simulation"""
        if self.state['reset']:
            self.reset_simulation()
        
        if not self.state['paused'] and not self.env.arrival_reached:
            # Le manager s'exécute EN PREMIER pour distribuer les hints
            for agent in self.agents:
                if agent.role == "manager":
                    agent.update(self.env, self.agents)
            
            # Ensuite les autres agents
            for agent in self.agents:
                if agent.role != "manager":
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
            
            self.clock.tick(self.state['speed'])
        
        pygame.quit()

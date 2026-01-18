"""Gestion des entrées utilisateur"""
import pygame
import agent

class InputHandler:
    """Gère les entrées utilisateur"""
    
    @staticmethod
    def handle_events(events, game_state):
        """Traite les événements pygame"""
        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                InputHandler._handle_keypress(event.key, game_state)
        return True
    
    @staticmethod
    def _handle_keypress(key, game_state):
        """Gère les touches clavier"""
        if key == pygame.K_SPACE:
            game_state['paused'] = not game_state['paused']
        elif key == pygame.K_r:
            game_state['reset'] = True
        elif key == pygame.K_UP:
            agent.vision_range = min(agent.vision_range + 1, 20)
        elif key == pygame.K_DOWN:
            agent.vision_range = max(agent.vision_range - 1, 1)
        elif key == pygame.K_LEFT:
            game_state['speed'] = max(game_state['speed'] - 1, 1)
        elif key == pygame.K_RIGHT:
            game_state['speed'] = min(game_state['speed'] + 1, 60)

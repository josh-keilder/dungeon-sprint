import pygame
from globals import *
from Components.component import Component

class Health(Component):
    def __init__(self, node, max_health):
        super().__init__(node)
        # --- ATTRIBUTES ---
        self.max_health = max_health
        self.current = max_health

    def take_damage(self, amount):
        self.current = max(0, self.current - amount)
    
    def heal(self, amount):
        self.current = min(self.max_health, self.current + amount)
        
    def is_dead(self):
        return self.current <= 0
    

class HealthBar(Component):
    def __init__(self, node, max_health, width = TILESIZE, height = 4, shrink_speed = 50, is_player = False, pos=(20, 20)):
        super().__init__(node)
        # --- VISUALS ---
        self.width, self.height = width, height
        self.pos = pos # Fixed screen position for player UI

        # --- ATTRIBUTES ---
        self.is_player = is_player       # Player Health bar check
        self.max_health = max_health     # Setting max health
        self.display_health = max_health # what's visually shown
        self.shrink_speed = shrink_speed # The speed in which the health bar shrinks from the entity being damaged

    def update(self, dt=0):
        health_comp = getattr(self.node, 'health', None)

        if not health_comp:
            return

        target_health = health_comp.current
        
        # Smoothly move display_health towards the current health
        if self.display_health != target_health:
            diff = target_health - self.display_health
            # Move display_health by shrink_speed per second
            step = self.shrink_speed * dt
            
            if abs(diff) < step:
                self.display_health = target_health
            else:
                self.display_health += step if diff > 0 else -step
    
    def draw(self, screen, camera=None):
        health_comp = getattr(self.node, 'health', None)
        if not health_comp: return

        # Hide health bar if enemy is at full health (optional, keeps screen clean)
        if not self.is_player and self.display_health >= self.max_health:
            return

        # Determine draw position
        if self.is_player:
            x, y = self.pos
        else:
            # Position above entity
            x = self.node.rect.centerx - self.width // 2
            y = self.node.rect.top - 8
            if camera:
                x -= camera.x
                y -= camera.y

        # Draw Background (Red or Gray)
        bg_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(screen, GRAY, bg_rect)

        # Draw Progress
        ratio = self.display_health / self.max_health
        if ratio > 0:
            fg_rect = pygame.Rect(x, y, self.width * ratio, self.height)
            # Change color based on health percentage
            color = GREEN if ratio > 0.5 else RED
            pygame.draw.rect(screen, color, fg_rect)
    
import pygame
from globals import *

class Health:
    def __init__(self, max_health):
        self.max_health = max_health
        self.current = max_health

    def take_damage(self, amount):
        self.current = max(0, self.current - amount)
    
    def heal(self, amount):
        self.current = min(self.max_health, self.current + amount)
        
    def is_dead(self):
        return self.current <= 0
    


class HealthBar:
    def __init__(self, max_health, width = TILESIZE, height = 4, shrink_speed = 0.5, is_player = False, pos=(20, 20)):

        # --- VISUALS ---
        self.width, self.height = width, height
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_frect()
        self.pos = pos # only used if it's a player bar

        # --- HEALTH BAR ATTRIBUTES ---
        self.is_player = is_player       # Player Health bar check
        self.max_health = max_health
        self.display_health = max_health # what's visually shown
        self.current_health = max_health # actual entity health
        self.shrink_speed = shrink_speed # The speed in which the health bar shrinks from the entity being damaged

    def update(self, current_health, entity_rect):
        self.current_health = max(0, min(current_health , self.max_health))
        
        # Smoothly move display_health towards the current_health
        if self.display_health > self.current_health:
            self.display_health -= self.shrink_speed
            if self.display_health < self.current_health:
                self.display_health = self.current_health
        elif self.display_health < self.current_health:
            self.display_health += self.shrink_speed
            if self.display_health > self.current_health:
                self.display_health = self.current_health

        # Calculate ratio
        display_ratio = self.display_health / self.max_health

        # Draw gray background and green front bar
        self.image.fill(GRAY)
        pygame.draw.rect(self.image, GREEN, (0, 0, self.width * display_ratio, self.height))

        # Position above entity
        if not self.is_player:
            self.rect.midbottom = (entity_rect.centerx, entity_rect.top - 4)
        else:
            self.rect.topleft = self.pos
    
    def draw(self, screen, camera):
        if self.is_player: # Fixed position on screen
            screen.blit(self.image, self.rect.topleft)  
        else: # Above entity
            screen.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
    
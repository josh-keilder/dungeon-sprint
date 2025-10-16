import pygame
from globals import *
from ui_objects.create_outline import create_outline

pygame.mixer.init()

class Button():
    def __init__(self, screen, image, pos =(0,0)):
        self.image = image
        self.rect = self.image.get_frect()
        self.rect.topleft = pos
        self.screen = screen
        self.hovered = False
        self.clicked = False
        self.mask = pygame.mask.from_surface(self.image)
        
        
        # Loads all the button sound effects once
        try:
            self.hover_sound = pygame.mixer.Sound("Assets/Sounds/Button_Hover.wav")
            self.click_sound = pygame.mixer.Sound("Assets/Sounds/Button_Click.wav")
        except Exception:
            self.hover_sound = None
            self.click_sound = None

        self.hover_sound.set_volume(0.3)
        self.click_sound.set_volume(0.3)

    def draw(self):
        # puts the buttons on screen at the rect topleft coordinates
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

        # Draws the outline if the cursor is hovering the button
        if self.hovered == True:
            create_outline(self.screen, self, WHITE, (self.rect.x, self.rect.y))

    def update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            # play hover sound only once when the mouse enters the button area
            if not self.hovered:
                if self.hover_sound:
                    self.hover_sound.play()
                self.hovered = True
        else:
            # reset hover state and cursor when mouse leaves
            self.hovered = False

    def is_clicked(self) -> bool:
        action = False
        # # checks if mouse is over the button, draws the outline and checks if player clicked the button
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True    
                self.click_sound.play()  

        # Resets our clicked state        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action